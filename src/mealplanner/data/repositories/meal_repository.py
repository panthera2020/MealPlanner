from abc import ABC, abstractmethod
from typing import List, Optional

from mealplanner.data.models.meal import Meal


class MealRepository(ABC):

    @abstractmethod
    def add(self, meal: Meal) -> Meal:
        ...

    @abstractmethod
    def get_meal(self, meal_id: str) -> Optional[Meal]:
        ...

    @abstractmethod
    def remove(self, meal_id: str) -> bool:
        ...

    @abstractmethod
    def update(self, meal: Meal, data: dict) -> Optional[Meal]:
        ...

    @abstractmethod
    def list(self) -> List[Meal]:
        ...
