import os
from flask import request
from statsig_python_core import Statsig, StatsigOptions, StatsigUser

statsig_client = None

def init_statsig():
    global statsig_client

    secret_key = os.getenv("STATSIG_SECRET_KEY", "secret-tu-key-por-defecto")

    options = StatsigOptions()
    options.environment = "development"

    statsig_client = Statsig(secret_key, options)
    statsig_client.initialize().wait()
    print("Statsig client initialized")

def es_administrador_por_ip():
    global statsig_client

    if statsig_client is None:
        return False

    # En desarrollo local request.remote_addr suele ser '127.0.0.1'
    ip_cliente = request.remote_addr

    # Creamos el usuario pasándole su IP correctamente
    user = StatsigUser(user_id="anon_user", ip=ip_cliente)

    # Evaluamos el Feature Gate usando nuestro cliente global ya inicializado
    return statsig_client.check_gate(user, "acceso_admin_por_ip")