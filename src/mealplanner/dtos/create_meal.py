from typing import Optional

from pydantic import BaseModel, Field

from mealplanner.data.models.days import Day


class CreateMeal(BaseModel):
    day: Day
    dish: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    calories: int = Field(..., ge=1, le=5000)