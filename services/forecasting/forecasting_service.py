"""
Forecasting Service.

Handles predictive trend projections and residual decay calculations for tabular datasets.
"""

import pandas as pd
import numpy as np


class ForecastingService:
    """Service class for predictive time-series forecasting."""

    @staticmethod
    def compute_forecast(df: pd.DataFrame, target_col: str, date_col: str, horizon: int) -> pd.DataFrame:
        """
        Compute trend projection and confidence intervals using linear trend + AR residuals.
        
        Args:
            df (pd.DataFrame): Input dataset.
            target_col (str): Variable to project.
            date_col (str): Date/timeline variable.
            horizon (int): Forecasting horizon steps.

        Returns:
            pd.DataFrame: Historical actuals merged with projected predictions.
        """
        if date_col and date_col != "[None]":
            df_clean = df[[date_col, target_col]].dropna().copy()
            df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors="coerce")
            df_clean = df_clean.dropna().sort_values(by=date_col)
            df_agg = df_clean.groupby(date_col)[target_col].mean().reset_index()
            df_agg = df_agg.rename(columns={date_col: "ds", target_col: "y"})
        else:
            df_agg = df[[target_col]].dropna().copy().reset_index()
            df_agg = df_agg.rename(columns={"index": "ds", target_col: "y"})

        n_hist = len(df_agg)
        if n_hist < 3:
            return pd.DataFrame()

        # Fit trend: y = alpha * t + beta
        t_hist = np.arange(n_hist)
        y_hist = df_agg["y"].values
        alpha, beta = np.polyfit(t_hist, y_hist, 1)

        residuals = y_hist - (alpha * t_hist + beta)
        sigma = np.std(residuals) if np.std(residuals) > 0 else 1.0

        # Project horizon
        if date_col and date_col != "[None]":
            last_date = df_agg["ds"].max()
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")
        else:
            last_val = df_agg["ds"].max()
            future_dates = np.arange(last_val + 1, last_val + 1 + horizon)

        t_future = np.arange(n_hist, n_hist + horizon)
        y_future = alpha * t_future + beta

        # Propagate last residual with decay
        last_res = residuals[-1]
        decay = 0.8
        residual_extrap = last_res * (decay ** np.arange(1, horizon + 1))
        y_future += residual_extrap

        # Standard errors growing with horizon
        se = sigma * np.sqrt(1 + 0.15 * np.arange(1, horizon + 1))
        upper_bounds = y_future + 1.96 * se
        lower_bounds = y_future - 1.96 * se

        # Assemble historical part
        hist_part = pd.DataFrame({
            "Timeline": df_agg["ds"],
            "Actual": df_agg["y"],
            "Forecast": np.nan,
            "Lower Bound": np.nan,
            "Upper Bound": np.nan,
        })

        # Assemble forecast part starting at the last point to connect lines
        forecast_timeline = [df_agg["ds"].iloc[-1]] + list(future_dates)
        forecast_y = [df_agg["y"].iloc[-1]] + list(y_future)
        forecast_lower = [df_agg["y"].iloc[-1]] + list(lower_bounds)
        forecast_upper = [df_agg["y"].iloc[-1]] + list(upper_bounds)

        fore_part = pd.DataFrame({
            "Timeline": forecast_timeline,
            "Actual": np.nan,
            "Forecast": forecast_y,
            "Lower Bound": forecast_lower,
            "Upper Bound": forecast_upper,
        })

        return pd.concat([hist_part, fore_part], ignore_index=True)
