from datetime import datetime

class ExitTicketModel:
    def __init__(self, id=None, student_id=None, carrera_interes=None, claridad=None, created_at=None):
        self.id = id
        self.student_id = student_id
        self.carrera_interes = carrera_interes
        self.claridad = claridad
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return ExitTicketModel(
            id=str(data.get('_id', '')),
            student_id=data.get('student_id'),
            carrera_interes=data.get('carrera_interes'),
            claridad=data.get('claridad'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'carrera_interes': self.carrera_interes,
            'claridad': self.claridad,
            'created_at': self.created_at
        }
