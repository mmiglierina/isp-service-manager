# -*- coding: utf-8 -*-
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import unittest
import time

os.environ['WDM_LOCAL'] = '1'


class SearchMissingCodeShowNotFound(unittest.TestCase):
    def setUp(self):
        options = Options()

        if os.getenv('GITHUB_ACTIONS') == 'true':
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
        else:
            options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
            service = Service(ChromeDriverManager().install())

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(30)
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_search_missing_code_show_not_found(self):
        driver = self.driver
        driver.get("https://um-2025-articulos.tiiny.site/")

        driver.find_element(By.ID, "code").click()
        driver.find_element(By.ID, "code").clear()
        driver.find_element(By.ID, "code").send_keys("1111111111112")
        driver.find_element(By.ID, "search").click()

        alert_text = driver.find_element(By.CSS_SELECTOR, ".alert-danger").text
        self.assertEqual("Artículo no encontrado", alert_text)

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to.alert
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()