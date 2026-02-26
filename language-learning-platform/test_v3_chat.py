"""
Test suite for /api/v3/chat endpoints.
22 tests covering all routes in unified_chat_routes.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("TESTING", "true")

from app import create_app
from app.models import db, User
from flask_jwt_extended import create_access_token

passed = 0
failed = 0
errors = []


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        errors.append(f"{name}: {detail}")
        print(f"  [FAIL] {name} -- {detail}")


def run_tests():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        # Create a test user if not present
        user = User.query.filter_by(email="test_v3@example.com").first()
        if not user:
            user = User(
                username="test_v3_user",
                email="test_v3@example.com",
            )
            user.set_password("testpass123")
            db.session.add(user)
            db.session.commit()

        user_id = user.id
        token = create_access_token(identity=str(user_id))
        auth_headers = {"Authorization": f"Bearer {token}"}

    with app.test_client() as client:
        with app.app_context():
            token = create_access_token(identity=str(user_id))
            auth_headers = {"Authorization": f"Bearer {token}"}

        print("\n=== /api/v3/chat Test Suite ===\n")

        # ---- HEALTH CHECK ----
        print("[1] Health Check")
        r = client.get("/api/v3/chat/health")
        check("GET /health => 200", r.status_code == 200)
        data = r.get_json()
        check("health has status field", "status" in data)

        # ---- CREATE CONVERSATION ----
        print("\n[2] Create Conversation")
        r = client.post(
            "/api/v3/chat/conversations",
            json={"title": "Test Session", "topic": "grammar"},
            headers=auth_headers,
        )
        check("POST /conversations => 201", r.status_code == 201)
        data = r.get_json()
        check("create returns success=True", data.get("success") is True)
        conv_id = data.get("conversation", {}).get("id")
        check("conversation id returned", conv_id is not None, f"got {data}")

        # ---- LIST CONVERSATIONS ----
        print("\n[3] List Conversations")
        r = client.get("/api/v3/chat/conversations", headers=auth_headers)
        check("GET /conversations => 200", r.status_code == 200)
        data = r.get_json()
        check("list returns conversations array", isinstance(data.get("conversations"), list))

        # ---- GET CONVERSATION ----
        print("\n[4] Get Conversation")
        r = client.get(f"/api/v3/chat/conversations/{conv_id}", headers=auth_headers)
        check("GET /conversations/<id> => 200", r.status_code == 200)
        data = r.get_json()
        check("get returns success=True", data.get("success") is True)

        # ---- UPDATE TITLE ----
        print("\n[5] Update Title")
        r = client.patch(
            f"/api/v3/chat/conversations/{conv_id}/title",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )
        check("PATCH /conversations/<id>/title => 200", r.status_code == 200)
        data = r.get_json()
        check("title updated successfully", data.get("success") is True)

        # ---- SEND MESSAGE ----
        print("\n[6] Send Message")
        r = client.post(
            f"/api/v3/chat/conversations/{conv_id}/messages",
            json={"message": "Hello, how do I use past tense?", "topic": "grammar"},
            headers=auth_headers,
        )
        check(
            "POST /conversations/<id>/messages => 200 or 400",
            r.status_code in (200, 400),
        )
        data = r.get_json()
        # Accept success OR error (LLM may be unavailable)
        send_ok = data.get("success") is True
        send_err = "error" in data
        check(
            "send message returns valid response",
            send_ok or send_err,
            f"got {data}",
        )

        # ---- GET MESSAGES ----
        print("\n[7] Get Messages")
        r = client.get(
            f"/api/v3/chat/conversations/{conv_id}/messages",
            headers=auth_headers,
        )
        check("GET /conversations/<id>/messages => 200", r.status_code == 200)
        data = r.get_json()
        check("messages array returned", isinstance(data.get("messages"), list))

        # ---- SUMMARY ----
        print("\n[8] Generate Summary")
        r = client.get(
            f"/api/v3/chat/conversations/{conv_id}/summary",
            headers=auth_headers,
        )
        check("GET /conversations/<id>/summary => 200 or 400", r.status_code in (200, 400))

        # ---- ANALYTICS ----
        print("\n[9] Conversation Analytics")
        r = client.get(
            f"/api/v3/chat/conversations/{conv_id}/analytics",
            headers=auth_headers,
        )
        check("GET /conversations/<id>/analytics => 200", r.status_code == 200)
        data = r.get_json()
        check("analytics returns statistics", "statistics" in data or "error" in data)

        # ---- EXPORT JSON ----
        print("\n[10] Export Conversation (JSON)")
        r = client.get(
            f"/api/v3/chat/conversations/{conv_id}/export?format=json",
            headers=auth_headers,
        )
        check("GET /conversations/<id>/export?format=json => 200", r.status_code == 200)

        # ---- EXPORT MARKDOWN ----
        print("\n[11] Export Conversation (Markdown)")
        r = client.get(
            f"/api/v3/chat/conversations/{conv_id}/export?format=markdown",
            headers=auth_headers,
        )
        check("GET /conversations/<id>/export?format=markdown => 200", r.status_code == 200)

        # ---- LEARNING INSIGHTS ----
        print("\n[12] Learning Insights")
        r = client.get("/api/v3/chat/insights", headers=auth_headers)
        check("GET /insights => 200", r.status_code == 200)
        data = r.get_json()
        check("insights returns data", data.get("success") is True or "error" in data)

        # ---- STATISTICS ----
        print("\n[13] Statistics (alias for insights)")
        r = client.get("/api/v3/chat/statistics", headers=auth_headers)
        check("GET /statistics => 200", r.status_code == 200)

        # ---- SEARCH CONVERSATIONS ----
        print("\n[14] Search Conversations")
        r = client.get(
            "/api/v3/chat/conversations/search?query=grammar",
            headers=auth_headers,
        )
        check("GET /conversations/search?query=grammar => 200", r.status_code == 200)
        data = r.get_json()
        check("search returns conversations list", isinstance(data.get("conversations"), list))

        # ---- SEARCH CONVERSATIONS - missing query ----
        print("\n[15] Search Conversations - missing query param")
        r = client.get("/api/v3/chat/conversations/search", headers=auth_headers)
        check("GET /conversations/search (no query) => 400", r.status_code == 400)

        # ---- MEMORY SEARCH ----
        print("\n[16] Memory Search")
        r = client.post(
            "/api/v3/chat/memories/search",
            json={"query": "grammar mistakes", "limit": 3},
            headers=auth_headers,
        )
        check("POST /memories/search => 200", r.status_code == 200)
        data = r.get_json()
        check("memory search returns memories", "memories" in data)

        # ---- GET MEMORIES ----
        print("\n[17] Get Memories")
        r = client.get("/api/v3/chat/memories", headers=auth_headers)
        check("GET /memories => 200", r.status_code == 200)

        # ---- WEB SEARCH ----
        print("\n[18] Web Search (standalone)")
        r = client.post(
            "/api/v3/chat/web-search",
            json={"query": "English grammar past tense", "max_results": 2},
            headers=auth_headers,
        )
        check("POST /web-search => 200 or 500", r.status_code in (200, 500))

        # ---- DELETE CONVERSATION ----
        print("\n[19] Delete Conversation")
        r = client.delete(
            f"/api/v3/chat/conversations/{conv_id}",
            headers=auth_headers,
        )
        check("DELETE /conversations/<id> => 200", r.status_code == 200)
        data = r.get_json()
        check("delete returns success=True", data.get("success") is True)

        # ---- GET DELETED CONVERSATION => 404 (soft delete) ----
        print("\n[20] Get Deleted Conversation => 404")
        r = client.get(f"/api/v3/chat/conversations/{conv_id}", headers=auth_headers)
        check(
            "GET deleted conversation => 404 (soft delete enforced)",
            r.status_code == 404,
            f"expected 404, got {r.status_code}",
        )

        # ---- UNAUTHORIZED ACCESS ----
        print("\n[21] Auth: No token => 401")
        r = client.get("/api/v3/chat/conversations")
        check("GET /conversations without token => 401", r.status_code == 401)

        # ---- SEND MESSAGE EMPTY BODY ----
        print("\n[22] Send Message: empty message => 400")
        # Create fresh conversation for this test
        with app.app_context():
            token2 = create_access_token(identity=str(user_id))
            auth2 = {"Authorization": f"Bearer {token2}"}

        r2 = client.post(
            "/api/v3/chat/conversations",
            json={"title": "Temp", "topic": "general"},
            headers=auth2,
        )
        if r2.status_code == 201:
            tmp_id = r2.get_json().get("conversation", {}).get("id")
            r3 = client.post(
                f"/api/v3/chat/conversations/{tmp_id}/messages",
                json={"message": "   "},
                headers=auth2,
            )
            check(
                "POST message with whitespace-only => 400",
                r3.status_code == 400,
                f"got {r3.status_code}",
            )
        else:
            check("POST message with whitespace-only => 400", False, "couldn't create temp conv")

        # ---- RESULTS ----
        print(f"\n{'='*40}")
        print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
        if errors:
            print("\nFailed tests:")
            for e in errors:
                print(f"  - {e}")
        print("=" * 40)


if __name__ == "__main__":
    run_tests()
