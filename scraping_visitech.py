import csv
import time
import os
import sys
import undetected_chromedriver as uc

from openpyxl import Workbook
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


options = Options()
options.headless = False  # Set to True if you want headless mode

# This line assumes geckodriver is in your PATH
driver = webdriver.Firefox(options=options)


def login():
    driver.get("https://www.visiotechsecurity.com/en/login")
    driver.maximize_window()


    # Fill in the username and password fields
    username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
    username_field.send_keys("VT8237JZJ")

    password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "password")))
    password_field.send_keys("Brother2020?")

    # Locate and click the login button
    login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='button-login btn-4']")))
    login_button.click()

    time.sleep(500000)

login()