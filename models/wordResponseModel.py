from datetime import datetime

class WordResponseModel:
    def __init__(self, id=None, palabra=None, student_id=None, created_at=None):
        self.id = id
        self.palabra = palabra
        self.student_id = student_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return WordResponseModel(
            id=str(data.get('_id', '')),
            palabra=data.get('palabra'),
            student_id=data.get('student_id'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'palabra': self.palabra,
            'student_id': self.student_id,
            'created_at': self.created_at
        }
