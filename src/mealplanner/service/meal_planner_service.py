from typing import List

from mealplanner.data.models.day_summary import DaySummary
from mealplanner.data.models.days import Day
from mealplanner.data.models.meal import Meal
from mealplanner.data.repositories.meal_repository import MealRepository
from mealplanner.dtos.create_meal import CreateMeal
from mealplanner.exceptions.meal_not_found_error import MealNotFoundError


class MealPlannerService:
    def __init__(self, repository: MealRepository):
        self.repository = repository

    def add(self, payload: CreateMeal) -> Meal:
        new_meal = Meal(day=payload.day, dish=payload.dish, description=payload.description, calories=payload.calories)
        return self.repository.add(new_meal)

    def get_meal(self, meal_id: str) -> Meal:
        meal = self.repository.get_meal(meal_id)
        if meal is None: raise MealNotFoundError("Meal not found")
        return  meal

    def get_meals(self, day: Day) -> List[Meal]:
        days_meal = self.repository.list()
        if len(days_meal) == 0: raise MealNotFoundError(f"No meals for {day}")
        return [meals for meals in days_meal if meals.day == day]

    def get_day_summary(self, day: Day) -> DaySummary:
        days_meal = self.get_meals(day)

        dish_list = [meal.dish for meal in days_meal]
        total_calories = sum(meal.calories for meal in days_meal)

        return DaySummary( day=day, dish_list=dish_list, total_calories=total_calories )

    def delete_meal(self, meal_id: str) -> None:
        status = self.repository.remove(meal_id)
        if not status: raise MealNotFoundError("Meal not found")
