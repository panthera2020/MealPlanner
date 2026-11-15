from fastapi import APIRouter, Depends, status, HTTPException

from mealplanner.data.models.day_summary import DaySummary
from mealplanner.data.models.days import Day
from mealplanner.data.models.meal import Meal
from mealplanner.dependency import get_meal_service
from mealplanner.dtos.create_meal import CreateMeal
from mealplanner.dtos.create_summary import CreateSummary
from mealplanner.exceptions.meal_not_found_error import MealNotFoundError
from mealplanner.service.meal_planner_service import MealPlannerService

router = APIRouter(prefix="/meals_planner", tags=["MealsPlanner"])

@router.post('/new', response_model=Meal, status_code=status.HTTP_201_CREATED)
def add_meal(
        payload: CreateMeal,
        service: MealPlannerService = Depends(get_meal_service),
):
    return service.add_meal(payload)

@router.get('/meal/{meal_id}', response_model= Meal, status_code=status.HTTP_200_OK)
def get_meal(
        meal_id: str,
        service: MealPlannerService = Depends(get_meal_service),
):
    try: return service.get_meal(meal_id)
    except MealNotFoundError as e: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get('/day_meals/{day}', response_model=list[Meal], status_code=status.HTTP_200_OK)
def get_meals(
        day: Day,
        service: MealPlannerService = Depends(get_meal_service),
):
    try: return service.get_meals(day)
    except MealNotFoundError as e: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post('/day_summary', response_model= DaySummary, status_code=status.HTTP_200_OK)
def get_day_summary(
        payload: CreateSummary,
        service: MealPlannerService = Depends(get_meal_service),
):
    try: return service.get_day_summary(payload)
    except MealNotFoundError as e: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete('/remove/{meal_id}', response_model=bool, status_code=status.HTTP_200_OK)
def delete_meal(
        meal_id: str,
        service: MealPlannerService = Depends(get_meal_service),
):
    try: return service.delete_meal(meal_id)
    except MealNotFoundError as e: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
