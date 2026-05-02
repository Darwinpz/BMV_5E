from datetime import datetime

class DiscResultModel:
    def __init__(self, id=None, student_id=None, respuestas=None, puntajes=None, perfil=None, created_at=None):
        self.id = id
        self.student_id = student_id
        self.respuestas = respuestas or {}
        self.puntajes = puntajes or {'D': 0, 'I': 0, 'S': 0, 'C': 0}
        self.perfil = perfil
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return DiscResultModel(
            id=str(data.get('_id', '')),
            student_id=data.get('student_id'),
            respuestas=data.get('respuestas', {}),
            puntajes=data.get('puntajes', {'D': 0, 'I': 0, 'S': 0, 'C': 0}),
            perfil=data.get('perfil'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'respuestas': self.respuestas,
            'puntajes': self.puntajes,
            'perfil': self.perfil,
            'created_at': self.created_at
        }
