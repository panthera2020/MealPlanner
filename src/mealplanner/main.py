from fastapi import FastAPI
from mealplanner.controllers.meal_planner_controller import router as meal_planner_router

app = FastAPI(title="Meal Planner")

app.include_router(meal_planner_router)