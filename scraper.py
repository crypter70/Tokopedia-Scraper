import selenium
from selenium.webdriver.common.by import By                             # By to get element using selector              
from selenium import webdriver as wb                                    # wb to run the driver
from selenium.webdriver.support import expected_conditions as EC        # EC to handle exception conditions
from selenium.webdriver.support.ui import WebDriverWait as wait         # wait to handle wait conditions
import pandas as pd                                                     # pd to export data
from tqdm import tqdm                                                   # tqdm to visualize looping process
from selenium.webdriver.common.keys import Keys                         # Keys as procedures using the keyboards


# initialize driver Chrome to run simulation and get URL
driver = wb.Chrome()
driver.get('https://www.tokopedia.com/')

driver.implicitly_wait(5)

# initialize input to get keywords and pages
keywords = input("Keywords: ")
pages = int(input("Pages: "))

# initialize search to search by keywords and press ENTER
search = driver.find_element(By.XPATH, '//*[@id="header-main-wrapper"]/div[2]/div[2]/div/div/div/div/input')
search.send_keys(keywords)
search.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

# initialize product_data to store product data as an array
product_data = []

# define scrolling to scroll page
def scrolling():
    scheight = .1
    while scheight < 9.9:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
        scheight += .01

# define reverse_scrolling to reverse the scroll
def reverse_scrolling():
    body = driver.find_element(By.TAG_NAME, 'body')

    i = 0
    while True:
        body.send_keys(Keys.PAGE_DOWN)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        i += 1
        if i >= 25:
            break

# define extract_data to extract data using driver
def extract_data(driver):

    driver.implicitly_wait(20)
    driver.refresh()
    scrolling()

    # get the data item using XPATH selector, wait up for 30 secs if it exceeds it will issue an exception
    data_item = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "css-12sieg3")]')))

    # if the data items do not add up to 80 it will repeat the data retrieval process
    if len(data_item) != 80:
        driver.refresh()
        driver.implicitly_wait(10)
        scrolling()

        data_item = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "css-12sieg3")]')))

    # loop to extract attribute data using XPATH selector
    for item in tqdm(data_item):

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

        # store data to the dictionary
        data = {
            'name': name,
            'price': price,
            'location': location,
            'rating': rating,
            'sold': sold,
            'details_link': details_link
        }

        # append data to product_data
        product_data.append(data)

stop = 1

# loop to scraping process 
while stop <= pages:
    extract_data(driver)

    # get the next button element using CSS selector, wait up for 60 secs if it exceeds it will issue an exception
    try:
        next_page = wait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Laman berikutnya"]')))
    except:
        driver.refresh()
        scrolling()
        reverse_scrolling()
        scrolling()
        next_page = wait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Laman berikutnya"]')))
    
    # click the next_page button
    try:
        next_page.click()
    except:
        break

    stop += 1

    
df = pd.DataFrame(product_data)

# export data to csv and json
df.to_csv('data.csv', index=False)
df.to_json('data.json', orient='records')



