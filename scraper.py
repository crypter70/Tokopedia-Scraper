import selenium
from selenium.webdriver.common.by import By                         
from selenium import webdriver as wb                                
from selenium.webdriver.support import expected_conditions as EC    
from selenium.webdriver.support.ui import WebDriverWait as wait     
import pandas as pd                                                 
from tqdm import tqdm                                               
from selenium.webdriver.common.keys import Keys


driver = wb.Chrome()
driver.get('https://www.tokopedia.com/')

driver.implicitly_wait(5)

keywords = input("Keywords: ")
pages = int(input("Pages: "))

search = driver.find_element(By.XPATH, '//*[@id="header-main-wrapper"]/div[2]/div[2]/div/div/div/div/input')
search.send_keys(keywords)
search.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

data_laptop = []

def scrolling():
    scheight = .1
    while scheight < 9.9:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
        scheight += .01

def reverse_scrolling():
    body = driver.find_element(By.TAG_NAME, 'body')

    i = 0
    while True:
        body.send_keys(Keys.PAGE_DOWN)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i = i + 1
        if i >= 25:
            break

def extract_data(driver):

    driver.implicitly_wait(20)
    driver.refresh()

    scrolling()

    item_laptop = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "css-12sieg3")]')))

    if len(item_laptop) != 80:
        driver.refresh()
        driver.implicitly_wait(10)
        scrolling()

        item_laptop = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "css-12sieg3")]')))

    for item in tqdm(item_laptop):

        element = wait(item, 10).until(EC.presence_of_element_located((By.XPATH, './/div[@class="css-y5gcsw"]')))

        name = element.find_element(By.XPATH, './/div[@class="prd_link-product-name css-3um8ox"]').text
        price = element.find_element(By.XPATH, './/div[@class="prd_link-product-price css-1ksb19c"]').text
        location = element.find_element(By.XPATH, './/span[@class="prd_link-shop-loc css-1kdc32b flip"]').text
        try:
            rating = element.find_element(By.XPATH, './/span[@class="prd_rating-average-text css-t70v7i"]').text
        except:
            rating = None

        try:
            sold = element.find_element(By.XPATH, './/span[@class="prd_label-integrity css-1duhs3e"]').text
        except:
            sold = None    

        details_link = element.find_element(By.XPATH, './/div[@class="css-1f2quy8"]/a').get_property('href')
        
        data = {
            'name': name,
            'price': price,
            'location': location,
            'rating': rating,
            'sold': sold,
            'details_link': details_link
        }

        data_laptop.append(data)

stop = 1

while stop <= pages:
    data_final = extract_data(driver)

    try:
        next_page = wait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Laman berikutnya"]')))
    except:
        driver.refresh()
        scrolling()
        reverse_scrolling()
        scrolling()
        next_page = wait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Laman berikutnya"]')))
    
    try:
        next_page.click()
    except:
        break

    stop = stop + 1

    
df = pd.DataFrame(data_laptop)


df.to_csv('data.csv', index=False)
df.to_json('data.json', orient='records')



