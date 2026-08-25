#!/usr/bin/env python3
"""
Automated, Idempotent File Backup & Sync Utility
Built with structured logging, isolated configuration, and failure-safe recovery.
"""

import os
import shutil
import json
import logging
import sys
import hashlib
from datetime import datetime

# Setup Structured Logging
LOG_FILE = "automation.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

DEFAULT_CONFIG = {
    "source_directory": "./source_data",
    "backup_directory": "./backup_vault",
    "dry_run": False
}

def load_config(config_path="config.json"):
    """Loads runtime configurations outside of source code."""
    if not os.path.exists(config_path):
        logging.warning(f"Config file '{config_path}' not found. Generating default configuration.")
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to parse config file: {e}")
        sys.exit(1)

def get_file_hash(filepath):
    """Calculates SHA256 checksum to ensure idempotency."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def sync_and_backup():
    config = load_config()
    src = config.get("source_directory", "./source_data")
    dest = config.get("backup_directory", "./backup_vault")

    logging.info(f"Starting backup sync from '{src}' to '{dest}'")

    if not os.path.exists(src):
        logging.info(f"Source directory '{src}' does not exist. Creating sample source folder.")
        os.makedirs(src, exist_ok=True)
        # Create a sample file if empty
        with open(os.path.join(src, "sample.txt"), "w") as f:
            f.write("Automated sync test data.")

    os.makedirs(dest, exist_ok=True)

    synced_count = 0
    skipped_count = 0

    for root, _, files in os.walk(src):
        for file in files:
            src_file = os.path.join(root, file)
            rel_path = os.path.relpath(src_file, src)
            dest_file = os.path.join(dest, rel_path)

            os.makedirs(os.path.dirname(dest_file), exist_ok=True)

            # Idempotency check: Skip if destination file is identical
            if os.path.exists(dest_file):
                if get_file_hash(src_file) == get_file_hash(dest_file):
                    logging.info(f"Skipping unchanged file (Idempotent): {rel_path}")
                    skipped_count += 1
                    continue

            # Safe Copy with temp extension (Recovery path on halfway failure)
            temp_dest = dest_file + ".tmp"
            try:
                shutil.copy2(src_file, temp_dest)
                os.replace(temp_dest, dest_file) # Atomic rename
                logging.info(f"Successfully backed up: {rel_path}")
                synced_count += 1
            except Exception as err:
                logging.error(f"Error copying '{rel_path}': {err}")
                if os.path.exists(temp_dest):
                    os.remove(temp_dest)

    logging.info(f"Sync complete. Files backed up: {synced_count}, Unchanged/Skipped: {skipped_count}\n")

if __name__ == "__main__":
    try:
        sync_and_backup()
    except KeyboardInterrupt:
        logging.warning("Script execution interrupted manually.")
        sys.exit(130)
