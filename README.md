# Conscious Curation Pipeline

This repo now supports a central server workflow with two parts:

1. **Ingest job** (periodic): fetch items and store them in a shared SQLite database.
2. **Web UI** (central server): browse and copy items of interest.

## Quick start

```bash
python ccp_ingest.py --db-path ccp.db
python ccp_server.py --db-path ccp.db --port 8000
```

Then open `http://localhost:8000` to see the feed.

## Suggested production workflow

- Run `ccp_ingest.py` on a schedule (cron, systemd timer, or your scheduler of choice).
- Keep `ccp_server.py` running on a central host so teammates can browse and copy items.

## Legacy script

The original `ccp_main.py` still produces a local `Daily_Dossier.txt` file.
