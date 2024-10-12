from google_alerts import GoogleAlerts
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get credentials from environment variables
email = os.environ.get('GOOGLE_ALERTS_EMAIL')
password = os.environ.get('GOOGLE_ALERTS_PASSWORD')

if not email or not password:
    logger.error("Email or password not set in environment variables")
    exit(1)

try:
    ga = GoogleAlerts(email, password)
    logger.info("GoogleAlerts instance created")
    
    ga.authenticate()
    logger.info("Authentication successful")
    
    alerts = ga.list()
    logger.info(f"Fetched {len(alerts)} alerts")
    
    for alert in alerts:
        logger.info(f"Alert: {alert}")

except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
