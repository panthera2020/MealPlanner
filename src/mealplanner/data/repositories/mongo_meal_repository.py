from typing import Optional, List

from mealplanner.data.models.meal import Meal
from mealplanner.data.repositories.meal_repository import MealRepository

from pymongo.collection import Collection
from pymongo import ReturnDocument

class MongoMealRepository(MealRepository):

    def __init__(self, collection: Collection):
        self._collection = collection

    def add(self, meal: Meal) -> Meal:
        document = self._to_document(meal)
        self._collection.insert_one(document)
        return meal

    def get_meal(self, meal_id: str) -> Optional[Meal]:
        document = self._collection.find_one({"_id": str(meal_id)})
        return self._to_model(document) if document else None

    def update(self, meal: Meal, data: dict) -> Optional[Meal]:
        document = self._collection.find_one_and_update(
            {"_id": str(meal.meal_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_model(document) if document else None

    def remove(self, meal_id: str) -> bool:
        result = self._collection.delete_one({"_id": str(meal_id)})
        return result.deleted_count == 1

    def list(self) -> List[Meal]:
        return [self._to_model(document) for document in self._collection.find()]



    @staticmethod
    def _to_document(meal: Meal) -> dict:
        document = meal.model_dump(exclude={"meal_id"})
        # Store the service's meal ID as MongoDB's document ID for later lookups.
        document["_id"] = meal.meal_id
        return document

    @staticmethod
    def _to_model(document: dict) -> Meal:
        document = dict(document)
        # Restore MongoDB's document ID as the meal ID expected by the model.
        document["meal_id"] = document.pop("_id")

        return Meal(**document)
