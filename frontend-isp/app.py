# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 1. IMPORTACIONES DE CAPAS EXTERNAS: Filtros y Servicios
from filters import format_iso_date
from services import (
    get_procedure_by_id,
    get_all_procedures,
    post_new_procedure,
    authenticate_admin,
    update_procedure_status,
    FASTAPI_BASE_URL
)

# 2. Importamos flags
from statsig_service import init_statsig, es_administrador_por_ip
init_statsig()

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_fallback_insecure_key")

# Registramos el filtro en Jinja2 para el manejo de fechas
app.jinja_env.filters['format_iso_date'] = format_iso_date

# Almacenamiento seguro en sesión simulada del token JWT obtenido en auth.py
SESSION_TOKEN = None

# ====================================================================
# Rutas del Lado del Cliente (Frontend Público)
# ====================================================================
@app.route('/')
def index():
    # Evaluamos con Statsig si la IP califica como admin
    es_admin = es_administrador_por_ip()

    return render_template('cliente_inicio.html', es_admin=es_admin)

@app.route('/alta', methods=['GET', 'POST'])
def request_service_activation():
    if request.method == 'POST':
        form_payload = {
            "nombre": request.form.get('nombre'),
            "apellido": request.form.get('apellido'),
            "dni": request.form.get('dni'),
            "email": request.form.get('email')
        }
        id_file = request.files.get('adjuntoDni')
        tax_file = request.files.get('adjuntoImpuesto')

        files_payload = {
            "adjuntoDni": (secure_filename(id_file.filename), id_file.stream, id_file.mimetype) if id_file else None,
            "adjuntoImpuesto": (secure_filename(tax_file.filename), tax_file.stream,
                                tax_file.mimetype) if tax_file else None
        }

        status_code, response_data = post_new_procedure("/tramite/alta", form_payload, files_payload)
        if status_code == 201:
            generated_uuid = response_data.get("uuid")
            # Redirigimos a la pantalla de éxito pasando los datos dinámicos
            return render_template('cliente_exito.html', uuid=generated_uuid, tipo="ALTA")
        else:
            flash("No se pudo procesar la solicitud de alta. Verifique si ya posee un trámite activo.", "danger")
            return redirect(url_for('index'))

    return render_template('cliente_alta.html')

@app.route('/baja', methods=['GET', 'POST'])
def request_service_deactivation():
    if request.method == 'POST':
        form_payload = {"dni": request.form.get('dni')}
        id_file = request.files.get('adjuntoDni')
        invoice_file = request.files.get('adjuntoFactura')

        files_payload = {
            "adjuntoDni": (secure_filename(id_file.filename), id_file.stream, id_file.mimetype) if id_file else None,
            "adjuntoFactura": (secure_filename(invoice_file.filename), invoice_file.stream,
                               invoice_file.mimetype) if invoice_file else None
        }

        status_code, response_data = post_new_procedure("/tramite/baja", form_payload, files_payload)
        if status_code == 201:
            generated_uuid = response_data.get("uuid")
            # Redirigimos a la pantalla de éxito pasando los datos dinámicos
            return render_template('cliente_exito.html', uuid=generated_uuid, tipo="BAJA")
        else:
            flash(
                "Error al registrar la baja. Asegúrese de contar con un servicio de Alta completado y sin trámites en curso.",
                "danger")
            return redirect(url_for('index'))

    return render_template('cliente_baja.html')


@app.route('/buscar_tramite', methods=['POST'])
def track_procedure_status():
    target_uuid = request.form.get('uuid', '').strip()

    # Consumimos de forma pública sin inyectar headers administrativos
    record = get_procedure_by_id(target_uuid)

    if not record:
        flash("No se encontró ningún trámite con el UUID provisto.", "danger")
        return redirect(url_for('index'))

    # Mapea los campos de clients.py: uuid, tipo, estado, observaciones
    return render_template('cliente_estado.html', procedure=record)

# ====================================================================
# Rutas de la Interfaz Administrativa (Back-Office Autenticado)
# ====================================================================
@app.route('/hidden-admin-portal', methods=['GET', 'POST'])
def admin_authenticate():
    """
    Punto de entrada único y oculto para el personal administrativo.
    """
    global SESSION_TOKEN
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        password = request.form.get('password')

        # Consumimos el servicio de autenticación aislado
        success, token = authenticate_admin(usuario, password)

        if success:
            SESSION_TOKEN = token
            flash("Sesión iniciada correctamente en el sistema central.", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Credenciales incorrectas de administración o error de conexión.", "danger")

    return render_template('admin_login.html')

@app.route('/admin/panel')
def admin_dashboard():
    global SESSION_TOKEN
    if not SESSION_TOKEN:
        return redirect(url_for('index'))

    selected_filter = request.args.get('estado')
    headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}

    # 1. Obtenemos el dataset crudo desde FastAPI
    dataset = get_all_procedures(status_filter=selected_filter, headers=headers)

    # 2. Ordenamos la lista en memoria asegurando que los más viejos queden arriba.
    if dataset:
        dataset.sort(key=lambda x: x.get('fechaCreacion', ''))

    return render_template('admin_panel.html', dataset=dataset, current_filter=selected_filter)

@app.route('/admin/tramite/<procedure_id>', methods=['GET', 'POST'])
def admin_manage_procedure(procedure_id):
    global SESSION_TOKEN
    if not SESSION_TOKEN:
        return redirect(url_for('index'))

    headers = {"Authorization": f"Bearer {SESSION_TOKEN}"}

    # GET: Consumimos el detalle completo desde el servicio externo
    record = get_procedure_by_id(procedure_id, headers=headers)
    if not record:
        flash("El trámite solicitado no existe en el sistema.", "danger")
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        new_status = request.form.get('estado')
        new_observations = request.form.get('observaciones')

        status_code, response_data = update_procedure_status(
            procedure_id=procedure_id,
            estado=new_status,
            observaciones=new_observations,
            headers=headers
        )

        if status_code == 200:
            flash("Trámite actualizado con éxito en la base de datos.", "success")
        elif status_code == 400:
            # si es rechazado exige observaciones
            error_detail = response_data.get('detail', 'Error de validación.')
            flash(f"Error: {error_detail}", "danger")
            return render_template('admin_detalle.html', procedure=record)
        else:
            flash("Error al guardar la actualización del trámite en el backend.", "danger")

        return redirect(url_for('admin_dashboard'))

    return render_template('admin_detalle.html', procedure=record)

if __name__ == '__main__':
    is_debug = os.getenv("FLASK_DEBUG", "False").lower() in ('true', '1', 't')
    app.run(debug=is_debug, port=5000)