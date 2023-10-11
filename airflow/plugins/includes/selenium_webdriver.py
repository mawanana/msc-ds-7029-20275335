from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def get_selenium_webdriver(source_url):
    try:
        # Ensure the correct Chrome WebDriver version is installed.
        chromedriver_autoinstaller.install()

        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()
        # Uncomment the following line to run in headless mode (without a GUI)
        chrome_options.add_argument('--lang=en-US')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Configure Chrome preferences to disable images
        chrome_prefs = {}
        chrome_options.experimental_options["prefs"] = chrome_prefs
        chrome_prefs["profile.default_content_settings"] = {"images": 2}

        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)

        # Open the specified URL
        driver.get(source_url)

        # Print a message indicating that the WebDriver is ready
        print("WebDriver Initialized")

        return driver

    except Exception as e:
        # If an error occurs, return an error message
        error_message = f"Error loading Chrome WebDriver: {str(e)}"
        return error_message

def enable_download_headless(driver):
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': '/home/airflow'}}
    driver.execute("send_command", params)