import pytest
from fastapi.testclient import TestClient
from mealplanner import dependency
from mealplanner.main import app


@pytest.fixture(autouse=True)
def clear_meals():
    yield
    dependency._repository._collection.delete_many({})


@pytest.fixture(scope="module")
def client():
    test_client = TestClient(app)
    yield test_client
    test_client.close()


def test_that_add_meal_returns_201_and_created_meal(client):
    response = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })
    assert response.status_code == 201
    assert response.json()["day"] == "Monday"
    assert response.json()["dish"] == "Rice and Boiled egg"

def test_that_when_i_add_meal_with_bad_json_error_returns_422(client):
    response = client.post(
        '/meals_planner/new',
        json={
            "day": "Moonday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })
    assert response.status_code == 422


def test_that_get_meal_returns_200_and_created_meal(client):
    post_response = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })

    meal_id = post_response.json()["meal_id"]

    get_response = client.get(f'/meals_planner/meal/{meal_id}')

    assert get_response.status_code == 200
    assert get_response.json()["meal_id"] == meal_id
    assert get_response.json()["day"] == "Monday"
    assert get_response.json()["dish"] == "Rice and Boiled egg"
    assert get_response.json()["description"] == "Breakfast"

def test_that_when_i_get_meal_with_invalid_id_returns_404(client):
    meal_id = "invalid_meal_id"

    response = client.get(f'/meals_planner/meal/{meal_id}')

    assert response.status_code == 404

def test_that_get_meals_returns_200_and_only_meals_for_requested_day(client):
    post_response_one = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })

    post_response_two = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Chicken and Chips",
            "description": "Lunch",
            "calories": 500
        })
    post_response_three = client.post(
        '/meals_planner/new',
        json={
            "day": "Tuesday",
            "dish": "Eba and Egusi",
            "description": "Breakfast",
            "calories": 600
        })
    assert post_response_one.status_code == 201
    assert post_response_two.status_code == 201
    assert post_response_three.status_code == 201

    meals_response = client.get('/meals_planner/day_meals/Monday')

    assert meals_response.status_code == 200

    returned_meals = meals_response.json()
    returned_dishes = {meal["dish"] for meal in returned_meals}
    assert {"Rice and Boiled egg", "Chicken and Chips"}.issubset(returned_dishes)
    assert all(meal["day"] == "Monday" for meal in returned_meals)


def test_that_get_meals_returns_404_if_day_is_invalid(client):
    response = client.get('/meals_planner/meal/invalid')
    assert response.status_code == 404

def test_that_i_can_get_summary_after_entering_various_meals_and_returns_200(client):
    post_response_one = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })

    post_response_two = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Chicken and Chips",
            "description": "Lunch",
            "calories": 500
        })
    post_response_three = client.post(
        '/meals_planner/new',
        json={
            "day": "Tuesday",
            "dish": "Eba and Egusi",
            "description": "Breakfast",
            "calories": 600
        })
    assert post_response_one.status_code == 201
    assert post_response_two.status_code == 201
    assert post_response_three.status_code == 201

    summary_response = client.post(
        '/meals_planner/day_summary',
        json={
            "day": "Monday",
            "maximum_calorie_target": 1000,
        }
    )

    assert summary_response.status_code == 200
    assert summary_response.json()["day"] == "Monday"
    returned_dishes = {dish for dish in summary_response.json()["dish_list"]}
    assert {"Rice and Boiled egg", "Chicken and Chips"}.issubset(returned_dishes)
    assert summary_response.json()["total_calories"] == 850
    assert summary_response.json()["target_acquired"] is True

def test_that_when_i_get_summary_of_incorrect_day_return_404(client):
    response = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })

    assert response.status_code == 201

    summary_response = client.post(
        '/meals_planner/day_summary',
        json={
            "day": "Wednesday",
            "maximum_calorie_target": 1000,
        }
    )

    assert summary_response.status_code == 404

def test_that_when_i_delete_meal_returns_201_meal_is_deleted(client):
    response = client.post(
        '/meals_planner/new',
        json={
            "day": "Monday",
            "dish": "Rice and Boiled egg",
            "description": "Breakfast",
            "calories": 350
        })
    assert response.status_code == 201

    delete_response = client.delete(f'/meals_planner/remove/{response.json()["meal_id"]}')

    assert delete_response.status_code == 200

    get_response = client.get(f'/meals_planner/meal/{response.json()["meal_id"]}')

    assert get_response.status_code == 404

def test_that_when_i_delete_with_invalid_id_error_is_returned(client):
    invalid_meal_id = "invalid_meal_id"
    response = client.delete(f'/meals_planner/remove/{invalid_meal_id}')

    assert response.status_code == 404

