from pydantic import BaseModel, Field

from mealplanner.data.models.days import Day


class CreateSummary(BaseModel):
    day: Day
    maximum_calorie_target: int = Field(..., ge=0, le=10000)