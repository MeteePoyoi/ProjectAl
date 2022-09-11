import json
import importlib
import uuid
import os

from loguru import logger
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from dependencies import RequestData
from logger import init_logger
import router.thainlp as thainlp

tags = [
    {"name": "thainlp", "description": "API for thai language processing"},
]


def load_config(filename):
    with open(filename) as file:
        config = json.load(file)
        return config


def create_model(filename):
    config = load_config(filename)
    logger.info("create instance of {}", config["className"])
    module = importlib.import_module(config["moduleName"])
    return getattr(module, config["className"])(config)


# load configuration
config_file = (
    os.getenv("AUTOBOT_CONFIG")
    if os.getenv("AUTOBOT_CONFIG") is not None
    else "config/config.json"
)
config = load_config(config_file)

# intercept long from uvicorn to loguru and
# use format from configuration file
init_logger(config["log"], ["uvicorn"])
logger.info(
    "start chatbot agent using {}: [name={}, id={}].",
    config_file,
    config["agentName"],
    config["agentId"],
)

# start API server
app = FastAPI(
    title="API server for chatbot", version="0.0.1", openapi_tags=tags
)
app.include_router(thainlp.router, tags=["thainlp"])


@app.on_event("startup")
async def on_startup():

    global response_model
    global intent_model

    # create Response and Intent instance
    response_model = create_model(config["model"]["response"])
    intent_model = create_model(config["model"]["intent"])
    logger.info("loading model completed...")


@app.on_event("shutdown")
async def on_shutdown():
    logger.warning("API server is shutting down...")


@app.post("/intent")
async def intent(req: RequestData):

    try:

        if req.requestId.startswith("00000000"):
            req.requestId = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, "autobot.convergence.co.th")
            )

        res = intent_model.query(req, response_model)
        res.agentId = config["agentId"]
        return JSONResponse(res.dict())

    except ValueError as err:
        return JSONResponse({"error": str(err)})
