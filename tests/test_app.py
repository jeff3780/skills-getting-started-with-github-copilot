from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

TEST_ACTIVITY = "Test Club"
TEST_EMAIL = "teststudent@mergington.edu"


def setup_module(module):
    # Ensure a clean test activity exists
    activities[TEST_ACTIVITY] = {
        "description": "A temporary activity for testing",
        "schedule": "Mondays 1pm",
        "max_participants": 5,
        "participants": []
    }


def teardown_module(module):
    # Remove test activity
    activities.pop(TEST_ACTIVITY, None)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert TEST_ACTIVITY in data


def test_signup_success():
    # Sign up a new participant
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 200
    data = resp.json()
    assert "Signed up" in data.get("message", "")
    # Verify in-memory state updated
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]


def test_signup_duplicate():
    # Signing up the same email again should error
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 400


def test_remove_participant_success():
    # Ensure participant exists
    assert TEST_EMAIL in activities[TEST_ACTIVITY]["participants"]
    resp = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")
    assert resp.status_code == 200
    data = resp.json()
    assert f"Removed {TEST_EMAIL}" in data.get("message", "")
    assert TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]


def test_remove_nonexistent_participant():
    resp = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email=doesnotexist@mergington.edu")
    assert resp.status_code == 404
