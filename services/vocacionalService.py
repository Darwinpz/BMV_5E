from models.studentModel import StudentModel
from models.wordResponseModel import WordResponseModel
from models.discResultModel import DiscResultModel
from models.exitTicketModel import ExitTicketModel
from repositories.studentRepository import StudentRepository
from repositories.wordResponseRepository import WordResponseRepository
from repositories.discResultRepository import DiscResultRepository
from repositories.exitTicketRepository import ExitTicketRepository
from data.disc_data import DISC_QUESTIONS
import re

class VocacionalService:
    def __init__(self):
        self.student_repo = StudentRepository()
        self.word_repo = WordResponseRepository()
        self.disc_repo = DiscResultRepository()
        self.ticket_repo = ExitTicketRepository()

    def registrar_estudiante(self, nombre: str, email: str, telefono: str, session_id: str) -> dict:
        nombre = nombre.strip() if nombre else ''
        email = email.strip() if email else ''
        telefono = telefono.strip() if telefono else ''

        if len(nombre) < 3:
            return {'success': False, 'message': 'El nombre debe tener al menos 3 caracteres.'}
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return {'success': False, 'message': 'Ingresa un correo electrónico válido.'}
        if len(telefono) < 7:
            return {'success': False, 'message': 'Ingresa un número de teléfono válido.'}

        existing = self.student_repo.find_by_email(email)
        if existing:
            return {'success': True, 'student_id': existing.id, 'nombre': existing.nombre, 'already_registered': True}

        student = StudentModel(nombre=nombre, email=email, telefono=telefono, session_id=session_id)
        student_id = self.student_repo.create(student)
        return {'success': True, 'student_id': student_id, 'nombre': nombre}

    def agregar_palabra(self, palabra: str, student_id: str) -> dict:
        palabra = palabra.strip() if palabra else ''
        if len(palabra) < 2:
            return {'success': False, 'message': 'La respuesta debe tener al menos 2 caracteres.'}
        if len(palabra) > 25:
            return {'success': False, 'message': 'La respuesta es demasiado larga (máx. 25 caracteres).'}

        count = self.word_repo.count_by_student(student_id)
        if count >= 3:
            return {'success': False, 'message': 'Ya enviaste el máximo de 3 respuestas.'}

        word = WordResponseModel(palabra=palabra, student_id=student_id)
        self.word_repo.create(word)
        new_count = count + 1
        return {'success': True, 'count': new_count, 'remaining': 3 - new_count}

    def get_palabras_frecuencias(self) -> list:
        freqs = self.word_repo.get_word_frequencies()
        return [{'text': word, 'weight': count} for word, count in sorted(freqs.items(), key=lambda x: -x[1])]

    def count_palabras_student(self, student_id: str) -> int:
        return self.word_repo.count_by_student(student_id)

    def get_student_words(self, student_id: str) -> list:
        return [d['palabra'] for d in self.word_repo.find_by_student(student_id)]

    def guardar_disc_result(self, student_id: str, respuestas: dict) -> dict:
        puntajes = {'D': 0, 'I': 0, 'S': 0, 'C': 0}

        for q in DISC_QUESTIONS:
            q_id = str(q['id'])
            letra_elegida = respuestas.get(q_id)
            if letra_elegida:
                for opcion in q['opciones']:
                    if opcion['letra'] == letra_elegida:
                        puntajes[opcion['perfil']] += 1
                        break

        perfil = max(puntajes, key=puntajes.get)

        disc_result = DiscResultModel(
            student_id=student_id,
            respuestas=respuestas,
            puntajes=puntajes,
            perfil=perfil
        )
        self.disc_repo.upsert_by_student_id(student_id, disc_result)
        return {'success': True, 'perfil': perfil, 'puntajes': puntajes}

    def get_disc_result(self, student_id: str):
        return self.disc_repo.find_by_student_id(student_id)

    def get_exit_ticket(self, student_id: str):
        return self.ticket_repo.find_by_student_id(student_id)

    def guardar_exit_ticket(self, student_id: str, carrera_interes: str, claridad: str, comentario: str = '') -> dict:
        ticket = ExitTicketModel(
            student_id=student_id,
            carrera_interes=carrera_interes,
            claridad=claridad,
            comentario=comentario.strip() if comentario else ''
        )
        self.ticket_repo.upsert_by_student_id(student_id, ticket)
        return {'success': True}

    def get_student(self, student_id: str):
        return self.student_repo.find_by_id(student_id)

    def get_student_detail(self, student_id: str) -> dict | None:
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return None
        disc = self.disc_repo.find_by_student_id(student_id)
        ticket = self.ticket_repo.find_by_student_id(student_id)
        words = [w['palabra'] for w in self.word_repo.find_by_student(student_id)]
        return {'student': student, 'disc': disc, 'ticket': ticket, 'words': words}

    def eliminar_estudiante(self, student_id: str) -> dict:
        student = self.student_repo.find_by_id(student_id)
        if not student:
            return {'success': False, 'message': 'Estudiante no encontrado.'}
        self.word_repo.delete_by_student_id(student_id)
        self.disc_repo.delete_by_student_id(student_id)
        self.ticket_repo.delete_by_student_id(student_id)
        self.student_repo.delete_by_id(student_id)
        return {'success': True, 'nombre': student.nombre}

    def get_all_resultados(self) -> list:
        students = self.student_repo.find_all()
        results = []
        for student in students:
            disc = self.disc_repo.find_by_student_id(student.id)
            ticket = self.ticket_repo.find_by_student_id(student.id)
            results.append({'student': student, 'disc': disc, 'ticket': ticket})
        return results

    def get_estadisticas(self) -> dict:
        students = self.student_repo.find_all()
        disc_results = self.disc_repo.find_all()
        tickets = self.ticket_repo.find_all()

        profile_counts = {'D': 0, 'I': 0, 'S': 0, 'C': 0}
        for dr in disc_results:
            if dr.perfil in profile_counts:
                profile_counts[dr.perfil] += 1

        career_counts: dict = {}
        claridad_values = []
        for t in tickets:
            if t.carrera_interes:
                career_counts[t.carrera_interes] = career_counts.get(t.carrera_interes, 0) + 1
            try:
                claridad_values.append(int(t.claridad))
            except (TypeError, ValueError):
                pass

        avg_claridad = round(sum(claridad_values) / len(claridad_values), 1) if claridad_values else 0
        career_counts = dict(sorted(career_counts.items(), key=lambda x: -x[1]))

        return {
            'total_estudiantes': len(students),
            'total_disc': len(disc_results),
            'total_tickets': len(tickets),
            'profile_counts': profile_counts,
            'career_counts': career_counts,
            'avg_claridad': avg_claridad,
            'most_common_profile': max(profile_counts, key=profile_counts.get) if any(profile_counts.values()) else None,
            'most_common_career': next(iter(career_counts), None),
        }
