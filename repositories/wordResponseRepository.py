from collections import Counter
from database.mongoDb import DatabaseConnection
from models.wordResponseModel import WordResponseModel

class WordResponseRepository:
    def __init__(self):
        self.collection = DatabaseConnection.get_collection('word_responses')

    def create(self, word_response: WordResponseModel) -> str:
        result = self.collection.insert_one(word_response.to_dict())
        return str(result.inserted_id)

    def get_word_frequencies(self) -> dict:
        palabras = [doc['palabra'].lower() for doc in self.collection.find({}, {'palabra': 1})]
        return dict(Counter(palabras))

    def count_by_student(self, student_id: str) -> int:
        return self.collection.count_documents({'student_id': student_id})

    def find_by_student(self, student_id: str) -> list:
        return list(self.collection.find({'student_id': student_id}))

    def delete_by_student_id(self, student_id: str):
        self.collection.delete_many({'student_id': student_id})
