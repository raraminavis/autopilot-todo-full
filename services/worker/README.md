# services/worker

Celery worker scaffold.

Planned tasks:
- Google calendar sync job
- conflict detection job
- replan job

Run:
```bash
pip install -e ".[dev]"
celery -A worker.celery_app worker --loglevel=INFO
```
