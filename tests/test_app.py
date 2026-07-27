def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    # Arrange
    required_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities

    for details in activities.values():
        assert required_keys.issubset(details.keys())


def test_signup_new_student_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    before = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}

    after = client.get("/activities").json()[activity_name]["participants"]
    assert new_email in after
    assert len(after) == len(before) + 1


def test_signup_duplicate_returns_400_without_mutation(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    before = list(client.get("/activities").json()[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"

    after = client.get("/activities").json()[activity_name]["participants"]
    assert after == before


def test_signup_unknown_activity_returns_404_without_mutation(client):
    # Arrange
    unknown_activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"
    before = client.get("/activities").json()

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

    after = client.get("/activities").json()
    assert after == before


def test_signup_empty_email_is_currently_allowed(client):
    # Arrange
    activity_name = "Debate Club"
    before = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": ""})

    # Assert
    assert response.status_code == 200

    after = client.get("/activities").json()[activity_name]["participants"]
    assert "" in after
    assert len(after) == len(before) + 1


def test_signup_email_matching_is_case_sensitive(client):
    # Arrange
    activity_name = "Programming Class"
    upper_case_email = "EMMA@MERGINGTON.EDU"
    before = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": upper_case_email},
    )

    # Assert
    assert response.status_code == 200

    after = client.get("/activities").json()[activity_name]["participants"]
    assert "emma@mergington.edu" in after
    assert upper_case_email in after
    assert len(after) == len(before) + 1


def test_activity_name_matching_is_case_sensitive(client):
    # Arrange
    wrong_case_activity_name = "chess club"

    # Act
    response = client.post(
        f"/activities/{wrong_case_activity_name}/signup",
        params={"email": "anotherstudent@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
