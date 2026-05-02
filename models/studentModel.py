from datetime import datetime

class StudentModel:
    def __init__(self, id=None, nombre=None, email=None, telefono=None, session_id=None, created_at=None):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.session_id = session_id
        self.created_at = created_at or datetime.utcnow()

    @staticmethod
    def from_dict(data):
        return StudentModel(
            id=str(data.get('_id', '')),
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            session_id=data.get('session_id'),
            created_at=data.get('created_at')
        )

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'session_id': self.session_id,
            'created_at': self.created_at
        }

    def __repr__(self):
        return f"<Student {self.nombre}>"
