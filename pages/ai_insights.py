"""
Insight AI Page.

Provides a premium ChatGPT-like assistant workspace.
Converses in natural, jargon-free English to explain data concepts.
Uses the active dataset in memory as context.
"""

import streamlit as st
import pandas as pd
import numpy as np

from components.section_header import render_section_header
from components.empty_state import render_empty_state
from components.glass_card import glass_card_panel


def generate_conversational_response(query: str, df: pd.DataFrame, filename: str) -> str:
    """
    Generate a dynamic, natural language explanation of the dataset based on query intent.
    Explains concepts in plain English, references columns, and avoids technical jargon.
    Tracks context in session state to enable multi-turn conversations.
    """
    import numpy as np
    import pandas as pd
    import streamlit as st

    # 1. Initialize Context & Pronoun Resolver
    q_lower = query.lower().strip()
    last_context = st.session_state.get("chat_context", "")

    # Check if query uses pronouns
    uses_pronouns = any(word in q_lower.split() for word in ["them", "it", "those", "that", "these"])
    if uses_pronouns and last_context:
        if any(w in q_lower for w in ["clean", "fix", "impute", "remove", "drop", "fill"]):
            if last_context == "missing":
                q_lower += " missing values"
            elif last_context == "outliers":
                q_lower += " outliers"
            elif last_context.startswith("col_"):
                col_name = last_context.replace("col_", "")
                q_lower += f" {col_name}"

    # Extract dataset properties
    num_cols = list(df.select_dtypes(include=[np.number]).columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "bool"]).columns)
    all_cols = list(df.columns)
    total_rows = len(df)
    
    # Pre-calculate quality metrics to use in conversation
    missing_cells = int(df.isnull().sum().sum())
    missing_pct = (missing_cells / df.size * 100) if df.size > 0 else 0.0
    duplicate_rows = int(df.duplicated().sum())
    
    # Outliers count
    outliers_count = 0
    outlier_cols = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        if df[col].notna().sum() > 3:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower = q1 - 1.5 * iqr
                upper = q3 + 1.5 * iqr
                mask = (df[col] < lower) | (df[col] > upper)
                cnt = int(mask.sum())
                if cnt > 0:
                    outlier_cols[col] = cnt
                    outliers_count += cnt

    # Helper to check matching column name in query
    referenced_col = None
    for col in all_cols:
        if col.lower() in q_lower:
            referenced_col = col
            break

    # Confidence and Context variables
    confidence = "High"
    confidence_reason = ""
    response_body = ""
    suggested_questions = []

    # ─────────────────────────────────────────────────────────────────────────
    # INTENT ROUTER
    # ─────────────────────────────────────────────────────────────────────────
    
    # A. Specific Business Questions
    # A1. "Why are sales decreasing?"
    if "sales decreasing" in q_lower or "why sales" in q_lower or "sales drop" in q_lower or "decrease in sales" in q_lower or "revenue drop" in q_lower:
        sales_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["sales", "revenue", "amount"])), None)
        date_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["date", "time", "year", "month"])), None)
        
        if sales_col and date_col:
            st.session_state["chat_context"] = "sales_trend"
            try:
                # Group sales by date period to find slope
                temp_df = df[[date_col, sales_col]].dropna().copy()
                temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors="coerce")
                temp_df = temp_df.dropna()
                if len(temp_df) > 5:
                    temp_df = temp_df.sort_values(by=date_col)
                    temp_df["idx"] = np.arange(len(temp_df))
                    slope, _ = np.polyfit(temp_df["idx"], temp_df[sales_col], 1)
                    
                    if slope < 0:
                        response_body = (
                            f"### Sales Decrease Analysis\n\n"
                            f"Analyzing the column **{sales_col}** over the timeline **{date_col}** reveals an overall **downward trend** "
                            f"(average drop of **{abs(slope):,.2f}** units per period).\n\n"
                            f"This decrease is typically driven by:\n"
                            f"- A drop in sales volumes in specific categories.\n"
                            f"- Seasonality patterns or outlier values skewing the end of the timeline.\n\n"
                            f"Go to the **Forecasting** page to project this trend forward and inspect model residuals."
                        )
                    else:
                        response_body = (
                            f"### Sales Trend Analysis\n\n"
                            f"Actually, my trend analysis on **{sales_col}** shows a **positive/increasing** slope of **{slope:,.2f}** per period. "
                            f"If there was a recent drop, it may be a minor outlier or seasonal fluctuation rather than a long-term decrease."
                        )
                else:
                    confidence = "Medium"
                    confidence_reason = "Dataset contains too few historical date records to perform a linear regression trend fit."
                    response_body = f"I see the sales column **{sales_col}** and date column **{date_col}**, but there are less than 5 valid chronological rows. A larger dataset is needed to determine the exact trajectory."
            except Exception as e:
                confidence = "Low"
                confidence_reason = f"Analysis error: {str(e)}"
                response_body = f"I detected sales variable **{sales_col}** and date **{date_col}** but encountered a parsing error during regression: {str(e)}."
        else:
            confidence = "Low"
            confidence_reason = "No sales/revenue or date variables detected in the uploaded dataset."
            response_body = "I cannot determine that from the uploaded dataset because it does not contain explicit timeline sales or revenue records."
        
        suggested_questions = [
            "Which columns are highly correlated?",
            "What should I clean first?",
            "Summarize the dataset"
        ]

    # A2. "Which customers perform best?"
    elif "customer" in q_lower or "client" in q_lower or "buyer" in q_lower:
        cust_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["customer", "client", "user", "buyer"])), None)
        val_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["sales", "revenue", "amount", "profit"])), None)
        
        if cust_col and val_col:
            st.session_state["chat_context"] = "customers"
            try:
                # Group and get top customers
                top_custs = df.groupby(cust_col)[val_col].sum().reset_index()
                top_custs = top_custs.sort_values(by=val_col, ascending=False).head(5)
                
                rows_html = ""
                for idx, row in enumerate(top_custs.itertuples(), 1):
                    rows_html += f"| {idx} | **{getattr(row, cust_col)}** | {getattr(row, val_col):,.2f} |\n"
                
                table_md = (
                    f"| Rank | Customer Group | Total {val_col} |\n"
                    f"|---|---|---|\n"
                    f"{rows_html}"
                )
                
                response_body = (
                    f"### Top Performing Customers\n\n"
                    f"Based on the dataset, the top performing groups in **{cust_col}** by total **{val_col}** are:\n\n"
                    f"{table_md}\n"
                    f"These customers represent your most valuable cohorts. Target marketing campaigns or retention programs toward these groups."
                )
            except Exception as e:
                confidence = "Low"
                confidence_reason = f"Aggregation error: {str(e)}"
                response_body = f"I found customer column **{cust_col}** and revenue column **{val_col}**, but encountered a calculation error: {str(e)}."
        else:
            confidence = "Low"
            confidence_reason = "No customer identifiers or numeric value columns found."
            response_body = "I cannot determine that from the uploaded dataset because no customer identifier or revenue variables were found."
            
        suggested_questions = [
            "Which region has the highest revenue?",
            "What should I clean first?",
            "Summarize the dataset"
        ]

    # A3. "Which region has the highest revenue?"
    elif "region" in q_lower or "country" in q_lower or "city" in q_lower or "state" in q_lower or "territory" in q_lower:
        geo_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["region", "country", "city", "state", "territory", "location"])), None)
        val_col = next((c for c in all_cols if any(kw in c.lower() for kw in ["sales", "revenue", "amount", "profit"])), None)
        
        if geo_col and val_col:
            st.session_state["chat_context"] = "region"
            try:
                top_geos = df.groupby(geo_col)[val_col].sum().reset_index()
                top_geos = top_geos.sort_values(by=val_col, ascending=False).head(5)
                
                rows_html = ""
                for idx, row in enumerate(top_geos.itertuples(), 1):
                    rows_html += f"| {idx} | **{getattr(row, geo_col)}** | {getattr(row, val_col):,.2f} |\n"
                    
                table_md = (
                    f"| Rank | Region/Location | Total {val_col} |\n"
                    f"|---|---|---|\n"
                    f"{rows_html}"
                )
                
                response_body = (
                    f"### Regional Performance Analysis\n\n"
                    f"The regional breakdown of **{geo_col}** aggregated by total **{val_col}** shows:\n\n"
                    f"{table_md}\n"
                    f"The top-performing location is **{top_geos.iloc[0][geo_col]}** with a total of **{top_geos.iloc[0][val_col]:,.2f}**."
                )
            except Exception as e:
                confidence = "Low"
                confidence_reason = f"Aggregation error: {str(e)}"
                response_body = f"I identified region variable **{geo_col}** and revenue column **{val_col}**, but encountered a grouping error: {str(e)}."
        else:
            confidence = "Low"
            confidence_reason = "No geographic fields or revenue variables detected."
            response_body = "I cannot determine that from the uploaded dataset because no regional or revenue variables were found."
            
        suggested_questions = [
            "Which customers perform best?",
            "What should I clean first?",
            "Summarize the dataset"
        ]

    # A4. "Which column should I remove?"
    elif "remove column" in q_lower or "column should i remove" in q_lower or "drop column" in q_lower or ("remove" in q_lower and "column" in q_lower):
        st.session_state["chat_context"] = "remove_column"
        removals = []
        
        # Check for constant columns
        const_cols = [c for c in all_cols if df[c].nunique() <= 1]
        for c in const_cols:
            removals.append(f"- **{c}**: This is a **constant column** with only 1 unique value. It offers zero statistical variance and should be removed.")
            
        # Check for heavily missing columns
        for c in all_cols:
            null_pct = df[c].isnull().sum() / total_rows
            if null_pct > 0.85:
                removals.append(f"- **{c}**: Contains **{null_pct * 100:.1f}% missing values**. With so many gaps, it cannot support reliable analysis.")
                
        # Check for high-cardinality ID columns
        for c in all_cols:
            if c not in const_cols:
                uniq = df[c].nunique()
                if uniq == total_rows and c.lower() in ["id", "index", "serial", "key", "pk", "uuid", "guid"]:
                    removals.append(f"- **{c}**: This appears to be a **unique identifier/key** column. It is not suitable as a feature in ML models, though it is useful as an index.")
                    
        if removals:
            response_body = (
                f"### Column Pruning Recommendations\n\n"
                f"I recommend removing or dropping the following columns to improve model performance and simplify your database structure:\n\n"
                + "\n".join(removals)
            )
        else:
            response_body = (
                f"### Column Pruning Recommendations\n\n"
                f"✓ **No columns require immediate removal.** All columns contain adequate variance, and none contain excessive missing cells (>85%) or redundant constant labels."
            )
            
        suggested_questions = [
            "What should I clean first?",
            "Is this dataset suitable for machine learning?",
            "Summarize the dataset"
        ]

    # A5. "What should I clean first?"
    elif "clean first" in q_lower or "what should i clean" in q_lower or "cleaning priority" in q_lower:
        st.session_state["chat_context"] = "cleaning_priority"
        priorities = []
        
        if duplicate_rows > 0:
            priorities.append(f"1. **Duplicate Rows ({duplicate_rows:,} records)**: Drop these first. Duplicate rows skew simple averages, count metrics twice, and lead to artificial inflation of values.")
        if missing_cells > 0:
            priorities.append(f"2. **Missing Values ({missing_cells:,} empty cells)**: Impute or fill these blanks next. Calculations will error or omit rows with missing cells, creating discrepancies.")
        if outliers_count > 0:
            priorities.append(f"3. **Extreme Outliers ({outliers_count:,} anomalies)**: Clip outliers using IQR limits. Outliers pull the mean away from the median, distorting baseline projections.")
            
        if priorities:
            response_body = (
                f"### Data Cleaning Priority Roadmap\n\n"
                f"Here is your recommended cleaning schedule based on the quality status of **{filename}**:\n\n"
                + "\n\n".join(priorities)
            )
        else:
            response_body = (
                f"### Data Cleaning Priority Roadmap\n\n"
                f"✓ **Your dataset is 100% clean!** There are no duplicates, missing cells, or extreme statistical outliers. You can proceed directly to forecasting or visualization."
            )
            
        suggested_questions = [
            "Is this dataset suitable for machine learning?",
            "Which column should I remove?",
            "Summarize the dataset"
        ]

    # A6. "Is this dataset suitable for machine learning?"
    elif "suitable for machine learning" in q_lower or "suitable for ml" in q_lower or "machine learning suitable" in q_lower or "ml suitability" in q_lower:
        st.session_state["chat_context"] = "ml_suitability"
        
        # ML metrics scorecard
        size_ok = "Pass" if total_rows >= 100 else "Fail"
        size_desc = f"{total_rows:,} rows (ideal is >100 rows)"
        
        null_ok = "Pass" if missing_pct < 20 else "Warning"
        null_desc = f"{missing_pct:.1f}% missing cells (ideal is <20%)"
        
        vars_ok = "Pass" if len(num_cols) >= 1 and len(cat_cols) >= 1 else "Warning"
        vars_desc = f"{len(num_cols)} Numeric, {len(cat_cols)} Categorical variables"
        
        suitability_score = "Highly Suitable"
        if size_ok == "Fail":
            suitability_score = "Unsuitable (Too small)"
        elif null_ok == "Warning" or vars_ok == "Warning":
            suitability_score = "Suitable after heavy cleaning"
            
        table_md = (
            f"| Metric Check | Status | Current Standing |\n"
            f"|---|---|---|\n"
            f"| **Dataset Size** | {size_ok} | {size_desc} |\n"
            f"| **Missing Data Rate** | {null_ok} | {null_desc} |\n"
            f"| **Feature Diversity** | {vars_ok} | {vars_desc} |\n"
        )
        
        response_body = (
            f"### Machine Learning Suitability Scorecard\n\n"
            f"**Overall Classification:** **{suitability_score}**\n\n"
            f"{table_md}\n"
            f"**Business Insight:** "
            f"{'Your dataset is ready for ML training. Go to the forecasting canvas to test projections.' if suitability_score == 'Highly Suitable' else 'I recommend cleaning missing cells and expanding sample sizes before modeling.'}"
        )
        
        suggested_questions = [
            "Which column should I remove?",
            "What should I clean first?",
            "Summarize the dataset"
        ]

    # B. Specific Column Query
    elif referenced_col:
        st.session_state["chat_context"] = f"col_{referenced_col}"
        col_type = "numerical" if referenced_col in num_cols else "categorical"
        null_count = int(df[referenced_col].isnull().sum())
        null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0.0
        
        response_body = f"### Column Profile: {referenced_col}\n\n"
        
        if col_type == "numerical":
            mean_val = df[referenced_col].mean()
            min_val = df[referenced_col].min()
            max_val = df[referenced_col].max()
            
            table_md = (
                f"| Statistic Metric | Computed Value |\n"
                f"|---|---|\n"
                f"| **Average (Mean)** | {mean_val:,.2f} |\n"
                f"| **Minimum Value** | {min_val:,.2f} |\n"
                f"| **Maximum Value** | {max_val:,.2f} |\n"
            )
            response_body += (
                f"This is a **numerical column** containing quantity measurements.\n\n"
                f"{table_md}\n"
            )
            if referenced_col in outlier_cols:
                response_body += (
                    f"⚠️ **Outliers Detected**: We found **{outlier_cols[referenced_col]} extreme values** "
                    f"that sit outside the normal IQR range. These can skew our averages.\n\n"
                )
        else:
            uniq_cnt = df[referenced_col].nunique()
            top_vals = df[referenced_col].value_counts().head(3).index.tolist()
            response_body += (
                f"This is a **categorical column** which groups data into labels.\n\n"
                f"- **Unique Classes**: {uniq_cnt}\n"
                f"- **Top Categories**: {', '.join(map(str, top_vals))}\n\n"
            )
            
        if null_count > 0:
            response_body += (
                f"⚠️ **Blank spots**: Contains **{null_count:,} missing cells** ({null_pct:.1f}%). "
                f"You should clean this column by imputing values."
            )
        else:
            response_body += "✓ **Data Completeness**: 100% complete, containing zero missing cells."
            
        suggested_questions = [
            f"What should I clean first?",
            "Which column should I remove?",
            "Summarize the dataset"
        ]

    # C. General Dataset Summary
    elif "summarize" in q_lower or "summary" in q_lower or "overall" in q_lower or "profile" in q_lower:
        st.session_state["chat_context"] = "summary"
        num_descr = f"**{len(num_cols)} columns with numbers** (like {', '.join(num_cols[:2])})" if num_cols else "no numerical columns"
        cat_descr = f"**{len(cat_cols)} columns with categories** (like {', '.join(cat_cols[:2])})" if cat_cols else "no text columns"
        
        response_body = (
            f"### Dataset Summary: {filename}\n\n"
            f"This dataset contains **{total_rows:,} rows** and **{len(all_cols)} variables**.\n\n"
            f"- **Numeric Columns**: {num_descr}\n"
            f"- **Categorical Columns**: {cat_descr}\n"
            f"- **Data Completeness**: **{100.0 - missing_pct:.2f}%** of cells are filled.\n"
            f"- **Anomalies**: {f'{duplicate_rows} duplicate rows' if duplicate_rows > 0 else 'No duplicates found'}."
        )
        
        suggested_questions = [
            "What should I clean first?",
            "Is this dataset suitable for machine learning?",
            "Which columns are highly correlated?"
        ]

    # D. Anomaly / Outliers / Missing Scan
    elif "anomal" in q_lower or "outlier" in q_lower or "extreme" in q_lower or "missing" in q_lower or "blank" in q_lower or "null" in q_lower:
        st.session_state["chat_context"] = "outliers" if "outlier" in q_lower else "missing"
        
        response_body = (
            f"### Anomaly & Quality Scan: {filename}\n\n"
            f"- **Missing Value Cells**: **{missing_cells:,} blanks** ({missing_pct:.2f}% of all cells).\n"
            f"- **Duplicate Rows**: **{duplicate_rows:,} records**.\n"
            f"- **Extreme Outliers**: **{outliers_count:,} anomalies** (out-of-bounds IQR values).\n\n"
        )
        
        if outliers_count > 0:
            top_outliers = sorted(outlier_cols.items(), key=lambda x: x[1], reverse=True)[:3]
            out_str = ", ".join([f"**{c}** ({cnt})" for c, cnt in top_outliers])
            response_body += f"Columns with the most outliers: {out_str}.\n"
            
        suggested_questions = [
            "What should I clean first?",
            "Which column should I remove?",
            "Summarize the dataset"
        ]

    # E. Predict Trends / Forecast
    elif "predict" in q_lower or "trend" in q_lower or "forecast" in q_lower or "future" in q_lower:
        st.session_state["chat_context"] = "forecast"
        date_cols = [c for c in all_cols if any(kw in c.lower() for kw in ["date", "time", "created", "updated"])]
        
        if date_cols and num_cols:
            response_body = (
                f"### Forecasting & Projections\n\n"
                f"We can project trends in **{filename}** by tracking how **{num_cols[0]}** changes over the timeline **{date_cols[0]}**.\n\n"
                f"To inspect this visually: \n"
                f"1. Navigate to the **Forecasting** workspace.\n"
                f"2. Select **{num_cols[0]}** as the Target Variable.\n"
                f"3. Select **{date_cols[0]}** as the Date Variable.\n\n"
                f"Our backend will fit actual historical data and extend a smoothed spline forecast into the future."
            )
        else:
            confidence = "Medium"
            confidence_reason = "No datetime columns were detected to support time-series forecast models."
            response_body = (
                f"### Forecasting & Projections\n\n"
                f"To run a forecast, the model requires at least one date/timeline variable and one numerical variable.\n\n"
                f"Currently, we have numerical variables like `{', '.join(num_cols[:2])}` but **no dates**. "
                f"We can project values sequentially by row indices, but temporal trend fitting is unavailable."
            )
            
        suggested_questions = [
            "What should I clean first?",
            "Which columns are highly correlated?",
            "Summarize the dataset"
        ]

    # F. Correlation Matrix
    elif "correlat" in q_lower or "relation" in q_lower or "heatmap" in q_lower:
        st.session_state["chat_context"] = "correlations"
        numeric_df = df.loc[:, ~df.isna().all()].select_dtypes(include=[np.number])
        if len(numeric_df.columns) >= 2:
            try:
                corr_matrix = numeric_df.corr().abs()
                upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                corrs = []
                for col in upper_tri.columns:
                    for row in upper_tri.index:
                        val = upper_tri.loc[row, col]
                        if pd.notna(val) and val >= 0.6:
                            sign = "positive" if numeric_df.corr().loc[row, col] > 0 else "negative"
                            corrs.append((row, col, numeric_df.corr().loc[row, col], sign))
                            
                if corrs:
                    corrs = sorted(corrs, key=lambda x: abs(x[2]), reverse=True)[:5]
                    rows_html = ""
                    for idx, (r, c, val, sign) in enumerate(corrs, 1):
                        rows_html += f"| {idx} | **{r}** & **{c}** | {val:+.2f} | {sign.upper()} |\n"
                        
                    table_md = (
                        f"| Rank | Variable Pair | Pearson Coefficient | Direction |\n"
                        f"|---|---|---|---|\n"
                        f"{rows_html}"
                    )
                    response_body = (
                        f"### Correlation Matrix Breakdown\n\n"
                        f"Here are the strongest correlations discovered in **{filename}**:\n\n"
                        f"{table_md}\n"
                        f"Use the **Visual Analytics** page to plot these pairs in a scatter matrix or correlation matrix."
                    )
                else:
                    response_body = "### Correlation Matrix Breakdown\n\n✓ All features are relatively independent. No strong correlations ($r \\ge 0.6$) were detected."
            except Exception as e:
                confidence = "Low"
                confidence_reason = f"Correlation calculation error: {str(e)}"
                response_body = f"I failed to calculate correlations due to a mathematical variance error: {str(e)}."
        else:
            confidence = "Low"
            confidence_reason = "Less than 2 numerical features are present in the dataset."
            response_body = "I cannot determine correlations because the dataset does not contain at least 2 numerical columns."
            
        suggested_questions = [
            "Is this dataset suitable for machine learning?",
            "What should I clean first?",
            "Summarize the dataset"
        ]

    # G. Default Conversational Fallback / Impossible Questions
    else:
        is_generic_question = any(kw in q_lower for kw in ["capital of", "weather", "who is", "who wrote", "formula of", "write a code", "how to make", "what is the meaning of"])
        
        if is_generic_question or len(q_lower.split()) > 8:
            confidence = "Low"
            confidence_reason = "The question falls outside the scope of the loaded dataset."
            response_body = (
                f"I cannot determine that from the uploaded dataset. "
                f"As your BI Copilot, my context is strictly limited to explaining the variables and rows of your uploaded file **{filename}**."
            )
        else:
            response_body = (
                f"Hello! I am your Kosvio BI Copilot. I have loaded **{filename}** into my context.\n\n"
                f"Think of me as a translator between your raw table rows and practical business clarity. "
                f"Your dataset has **{len(all_cols)} characteristics** (columns) and **{total_rows:,} entries** (rows).\n\n"
                f"**Here are some questions we can explore together:**\n"
                f"- *'Can you summarize the columns and tell me what types of data we have?'*\n"
                f"- *'Are there any blank entries or outliers that might skew our calculations?'*\n"
                f"- *'What should I clean first?'*\n"
                f"- *'Which customers perform best?'*\n\n"
                f"Feel free to ask a business question or click one of the preset actions."
            )
            
        suggested_questions = [
            "Summarize the dataset",
            "What should I clean first?",
            "Is this dataset suitable for machine learning?"
        ]

    # Save to session state so that render() can display interactive follow-up buttons
    st.session_state["suggested_questions"] = suggested_questions

    # ─────────────────────────────────────────────────────────────────────────
    # RENDER CONFIDENCE AND RESPONSE
    # ─────────────────────────────────────────────────────────────────────────
    confidence_color = "🟢" if confidence == "High" else "🟡" if confidence == "Medium" else "🔴"
    confidence_explain = f" ({confidence_reason})" if confidence_reason else ""
    
    badge_html = f"{confidence_color} **Confidence: {confidence}**{confidence_explain}\n\n"
    
    # Render final markdown response
    final_response = f"{badge_html}{response_body}"
    
    # Append suggested questions if present
    if suggested_questions:
        final_response += "\n\n---\n**Suggested Follow-up Questions:**\n"
        for q in suggested_questions:
            final_response += f"- *\"{q}\"*\n"
            
    return final_response


def render() -> None:
    """Render the Insight AI chatbot panel."""
    # Check dataset
    if "dataset" not in st.session_state:
        render_empty_state(
            title="No Dataset Selected",
            message="We couldn't locate an active dataset in memory. Please upload a dataset first.",
            action_label="Go to Upload Workspace",
            navigate_to="upload",
            navigate_label="Upload",
        )
        return

    df = st.session_state.get("cleaned_df", st.session_state["dataset"])
    filename = st.session_state.get("dataset_filename", "dataset.csv")

    render_section_header(
        title="Insight AI Workspace",
        subtitle=f"Query machine learning insights and descriptive context for {filename}.",
        label="Insight AI Panel",
    )

    if st.session_state.get("cleaned_df") is not None:
        st.info("All insights and metrics are generated from the cleaned dataset.")

    # Initialize suggested questions
    if "suggested_questions" not in st.session_state:
        st.session_state["suggested_questions"] = [
            "Summarize the dataset",
            "What should I clean first?",
            "Is this dataset suitable for machine learning?"
        ]

    # Initialize chat history
    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [
            {
                "role": "assistant", 
                "content": (
                    f"Hello! I am **Kosvio Insight Assistant**. I have loaded your dataset **{filename}** into context. "
                    f"You don't need to be a data scientist to explore your data — simply ask me questions in plain English. "
                    f"What would you like to explore today?"
                )
            }
        ]

    # Two column layout: Left Quick Prompts, Right ChatGPT bubble feed
    col_prompts, col_chat = st.columns([1, 2.5])

    # Callback helper for preset buttons
    def trigger_preset_prompt(preset_text: str):
        st.session_state["ai_messages"].append({"role": "user", "content": preset_text})
        response = generate_conversational_response(preset_text, df, filename)
        st.session_state["ai_messages"].append({"role": "assistant", "content": response})
        # Add to dashboard activity log
        if "activity_log" in st.session_state:
            import datetime
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            st.session_state["activity_log"].insert(0, {"time": now_str, "event": f"Query: '{preset_text[:25]}...'"})

    with col_prompts:
        st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0; margin-bottom: 0.75rem;">Workspace Actions</p>', unsafe_allow_html=True)
        
        with glass_card_panel():
            if st.button("Summarize Dataset", width="stretch", key="prompt_btn_summary"):
                trigger_preset_prompt("Summarize dataset")
                st.rerun()
            if st.button("Explain Charts", width="stretch", key="prompt_btn_charts"):
                trigger_preset_prompt("Explain charts")
                st.rerun()
            if st.button("Detect Anomalies", width="stretch", key="prompt_btn_anomalies"):
                trigger_preset_prompt("Detect anomalies")
                st.rerun()
            if st.button("Business Recommendations", width="stretch", key="prompt_btn_recs"):
                trigger_preset_prompt("Business recommendations")
                st.rerun()
            if st.button("Predict Trends", width="stretch", key="prompt_btn_predict"):
                trigger_preset_prompt("Predict trends")
                st.rerun()
            if st.button("Generate Insights", width="stretch", key="prompt_btn_insights"):
                trigger_preset_prompt("Generate insights")
                st.rerun()

    with col_chat:
        st.markdown('<p style="font-size: 0.95rem; font-weight: 600; color: var(--text); margin-top: 0; margin-bottom: 0.75rem;">Conversation</p>', unsafe_allow_html=True)
        
        # Chat container window
        chat_container = st.container(border=True)
        with chat_container:
            for msg in st.session_state["ai_messages"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Clickable follow-up buttons row
        sugs = st.session_state.get("suggested_questions", [])
        if sugs:
            st.markdown('<p style="font-size: 0.8rem; font-weight: 600; color: var(--subtext); margin-bottom: 0.35rem; margin-top: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">Suggested follow-ups</p>', unsafe_allow_html=True)
            cols = st.columns(len(sugs))
            for i, q_text in enumerate(sugs):
                with cols[i]:
                    btn_label = q_text if len(q_text) < 32 else q_text[:30] + "..."
                    if st.button(btn_label, key=f"sug_btn_{i}", width="stretch"):
                        st.session_state["ai_messages"].append({"role": "user", "content": q_text})
                        response_content = generate_conversational_response(q_text, df, filename)
                        st.session_state["ai_messages"].append({"role": "assistant", "content": response_content})
                        if "activity_log" in st.session_state:
                            import datetime
                            now_str = datetime.datetime.now().strftime("%I:%M %p")
                            st.session_state["activity_log"].insert(0, {"time": now_str, "event": f"Query: '{q_text[:25]}...'"})
                        st.rerun()

        # Chat Input at bottom
        user_query = st.chat_input("Ask a question about your data...")
        if user_query:
            st.session_state["ai_messages"].append({"role": "user", "content": user_query})
            response_content = generate_conversational_response(user_query, df, filename)
            st.session_state["ai_messages"].append({"role": "assistant", "content": response_content})
            # Add to dashboard activity log
            if "activity_log" in st.session_state:
                import datetime
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                st.session_state["activity_log"].insert(0, {"time": now_str, "event": f"Query: '{user_query[:25]}...'"})
            st.rerun()


if __name__ == "__main__":
    render()
