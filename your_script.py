import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
import logging
import os

# Setup logging
logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to create a new WebDriver instance
def create_webdriver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# Initialize WebDriver
driver = create_webdriver()

# Define the path for the input file containing links
input_file_path = 'collected_links.txt'

# Define the path for the output CSV file
output_file_path = 'extracted_data.csv'

# Define the path for the progress file
progress_file_path = 'progress.txt'

# Function to extract data from a given URL
def extract_data_from_url(url):
    global driver
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Extract the headword
    headword_element = driver.find_element(By.CSS_SELECTOR, "h1.oxencycl-title span.oxencycl-headword")
    headword = headword_element.text

    # Extract the frequency
    frequency_element = driver.find_element(By.CSS_SELECTOR, "h1.oxencycl-title span.headwordInfo")
    frequency = frequency_element.text.split(':')[-1].strip()  # Extract the number after the colon

    # Extract the description text from all sub divs
    sub_divs = driver.find_elements(By.CSS_SELECTOR, "div.bodyCssRoot div.div1")
    description = "\n".join([div.text for div in sub_divs])

    return headword, frequency, description

# Read all the links from the input file
with open(input_file_path, 'r') as file:
    links = [line.strip() for line in file.readlines()]

# Determine the start index
start_index = 0

# Read the progress file to get the last processed link
if os.path.exists(progress_file_path):
    with open(progress_file_path, 'r') as file:
        last_processed_link = file.read().strip()
        if last_processed_link in links:
            start_index = links.index(last_processed_link) + 1

# Open the CSV file for writing (append mode)
with open(output_file_path, 'a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Link', 'Headword', 'Frequency', 'Description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    if start_index == 0:
        writer.writeheader()  # Write header only if starting from the beginning

    # Iterate through each link starting from the last processed link
    for link in tqdm(links[start_index:], desc="Processing links"):
        try:
            headword, frequency, description = extract_data_from_url(link)
            writer.writerow({'Link': link, 'Headword': headword, 'Frequency': frequency, 'Description': description})
            logging.info(f"Extracted data from {link}")

            # Write the last processed link to the progress file
            with open(progress_file_path, 'w') as progress_file:
                progress_file.write(link)
        except Exception as e:
            logging.error(f"Failed to extract data from {link}: {e}")
            # Restart the WebDriver in case of an exception
            driver.quit()
            driver = create_webdriver()

# Close the browser
driver.quit()
logging.info("All data has been saved to extracted_data.csv")
