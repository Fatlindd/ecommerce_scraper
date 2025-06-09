# VisioTechSecurity-ScrappingWebsite

🌏 Website for scrapping: https://www.visiotechsecurity.com/en

Details of project:
  1. **main.py** file is file that we need to execute.
  2. In file **scrapping_visiotechSecurity.py** are methods:
     - login(), to login in website with credentials
     - get_all_categories(), get all categories from website(category_ancestor, category_parent, category_child) and save all of these categories into file Resources/url_of_categories.txt.
     - has_other_category(), read file Resources/url_of_categories.txt and check if url of category has another category inside them.
     - check_page_on_pagination(), read file Resources/url_of_categories.txt and check for page in pagination, to jump into it.
     - get_url_of_products_and_save(), check how many cards of products exists and then loop into that number to get the href of product in card and save it into file Resources/url_of_products.txt.
     - get_details_of_products(), this method get all detail of products by navigating into urls saved on Resources/url_of_products.txt.
  3. **Resources/**, folder to save files for urls of category, products, .csv and .xlsx(Excel). 
