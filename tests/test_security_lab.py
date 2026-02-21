import app as lab_app


def set_mode(client, secure):
    response = client.post("/api/set_security_mode", json={"secure": secure})
    assert response.status_code == 200


def reset_state(client):
    response = client.post("/api/reset_lab_state")
    assert response.status_code == 200


def test_sqli_login_bypass_vulnerable_awards_flag():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    payload = {"username": "admin' OR '1'='1", "password": "abc"}
    response = client.post("/api/login", json=payload)
    data = response.get_json()

    assert data["status"] == "success"
    assert data["secure"] is False
    assert data["flag_awarded"] is True


def test_sqli_login_bypass_secure_blocked():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = {"username": "admin' OR '1'='1", "password": "abc"}
    response = client.post("/api/login", json=payload)
    data = response.get_json()

    assert data["status"] == "fail"
    assert data["secure"] is True


def test_union_sqli_vulnerable_exfiltrates_usernames():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    payload = {"search": "%' UNION SELECT 1, username, password, email FROM users --"}
    response = client.post("/api/search_product", json=payload)
    data = response.get_json()

    names = [item["name"] for item in data["products"]]
    assert "admin" in names
    assert data["flag_awarded"] is True


def test_union_sqli_secure_does_not_exfiltrate():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = {"search": "%' UNION SELECT 1, username, password, email FROM users --"}
    response = client.post("/api/search_product", json=payload)
    data = response.get_json()

    names = [item["name"] for item in data["products"]]
    assert "admin" not in names
    assert data["secure"] is True


def test_blind_sqli_time_based_vulnerable_has_delay():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    payload = {"probe": "admin' AND sleep(1)=0 --"}
    response = client.post("/api/blind_check", json=payload)
    data = response.get_json()

    assert data["status"] == "success"
    assert data["duration_ms"] >= 900
    assert data["flag_awarded"] is True


def test_blind_sqli_time_based_secure_has_no_delay():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = {"probe": "admin' AND sleep(1)=0 --"}
    response = client.post("/api/blind_check", json=payload)
    data = response.get_json()

    assert data["status"] == "success"
    assert data["duration_ms"] < 500
    assert data["secure"] is True


def test_stored_xss_secure_is_escaped():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = "<script>alert('xss')</script>"
    post_response = client.post(
        "/api/post_comment",
        json={"username": "test", "content": payload},
    )
    assert post_response.status_code == 200

    comments_response = client.get("/api/get_comments")
    data = comments_response.get_json()
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" in data["comments"][0]["content"]


def test_reflected_xss_secure_is_escaped():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = "<img src=x onerror=alert(1)>"
    response = client.post("/api/search_reflect", json={"search": payload})
    data = response.get_json()

    assert "&lt;img src=x onerror=alert(1)&gt;" in data["message"]
    assert data["secure"] is True


def test_dom_claim_vulnerable_awards_flag():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    payload = "<img src=x onerror=alert(1)>"
    response = client.post("/api/claim_dom_xss", json={"payload": payload})
    data = response.get_json()

    assert data["status"] == "success"
    assert data["flag_awarded"] is True


def test_context_demo_secure_sample_uses_safe_js_encoding():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, True)

    payload = "x';alert(1);//"
    response = client.post("/api/xss_context_demo", json={"value": payload})
    data = response.get_json()

    secure_js = data["secure_samples"]["javascript_string"]
    assert "const userValue = \"x';alert(1);//\";" in secure_js


def test_token_capture_vulnerable_awards_flag():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    token_response = client.get("/api/lab_token")
    token = token_response.get_json()["token"]

    capture_response = client.post(
        "/api/capture_token",
        json={"token": token, "source": "pytest"},
    )
    data = capture_response.get_json()

    assert data["status"] == "success"
    assert data["flag_awarded"] is True


def test_security_events_receive_suspicious_payload():
    client = lab_app.app.test_client()
    reset_state(client)
    set_mode(client, False)

    client.post("/api/login", json={"username": "admin' OR '1'='1", "password": "x"})
    events_response = client.get("/api/security_events")
    events_data = events_response.get_json()

    assert events_data["total"] >= 1
    assert any("SQLi/Login" == item["category"] for item in events_data["events"])
