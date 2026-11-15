from typing import List

from pydantic import BaseModel

from mealplanner.data.models.days import Day

class DaySummary(BaseModel):
    day: Day
    dish_list: List[str]
    total_calories: int
    target_acquired: bool
