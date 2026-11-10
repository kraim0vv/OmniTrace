import os
import sys
import tempfile
from pathlib import Path

# Must run before app.config is imported so tests never touch the real database
os.environ["OMNITRACE_DATA_DIR"] = tempfile.mkdtemp(prefix="omnitrace-test-")
os.environ.pop("OMNITRACE_PASSWORD", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def restore_settings():
    snapshot = settings.model_dump()
    yield settings
    for key, value in snapshot.items():
        setattr(settings, key, value)
