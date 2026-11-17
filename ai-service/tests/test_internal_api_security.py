import base64
import os
os.environ.setdefault('AI_SERVICE_TOKEN', 'phase8-integration-test-token')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
TOKEN = os.environ['AI_SERVICE_TOKEN']
HEADERS = {'Authorization': f'Bearer {TOKEN}'}

def test_public_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'

def test_rag_requires_internal_identity():
    data = {'question': 'Quy trinh Kaizen?', 'evidence': []}
    assert client.post('/internal/rag/answer', json=data).status_code == 401
    assert client.post('/internal/rag/answer', json=data, headers={'Authorization':'Bearer wrong'}).status_code == 401

def test_rag_no_evidence_does_not_hallucinate():
    response = client.post('/internal/rag/answer', json={'question':'Kaizen?', 'evidence':[]}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()['mode'] == 'no_evidence'

def test_reject_invalid_base64():
    response = client.post('/internal/rag/extract', json={'content_base64':'not-base64!', 'mime_type':'text/plain'}, headers=HEADERS)
    assert response.status_code == 422

def test_txt_extraction():
    payload = {'content_base64':base64.b64encode(b'Kaizen means continuous improvement.').decode(), 'mime_type':'text/plain'}
    response = client.post('/internal/rag/extract',json=payload,headers=HEADERS)
    assert response.status_code == 200
    assert 'Kaizen' in ' '.join(response.json()['chunks'])

def test_forecast_input_validation():
    response = client.post('/internal/forecasting/predict',json={'observations':[],'horizon':100},headers=HEADERS)
    assert response.status_code == 422
