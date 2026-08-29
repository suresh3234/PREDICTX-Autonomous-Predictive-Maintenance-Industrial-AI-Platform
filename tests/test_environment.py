from app.core.config import settings


def test_environment():
    assert settings.app_name == "PredictX"
    assert settings.environment == "development"
