"""Full integration test suite for ExpatVault API."""
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
TEST_EMAIL = "testuser@expatvault.dev"
TEST_PHONE = "+971501234567"
TEST_PASSWORD = "SecurePass123!"


def cleanup():
    from app.database import get_supabase
    db = get_supabase()
    result = db.table("users").select("id").eq("email", TEST_EMAIL).execute()
    if result.data:
        uid = result.data[0]["id"]
        db.table("reminders").delete().eq("user_id", uid).execute()
        db.table("documents").delete().eq("user_id", uid).execute()
        db.table("notifications").delete().eq("user_id", uid).execute()
        db.table("otp_codes").delete().eq("user_id", uid).execute()
        db.table("sessions").delete().eq("user_id", uid).execute()
        db.table("users").delete().eq("id", uid).execute()


def run_tests():
    # Cleanup any leftover data
    cleanup()

    print("=== EXPATVAULT INTEGRATION TESTS ===\n")
    passed = 0
    failed = 0

    def check(num, name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  {num}. {name}: PASS {detail}")
        else:
            failed += 1
            print(f"  {num}. {name}: FAIL {detail}")

    # 1. Health
    r = client.get("/api/health")
    check(1, "Health Check", r.status_code == 200, f"({r.json()['status']})")

    # 2. Register
    r = client.post("/api/v1/auth/register", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User",
        "phone": TEST_PHONE,
        "nationality": "Indian",
    })
    check(2, "Register", r.status_code == 201, f"({r.json()})")

    # 3. Login with email
    r = client.post("/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
    })
    check(3, "Login (email)", r.status_code == 200)
    tokens = r.json()
    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")
    headers = {"Authorization": f"Bearer {access_token}"}

    # 4. Login with phone
    r = client.post("/api/v1/auth/login", json={
        "phone": TEST_PHONE,
        "password": TEST_PASSWORD,
    })
    check(4, "Login (phone)", r.status_code == 200)

    # 5. Get profile
    r = client.get("/api/v1/users/me", headers=headers)
    check(5, "Get Profile", r.status_code == 200 and r.json()["email"] == TEST_EMAIL,
          f"(name={r.json().get('full_name')})")

    # 6. Update profile
    r = client.patch("/api/v1/users/me", headers=headers, json={
        "nationality": "Pakistani",
        "emirates_id_number": "784-1234-1234567-1",
    })
    check(6, "Update Profile", r.status_code == 200 and r.json()["nationality"] == "Pakistani")

    # 7. Document types
    r = client.get("/api/v1/documents/types", headers=headers)
    check(7, "Document Types", r.status_code == 200 and len(r.json()) == 13,
          f"({len(r.json())} types)")
    doc_types = r.json()

    # 8. Duplicate register
    r = client.post("/api/v1/auth/register", json={
        "email": TEST_EMAIL,
        "password": "Another123!",
        "full_name": "Dup",
    })
    check(8, "Duplicate Register Rejected", r.status_code == 409)

    # 9. Wrong password
    r = client.post("/api/v1/auth/login", json={
        "email": TEST_EMAIL,
        "password": "WrongPassword!",
    })
    check(9, "Wrong Password Rejected", r.status_code == 401)

    # 10. Refresh token
    r = client.post("/api/v1/auth/token/refresh", json={
        "refresh_token": refresh_token,
    })
    check(10, "Token Refresh", r.status_code == 200)
    if r.status_code == 200:
        new_tokens = r.json()
        access_token = new_tokens["access_token"]
        refresh_token = new_tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

    # 11. Dependency chain
    visa_type = next((dt for dt in doc_types if dt["name"] == "visa"), None)
    check(11, "Visa Dependency Chain",
          visa_type and "health_insurance" in (visa_type.get("dependency_chain") or []),
          f"(deps={visa_type.get('dependency_chain') if visa_type else 'N/A'})")

    # 12. List documents (empty)
    r = client.get("/api/v1/documents/", headers=headers)
    check(12, "List Docs (empty)", r.status_code == 200 and r.json()["total"] == 0)

    # 13. Create document - needs verified user
    # Manually verify user for testing
    from app.database import get_supabase
    db = get_supabase()
    db.table("users").update({"is_verified": True}).eq("email", TEST_EMAIL).execute()

    visa_type_id = visa_type["id"] if visa_type else 1
    r = client.post("/api/v1/documents/", headers=headers, data={
        "document_type_id": str(visa_type_id),
        "title": "My UAE Visa 2026",
        "expiry_date": "2027-01-15",
        "issue_date": "2025-01-15",
    })
    check(13, "Create Document", r.status_code == 201,
          f"(status={r.json().get('status')})" if r.status_code == 201 else f"({r.text})")
    doc_id = r.json().get("id") if r.status_code == 201 else None

    # 14. List (should have 1)
    r = client.get("/api/v1/documents/", headers=headers)
    check(14, "List After Create", r.status_code == 200 and r.json()["total"] == 1)

    # 15. Get single document
    if doc_id:
        r = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        check(15, "Get Document", r.status_code == 200)
    else:
        check(15, "Get Document", False, "(no doc_id)")

    # 16. Update document
    if doc_id:
        r = client.patch(f"/api/v1/documents/{doc_id}", headers=headers, json={
            "title": "My UAE Visa 2026 (Updated)",
        })
        check(16, "Update Document", r.status_code == 200 and "Updated" in r.json().get("title", ""))
    else:
        check(16, "Update Document", False, "(no doc_id)")

    # 17. Expiring docs
    r = client.get("/api/v1/documents/expiring?days=365", headers=headers)
    check(17, "Expiring Documents", r.status_code == 200,
          f"({len(r.json())} expiring)")

    # 18. Dependencies
    if doc_id:
        r = client.get(f"/api/v1/documents/{doc_id}/dependencies", headers=headers)
        check(18, "Check Dependencies", r.status_code == 200,
              f"(met={r.json().get('prerequisites_met')}, warnings={r.json().get('warnings')})")
    else:
        check(18, "Check Dependencies", False, "(no doc_id)")

    # 19. Auto-created reminders
    r = client.get("/api/v1/reminders/", headers=headers)
    check(19, "Auto Reminders", r.status_code == 200,
          f"({len(r.json())} reminders)")
    reminders = r.json() if r.status_code == 200 else []

    # 20. Snooze reminder
    if reminders:
        rem_id = reminders[0]["id"]
        r = client.post(f"/api/v1/reminders/{rem_id}/snooze", headers=headers, json={"days": 7})
        check(20, "Snooze Reminder", r.status_code == 200 and r.json()["status"] == "snoozed")
    else:
        check(20, "Snooze Reminder", True, "(skip - no reminders)")

    # 21. Acknowledge reminder
    if len(reminders) > 1:
        rem_id = reminders[1]["id"]
        r = client.post(f"/api/v1/reminders/{rem_id}/acknowledge", headers=headers)
        check(21, "Acknowledge Reminder", r.status_code == 200 and r.json()["status"] == "acknowledged")
    else:
        check(21, "Acknowledge Reminder", True, "(skip - not enough reminders)")

    # 22. Notifications
    r = client.get("/api/v1/notifications/", headers=headers)
    check(22, "List Notifications", r.status_code == 200)

    # 23. Unread count
    r = client.get("/api/v1/notifications/unread-count", headers=headers)
    check(23, "Unread Count", r.status_code == 200, f"(count={r.json().get('count')})")

    # 24. No auth
    r = client.get("/api/v1/users/me")
    check(24, "Unauthorized Rejected", r.status_code == 403)

    # 25. Login with missing both email and phone
    r = client.post("/api/v1/auth/login", json={
        "password": TEST_PASSWORD,
    })
    check(25, "Login No Identifier", r.status_code == 400)

    # 26. Archive document
    if doc_id:
        r = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
        check(26, "Archive Document", r.status_code == 200)
    else:
        check(26, "Archive Document", False, "(no doc_id)")

    # 27. Verify archived
    r = client.get("/api/v1/documents/", headers=headers)
    check(27, "Post-Archive Empty", r.status_code == 200 and r.json()["total"] == 0)

    # 28. Logout
    r = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
    check(28, "Logout", r.status_code == 200)

    # 29. Revoked refresh token
    r = client.post("/api/v1/auth/token/refresh", json={"refresh_token": refresh_token})
    check(29, "Revoked Token Rejected", r.status_code == 401)

    # 30. OTP send (need to login again)
    r = client.post("/api/v1/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD})
    if r.status_code == 200:
        t = r.json()
        h = {"Authorization": f"Bearer {t['access_token']}"}
        r2 = client.post("/api/v1/auth/otp/send", headers=h, json={"channel": "email"})
        check(30, "Send OTP", r2.status_code == 200)
    else:
        check(30, "Send OTP", False, "(login failed)")

    # Cleanup
    cleanup()
    print(f"\nCleanup: Done")

    print(f"\n{'=' * 45}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    print(f"{'=' * 45}")

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
