from loguru import logger
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pythainlp import word_tokenize
from pythainlp.tag.named_entity import NER
from pythainlp.wangchanberta import ThaiNameTagger


from dependencies import RequestData, dict_converter

router = APIRouter(prefix="/thainlp")

# create NER and ThaiNameTagger to reduce load time
ner = NER("thainer")
nametag = ThaiNameTagger("thainer")


@router.post("/tokenizer", summary="Word tokenize")
async def tokenize(req: RequestData):

    params = req.dict()
    tokens = word_tokenize(params["text"])

    logger.debug("tokenize: [{}] -> {}", params["text"], tokens)
    return JSONResponse(tokens)


@router.post("/pos", summary="Part-of-Speech tagging")
async def pos(req: dict):

    params = req.dict()
    tags = ner.tag(params["text"])

    logger.debug("pos: [{}] -> {}", params["text"], tags)
    return JSONResponse(tags)


@router.post("/ner", summary="Name Entity Recognition")
async def ner(req: RequestData):

    params = req.dict()
    options = dict_converter(params["options"])
    names = nametag.get_ner(params["text"], **options)

    logger.debug("name tagging: [{}] -> {}", params["text"], names)
    return JSONResponse(names)
