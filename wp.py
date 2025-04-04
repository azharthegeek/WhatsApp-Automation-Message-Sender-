from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import pyperclip
import sys
import pandas as pd

# Load the Excel file
df = pd.read_excel('new_plant_data3.xlsx')

# Extract mobile numbers from the specified range and clean them
all_names = df['Phone 1 - Value'][:100]

all_names = list(all_names)


# Statistics tracking
successfully_sent = 0
failed_list = []
fail_to_send = 0

# Initialize Options for Chrome
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

with open('msg.txt', 'r', encoding='utf8') as f:
    msg = f.read()

# Uncomment and set path if you want to use existing Chrome profile
# options.add_argument("--user-data-dir=YOUR_CHROME_PROFILE_PATH")

try:

#    service = Service('/usr/bin/chromedriver') # Explicitly set ChromeDriver location
    service = Service(ChromeDriverManager().install())

    browser = webdriver.Chrome(service = service,  options=options)

except Exception as e:

    print(f"Error initializing ChromeDriver with explicit path: {e}")

    try:

        browser = webdriver.Chrome(options=options) # Try without explicit service

    except Exception as e2:

        print(f"Error initializing ChromeDriver without Service: {e2}")

        try:

            service = Service(ChromeDriverManager().install()) # Try with webdriver-manager

            browser = webdriver.Chrome(service=service, options=options)

        except Exception as e3:

            print(f"Error initializing ChromeDriver with ChromeDriverManager: {e3}")

            raise

browser.maximize_window()

browser.get('https://web.whatsapp.com/')
browser.implicitly_wait(120)
time.sleep(30)


# Replace this with your code to get contact names
# Example:
# all_names = ["03152983545", "923152983545"] 

loop_count = 0
wait = WebDriverWait(browser, 10)  # Wait for a maximum of 10 seconds

# Main loop to send messages
for name in all_names:
    name = str(name)
    name = list(name)
    name = name[-7:]  # Get last 7 characters
    name = "".join(name)
    loop_count += 1
    print(f"Processing {name} (Loop {loop_count}/{len(all_names)})")
    
    try:
        # Click on search/compose button
        # search_path = '//div[@contenteditable="true"][@data-tab="3"]'
        # search_box = browser.find_element(By.XPATH, search_path)
        # search_box.clear()
        # print("sdfs")
        # print("Search box cleared successfully")
        # time.sleep(1)

        # #pyperclip.copy(group)
        # search_box.click()
        # time.sleep(2)
        # print("1111asd1")
        # search_box.send_keys(name)
         # Clear and focus the search box
        search_path = '//div[@contenteditable="true"][@data-tab="3"]'
        search_box = browser.find_element(By.XPATH, search_path)
        
        search_box.click()
        search_box.clear()
        
        # Type the contact name and wait for search results to update
        search_box.send_keys(name)
        
        
        print("11111")
        # Click on the first search result
        
        time.sleep(3)
        contact = browser.find_element(By.XPATH, '//*[@id="pane-side"]/div/div/div/div[2]/div/div/div/div[2]')
        contact.click()
        
    #     time.sleep(5)
    #     input_xpath = '//div[@contenteditable="true"][@data-tab="10"]'
    #     input_box = WebDriverWait(browser, 10).until(
    #     EC.presence_of_element_located((By.XPATH, input_xpath))
    # )
    #     actions = ActionChains(browser)
    #     actions.move_to_element(input_box).click().perform()
    #     time.sleep(2)

    #     browser.execute_cdp_cmd('Input.insertText', {'text': msg})

    #     time.sleep(2)

        try:
            if 1==1:
                attachment_box = browser.find_element(By.XPATH,'//button[@title="Attach"]')
                attachment_box.click()
                time.sleep(1)
                image_path = os.path.abspath("bluecap.jpg")

                image_box = browser.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                image_box.send_keys(image_path)
                time.sleep(2)
            

                send_btn = browser.find_element(By.XPATH,'//div[@role="button"][@aria-label="Send"]')
                send_btn.click()
                time.sleep(4)

        except IndexError:
            pass
        time.sleep(2)
        print("555555")
        print(f"Successfully sent message to: {name}")
        successfully_sent += 1
        
        # search_box.clear()
    except Exception as e:
        print(f"Failed to send message to {name}. Error: {str(e)}")
        failed_list.append(name)
        fail_to_send += 1
        
        # Try to go back to the main screen to continue with next contact
        try:
            # back_button = browser.find_element(By.XPATH, 
            #     '//span[@data-icon="back" or @data-icon="x"]')
            search_path = '//div[@contenteditable="true"][@data-tab="3"]'
            search_box = browser.find_element(By.XPATH, search_path)
            
            search_box.click()
            search_box.clear()
            
            back_button = browser.find_element(By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/button')
    
            back_button.click()
        except:
            print("Could not find back button")

# Print summary results
print("\n--- Summary ---")
print(f"Total contacts processed: {loop_count}")
print(f"Successfully sent: {successfully_sent}")
print(f"Failed to send: {fail_to_send}")
print("Failed list:", failed_list)

# Keep browser open until user decides to close
input("Press Enter to close the browser...")
browser.quit()
