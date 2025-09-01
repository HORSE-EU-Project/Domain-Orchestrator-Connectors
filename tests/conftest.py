import pytest
# ---------- FastAPI TestClient ---------- #
from starlette.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


# Patch Mongo
@pytest.fixture(autouse=True)
def patch_mongo(mocker):
    """
    Replace utils.mongo.insert_raw with a stub returning a fake _id.
    Runs automatically for every test.
    """
    stub = mocker.patch("src.utils.mongo.insert_raw", return_value="fake-mongo-id")
    return stub


# Patch translator
def patch_upstream(mocker):
    # Patch the dispatcher instead of build_dispatch_spec
    mocker.patch(
        "src.dispatch.http.dispatch",         # ← correct path in your project
        return_value={"result": "ok"}
    )
