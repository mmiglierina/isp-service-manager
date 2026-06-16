# -*- coding: utf-8 -*-
import os
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Intentamos cargar el archivo .env si existe localmente
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # En GitHub Actions las cargaremos nativamente de otra forma


class BaseSeleniumTest(unittest.TestCase):
    def setUp(self):
        options = Options()

        # 1. Detectamos entorno (GitHub Actions vs Local)
        if os.getenv('GITHUB_ACTIONS') == 'true':
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            service = Service(ChromeDriverManager().install())
        else:
            # Configuración local para Brave
            options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            options.add_argument("--disable-extensions")
            service = Service(ChromeDriverManager().install())

        # 2. Inicialización del Driver
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(15)
        self.verificationErrors = []
        self.accept_next_alert = True

        # 3. Lectura de URLs desde variables de entorno (con fallbacks por si acaso)
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://127.0.0.1:5000')
        self.backend_url = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)