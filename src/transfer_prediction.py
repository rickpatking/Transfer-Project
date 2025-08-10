import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def get_recent_transfers():
    url = 'https://www.on3.com/transfer-portal/wire/basketball/2025/'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    while True:
        try:
            # not working correctly
            load_more_button = driver.find_element(By.CLASS_NAME, 'MuiButtonBase-root MuiButton-root MuiButton-text MuiButton-textPrimary MuiButton-sizeMedium MuiButton-textSizeMedium MuiButton-disableElevation MuiButton-root MuiButton-text MuiButton-textPrimary MuiButton-sizeMedium MuiButton-textSizeMedium MuiButton-disableElevation TransferPortalPage_btnLoadMore__JwJT3 css-1vy56sb')
            load_more_button.click()
            time.sleep(2)
            print('cow')
        except Exception as e:
            print(f'No more products to load')
            break

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    driver.quit()

    all_ols = soup.find_all('ol', {'class': 'TransferPortalPage_transferPortalList__vbYpa' })
    if all_ols:
        for ol in all_ols:
            list_items = ol.find_all('li')
            for item in list_items:
                # two spans, one for position and one for enrollment/status
                link = item.find_all('span')
                print(link.get_text(strip=True))

get_recent_transfers()