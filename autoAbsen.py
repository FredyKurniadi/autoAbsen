from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def absen(driver):
  # Navigate to attendance page
  driver.get("https://akademik.polban.ac.id/ajar/absen#")

  # Find all buttons with class name "btn btn-info"
  buttons = driver.find_elements(By.ID, "simpan_awal")

  # Check if attendance has been done
  if len(buttons) == 0:
    print("Sudah absen")
  else:
    # Loop through each button and click on it
    for button in buttons:
      button.click()
      time.sleep(1)  # Add a small delay to allow the action to complete

  # Do not quit the driver, keep it running in the minimized state
  # driver.quit()

  # Set Chrome options to start in headless and minimized mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--start-minimized")  # Minimize the window

driver = webdriver.Chrome(options=chrome_options)

# Set implicit wait to 10 seconds
driver.implicitly_wait(10)

driver.get("https://akademik.polban.ac.id/")
print(driver.title)

# Enter username and password
driver.find_element(By.NAME, "username").send_keys("231524010")
driver.find_element(By.NAME, "password").send_keys("*Polban8306#")

# Click login button
driver.find_element(By.NAME, "submit").click()

# Explicitly wait for the alert
try:
  WebDriverWait(driver, 10).until(EC.alert_is_present())
  alert = driver.switch_to.alert
  alert.accept()
except TimeoutException:
  print("No alert found within the specified timeout period.")
except Exception as e:
  print("An error occurred:", str(e))

while True:
  absen(driver)
  time.sleep(300)
  print('hi')
