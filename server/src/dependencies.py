from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


# supporting languages
class Language(str, Enum):
    th = "th"
    en = "en"


class RequestData(BaseModel):
    """
    Data model for intent request
    """

    requestId: Optional[str] = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="Unquie ID of the request",
    )
    text: str = Field(
        min_length=5,
        description="Text to search for intent",
    )
    language: Optional[Language] = Field(
        default=Language.th, description="Langauge for the intent"
    )
    sentimental: Optional[bool] = Field(
        default=False, description="Execute sentmental analysis"
    )
    threshold: Optional[float] = Field(
        default=float(0.8),
        description="Threshold for confidential level",
        ge=0.0,
        le=1.0,
    )

    options: Optional[dict] = Field(description="Options pass to the function")

    class Config:
        anystr_strip_whitespace = True


class QueryResult(BaseModel):
    """
    Data model for query result
    """

    # need default= for all fields to ease when object is created
    queryText: str = Field(default="", description="Query text")
    parameters: dict = Field(
        default={}, description="Parameters for the intent"
    )
    allRequiredParamsPresent: bool = Field(default=True)
    fulfillmentText: str = Field(
        default="", description="Response for the intent"
    )
    fulfillmentMessages: list = Field(
        default=[], description="All possible responses"
    )
    intent: dict = Field(default={}, description="Intent id and name")
    intentDetectionConfidence: float = Field(
        default=float(0.0), description="Confidential level of the result"
    )
    requestThreshold: float = Field(
        default=float(0.0),
        description="Request threshold for confidential level",
    )
    languageCode: Language = Field(default=Language.th)
    sentimentAnalysisResult: dict = Field(
        default={}, description="Sentimental analysis result"
    )


class ResponseData(BaseModel):
    """
    Data model for response
    """

    agentId: str = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="ID of the instance of API Server",
    )

    modelName: str = Field(
        default="", description="Model name use for prediction"
    )

    version: str = Field(default="", description="Version of the model")

    responseId: str = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="Unique id for the response",
    )

    queryResult: QueryResult


def dict_converter(d: dict) -> dict:
    for k, v in d.items():

        # check boolean text
        if type(v) is str:
            s = v.lower()
            if s == "true" or s == "false":
                d[k] = bool(s)

    return d
