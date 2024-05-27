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
    
    # Main Div
    building_information = {}

    main_div= soup.find('div', {"class": "sc-dtInlm kAECJC"})
    card_divs= main_div.find_all("div", {"class": "sc-bbSZdi bgXkNZ card"}) if main_div else []
    if card_divs:
      for card_div in card_divs:
        heading_divs= card_div.find_all("div", {"class": "sc-fBWQRz cMuqSl"}) if card_div else None
        if heading_divs:
          for heading_div in heading_divs:
            p_tag= heading_div.find("p", {"class": "sc-hknOHE cPNIiJ"})
            if p_tag:
                heading_text= p_tag.text.strip()

                # For Table of Sales and Assessed Value History
                if heading_text == "Assessed Value History" or heading_text == "Sales":
                    table_div= card_div.find("div", {"class": "sc-gFAWRd evnkkT table-responsive"})
                    table = table_div.find('table', {'class': 'mt-2 table table-sm table-bordered'})
                    # Extract headers
                    headers = []
                    for th in table.find('thead').find_all('th'):
                        headers.append(th.get_text(strip=True).replace("/", "").replace(" ", "_").lower())
                    
                    # Sales has link
                    if heading_text == "Sales":
                        headers.append("ACRIS_Doc_ID_link")   # new header ACRIS_Doc_ID_link

                    # Extract rows
                    rows = []
                    acris_doc_id_link= None
                    for tr in table.find('tbody').find_all('tr'):
                        cells = tr.find_all('td')
                        row= []
                        for cell in cells:
                            cell_text = cell.get_text(strip=True)
                            # Sales has link   for new header ACRIS_Doc_ID_link
                            a_tag= cell.find("a", href=True)
                            if a_tag:
                                acris_doc_id_link= a_tag['href']

                            row.append(cell_text)
                        # row = [cell.get_text(strip=True) for cell in cells]
                        
                        # Sales has link for new header ACRIS_Doc_ID_link
                        if acris_doc_id_link:
                            row.append(acris_doc_id_link)
                        rows.append(row)

                    df = pd.DataFrame(rows, columns=headers)
                    # Convert to dict
                    sales = df.to_dict(orient='records')

                    if heading_text == "Sales":
                        data['sales']= sales[:3]
                    if heading_text == "Assessed Value History":
                        data['assessed_value_history']= sales[:3]
                    
                
                if heading_text == "Building Information":
                    all_block_divs= card_div.find_all("div", {"class": "sc-kdBSHD eFDPU"})
                    if all_block_divs:
                        for block_div in all_block_divs:
                            field_p_tag= block_div.find("p", {"class": "sc-cfxfcM YNUrQ"})
                            value_p_tag= block_div.find("p", {"class": "sc-hRJfrW eAqXwF"})
                            if field_p_tag and value_p_tag:
                                if heading_text == "Building Information":
                                    building_information[field_p_tag.text.strip().replace(" ", "_").replace("/", "").lower()]= value_p_tag.text.strip().replace(" ", "_")


    data['building_information']= building_information

    return data
    



def scrap_account_history_summary(html):
    soup= BeautifulSoup(html, "html.parser")
    table = soup.find("table", {'id': 'Account History Summary'})
    # Extract headers
    headers = [header.text.strip().replace("/", "").replace(" ", "_") for header in table.find_all('td', {'class': 'DataletTopHeading'})]

    # Extract data
    data = []
    for row in table.find_all('tr')[1:]:
        row_data = [cell.text.strip() for cell in row.find_all('td')]
        # Check if any cell in the row has non-empty data
        if any(cell.strip() for cell in row_data):
            data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data, columns=headers)
    # Save DataFrame to CSV
    data= df.to_dict(orient='records')

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


        try:
            driver.implicitly_wait(20)
            # Find the div with class sc-tagGq etCJEH
            div_element = driver.find_element(By.CLASS_NAME, "sc-tagGq.etCJEH")
            # Find all a tags within the div
            driver.implicitly_wait(20)
            a_tags = div_element.find_elements(By.XPATH, "//a[@class='sc-fxwrCY bJcvgu']")
            # Click on the 4th index (indexing starts from 0)
            href= a_tags[3].get_attribute("href")
            driver.implicitly_wait(20)
            driver.execute_script("window.location.href = arguments[0]", href)

        except Exception as e:
            return {
                "status": False, 
                "message": "Error while finding or clicking on the property tax button",
                "exception": e
                }
        
        try:
            # Wait for the button with "Account History" span text to be clickable
            account_history_button = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, "//a[span[contains(text(), 'Account History')]]"))
            )
            account_history_button.click()            
        
        except Exception as e:
            data['account_history_summary']= []
            return {
                "status": False,
                "message": "Error while finding or clicking on the Account History button",
                "data": data,
                "exception": e
                }

        time.sleep(2)
        html= driver.page_source
        new_data= scrap_account_history_summary(html)

        data['account_history_summary']= new_data


        return {
            "status": True,
            "data": data
        }


    finally:
        # display.stop()
        if driver:
            driver.quit()


def start_nyc_scrapping(address):
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
