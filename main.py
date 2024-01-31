import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import random

class AutoInitialSendout:

    def __init__(self):
        try:
            self.service = ChromeService(executable_path=ChromeDriverManager().install())
            self.chrome_options = Options()
            self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            self.auto_sendout_driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.auto_sendout_driver.implicitly_wait(10)
            self.login_to_trieste()
            self.wait = WebDriverWait(self.auto_sendout_driver, 15)
        except Exception as error_message:
            print(f"An error occurred during Selenium initialization: {error_message}")

    def login_to_trieste(self):
        try:
            print("Logging in to Trieste...")
            self.auto_sendout_driver.get("http://trieste.io")
            trieste_username = self.auto_sendout_driver.find_element(By.ID, "user_email")
            trieste_password = self.auto_sendout_driver.find_element(By.ID, "user_password")
            login_submit_button = self.auto_sendout_driver.find_element(By.NAME, "commit")

            trieste_username.send_keys(os.environ.get('TRIESTE_USERNAME'))
            trieste_password.send_keys(os.environ.get("TRIESTE_PASSWORD"))
            login_submit_button.click()

        except Exception as error_message:
            print(f"An error occurred during login: {error_message}")

        time.sleep(2)
        if self.auto_sendout_driver.current_url == "http://trieste.io/companies/dashboard/14": print("Login successful..")

    def auto_initial_email(self, lead_url, email_account):
        sleep_time = random.randint(120, 241)
        self.auto_sendout_driver.get(lead_url)
        lead_email_for_sending = ''

        try:
            with open('email_addresses.json', "r", encoding="UTF-8") as email_addresses_json:
                email_addresses_initial_template = json.load(email_addresses_json)
        except Exception as error_message:
            print(f"email_addresses.json file error occurred: {error_message}")

        contact_form_textbox = self.auto_sendout_driver.find_element(By.NAME, 'site_link[contact_url]')
        lead_status_dropdown = Select(self.auto_sendout_driver.find_element(By.NAME, 'site_link[status_event]'))
        lead_emails = self.auto_sendout_driver.find_elements(By.XPATH, '//*[@id="emailTable"]/tbody/tr[1]/td[2]/label')
        linkdev_email_address_dropdown = Select(self.auto_sendout_driver.find_element(By.NAME, 'email[email_account_id]'))
        email_subject_textbox = self.auto_sendout_driver.find_element(By.XPATH, '//*[@id="email_subject"]')
        send_button = self.auto_sendout_driver.find_element(By.XPATH, '//*[@id="send_email_submit"]')
        site_link_page_soup = self.auto_sendout_driver.page_source
        first_name_text_boxes = self.auto_sendout_driver.find_elements(By.CLASS_NAME, 'contact_first_name')
        update_button = self.auto_sendout_driver.find_element(By.XPATH, '//*[@id="site_link_form"]/input[1]')

        if contact_form_textbox.get_attribute('value') != '' or lead_status_dropdown.first_selected_option.text != "New": return

        lead_type_dropdown = Select(self.wait.until(EC.visibility_of_element_located((By.NAME, 'site_link[link_type_event]'))))

        if len(lead_emails) > 1:
            for email in lead_emails:
                if site_link_page_soup.count(email.text) > 2:
                    lead_email_for_sending = email.text
                    break
        elif len(lead_emails) < 1:
            lead_type_dropdown.select_by_visible_text("Free")
            update_button.click()
            time.sleep(1)
            return
        else:
            lead_email_for_sending = lead_emails[0].text

        lead_type_dropdown.select_by_visible_text("Guest Post Paid")


        linkdev_email_address_dropdown.select_by_visible_text(email_account)
        time.sleep(1)

        email_template_dropdown = Select(self.auto_sendout_driver.find_element(By.XPATH, f'//*[@id="email_template_id_{email_addresses_initial_template[email_account][0]}"]'))

        email_template_dropdown.select_by_visible_text(email_addresses_initial_template[email_account][1])

        lead_first_name = first_name_text_boxes[0].get_attribute('value')

        while True:
            if email_subject_textbox.get_attribute('value') != '': break
            email_subject_textbox = self.auto_sendout_driver.find_element(By.XPATH, '//*[@id="email_subject"]')
            time.sleep(1)

        if lead_first_name != '' and len(email_addresses_initial_template[email_account]) == 3:
            customized_subject = email_addresses_initial_template[email_account][2]
            email_subject_textbox.clear()
            email_subject_textbox.send_keys(customized_subject.replace("<<name>>", lead_first_name))

        lead_email_tickbox_for_sending = self.auto_sendout_driver.find_elements(By.XPATH, '/html/body/div[1]/div[2]/div/div/table/tbody/tr/td[1]/div/div[2]/div[5]/ul/li[2]/form/table/tbody/tr[1]/td[2]/label')
        for box in lead_email_tickbox_for_sending:

            if box.text != lead_email_for_sending:
                box.click()

        send_button.click()
        print(f"{lead_url} send button clicked")
        time.sleep(sleep_time)


if __name__ == "__main__":

    site_links = []

    user_keywords_input = input("Enter site links: ")

    while user_keywords_input != '':
        site_links.append(user_keywords_input)
        user_keywords_input = input()

    try:
        with open('email_addresses.json', "r", encoding="UTF-8") as email_addresses_json:
            email_addresses_initial_template = json.load(email_addresses_json)
    except FileNotFoundError:
        print("email_addresses.json file not found")

    email_persona_list = []

    auto_sendout = AutoInitialSendout()

    for url in site_links:

        if len(email_persona_list) < 1: email_persona_list = list(email_addresses_initial_template.keys())
        email_used = random.choice(email_persona_list)

        email_persona_list.remove(email_used)
        auto_sendout.auto_initial_email(lead_url=url, email_account=email_used)


    input("Continue?")

