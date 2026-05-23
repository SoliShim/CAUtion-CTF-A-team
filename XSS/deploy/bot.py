from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import shutil
import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:80")


def visit_ticket(ticket_id):

    options = Options()

    chromium_path = shutil.which("chromium") or shutil.which("chromium-browser")
    chromedriver_path = shutil.which("chromedriver")

    if chromium_path:
        options.binary_location = chromium_path

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    service = Service(chromedriver_path)

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    try:
        driver.get(BASE_URL + "/admin/login")
        time.sleep(1)

        driver.get(BASE_URL + f"/admin/ticket/{ticket_id}")
        time.sleep(5)

    finally:
        driver.quit()
