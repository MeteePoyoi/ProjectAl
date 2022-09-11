import random
import pandas as pd

from abc import ABC, abstractmethod
from dependencies import QueryResult


# All Response classes must derive from this interface
class ResponseInterface(ABC):
    def __init__(self, config):
        ResponseInterface.config = config

    @abstractmethod
    def query(self, intent_id: int) -> QueryResult:
        pass


# Get response text from CSV file
class CSVResponse(ResponseInterface):
    # CSVResponse.config is inherited from super class

    def query(self, intent_id: int) -> QueryResult:

        label_df = pd.read_csv(CSVResponse.config["params"]["dataFile"])
        match = label_df.loc[label_df["intent_id"] == intent_id]

        # return string if found else None
        messages = (
            match.to_dict("list")["response"] if not match.empty else None
        )

        result = QueryResult()
        result.fulfillmentText = (
            random.choice(messages) if len(messages) > 0 else None
        )
        result.fulfillmentMessages = [{"text": {"text": messages}}]
        result.intent = {"name": intent_id, "displayName": intent_id}

        return result
