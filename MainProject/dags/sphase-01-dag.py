from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import time
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

def setup_driver(download_directory):
    """Set up the Selenium WebDriver with the necessary options."""
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
    return driver

def navigate_to_url(driver, url):
    """Navigate to the given URL."""
    driver.get(url)
    time.sleep(30)  # Wait for the page to load

def select_year(driver, year):
    """Select the desired year from the dropdown menu."""
    button = driver.find_element(By.XPATH, "//button[@title='Time period']")
    button.click()
    time.sleep(5)
    label = driver.find_element(By.XPATH, f"//label[@for='selectTimePeriod_{year}']")
    label.click()

def start_export(driver):
    """Click the necessary buttons to start the export process."""
    time.sleep(5)
    export_button = driver.find_element(By.ID, "ecdc-btn-export")
    export_button.click()

    time.sleep(5)
    driver.find_element(By.ID, "cckPostponeCookies").click()

    time.sleep(5)
    radio_button = driver.find_element(By.ID, "optionsRadios1")
    radio_button.click()

    time.sleep(5)
    download_button = driver.find_element(By.ID, "ecdc-btn-export-csv")
    download_button.click()

def rename_downloaded_file(original_file_path, new_file_path):
    """Rename the downloaded file."""
    time.sleep(5)
    if os.path.exists(original_file_path):
        os.rename(original_file_path, new_file_path)
        print(f"File renamed to: {new_file_path}")
    else:
        print(f"File not found: {original_file_path}")

def download_csv(year):
    url = "https://atlas.ecdc.europa.eu/public/index.aspx?Dataset=27&HealthTopic=31"
    download_directory = os.path.join(os.getcwd(), "data")
    original_filename = "ECDC_surveillance_data_Leptospirosis.csv"  # Replace with the actual file name
    new_filename = f"{year}.csv"  # The new name you want to give to the file

    # Construct full file paths
    original_file_path = os.path.join(download_directory, original_filename)
    new_file_path = os.path.join(download_directory, new_filename)

    # Setup WebDriver
    driver = setup_driver(download_directory)

    try:
        # Navigate and interact with the webpage
        navigate_to_url(driver, url)
        select_year(driver, year)
        start_export(driver)

        # Rename the downloaded file
        rename_downloaded_file(original_file_path, new_file_path)
        return new_file_path  # Return the new file path
    finally:
        # Ensure the browser is closed after the process
        driver.quit()

def merge_csv_files(file_paths, merged_file_path):
    """Merge multiple CSV files into a single CSV file."""
    dataframes = [pd.read_csv(file_path) for file_path in file_paths]
    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df.to_csv(merged_file_path, index=False)

def push_to_api_gateway(file_path, api_endpoint):
    """Push each row of the CSV file to the API Gateway in JSON format."""
    headers = {'Content-Type': 'application/json'}
    
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    for index, row in df.iterrows():
        # Convert each row to JSON
        row_dict = row.to_dict()
        payload = {'MessageBody': row_dict}
        
        # Send POST request to API Gateway
        response = requests.post(api_endpoint, headers=headers, data=json.dumps(payload))
        
        # Check response
        if response.status_code == 200:
            print(f"Successfully pushed row {index}")
        else:
            print(f"Failed to push row {index}: {response.text}")

def merge_and_upload(**kwargs):
    """Download, merge CSV files, and push data to API Gateway."""
    download_directory = os.path.join(os.getcwd(), "data")
    file_paths = []

    # Download CSV files for each year
    for year in range(2007, 2016):
        file_path = download_csv(year)
        file_paths.append(file_path)

    # Merge CSV files
    merged_file_path = os.path.join(download_directory, "merged_data.csv")
    merge_csv_files(file_paths, merged_file_path)

    # Push data to API Gateway
    api_endpoint = 'https://19ovcm1x06.execute-api.eu-north-1.amazonaws.com/publisher'
    push_to_api_gateway(merged_file_path, api_endpoint)

with DAG(
    dag_id='csv_to_api_gateway_dag',
    schedule_interval='@daily',
    start_date=datetime(2024, 8, 12),
    catchup=False
) as dag:

    # Merge and upload task
    task_merge_and_upload = PythonOperator(
        task_id='merge_and_upload',
        python_callable=merge_and_upload,
        provide_context=True
    )

    task_merge_and_upload