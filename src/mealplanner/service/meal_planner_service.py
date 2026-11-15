from typing import List

from mealplanner.data.models.day_summary import DaySummary
from mealplanner.data.models.days import Day
from mealplanner.data.models.meal import Meal
from mealplanner.data.repositories.meal_repository import MealRepository
from mealplanner.dtos.create_meal import CreateMeal
from mealplanner.dtos.create_summary import CreateSummary
from mealplanner.exceptions.meal_not_found_error import MealNotFoundError


class MealPlannerService:
    def __init__(self, repository: MealRepository):
        self.repository = repository

    def add_meal(self, payload: CreateMeal) -> Meal:
        new_meal = Meal(day=payload.day, dish=payload.dish, description=payload.description, calories=payload.calories)
        return self.repository.add(new_meal)

    def get_meal(self, meal_id: str) -> Meal:
        meal = self.repository.get_meal(meal_id)
        if meal is None: raise MealNotFoundError("Meal not found")
        return  meal

    def get_meals(self, day: Day) -> List[Meal]:
        meals_for_day = [meal for meal in self.repository.list() if meal.day == day]
        if not meals_for_day:
            raise MealNotFoundError(f"No meals for {day}")
        return meals_for_day

    def get_day_summary(self, payload: CreateSummary) -> DaySummary:
        days_meal = self.get_meals(payload.day)

        dish_list = [meal.dish for meal in days_meal]
        total_calories = sum(meal.calories for meal in days_meal)
        target_achieved = total_calories <= payload.maximum_calorie_target

        return DaySummary( day=payload.day, dish_list=dish_list, total_calories=total_calories, target_acquired= target_achieved )

    def delete_meal(self, meal_id: str) -> bool:
        status = self.repository.remove(meal_id)
        if not status: raise MealNotFoundError("Meal not found")
        return status
