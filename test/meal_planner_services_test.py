import os
from uuid import uuid4

import pytest
from pymongo import MongoClient

from mealplanner.data.models import days, day_summary
from mealplanner.data.repositories.mongo_meal_repository import MongoMealRepository
from mealplanner.dtos.create_meal import CreateMeal
from mealplanner.dtos.create_summary import CreateSummary
from mealplanner.exceptions.meal_not_found_error import MealNotFoundError
from mealplanner.service.meal_planner_service import MealPlannerService


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    )

    yield client

    client.close()


@pytest.fixture
def service(mongo_client):
    # Create a fresh database per test so test data stays isolated from app data and other tests.
    database = mongo_client[f"mealplanner_test_{uuid4().hex}"]

    # Store this test's meals in a dedicated collection inside the isolated database.
    repository = MongoMealRepository(database["meals"])
    meal_service = MealPlannerService(repository)

    yield meal_service

    # Remove this test's temporary database after its assertions finish.
    mongo_client.drop_database(database.name)


def test_that_when_i_add_meal_it_is_saved(service):
    payload = CreateMeal(
        day=days.Day.Monday,
        dish="Semo and Egusi",
        description="Added some fish and meat",
        calories=200,
    )

    meal = service.add_meal(payload)

    saved_meal = service.get_meal(meal.meal_id)

    assert saved_meal is not None
    assert saved_meal.meal_id == meal.meal_id
    assert saved_meal.day == days.Day.Monday
    assert saved_meal.dish == "Semo and Egusi"
    assert saved_meal.description == "Added some fish and meat"
    assert saved_meal.calories == 200

def test_that_when_i_can_get_all_meals_for_a_day(service):
    payload_one = CreateMeal(
        day=days.Day.Monday,
        dish="Semo and Egusi",
        description="Added some fish and meat",
        calories=200,
    )

    payload_two = CreateMeal(
        day=days.Day.Monday,
        dish= "Rice and Stew",
        description="Added some crayfish",
        calories= 1000,
    )

    payload_three = CreateMeal(
        day=days.Day.Tuesday,
        dish="Yam and egg",
        description="Boiled eggs",
        calories= 900,
    )

    service.add_meal(payload_one)
    service.add_meal(payload_two)
    service.add_meal(payload_three)

    monday_meals = service.get_meals(day=days.Day.Monday)

    assert len(monday_meals) == 2

    for meal in monday_meals:
        assert meal.day == days.Day.Monday

def test_that_when_there_is_no_meals_for_day_error_is_thrown_when_i_get_meals(service):
    with pytest.raises(MealNotFoundError):
        service.get_meals(day=days.Day.Monday)


def test_that_when_i_can_get_a_summary_of_each_day_meals(service):
    payload_one = CreateMeal(
        day=days.Day.Monday,
        dish="Semo and Egusi",
        description="Added some fish and meat",
        calories=200,
    )

    payload_two = CreateMeal(
        day=days.Day.Monday,
        dish="Rice and Stew",
        description="Added some crayfish",
        calories=1000,
    )

    payload_three = CreateMeal(
        day=days.Day.Tuesday,
        dish="Yam and egg",
        description="Boiled eggs",
        calories=900,
    )

    service.add_meal(payload_one)
    service.add_meal(payload_two)
    service.add_meal(payload_three)

    monday_summary = service.get_day_summary(
        CreateSummary(
            day=days.Day.Monday,
            maximum_calorie_target=2000
        ))
    tuesday_summary = service.get_day_summary(
        CreateSummary(
            day=days.Day.Tuesday,
            maximum_calorie_target=300
        ))


    assert monday_summary.total_calories == 1200
    assert tuesday_summary.total_calories == 900
    assert monday_summary.target_acquired is True
    assert tuesday_summary.target_acquired is False


def test_that_when_i_delete_meal_it_is_deleted_error_is_thrown_when_i_get_deleted_id(service):
    payload = CreateMeal(
        day=days.Day.Monday,
        dish="Semo and Egusi",
        description="Added some fish and meat",
        calories=200,
    )

    meal = service.add_meal(payload)
    service.delete_meal(meal.meal_id)

    with pytest.raises(MealNotFoundError):
        service.get_meal(meal.meal_id)


def test_get_meal_raises_error_when_id_does_not_exist(service):
    missing_meal_id = "meal-that-does-not-exist"

    with pytest.raises(MealNotFoundError, match="Meal not found"):
        service.get_meal(missing_meal_id)


def test_get_meals_raises_error_when_only_other_days_have_meals(service):
    service.add_meal(
        CreateMeal(
            day=days.Day.Tuesday,
            dish="Yam and egg",
            description="Boiled eggs",
            calories=900,
        )
    )

    with pytest.raises(MealNotFoundError, match="No meals"):
        service.get_meals(day=days.Day.Monday)


def test_get_day_summary_includes_dishes_and_requested_day(service):
    service.add_meal(
        CreateMeal(
            day=days.Day.Monday,
            dish="Semo and Egusi",
            description="Lunch",
            calories=200,
        )
    )
    service.add_meal(
        CreateMeal(
            day=days.Day.Monday,
            dish="Rice and Stew",
            description="Dinner",
            calories=500,
        )
    )

    summary = service.get_day_summary(
        CreateSummary(
            day=days.Day.Monday,
            maximum_calorie_target=1000
        ))

    assert summary.day == days.Day.Monday
    assert summary.dish_list == ["Semo and Egusi", "Rice and Stew"]
    assert summary.total_calories == 700
    assert summary.target_acquired is True


def test_delete_meal_raises_error_when_id_does_not_exist(service):
    missing_meal_id = "meal-that-does-not-exist"

    with pytest.raises(MealNotFoundError, match="Meal not found"):
        service.delete_meal(missing_meal_id)


