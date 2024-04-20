"""
Scrap with Login
https://sums.stewart.com/Default.aspx

scrap after filtering
https://priorfiles.stewart.com/Search/SearchPriorFiles.aspx
"""

import time, random
from bs4 import BeautifulSoup
# from pyvirtualdisplay import Display
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL= "https://sums.stewart.com/Default.aspx"


def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers


def random_delay():
    time.sleep(random.uniform(1, 3))



def scrap_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Initialize an empty list to store dictionaries
    data = []

    # Find all tables with specific attributes
    all_table = soup.find_all('table', attrs={'width': '100%', 'border': '0', 'cellpadding': '0', 'cellspacing': '0', 'style': 'font-family: Verdana; font-size: x-small'})

    # Iterate over each table
    for table in all_table:
        # Extract data from the first table
        first_table = table.find('table', attrs={'width': '100%', 'border': '0', 'cellpadding': '0', 'style': 'font-family: Verdana; font-size: x-small'})
        headers_td = first_table.find('tr').find_all('td')
        headers = [header.text.strip().replace(" ", "_") for header in headers_td]

        # Extract data from each row in the first table
        all_rows_tr = first_table.find_all('tr')[1:]
        single_data= []
        for row_tr in all_rows_tr:
            all_td = row_tr.find_all('td')
            base_url= "https://priorfiles.stewart.com/Search/"
            row_data = [base_url+td.a['href'] if td.a and 'href' in td.a.attrs else td.text.strip() for td in all_td if td.a or td.text.strip()]
            row_data = {header: data for header, data in zip(headers, row_data)}
            single_data.append(row_data)


            

        # Extract data from the second table
        second_table = table.find('table', attrs={'width': '100%', 'border': '0', 'cellpadding': '0', 'style': 'font-family: Verdana; font-size: x-small; vertical-align:top'})
        agency_tr = second_table.find('tr', {'style': 'vertical-align:top; text-decoration: underline; font-weight: bold'})
        agency = agency_tr.text.strip()
        key, value = [part.strip().replace(' ', '_') for part in agency.split(':')]

        # Append the agency data to the list
        data.append({key: value, "property_records":single_data})

    return data

    


def sysInit(options, params):

    # display = Display(visible=0, size=(800, 600))
    # display.start()
    try:
        print("Starting........")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()

        driver.get("https://sums.stewart.com/Default.aspx")
        # time.sleep(1)

        username_input = driver.find_element(By.ID, "ctl00_loginView_SumsLoginControl_UserName")
        password_input = driver.find_element(By.ID, "ctl00_loginView_SumsLoginControl_Password")

        # Input your desired first name and last name
        username = "Tsahakyan"
        password = "Tiko1979$"

        # Clear any existing text in the fields (if any)
        username_input.clear()
        password_input.clear()

        # Input the first name and last name
        username_input.send_keys(username)
        password_input.send_keys(password)

        # Find the "Find" button
        login_button = driver.find_element(By.ID, "ctl00_loginView_SumsLoginControl_LoginButton")
        login_button.click()

        td_element = driver.find_element(By.ID, "ctl00_loginView_portalMenun0")
        td_element.click()

        td_element = driver.find_element(By.ID, "ctl00_loginView_portalMenun1")
        td_element.click()

        # street_address= "243 west end avenue"
        # city= "Brooklyn"
        # postal_code= "11235"
        street_address= params['street_address']
        city= params['city']
        postal_code= params['postal_code']

        street_input= driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtAddress")
        city_input= driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtCity")
        postalcode_input= driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtPostalCode")

        street_input.clear()
        city_input.clear()
        postalcode_input.clear()

        street_input.send_keys(street_address)
        city_input.send_keys(city)
        postalcode_input.send_keys(postal_code)

        search_button= driver.find_element_by_id("ctl00_ContentPlaceHolder1_btnSearch")
        search_button.click()

        # time.sleep(2)
        soup= BeautifulSoup(driver.page_source, 'html.parser')
        message_span= soup.find('span', {'id': 'ctl00_ContentPlaceHolder1_informationBox_lblTextMessage1'})
        message= message_span.text.strip() if message_span else ""
        if message == "No results found.":
            return {
                "status": False,
                "all_scraped_results": [],
                "message": "No results found from your params",
            }

        all_data= []

        while True:
            try:
                for i in range(1, 6):
                    btn_id = f"ctl00_ContentPlaceHolder1_grdSearchResults_ctl09_lnkPageNumberPosition{i}"
                    btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, btn_id)))
                    btn.click()
                    time.sleep(2)
                    html = driver.page_source
                    data = scrap_data(html)
                    all_data.extend(data)

                next_five_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_grdSearchResults_ctl09_lnkNextFivePages")))
                if not next_five_button:
                    break  # Break the loop if the "Next 5" button is not displayed
                
                next_five_button.click ()
                time.sleep(2)

            except Exception as e:
                break
        
        return {"status": True, "count": len(all_data), "all_scraped_results": all_data}



    finally:
        print("QUIT WEB DRIVER ______________")
        # display.stop()

        # Quit the WebDriver
        if driver:
            driver.quit()


def start_priorfile_scrapping(params):
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

    data= sysInit(options, params)
    return data