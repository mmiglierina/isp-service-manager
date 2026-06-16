# -*- coding: utf-8 -*-
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_test import BaseSeleniumTest

class SearchInvalidUUIDShowError(BaseSeleniumTest):

    def test_search_invalid_uuid_show_error(self):
        driver = self.driver

        # 1. Abrir la página principal (Frontend Flask)
        driver.get(self.frontend_url)

        # 2. Localizar el campo de entrada UUID por su atributo 'name' o clase
        uuid_input = driver.find_element(By.NAME, "uuid")
        uuid_input.click()
        uuid_input.clear()

        # Colocamos un UUID inexistente o erróneo
        uuid_input.send_keys("00000000-0000-0000-0000-000000000000")

        # 3. Localizar y clickear el botón de enviar
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Buscar Estado')]")
        submit_button.click()

        # 4. Esperar que aparezca el mensaje de alerta flash generado por Flask
        elemento_alerta = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert, .alert-danger"))
        )

        alert_text = elemento_alerta.text

        # 5. Verificación: Comprobar el mensaje exacto inyectado en app.py
        self.assertIn("No se encontró ningún trámite con el UUID provisto.", alert_text)


if __name__ == "__main__":
    import unittest

    unittest.main()