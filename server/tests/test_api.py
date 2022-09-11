import pandas as pd
import pytest
import requests
import json

url = "http://localhost:8000"
test_data = ["tests/data/test_data1.csv"]
thresholds = [0, 85, 90, 95]


def data(index):
    with open(test_data[index]) as file:
        df = pd.read_csv(file)
        df = list(df.itertuples(index=True, name=None))
        return df


@pytest.mark.parametrize("index, text", data(0))
@pytest.mark.parametrize("threshold", thresholds)
class TestApi:
    @pytest.mark.it("Keyword with threshold")
    def test_keyword(self, rp_logger, index, text, threshold):
        body = {"text": text, "language": "th", "threshold": threshold / 100}
        res = requests.post(url + "/intent", json=body).json()

        rp_logger.debug("request: %s", body)
        rp_logger.debug(
            "response: %s", json.dumps(res, ensure_ascii=False, indent=2)
        )
        fulfillment = res["queryResult"]["fulfillmentText"]
        confidence = round(
            res["queryResult"]["intentDetectionConfidence"] * 100, 2
        )

        if confidence == 0:
            assert fulfillment is not None
        else:
            assert confidence > threshold
