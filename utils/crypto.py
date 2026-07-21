"""
Cryptography utility for Kosvio.

Handles environment variable encryption/decryption using Fernet symmetric encryption.
Provides CLI commands to generate keys and encrypt environment files.
"""

import os
import sys
import logging
from pathlib import Path
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Resolve base directories relative to this file's location
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_ENC_PATH = BASE_DIR / ".env.enc"
ENV_PATH = BASE_DIR / ".env"


def decrypt_file_to_env() -> bool:
    """
    Reads the local .env.enc file, decrypts it using the KOSVIO_DECRYPT_KEY
    environment variable, and loads the key-value pairs into os.environ.

    Returns:
        bool: True if variables were successfully decrypted and loaded, False otherwise.
    """
    key = os.environ.get("KOSVIO_DECRYPT_KEY")
    if not key:
        logger.info("KOSVIO_DECRYPT_KEY environment variable is not set. Skipping configuration decryption.")
        return False

    if not ENV_ENC_PATH.exists():
        logger.warning(f"Encrypted environment file {ENV_ENC_PATH} not found.")
        return False

    try:
        f = Fernet(key.strip().encode("utf-8"))
        encrypted_data = ENV_ENC_PATH.read_bytes()
        decrypted_data = f.decrypt(encrypted_data).decode("utf-8")

        loaded_count = 0
        for line in decrypted_data.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")  # Strip outer quotes if any
                os.environ[k] = v
                loaded_count += 1

        logger.info(f"Successfully decrypted .env.enc and loaded {loaded_count} environment variables.")
        return True
    except Exception as e:
        logger.error(f"Failed to decrypt environment file: {str(e)}", exc_info=True)
        return False


def encrypt_env_file(key: str) -> bool:
    """
    Encrypts the plain text .env file into .env.enc using the provided key.

    Args:
        key (str): The Fernet symmetric encryption key.

    Returns:
        bool: True if encryption succeeded, False otherwise.
    """
    if not ENV_PATH.exists():
        print(f"Error: Source file {ENV_PATH} does not exist.")
        return False

    try:
        f = Fernet(key.strip().encode("utf-8"))
        data = ENV_PATH.read_bytes()
        encrypted_data = f.encrypt(data)
        ENV_ENC_PATH.write_bytes(encrypted_data)
        print(f"Successfully encrypted {ENV_PATH} to {ENV_ENC_PATH}")
        return True
    except Exception as e:
        print(f"Failed to encrypt: {str(e)}")
        return False


def main():
    """CLI Entrypoint for key generation and encryption."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python utils/crypto.py generate-key")
        print("  python utils/crypto.py encrypt <key>")
        sys.exit(1)

    action = sys.argv[1].lower()
    if action == "generate-key":
        key = Fernet.generate_key().decode("utf-8")
        print("Generated KOSVIO_DECRYPT_KEY:")
        print(key)
    elif action == "encrypt":
        if len(sys.argv) < 3:
            print("Error: Please provide the encryption key as the second argument.")
            sys.exit(1)
        key = sys.argv[2]
        encrypt_env_file(key)
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
