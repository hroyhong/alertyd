import os
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

GOOGLE_ALERTS_EMAIL="hroyhong@gmail.com"
GOOGLE_ALERTS_PASSWORD="sauo adfm kxlk khmp"

# Get credentials from environment variables
email = GOOGLE_ALERTS_EMAIL
password = GOOGLE_ALERTS_PASSWORD

print(email)
print(password)

if not email or not password:
    logger.error("Email or password not set in .env file")
    exit(1)

try:
    # Automatically install ChromeDriver and get its path
    chromedriver_path = chromedriver_autoinstaller.install()
    logger.info(f"ChromeDriver installed at: {chromedriver_path}")

    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome driver with the Service
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Navigate to Google Alerts
    driver.get('https://www.google.com/alerts')
    logger.info("Navigated to Google Alerts page")

    # Wait for and click the sign-in button
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign in"))).click()
    logger.info("Clicked Sign in button")

    # Enter email
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "identifier"))).send_keys(email)
    driver.find_element(By.ID, "identifierNext").click()
    logger.info("Entered email")

    # Enter password
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
    driver.find_element(By.ID, "passwordNext").click()
    logger.info("Entered password")

    # Wait for alerts page to load
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "alert-list")))
    logger.info("Alerts page loaded")

    # Get alerts
    alerts = driver.find_elements(By.CLASS_NAME, "alert-row")
    
    for alert in alerts:
        alert_text = alert.text
        logger.info(f"Alert: {alert_text}")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")

finally:
    if 'driver' in locals():
        driver.quit()
