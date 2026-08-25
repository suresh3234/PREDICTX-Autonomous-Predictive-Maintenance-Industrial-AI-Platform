from src.config.settings import settings


def test_environment():
    assert settings.app_name == "PredictX"
    assert settings.environment == "development"