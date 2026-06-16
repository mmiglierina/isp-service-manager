# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_test import BaseSeleniumTest

class SearchValidUUIDNavigatesToStatus(BaseSeleniumTest):

    def test_search_valid_uuid_navigates_to_status(self):
        driver = self.driver

        # 1. Abrir la página principal (Frontend Flask)
        driver.get(self.frontend_url)

        # 2. Rellenar el formulario con un UUID válido existente en el backend
        valid_uuid = "2319c867-1c75-4213-8719-224ad01a85f0"

        uuid_input = driver.find_element(By.NAME, "uuid")
        uuid_input.click()
        uuid_input.clear()
        uuid_input.send_keys(valid_uuid)

        # 3. Enviar el formulario
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar Estado')]")
        submit_button.click()

        # 4. Esperar el cambio de vista y comprobar que no estamos en el index
        # El endpoint final según app.py renderiza la plantilla 'cliente_estado.html'
        # Podés chequear si la URL cambió o si se visualiza un componente específico de esa página.
        WebDriverWait(driver, 10).until(
            EC.url_contains("/buscar_tramite")
        )

        # 5. Verificación opcional del DOM interno de cliente_estado.html
        # Comprobar que NO salte la alerta de error en la pantalla
        alertas = driver.find_elements(By.CSS_SELECTOR, ".alert-danger")
        self.assertEqual(len(alertas), 0, "Se encontró una alerta de error y se esperaba ingresar al detalle.")


if __name__ == "__main__":
    import unittest

    unittest.main()