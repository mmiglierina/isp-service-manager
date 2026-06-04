# services.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000")


def authenticate_admin(usuario: str, password: str) -> tuple:
    """
    Envía las credenciales a FastAPI para autenticar al administrador.
    Devuelve un booleano (si fue exitoso) y el token (o None).
    """
    try:
        url = f"{FASTAPI_BASE_URL}/auth/login"
        login_payload = {"usuario": usuario, "password": password}
        response = requests.post(url, json=login_payload, timeout=5)

        if response.status_code == 200:
            token_data = response.json()
            return True, token_data.get("accessToken")
        return False, None
    except requests.exceptions.RequestException as error:
        print(f"[LOG ERROR] Fallo de red en la autenticación: {error}")
        return False, None

def get_procedure_by_id(procedure_id: str, headers: dict = None) -> dict:
    """
    Recupera un trámite detallado desde FastAPI.
    Si se proveen headers, usa el endpoint protegido de administración para traer todo.
    """
    try:
        if headers and "Authorization" in headers:
            url = f"{FASTAPI_BASE_URL}/admin/tramite/{procedure_id}"
        else:
            url = f"{FASTAPI_BASE_URL}/tramite/{procedure_id}"

        req_headers = headers if headers else {}
        response = requests.get(url, headers=req_headers, timeout=5)

        if response.status_code == 200:
            return response.json()

        print(f"[LOG WARN] Error {response.status_code} al consultar trámite {procedure_id}")
        return None
    except requests.exceptions.RequestException as error:
        print(f"[LOG ERROR] Error de conexión en get_procedure_by_id: {error}")
        return None


def get_all_procedures(status_filter: str = None, headers: dict = None) -> list:
    """
    Recupera el listado de trámites desde el área protegida de FastAPI.
    Llama al endpoint: GET /admin/tramites
    """
    try:
        url = f"{FASTAPI_BASE_URL}/admin/tramites"
        query_params = {}
        if status_filter:
            query_params['estado'] = status_filter

        response = requests.get(url, params=query_params, headers=headers, timeout=5)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            print("[LOG WARN] Token de administración inválido o expirado.")
            return []
        return []
    except requests.exceptions.RequestException as error:
        print(f"[LOG ERROR] Error de conexión en get_all_procedures: {error}")
        return []


def post_new_procedure(endpoint_path: str, form_fields: dict, file_fields: dict) -> tuple:
    """ Abstracción genérica para el envío de solicitudes multipart/form-data. """
    try:
        url = f"{FASTAPI_BASE_URL}{endpoint_path}"
        response = requests.post(url, data=form_fields, files=file_fields, timeout=10)
        return response.status_code, response.json() if response.status_code == 201 else {}
    except requests.exceptions.RequestException as error:
        print(f"[LOG ERROR] Fallo al enviar payload a FastAPI: {error}")
        return 500, {}