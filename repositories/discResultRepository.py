from bson import ObjectId
from database.mongoDb import DatabaseConnection
from models.discResultModel import DiscResultModel

class DiscResultRepository:
    def __init__(self):
        self.collection = DatabaseConnection.get_collection('disc_results')

    def create(self, disc_result: DiscResultModel) -> str:
        result = self.collection.insert_one(disc_result.to_dict())
        return str(result.inserted_id)

    def find_by_student_id(self, student_id: str):
        data = self.collection.find_one({'student_id': student_id})
        return DiscResultModel.from_dict(data) if data else None

    def upsert_by_student_id(self, student_id: str, disc_result: DiscResultModel):
        self.collection.update_one(
            {'student_id': student_id},
            {'$set': disc_result.to_dict()},
            upsert=True
        )

    def find_all(self):
        return [DiscResultModel.from_dict(d) for d in self.collection.find()]
