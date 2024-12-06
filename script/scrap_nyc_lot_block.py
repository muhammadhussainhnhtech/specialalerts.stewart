"""

https://propertyinformationportal.nyc.gov/

"""
import time
from bs4 import BeautifulSoup
# from pyvirtualdisplay import Display
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


BASE_URL= "https://propertyinformationportal.nyc.gov/"


def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers


def scrap_data(html):
    data= {
        "lot": "",
        "block": ""
    }
    soup= BeautifulSoup(html, "html.parser")
    
    # For lot and block
    div_container = soup.find('div', class_='sc-eZkCL elkQpd')
    if div_container:
        # Find all p tags within the div container
        p_tags = div_container.find_all('p', class_='sc-fvtFIe gWOpDD')
        
        for p in p_tags:
            strong_tag = p.find('strong')
            if strong_tag:
                label = strong_tag.text.strip()
                value = strong_tag.next_sibling.strip()
                if label == 'Block:':
                    data['block'] = value
                elif label == 'Lot:':
                    data['lot'] = value

    return data
    








def sysInit(options, address):

    # display = Display(visible=0, size=(800, 600))
    # display.start()
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(50)
        driver.implicitly_wait(20)
        driver.get("https://propertyinformationportal.nyc.gov/")
        # time.sleep(1)

        try:
            # Wait for the "Select" button to be clickable and click it
            select_btn = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(@class, 'btn') and contains(@class, 'btn-primary')]"))
            )
            select_btn.click()

            # Wait for the dropdown items to be present
            driver.implicitly_wait(20)
            
            # Wait for the "Address" button to be clickable and click it
            address_btn = WebDriverWait(driver, 50).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-item') and text()='Address']"))
            )
            address_btn.click()

            # Wait for the input field to be present
            driver.implicitly_wait(20)
            
            # Wait for the input field to be present
            search_input = WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Find address or place']"))
            )
            search_input.send_keys(address)
            search_input.send_keys(Keys.ENTER)
            

            try:
                driver.implicitly_wait(20)
                # Check for the presence of the alert
                alert = driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger') and contains(@class, 'alert') and text()='Address not found within the NYC limits']")
                alert_text = alert.text
    
                time.sleep(20)
                return {"status": False, "message": alert_text}
            except:
                # Alert not found, continue
                pass
            
        except Exception as e:
            return {
                "status": False, 
                "message": "Error while finding or clicking the button",
                "exception": e
                }
        
        time.sleep(2)
        html= driver.page_source
        data= scrap_data(html)

        return {
            "status": True,
            "data": data
        }


    finally:
        # display.stop()
        if driver:
            driver.quit()


def start_nyc_lot_block(address):
    headers = get_random_headers()

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
    # options.add_argument('--timeout=500') # for loading page

    data= sysInit(options, address)
    return data
