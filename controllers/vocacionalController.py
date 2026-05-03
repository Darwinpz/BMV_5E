import uuid
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, g
from services.vocacionalService import VocacionalService
from data.disc_data import DISC_QUESTIONS, DISC_PROFILES, CARRERAS_TECNICAS
from functools import wraps

vocacional_bp = Blueprint('vocacional', __name__, url_prefix='/vocacional')


def get_service() -> VocacionalService:
    if 'vocacional_service' not in g:
        g.vocacional_service = VocacionalService()
    return g.vocacional_service


def _mark_complete(module: str):
    modules = session.get('completed_modules', [])
    if module not in modules:
        modules.append(module)
        session['completed_modules'] = modules
        session.modified = True


def _require_student():
    student_id = session.get('student_id')
    if not student_id:
        flash('Por favor regístrate para continuar.', 'warning')
        return None
    return student_id


# ── Landing ──────────────────────────────────────────────────────────────────

@vocacional_bp.route('/', methods=['GET'])
def index():
    return render_template('vocacional/index.html')


# ── Registro ─────────────────────────────────────────────────────────────────

@vocacional_bp.route('/registro', methods=['GET'])
def registro():
    if session.get('student_id'):
        return redirect(url_for('vocacional.enganchar'))
    return render_template('vocacional/registro.html')


@vocacional_bp.route('/registro', methods=['POST'])
def registro_post():
    if session.get('student_id'):
        return redirect(url_for('vocacional.enganchar'))

    session_id = str(uuid.uuid4())
    result = get_service().registrar_estudiante(
        nombre=request.form.get('nombre', ''),
        email=request.form.get('email', ''),
        telefono=request.form.get('telefono', ''),
        session_id=session_id
    )

    if result['success']:
        session['student_id'] = result['student_id']
        session['student_name'] = result['nombre']
        if result.get('already_registered'):
            flash(f'Ya estás registrado, {result["nombre"]}. Continuamos donde te quedaste.', 'info')
        else:
            session['completed_modules'] = []
        return redirect(url_for('vocacional.enganchar'))

    flash(result['message'], 'danger')
    return redirect(url_for('vocacional.registro'))


# ── Módulo 1: Enganchar ───────────────────────────────────────────────────────

@vocacional_bp.route('/enganchar', methods=['GET'])
def enganchar():
    student_id = _require_student()
    if not student_id:
        return redirect(url_for('vocacional.registro'))

    svc = get_service()
    word_count = svc.count_palabras_student(student_id)
    my_words = svc.get_student_words(student_id)
    return render_template('vocacional/enganchar.html', word_count=word_count, my_words=my_words)


@vocacional_bp.route('/enganchar/palabra', methods=['POST'])
def enganchar_palabra():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'message': 'Sesión no encontrada.'}), 401

    data = request.get_json(silent=True) or {}
    palabra = data.get('palabra', '').strip()

    result = get_service().agregar_palabra(palabra, student_id)
    if result.get('success'):
        _mark_complete('enganchar')
    return jsonify(result)


@vocacional_bp.route('/api/palabras', methods=['GET'])
def api_palabras():
    words = get_service().get_palabras_frecuencias()
    return jsonify(words)


# ── Módulo 2: Explorar (Test DISC) ────────────────────────────────────────────

@vocacional_bp.route('/explorar', methods=['GET'])
def explorar():
    student_id = _require_student()
    if not student_id:
        return redirect(url_for('vocacional.registro'))
    svc = get_service()
    if svc.count_palabras_student(student_id) == 0:
        flash('Primero completa el Módulo 1: envía al menos una respuesta.', 'warning')
        return redirect(url_for('vocacional.enganchar'))
    if svc.get_disc_result(student_id):
        return redirect(url_for('vocacional.explicar'))
    return render_template('vocacional/explorar.html', questions=DISC_QUESTIONS)


@vocacional_bp.route('/explorar/guardar', methods=['POST'])
def explorar_guardar():
    student_id = session.get('student_id')
    if not student_id:
        return jsonify({'success': False, 'message': 'Sesión no encontrada.'}), 401

    data = request.get_json(silent=True) or {}
    respuestas = data.get('respuestas', {})

    result = get_service().guardar_disc_result(student_id, respuestas)
    if result.get('success'):
        session['disc_perfil'] = result['perfil']
        session['disc_puntajes'] = result['puntajes']
        session.modified = True
        _mark_complete('explorar')
    return jsonify(result)


# ── Módulo 3: Explicar ────────────────────────────────────────────────────────

@vocacional_bp.route('/explicar', methods=['GET'])
def explicar():
    student_id = _require_student()
    if not student_id:
        return redirect(url_for('vocacional.registro'))

    svc = get_service()
    disc_result = svc.get_disc_result(student_id)

    if not disc_result:
        if svc.count_palabras_student(student_id) == 0:
            flash('Primero completa el Módulo 1.', 'warning')
            return redirect(url_for('vocacional.enganchar'))
        flash('Primero completa el Test DISC en el Módulo 2.', 'warning')
        return redirect(url_for('vocacional.explorar'))

    _mark_complete('explicar')
    return render_template(
        'vocacional/explicar.html',
        perfil=disc_result.perfil,
        puntajes=disc_result.puntajes,
        profiles=DISC_PROFILES
    )


# ── Módulo 4: Elaborar ────────────────────────────────────────────────────────

@vocacional_bp.route('/elaborar', methods=['GET'])
def elaborar():
    student_id = _require_student()
    if not student_id:
        return redirect(url_for('vocacional.registro'))

    svc = get_service()
    disc_result = svc.get_disc_result(student_id)

    if not disc_result:
        if svc.count_palabras_student(student_id) == 0:
            flash('Primero completa el Módulo 1.', 'warning')
            return redirect(url_for('vocacional.enganchar'))
        flash('Primero completa el Test DISC en el Módulo 2.', 'warning')
        return redirect(url_for('vocacional.explorar'))

    if 'explicar' not in session.get('completed_modules', []):
        flash('Primero revisa tu perfil DISC en el Módulo 3.', 'warning')
        return redirect(url_for('vocacional.explicar'))

    _mark_complete('elaborar')
    perfil = disc_result.perfil
    return render_template('vocacional/elaborar.html', perfil=perfil, perfil_data=DISC_PROFILES.get(perfil))


# ── Módulo 5: Evaluar ─────────────────────────────────────────────────────────

@vocacional_bp.route('/evaluar', methods=['GET'])
def evaluar():
    student_id = _require_student()
    if not student_id:
        return redirect(url_for('vocacional.registro'))

    svc = get_service()
    disc_result = svc.get_disc_result(student_id)

    if not disc_result:
        if svc.count_palabras_student(student_id) == 0:
            flash('Primero completa el Módulo 1.', 'warning')
            return redirect(url_for('vocacional.enganchar'))
        flash('Primero completa el Test DISC en el Módulo 2.', 'warning')
        return redirect(url_for('vocacional.explorar'))

    if 'elaborar' not in session.get('completed_modules', []):
        flash('Primero explora las opciones de carrera en el Módulo 4.', 'warning')
        return redirect(url_for('vocacional.elaborar'))

    perfil = disc_result.perfil
    existing_ticket = svc.get_exit_ticket(student_id)
    return render_template('vocacional/evaluar.html', carreras=CARRERAS_TECNICAS, perfil=perfil, existing_ticket=existing_ticket)


@vocacional_bp.route('/evaluar/guardar', methods=['POST'])
def evaluar_guardar():
    student_id = session.get('student_id')
    if not student_id:
        flash('Sesión no encontrada.', 'danger')
        return redirect(url_for('vocacional.registro'))

    carrera_interes = request.form.get('carrera_interes', '')
    claridad = request.form.get('claridad', '')
    comentario = request.form.get('comentario', '')

    get_service().guardar_exit_ticket(student_id, carrera_interes, claridad, comentario)
    _mark_complete('evaluar')

    return redirect(url_for('vocacional.completado'))


# ── Completado ────────────────────────────────────────────────────────────────

@vocacional_bp.route('/completado', methods=['GET'])
def completado():
    nombre = session.get('student_name', 'Estudiante')
    perfil = session.get('disc_perfil')
    perfil_data = DISC_PROFILES.get(perfil) if perfil else None
    return render_template('vocacional/completado.html', nombre=nombre, perfil_data=perfil_data)


# ── Nube Display (modo proyector) ─────────────────────────────────────────────

@vocacional_bp.route('/nube-display', methods=['GET'])
def nube_display():
    return render_template('vocacional/nube_display.html')


# ── Cerrar sesión del estudiante ──────────────────────────────────────────────

@vocacional_bp.route('/salir', methods=['POST'])
def salir():
    for key in ('student_id', 'student_name', 'completed_modules', 'disc_perfil', 'disc_puntajes'):
        session.pop(key, None)
    flash('Sesión cerrada. ¡Hasta pronto!', 'info')
    return redirect(url_for('vocacional.index'))


# ── Admin: resultados ─────────────────────────────────────────────────────────

def _require_admin():
    if not session.get('user_id'):
        flash('Debes iniciar sesión como administrador.', 'warning')
        return False
    return True


@vocacional_bp.route('/admin/resultados', methods=['GET'])
def admin_resultados():
    if not _require_admin():
        return redirect(url_for('users.login'))

    svc = get_service()
    resultados = svc.get_all_resultados()
    estadisticas = svc.get_estadisticas()

    filtro_perfil = request.args.get('perfil', 'TODOS')
    if filtro_perfil != 'TODOS':
        resultados = [r for r in resultados if r['disc'] and r['disc'].perfil == filtro_perfil]

    return render_template(
        'vocacional/admin_resultados.html',
        resultados=resultados,
        estadisticas=estadisticas,
        profiles=DISC_PROFILES,
        filtro_perfil=filtro_perfil
    )


@vocacional_bp.route('/admin/estudiante/<student_id>', methods=['GET'])
def admin_detalle(student_id):
    if not _require_admin():
        return jsonify({'error': 'No autorizado'}), 401
    detail = get_service().get_student_detail(student_id)
    if not detail:
        return jsonify({'error': 'No encontrado'}), 404
    s = detail['student']
    d = detail['disc']
    t = detail['ticket']
    return jsonify({
        'nombre': s.nombre,
        'email': s.email,
        'telefono': s.telefono,
        'created_at': s.created_at.strftime('%d/%m/%Y %H:%M') if s.created_at else '—',
        'words': detail['words'],
        'disc': {
            'perfil': d.perfil,
            'puntajes': d.puntajes,
        } if d else None,
        'ticket': {
            'carrera_interes': t.carrera_interes,
            'claridad': t.claridad,
            'comentario': t.comentario or '',
        } if t else None,
    })


@vocacional_bp.route('/admin/estudiante/<student_id>/eliminar', methods=['POST'])
def admin_eliminar(student_id):
    if not _require_admin():
        return jsonify({'error': 'No autorizado'}), 401
    result = get_service().eliminar_estudiante(student_id)
    if result['success']:
        flash(f'Registro de {result["nombre"]} eliminado correctamente.', 'success')
    else:
        flash(result['message'], 'danger')
    return redirect(url_for('vocacional.admin_resultados'))


@vocacional_bp.route('/admin/reporte', methods=['GET'])
def admin_reporte():
    if not _require_admin():
        return redirect(url_for('users.login'))
    svc = get_service()
    resultados = svc.get_all_resultados()
    estadisticas = svc.get_estadisticas()
    from datetime import datetime
    return render_template(
        'vocacional/admin_reporte.html',
        resultados=resultados,
        estadisticas=estadisticas,
        profiles=DISC_PROFILES,
        fecha=datetime.now().strftime('%d/%m/%Y %H:%M'),
    )
