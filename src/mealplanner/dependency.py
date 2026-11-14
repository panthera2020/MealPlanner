from fastapi import Depends

from mealplanner.data.repositories.meal_repository import MealRepository
from mealplanner.data.repositories.mongo_meal_repository import MongoMealRepository
from mealplanner.database import mealplanner_collection
from mealplanner.service.meal_planner_service import MealPlannerService

_repository = MongoMealRepository(mealplanner_collection)

def get_meal_repository() -> MealRepository:
    return _repository

def get_meal_service( repository: MealRepository = Depends(get_meal_repository)) -> MealPlannerService:
    return MealPlannerService(repository)