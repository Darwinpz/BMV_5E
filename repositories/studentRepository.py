from bson import ObjectId
from database.mongoDb import DatabaseConnection
from models.studentModel import StudentModel

class StudentRepository:
    def __init__(self):
        self.collection = DatabaseConnection.get_collection('students')

    def create(self, student: StudentModel) -> str:
        result = self.collection.insert_one(student.to_dict())
        return str(result.inserted_id)

    def find_by_id(self, student_id: str):
        data = self.collection.find_one({'_id': ObjectId(student_id)})
        return StudentModel.from_dict(data) if data else None

    def find_by_session_id(self, session_id: str):
        data = self.collection.find_one({'session_id': session_id})
        return StudentModel.from_dict(data) if data else None

    def find_by_email(self, email: str):
        data = self.collection.find_one({'email': email})
        return StudentModel.from_dict(data) if data else None

    def find_all(self):
        return [StudentModel.from_dict(d) for d in self.collection.find().sort('created_at', -1)]
