#### Dependency

- ```Redis```

#### Start server

```commandline
gunicorn -w 4 -b 0.0.0.0:5000 index:app -t 90 --reload
```
- `-w` - Background workers
- `-b` - Bind host@port
- `index:app` - Since our main file name is other than app so, `file_name:app`
- `-t` - Timeout in secs
- `--reload` - Flag to indicate gunicorn to listen for code changes and restart server
_____________________________________________________
#### Start celery worker

command
```commandline
celery -A index.celery_app worker --loglevel=debug
```

- `-A` - Location of celery app instance (here in `index.py`)
- `--loglevel` - Logging level (i.e. debug/info), debug preferred in dev mode

________________________________________________

#### Docker setup

```commandline
docker compose up
```