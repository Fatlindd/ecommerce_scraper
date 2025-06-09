import csv
import time
import os
import sys
import undetected_chromedriver as uc

from openpyxl import Workbook
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
time.sleep(3)

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

    get_all_categories()
    # check_page_on_pagination()


###################################################################################################
####################### Scrapping Categories Of VisioTechSecurity Website #########################
###################################################################################################

def get_all_categories():
    driver.get("https://www.visiotechsecurity.com/")
    driver.maximize_window()

    # Get Number Of Ancestor Category
    num_of_ancestor = driver.find_elements(By.XPATH, "//aside[@id='cat-aside']/li") # 17

    # Save all Parent and Child Category into file url_of_categories.txt
    with open("Resources/url_of_categories_1.txt", "w") as f:
         for i in range(len(num_of_ancestor)):
            # Rel XPATH for: Ancestor Categories
            products_links = driver.find_elements(By.XPATH, f"//div[@id='cat-div-{i}']/ul/li")
            
            for link in products_links:
                # has_url used for check if Parent Category has or not <ul><li> inside them.
                has_ul = link.find_elements(By.XPATH, "./ul")
                if has_ul:
                    for ul_element in has_ul:
                        # get_all_child_categories_url contains all child category urls.
                        get_all_child_categories_url = ul_element.find_elements(By.XPATH, ".//a")
                        for a_tag in get_all_child_categories_url:
                            # href contains href value of all childs category.
                            href = a_tag.get_attribute('href')
                            f.write(href + "\n")
                else:
                    # If Parent category does not has <ul><li> then give the url of parent category
                    without_ul = link.find_element(By.XPATH, "./a")
                    href = without_ul.get_attribute('href')
                    f.write(href + "\n")

    # some categories have other categories inside them so we need to check twice url_of_categories.txt file
    has_other_category()

    # call function save_product_url() to get url of products into urls saved in url_of_categories.txt file.
    check_page_on_pagination()



###################################################################################################
###################### Check if all categories has another category inside ########################
###################################################################################################
    
def has_other_category():
    with open("Resources/url_of_categories_1.txt", "r") as file:
            lines = file.readlines()

    existing_urls = set(line.strip() for line in lines)
    for line in lines:
        url = line.strip()
        driver.get(url)

        try:
            other_category = driver.find_elements(By.XPATH, "//div[@class='category-view']/div/div/a")
            if len(other_category):
                for category in other_category:
                    new_category = category.get_attribute("href")

                    if new_category not in existing_urls:
                        with open("Resources/url_of_categories_1.txt", "a") as file:
                            file.write(new_category + "\n")
                            existing_urls.add(new_category)

        except NoSuchElementException:
            pass


###################################################################################################
############## Read all categories url and save all products of url inside categories #############
###################################################################################################
   
def check_page_on_pagination():
    # Open file url_of_categories.txt to read row by row url of all categories
    with open("Resources/url_of_categories_1.txt", "r") as file:
        for line in file:
            url = line.strip()
            print("Scrape URL:", url)
            driver.get(url)
            driver.maximize_window()
            time.sleep(3)

            # Get all product URLs on the current page
            get_url_of_products_and_save()

            # Check if there's a next page button
            next_page = driver.find_elements(By.XPATH, "//a[text()='Next']")
            if next_page:
                # Iterate through the pagination
                while True:
                    # Click on the next page button
                    driver.execute_script("arguments[0].click();", next_page[0])
                    
                    # Get all product URLs on the current page
                    get_url_of_products_and_save()

                    # Check if there's a next page button
                    next_page = driver.find_elements(By.XPATH, "//a[text()='Next']")
                    if not next_page:
                        break

    # save detail of products to csv file and excel sheet
    get_details_of_products()
            
  
def get_url_of_products_and_save():
    """ This function check how many cards of product are, and with a for loop we can give the 
        href attribute for product's url  """
    
    # numb_of_cards_link: number of products card in section.
    num_of_cards_link = driver.find_elements(By.XPATH, "//div[@id='vm_right_view']/div[not(@name='pagCounter') and not(@class='loadingGif')]")
    
    with open("Resources/url_of_products_1.txt", "r") as f:
        existing_urls = set(line.strip() for line in f)

    for url_product_index in range(1, len(num_of_cards_link) + 1):
        # h2_element contain url of href attribute in each cards
        h2_element = driver.find_element(By.XPATH, f"(//div[@class='spacer'])[{url_product_index}]/h2/a").get_attribute("href")
        
        if h2_element not in existing_urls:
            with open("Resources/url_of_products_1.txt", "a") as f:
                f.write(h2_element + "\n")
                existing_urls.add(h2_element)


###################################################################################################
#################### Read All Data From Product Url File And Save Into CSV FILE ###################
###################################################################################################
  
def get_details_of_products():
    # Define the field names
    field_names = ['name', 'image_path', 'brand_name', 'descriptions', 'specifications', 'category_ancestor', 'category_parent', 'category_child', 'price']

    # Write to CSV
    with open('Resources/product_details.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()

        # Write to Excel workbook
        wb = Workbook()
        ws = wb.active
        ws.append(field_names)

        # Read URLs from the file
        with open('Resources/url_of_products_1.txt', 'r') as urls:
            for url in urls:
                # Open URL in Chrome browser
                driver.get(url.strip())  # Remove any leading/trailing whitespaces from URL

                # Initialize category_child with a default value
                category_child = 'None'


                # Product name
                try:
                    name_element = driver.find_element(By.XPATH, "//div[@class='productdetails_wrap']//h1")
                    name = name_element.text.strip() if name_element else "N/A"
                except NoSuchElementException:
                    name = "N/A"

                # Description details on a list
                try:
                    description_element = driver.find_elements(By.XPATH, "//div[@id='content_tabs']//div[@class='content active']/ul//li")
                    data_of_description = []
                    for desc_ele in description_element:
                        description = desc_ele.text.strip() if desc_ele else "N/A"

                        if description:
                            data_of_description.append(description)
                except NoSuchElementException:
                    data_of_description = "N/A"

                # Specification details on a list
                try:
                    specification = driver.find_element(By.XPATH, "//div[normalize-space()='Specifications']")
                    driver.execute_script("arguments[0].click();", specification)
                    data_of_specifications = {}
                    numberOfRows = driver.find_elements(By.XPATH, "//div[@id='content_tabs']//table[@class='specs']//tr")
                    for i in range(1, len(numberOfRows) + 1):
                        key = driver.find_element(By.XPATH, f"//div[@id='content_tabs']//table[@class='specs']//tr[{i}]/td/strong").text
                        value = driver.find_element(By.XPATH, f"//div[@id='content_tabs']//table[@class='specs']//tr[{i}]/td[2]").text
                        data_of_specifications[key] = value
                except NoSuchElementException:
                    data_of_specifications = "N/A"

                # Brand name
                try:
                    is_brand = driver.find_element(By.XPATH, "//div[@id='content_tabs']//table[@class='specs']//tr[1]/td[1]")
                    if is_brand.text == "Brand":
                        brand_element = driver.find_element(By.XPATH, "//div[@id='content_tabs']//table[@class='specs']//tr[1]/td[2]")
                        brand_name = brand_element.text.strip()
                    else:
                        brand_name = "N/A"
                except NoSuchElementException:
                    brand_name = "N/A"

                # Image Path Url
                try:
                    image_element = driver.find_element(By.XPATH, "//img[@id='image_product_detail']")
                    image_path = image_element.get_attribute('src').strip() if image_element else "N/A"
                except NoSuchElementException:
                    image_path = "N/A"

                # Ancestor Category Name
                try:
                    ancestor_element = driver.find_element(By.XPATH, "//div[@class='breadcrumbs']/a[3]")
                    category_ancestor = ancestor_element.text.strip() if ancestor_element else "N/A"
                except NoSuchElementException:
                    category_ancestor = "N/A"

                # Parent Category Name
                try:
                    parent_element = driver.find_element(By.XPATH, "//div[@class='breadcrumbs']/a[4]")
                    category_parent = parent_element.text.strip() if parent_element else "N/A"
                except NoSuchElementException:
                    category_parent = "N/A"
                
                # Child Category Name
                try:
                    child_element = driver.find_element(By.XPATH, "//div[@class='breadcrumbs']/a[5]")
                    category_child = child_element.text.strip() if child_element else "N/A"
                except NoSuchElementException:
                    category_child = "N/A"

                # Price Attribute 
                try:
                    price_element = driver.find_element(By.XPATH, "//span[@class='PricesalesPrice']")
                    price = price_element.text.strip() if price_element else "N/A"
                except NoSuchElementException:
                    price_element = "N/A"

                # Write scraped data to CSV
                writer.writerow({
                    'name': name,
                    'image_path': image_path,
                    'brand_name': brand_name,
                    'descriptions': str(data_of_description),
                    'specifications': str(data_of_specifications),
                    'category_ancestor': category_ancestor,
                    'category_parent': category_parent,
                    'category_child': category_child,
                    'price': price
                })

                # Write scraped data to Excel
                ws.append([name, image_path, brand_name, str(data_of_description), str(data_of_specifications), category_ancestor, category_parent, category_child, price])

                # clear the list after writing the data
                data_of_description = []

                # clear the dictionary after writing the data
                data_of_specifications = {}
        
        # Save the Excel workbook
        wb.save('Resources/product_details.xlsx')
