from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent

def get_random_headers():
    ua = UserAgent()
    headers = {"User-Agent": ua.random, "Accept-Language": "en-US, en;q=0.5"}
    return headers

def scrap_data(html):
    data = {
        "lot": "",
        "block": ""
    }
    soup = BeautifulSoup(html, "html.parser")

    # For lot and block
    div_container = soup.find('div', class_='sc-eZkCL elkQpd')
    if div_container:
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
    try:
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.maximize_window()
        driver.set_page_load_timeout(50)
        driver.get("https://propertyinformationportal.nyc.gov/")

        # Click the select button
        select_btn = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-toggle') and contains(@class, 'btn') and contains(@class, 'btn-primary')]"))
        )
        select_btn.click()

        # Click the Address button
        address_btn = WebDriverWait(driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown-item') and text()='Address']"))
        )
        address_btn.click()

        # Input the address
        search_input = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Find address or place']"))
        )
        search_input.send_keys(address)
        search_input.send_keys(Keys.ENTER)

        # Check for alert
        alert = driver.find_elements(By.XPATH, "//div[contains(@class, 'alert-danger')]")
        if alert:
            return {"status": False, "message": alert[0].text}

        # Wait for the page to load and get HTML
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'sc-eZkCL')))
        html = driver.page_source
        data = scrap_data(html)

        return {
            "status": True,
            "data": data
        }

    finally:
        if driver:
            driver.quit()

def nyc_lot_block_scraping(address):
    headers = get_random_headers()

    # Set Chrome options
    options = Options()
    options.headless = True
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument("--no-sandbox")

    data = sysInit(options, address)
    return data

