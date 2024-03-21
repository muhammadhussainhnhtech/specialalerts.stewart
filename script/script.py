"""
https://specialalerts.stewart.com/Search

"""

import time, json, random
from bs4 import BeautifulSoup
# from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

BASE_URL= "https://specialalerts.stewart.com"


def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers


def random_delay():
    time.sleep(random.uniform(1, 3))



def scrap_data(html):
    soup= BeautifulSoup(html, 'html.parser')

    data = {
        "fname": "",
        "lname": "",
        "results_found": "",
        "data": []
    }
    
    main_div= soup.find('div', id='ColumnOne')
    table= main_div.find('table', class_='query-results') if main_div else None
    rows= table.find_all('td', class_='TdNameEven') if table else []
    td = rows[1] if len(rows) >=1 else None
    if td :
        data['results_found']= td.text.strip()

    table= soup.find('table', class_= 'TableResults')
    if table:
        headers_tr = table.find('tr', {'valign': 'bottom'})
        headers_tag = headers_tr.find_all('td') if headers_tr else []
        headers = [header.text.strip() for header in headers_tag]
        all_rows_tr = table.find_all('tr', {'valign': 'top'})
        if all_rows_tr:
            for row_tr in all_rows_tr:
                row_tds= row_tr.find_all('td')
                row_data = [row_td.text.strip() for row_td in row_tds]
                row_object= {header: row for header, row in zip(headers, row_data)}
                data['data'].append(row_object)

    return data


def sysInit(options, name):

    # display = Display(visible=0, size=(800, 600))
    # display.start()
    try:
        print("Starting........")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()

        driver.get("https://specialalerts.stewart.com/Search")
        time.sleep(1)

        first_name_input = driver.find_element(By.ID, "FirstName_1")
        last_name_input = driver.find_element(By.ID, "LastName_1")

        # Input your desired first name and last name
        first_name = name['fname']
        last_name = name['lname']

        # Clear any existing text in the fields (if any)
        first_name_input.clear()
        last_name_input.clear()

        # Input the first name and last name
        first_name_input.send_keys(first_name)
        last_name_input.send_keys(last_name)

        # Find the "Find" button
        find_button = driver.find_element(By.ID, "ButtonFind")
        find_button.click()

        html= driver.page_source
        data= scrap_data(html)
        data['fname']= first_name
        data['lname']= last_name

        print(json.dumps(data, indent=2))

        return data


    finally:
        print("QUIT WEB DRIVER ______________")
        # display.stop()

        # Quit the WebDriver
        if driver:
            driver.quit()


def start_scrapping(name):
    headers = get_random_headers()
    print("\nMy Random Header is : \n", headers)
    print("\n\n")

    # Set Chrome options
    options = Options()
    options.headless = True
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    # options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument("--no-sandbox")
    options.add_argument("chrome://settings/")
    options.add_argument("--lang=en")
    options.add_argument("--disable-translate")

    data= sysInit(options, name)
    return data

