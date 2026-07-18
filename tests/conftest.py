import pytest
from pathlib import Path


@pytest.fixture
def sample_project_path():
    return Path(__file__).parent / "fixtures" / "sample-java-project"


@pytest.fixture
def order_service_path(sample_project_path):
    return sample_project_path / "order-service"
