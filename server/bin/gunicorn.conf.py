from logger import init_logger
from loguru import logger


def on_starting(server):
    # intercept log from gunicorn and reformat as in configuration file
    init_logger("config/log.gunicorn.json", ["gunicorn"])


def on_reload(server):
    logger.info("Gunicorn is reloading...")


def when_ready(server):
    pass


def on_exit(server):
    logger.info("Gunicorn terminated.")


def pre_request(worker, req):
    logger.debug(worker)
    logger.debug("{} {}", req.method, req.path, req.body)


def post_request(worker, req, environ, resp):
    logger.debug(worker)
    logger.debug("{}", resp)


# configuration
bind = "127.0.0.1:8000"
wsgi_app = "main:app"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 1
threads = 1

# set daemon to True to run in background
daemon = False

# set to True to speed up loadint time
preload_app = False

# timeout
#   0 --> disable
#   N --> restart worker if not response in N seconds
timeout = 120

# keep_alive
#   N --> seconds to wait for keep alive message
keep_alive = 5

# max_requests
#   0 --> disable process restart
#   N --> restart process after N request
max_requests = 0
max_requests_jitter = 100

reload = False
reload_extra_files = [
    "config/config.json",
]

# logging
#   "-" --> capture to stdout
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = False

# SSL
keyfile = None
certfile = None
