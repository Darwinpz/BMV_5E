from database.mongoDb import DatabaseConnection
from models.exitTicketModel import ExitTicketModel

class ExitTicketRepository:
    def __init__(self):
        self.collection = DatabaseConnection.get_collection('exit_tickets')

    def create(self, exit_ticket: ExitTicketModel) -> str:
        result = self.collection.insert_one(exit_ticket.to_dict())
        return str(result.inserted_id)

    def find_by_student_id(self, student_id: str):
        data = self.collection.find_one({'student_id': student_id})
        return ExitTicketModel.from_dict(data) if data else None

    def find_all(self):
        return [ExitTicketModel.from_dict(d) for d in self.collection.find().sort('created_at', -1)]

    def delete_by_student_id(self, student_id: str):
        self.collection.delete_many({'student_id': student_id})

    def count_by_carrera(self) -> dict:
        pipeline = [
            {'$group': {'_id': '$carrera_interes', 'total': {'$sum': 1}}},
            {'$sort': {'total': -1}}
        ]
        return {doc['_id']: doc['total'] for doc in self.collection.aggregate(pipeline)}
