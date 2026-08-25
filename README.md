# Idempotent Automation Script with Scheduling & Logging

A production-safe automated file backup and sync script designed to run unattended via Cron or Windows Task Scheduler.

## Key Features
- **Idempotent Operations:** Uses SHA-256 hash comparison to avoid redundant file transfers if executed multiple times.
- **Structured Logging:** Timestamps and severity levels logged simultaneously to stdout and `automation.log`.
- **Decoupled Config:** Runtime behavior managed cleanly via `config.json`.
- **Failure Recovery:** Employs atomic temp-file replacement to prevent file corruption during sudden interruptions.

## Setup & Execution
```bash
# Run the backup job
python backup_automation.py
