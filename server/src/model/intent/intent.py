import os
import textwrap
import json
import pickle

from abc import ABC, abstractmethod
from dependencies import ResponseData, RequestData
from loguru import logger

# turn off log from tensorflow, seems not work
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf  # noqa: E402
import tensorflow_hub as hub  # noqa: E402
import tensorflow_text  # noqa: F401 E402 # needed by not used


class IntentInterface(ABC):
    encoder = None
    model = None

    def __init__(self, config):
        self.config = config
        self.load_model(config["params"]["modelPath"])

    @abstractmethod
    def query(self, req: RequestData, response_model) -> ResponseData:
        pass

    def save_result(self, result: ResponseData):
        logger.debug(result)

    @classmethod
    @abstractmethod  # must be inner most otherwise will error
    def load_encoder(cls, url):
        pass

    @classmethod
    def load_model(cls, path):
        if cls.model is None:
            cls.model = tf.keras.models.load_model(path)
            cls.model.summary()


class BasicIntent(IntentInterface):
    labels = None

    def __init__(self, config):
        super().__init__(config)

        # load encoder for this class
        self.load_encoder(config["params"]["encoderUrl"])
        self.load_label(config["params"]["modelPath"])

    def query(self, req, response_model) -> ResponseData:

        embed = self.encoder(req.text)
        embed = tf.reshape(embed, (1, 1, 512))
        prediction = self.model.predict(embed)
        index = prediction.argmax()
        confidence = prediction[0][index]
        indent_id = self.labels[index]
        threshold = req.threshold

        result = response_model.query(indent_id)
        result.queryText = req.text
        result.intentDetectionConfidence = float(confidence)
        result.requestThreshold = threshold
        result.languageCode = req.language

        response = ResponseData(
            modelName=self.config["name"],
            version=self.config["version"],
            queryResult=result,
            responseId=req.requestId,
        )

        # use .opt(lazy=True) to check if TRACE/DEBUG is enabled
        logger.opt(lazy=True).debug(
            "{}",
            lambda: "predict [id={}, text={}] -> [id={}, text={}, confidence={}]".format(  # noqa: E501
                req.requestId,
                req.text,
                indent_id,
                textwrap.shorten(
                    result.fulfillmentText, width=20, placeholder="..."
                ),
                confidence,
            ),
        )
        # log full response in TRACE level
        logger.opt(lazy=True).trace(
            "response ->\n{}",
            lambda: json.dumps(result.dict(), indent=2, ensure_ascii=False),
        )

        return response

    @classmethod
    def load_encoder(cls, url):
        if cls.encoder is None:
            cls.encoder = hub.load(url)

    @classmethod
    def load_label(cls, model_path):
        with open(model_path + "_labels.pickle", "rb") as file:
            cls.labels = pickle.loads(file.read())
            file.close()

        logger.bind(payload=cls.labels).debug("class labels")
