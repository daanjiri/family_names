import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options

# Setup the Chrome WebDriver with headless options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define the path for the input file containing links
input_file_path = 'collected_links.txt'

# Define the path for the output CSV file
output_file_path = 'extracted_data.csv'

# Function to extract data from a given URL
def extract_data_from_url(url):
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

# Open the CSV file for writing
with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Link', 'Headword', 'Frequency', 'Description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through each link and extract the data with progress tracking
    for link in tqdm(links, desc="Processing links"):
        try:
            headword, frequency, description = extract_data_from_url(link)
            writer.writerow({'Link': link, 'Headword': headword, 'Frequency': frequency, 'Description': description})
            print(f"Extracted data from {link}")
        except Exception as e:
            print(f"Failed to extract data from {link}: {e}")

# Close the browser
driver.quit()
print(f"All data has been saved to {output_file_path}")
