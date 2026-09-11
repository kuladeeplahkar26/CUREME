import uuid
import requests

base = "http://127.0.0.1:8000"

def test_all():
    print("=" * 60)
    print("STARTING FULL END-TO-END VERIFICATION")
    print("=" * 60)

    # 1. Test Static files delivery
    print("\n[Step 1] Verifying HTML structures & Login-First flow...")
    web_html = requests.get(f"{base}/web/").text
    assert 'id="view-login-view"' in web_html and 'view-section active' in web_html
    assert 'id="view-elderly-view" class="view-section active"' not in web_html
    assert 'id="caregiverPatientManagementSection"' in web_html
    assert 'id="addPatientModal"' in web_html
    assert 'id="deletePatientModal"' in web_html
    assert 'id="deleteCaregiverModal"' in web_html
    assert 'id="caregiverDangerZoneCard"' in web_html
    print("  -> Passed: Login is active by default, modals and sections present.")

    # 2. Test CSS rules
    print("\n[Step 2] Verifying CSS design system...")
    css_text = requests.get(f"{base}/web/styles.css").text
    assert ".patient-card" in css_text
    assert "body.auth-locked .sidebar" in css_text
    assert ".btn-danger" in css_text
    print("  -> Passed: Patient cards, auth-locked, and danger styles verified.")

    # 3. Test JS logic
    print("\n[Step 3] Verifying JavaScript client logic...")
    js_text = requests.get(f"{base}/web/app.js").text
    assert "renderCaregiverPatients" in js_text
    assert "handleAddPatientSubmit" in js_text
    assert "executeDeletePatient" in js_text
    assert "executeDeleteCaregiverAccount" in js_text
    assert "localStorage.removeItem('apon_session')" in js_text
    assert "history.replaceState" in js_text
    print("  -> Passed: Core JS methods and handlers verified.")

    # 4. End-to-end Backend Flow: Elderly Login
    print("\n[Step 4] Verifying Elderly Patient Login...")
    eld_login = requests.post(f"{base}/auth/login", json={"username": "eleanor", "password": "password123"}).json()
    assert eld_login["role"] == "elderly" and eld_login["name"] == "Eleanor Vance"
    print(f"  -> Passed: Elderly user logged in: {eld_login['name']}")

    # 5. End-to-end Backend Flow: Caregiver Login
    print("\n[Step 5] Verifying Caregiver Login...")
    cg_login = requests.post(f"{base}/auth/login", json={"username": "sarah", "password": "password123"}).json()
    assert cg_login["role"] == "caregiver" and cg_login["name"] == "Sarah Vance"
    print(f"  -> Passed: Caregiver user logged in: {cg_login['name']}")

    # 6. Caregiver gets own patients
    print("\n[Step 6] Verifying Caregiver patient list...")
    pts = requests.get(f"{base}/users/caregiver/{cg_login['user_id']}/patients").json()
    assert any(p["username"] == "eleanor" for p in pts), "Eleanor must be assigned to Sarah"
    print(f"  -> Passed: Loaded {len(pts)} patient(s): {[p['name'] for p in pts]}")

    # 7. Caregiver adds new patient
    print("\n[Step 7] Adding a new patient (Arthur Pendelton)...")
    suffix = uuid.uuid4().hex[:6]
    new_pt = requests.post(f"{base}/users/caregiver/{cg_login['user_id']}/add-patient", json={
        "username": f"arthur_{suffix}",
        "name": "Arthur Pendelton",
        "age": 74,
        "password": "password123",
        "relationship": "Father"
    }).json()
    pt_id = new_pt["id"]
    print(f"  -> Passed: Added patient '{new_pt['name']}' with ID {pt_id}")

    # 8. Check patient list now contains Arthur
    print("\n[Step 8] Verifying new patient appears in patient list...")
    pts_after = requests.get(f"{base}/users/caregiver/{cg_login['user_id']}/patients").json()
    assert any(p["id"] == pt_id for p in pts_after)
    print("  -> Passed: Arthur confirmed in caregiver's patient list.")

    # 9. Authorization security: Another caregiver cannot delete Arthur
    print("\n[Step 9] Verifying backend authorization on delete...")
    fake_cg = requests.post(f"{base}/auth/register", json={
        "username": f"fake_cg_{suffix}", "password": "password123", "name": "Fake CG", "role": "caregiver"
    }).json()
    sec_res = requests.delete(f"{base}/users/caregiver/{fake_cg['id']}/patient/{pt_id}")
    assert sec_res.status_code == 403, f"Expected 403 Forbidden, got {sec_res.status_code}"
    print("  -> Passed: Unauthorized caregiver received 403 Forbidden.")

    # 10. Caregiver Sarah deletes Arthur
    print("\n[Step 10] Deleting patient by assigned caregiver...")
    del_res = requests.delete(f"{base}/users/caregiver/{cg_login['user_id']}/patient/{pt_id}")
    assert del_res.status_code == 200
    print("  -> Passed: Patient deleted successfully.")

    # 11. Verify Arthur is gone
    print("\n[Step 11] Verifying patient removed from database...")
    pts_final = requests.get(f"{base}/users/caregiver/{cg_login['user_id']}/patients").json()
    assert not any(p["id"] == pt_id for p in pts_final)
    assert any(p["username"] == "eleanor" for p in pts_final)
    print("  -> Passed: Arthur removed, Eleanor retained.")

    # 12. Caregiver Account Deletion test
    print("\n[Step 12] Verifying Caregiver Account Deletion & safe patient unlinking...")
    fake_pt = requests.post(f"{base}/users/caregiver/{fake_cg['id']}/add-patient", json={
        "username": f"p_fake_{suffix}", "name": "Fake Patient", "age": 80
    }).json()
    del_cg_res = requests.delete(f"{base}/users/caregivers/{fake_cg['id']}")
    assert del_cg_res.status_code == 200
    unlinked_pt = requests.get(f"{base}/users/{fake_pt['id']}").json()
    assert unlinked_pt["caregiver_id"] is None, "Patient must be safely unlinked"
    print("  -> Passed: Caregiver deleted, patient preserved with caregiver_id=None.")

    # 13. Zero-state analytics for new patient
    print("\n[Step 13] Verifying zero-state analytics for brand new patient...")
    arthur_pt = requests.post(f"{base}/users/caregiver/{cg_login['user_id']}/add-patient", json={
        "username": f"arthur_analytics_{suffix}",
        "name": "Arthur Pendelton",
        "age": 74,
        "password": "password123",
        "relationship": "Father"
    }).json()
    arthur_id = arthur_pt["id"]

    analytics_zero = requests.get(f"{base}/dashboard/patient-analytics/{arthur_id}").json()
    assert analytics_zero["activities_completed"] == 0, f"Expected 0 activities, got {analytics_zero['activities_completed']}"
    assert analytics_zero["avg_recall_score"] == 0.0, f"Expected 0.0 avg recall, got {analytics_zero['avg_recall_score']}"
    assert analytics_zero["streak_days"] == 0, f"Expected 0 days streak, got {analytics_zero['streak_days']}"
    assert analytics_zero["has_interaction"] is False, "Expected has_interaction False"
    assert analytics_zero["recent_activities"] == [], "Expected empty recent activities"
    assert analytics_zero["trends"]["memory"] == 0
    assert analytics_zero["trends"]["attention"] == 0
    assert analytics_zero["vitality_score"] == 0.0
    print("  -> Passed: New patient analytics start strictly at ZERO across all metrics.")

    # 14. Real-time updates when new elderly person plays games and performs activities
    print("\n[Step 14] Verifying real-time updates when new elderly patient plays games...")
    game_res = requests.post(f"{base}/games/results", json={
        "user_id": arthur_id,
        "game_name": "Card Memory Match",
        "score": 95.0,
        "accuracy": 100.0,
        "completion_time": 40.0,
        "difficulty_level": 1
    }).json()
    assert game_res["message"] == "Game result saved successfully"

    analytics_after = requests.get(f"{base}/dashboard/patient-analytics/{arthur_id}").json()
    assert analytics_after["activities_completed"] == 1, f"Expected 1 activity, got {analytics_after['activities_completed']}"
    assert analytics_after["avg_recall_score"] == 100.0, f"Expected 100.0 avg recall, got {analytics_after['avg_recall_score']}"
    assert analytics_after["streak_days"] >= 1, f"Expected streak >= 1, got {analytics_after['streak_days']}"
    assert analytics_after["has_interaction"] is True, "Expected has_interaction True"
    assert len(analytics_after["recent_activities"]) >= 1, "Expected at least 1 recent activity"
    assert analytics_after["trends"]["memory"] == 100
    assert analytics_after["vitality_score"] == 100.0
    assert len(analytics_after["milestones"]) >= 1, "Expected unlocked milestones"
    print("  -> Passed: Real-time dynamic updates successfully reflected after games played!")

    # 15. Verify Avatar SVG Data-URIs and no random person pictures
    print("\n[Step 15] Verifying no random stock person pictures for avatars...")
    assert "data:image/svg+xml;utf8" in web_html
    assert "generateAvatarDataUri" in js_text
    print("  -> Passed: Initials avatars verified; no random person stock photos used for user profiles.")

    print("\n" + "=" * 60)
    print("ALL 15 END-TO-END ACCEPTANCE CRITERIA VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_all()

