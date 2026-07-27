import os
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import io

from app.main import app

@pytest.fixture
def client():
    # Context manager 'with TestClient' forces FastAPI lifespan setup/teardown to run
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["classes_registered"] == 15

def test_triage_critical_symptoms(client):
    payload = {
        "bitten": True,
        "time_elapsed_minutes": 20,
        "local_swelling": True,
        "drooping_eyelids": True,
        "difficulty_breathing": False,
        "spontaneous_bleeding": False
    }
    response = client.post("/triage", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == "CRITICAL"
    assert "dos" in data["action_protocol"]
    assert "donts" in data["action_protocol"]

def test_predict_endpoint_valid_image(client):
    # Create dummy RGB test image in memory
    img = Image.new("RGB", (224, 224), color="green")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    response = client.post("/predict", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["top_predictions"]) == 3
    assert "safety_disclaimer" in data