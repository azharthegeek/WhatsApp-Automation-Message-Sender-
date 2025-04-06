from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
import time
import logging
import os
import csv
from selenium.webdriver.remote.webelement import WebElement

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define message content
text_msg = "Hello How may i Help you"
caption_msg = "Flower image"
image_path = os.path.abspath("bluecap.png")

# List of phone numbers to process
phone_numbers = ["03120001547", "03152552452", "923010001547", "03154545213"]
non_whatsapp = []


def setup_driver():
    """Set up and configure Firefox WebDriver."""
    try:
        firefox_options = Options()
        # Uncomment the line below if you want to run in headless mode
        # firefox_options.add_argument("--headless")
        firefox_options.add_argument("--window-size=1456,876")
        
        # Use webdriver_manager to automatically download the correct driver
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        return driver
    except Exception as e:
        logger.error(f"Failed to set up WebDriver: {e}")
        raise

def wait_for_element(driver, by, selector, timeout=30):
    """Wait for an element to be present and return it."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except Exception as e:
        logger.error(f"Element not found: {selector}. Error: {e}")
        raise

def wait_for_element_clickable(driver, by, selector, timeout=30):
    """Wait for an element to be clickable and return it."""
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, selector))
    )
    return element

def element_exists(driver, by, selector, timeout=5):
    """Check if an element exists without raising an exception."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return True
    except TimeoutException:
        return False

def safe_click(driver, element, retries=3, delay=1):
    """Try to click an element safely with retries."""
    for i in range(retries):
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            if i == retries - 1:
                raise
            logger.warning(f"Click intercepted, retrying in {delay} seconds...")
            time.sleep(delay)
    return False

def go_back_to_main_chat_screen(driver):
    """Return to the main chat screen safely."""
    try:
        # Try to click the back button if we're in a chat or search view
        if element_exists(driver, By.CSS_SELECTOR, "div[data-testid='back']"):
            back_button = driver.find_element(By.CSS_SELECTOR, "div[data-testid='back']")
            safe_click(driver, back_button)
            time.sleep(1)
            
        # Try clicking the close button if in search results
        if element_exists(driver, By.CSS_SELECTOR, "div[data-testid='x-viewer']"):
            close_button = driver.find_element(By.CSS_SELECTOR, "div[data-testid='x-viewer']")
            safe_click(driver, close_button)
            time.sleep(1)
            
        # Wait for the main chat list to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".x17adc0v:nth-child(1) > .x78zum5 > span"))
        )
        logger.info("Successfully returned to main chat screen")
        return True
    except Exception as e:
        logger.warning(f"Failed to return to main chat screen: {e}")
        try:
            # As a last resort, reload the page
            driver.get("https://web.whatsapp.com")
            time.sleep(5)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".x17adc0v:nth-child(1) > .x78zum5 > span"))
            )
            logger.info("Page reloaded to return to main screen")
            return True
        except:
            logger.error("Could not recover WhatsApp state")
            return False

def send_text_character_by_character(element, text, delay=0.1):
    """Send text character by character with a delay to ensure proper input."""
    for char in text:
        element.send_keys(char)
        time.sleep(delay)  # Add a small delay between characters

def send_message_to_number(driver, full_number, phone_number, text_msg, image_path=None, caption_msg=None):
    """Send a message to a specific phone number."""
    try:
        # Ensure we're at the main chat screen before starting
        if not go_back_to_main_chat_screen(driver):
            logger.error("Could not navigate to main chat screen")
            return False
        
        # Click on new chat button
        logger.info("Clicking on new chat button")
        new_chat_button = wait_for_element_clickable(
            driver, By.CSS_SELECTOR, ".x17adc0v:nth-child(1) > .x78zum5 > span"
        )
        safe_click(driver, new_chat_button)
        time.sleep(3)  # Wait for animation
        
        # Wait for and click on search input using the specified XPath
        logger.info("Focusing search input")
        xpath_locator_role = '//div[@contenteditable="true" and @role="textbox"]'
        search_box_role = wait_for_element_clickable(driver, By.XPATH, xpath_locator_role)
        safe_click(driver, search_box_role)
        time.sleep(1)
        
        # Type phone number character by character
        logger.info(f"Typing phone number: {phone_number}")
        send_text_character_by_character(search_box_role, phone_number)
        logger.info("Phone number entered successfully!")
        time.sleep(3)  # Wait for search results
        
        # Try to find the contact with a 5-second timeout
        logger.info("Checking if contact exists on WhatsApp...")
        contact_found = element_exists(
            driver, 
            By.CSS_SELECTOR, 
            ".x10l6tqk:nth-child(2) > div > ._ak72 > ._ak8l", 
            timeout=5
        )
        
        if contact_found:
            # Contact exists on WhatsApp
            logger.info(f"Contact found for number: {phone_number}")
            contact_result = driver.find_element(By.CSS_SELECTOR, ".x10l6tqk:nth-child(2) > div > ._ak72 > ._ak8l")
            safe_click(driver, contact_result)
            time.sleep(2)  # Wait for chat to load
            
            # Find and click on the message input field
            logger.info("Focusing message input field")
            xpath_locator_message_label = '//div[@contenteditable="true" and @aria-label="Type a message"]'
            message_box = wait_for_element_clickable(driver, By.XPATH, xpath_locator_message_label)
            safe_click(driver, message_box)
            time.sleep(1)
            
            # Send message text character by character
            logger.info(f"Typing message: {text_msg}")
            send_text_character_by_character(message_box, text_msg)
            logger.info("Message text entered successfully!")
            time.sleep(1)  # Wait for text to settle

            # Click send button
            logger.info("Clicking send button")
            send_button = wait_for_element_clickable(
                driver, By.CSS_SELECTOR, ".x1iy03kw > span"
            )
            safe_click(driver, send_button)
            time.sleep(2)  # Wait for message to be sent
            
            # Send image if provided
            if image_path and os.path.exists(image_path):
                # Click on attach button (paperclip)
                logger.info("Clicking on attach button")
                attach_button = wait_for_element_clickable(
                    driver, By.CSS_SELECTOR, ".xlkovuz > span"
                )
                safe_click(driver, attach_button)
                time.sleep(1)  # Wait for menu to appear
                
                # Send image file using the file input element
                logger.info(f"Sending image: {image_path}")
                xpath_locator_file_input = '/html/body/div[1]/div/div/span[5]/div/ul/div/div/div[2]/li/div/input'
                file_input = wait_for_element(driver, By.XPATH, xpath_locator_file_input)
                file_input.send_keys(image_path)
                logger.info(f"Successfully selected image: {image_path}")
                time.sleep(3)  # Wait for image to upload
                
                # Click on caption field
                logger.info("Focusing caption field")
                xpath_locator_caption_label = '//div[@contenteditable="true" and @aria-label="Add a caption"]'
                caption_input = wait_for_element_clickable(driver, By.XPATH, xpath_locator_caption_label)
                safe_click(driver, caption_input)
                time.sleep(1)  # Give time for focus
                
                # Type caption character by character
                logger.info(f"Typing caption: {caption_msg}")
                send_text_character_by_character(caption_input, caption_msg)
                logger.info("Caption entered successfully!")
                time.sleep(1)  # Wait for text to settle
                
                # Click send media button
                logger.info("Clicking send media button")
                send_media_button = wait_for_element_clickable(
                    driver, By.CSS_SELECTOR, ".x1rluvsa"
                )
                safe_click(driver, send_media_button)
                
                # Wait for media to be sent
                logger.info("Waiting for media to be sent")
                time.sleep(5)
            
            logger.info(f"Message sent successfully to {full_number}")
            return True
        
        else:
            # Contact not found on WhatsApp
            logger.info(f"Back from: {phone_number}")
            xpath_locator_back_button_label = '//div[@role="button" and @aria-label="Back"]'
            back_button = driver.find_element(By.XPATH, xpath_locator_back_button_label)
            back_button.click()
            print("Clicked the back button using aria-label!")
            logger.warning(f"Contact not found for number: {full_number} (not on WhatsApp)")
            return False
            
    except Exception as e:
        logger.error(f"Error sending message to {full_number}: {e}")
        # Take screenshot on error
        try:
            driver.save_screenshot(f"error_{phone_number}_screenshot.png")
            logger.info(f"Error screenshot saved for {phone_number}")
        except:
            logger.error("Failed to save error screenshot")
        return False

def save_to_csv(non_whatsapp_list, filename="non_whatsapp_numbers.csv"):
    """Save the list of numbers not on WhatsApp to a CSV file."""
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Phone Number", "Reason"])
            for number in non_whatsapp_list:
                writer.writerow([number, "Not found on WhatsApp"])
        logger.info(f"Non-WhatsApp numbers saved to '{filename}'")
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")

def run_whatsapp_automation():
    """Run the WhatsApp Web automation script for multiple phone numbers."""
    
    success_count = 0
    
    driver = setup_driver()
    
    try:
        # Open WhatsApp Web
        logger.info("Opening WhatsApp Web")
        driver.get("https://web.whatsapp.com")
        
        # Set window size
        driver.set_window_size(1456, 876)
        
        # Wait for QR code scan and WhatsApp to load
        logger.info("Waiting for QR code scan...")
        # Wait for the main WhatsApp interface to load after QR scan
        wait_for_element(driver, By.CSS_SELECTOR, ".x17adc0v:nth-child(1) > .x78zum5 > span", timeout=120)
        logger.info("QR code scanned and WhatsApp loaded")
        
        # Process each phone number
        for full_number in phone_numbers:
            # Process phone number: extract last 7 digits
            phone_number = str(full_number)
            last_seven = phone_number[-7:]  # Get last 7 characters
            
            logger.info(f"Processing number: {full_number} (using last 7 digits: {last_seven})")
            
            # Try to send message to this number
            success = send_message_to_number(driver, full_number, last_seven, text_msg, image_path, caption_msg)
            
            # Track success/failure
            if success:
                success_count += 1
            else:
                non_whatsapp.append(full_number)
                logger.warning(f"Added {full_number} to non-WhatsApp list")
            
            # Make sure we're back at the main screen before the next number
            # go_back_to_main_chat_screen(driver)
            time.sleep(2)  # Short delay before processing the next number
        
        logger.info("WhatsApp automation completed successfully!")
        logger.info(f"Numbers not found on WhatsApp: {non_whatsapp}")
        
        # Save the non-WhatsApp numbers to a CSV
        save_to_csv(non_whatsapp)
        
        logger.info(f"Successfully sent message to {success_count} numbers")
        return non_whatsapp
        
    except Exception as e:
        logger.error(f"Error during automation: {e}")
        # Take screenshot on error
        try:
            driver.save_screenshot("error_screenshot.png")
            logger.info("Error screenshot saved as 'error_screenshot.png'")
        except:
            logger.error("Failed to save error screenshot")
        return []
    finally:
        # Ask user if they want to keep the browser open
        keep_open = input("Do you want to keep the browser open? (y/n): ")
        if keep_open.lower() != 'y':
            driver.quit()
            logger.info("Browser closed")
        else:
            logger.info("Browser kept open")

if __name__ == "__main__":
    non_whatsapp_numbers = run_whatsapp_automation()
    print(f"\nNumbers not found on WhatsApp: {non_whatsapp_numbers}")
        # Save non-WhatsApp numbers to a csv file
    with open("non_whatsapp_numbers.csv", "w") as f:
        for number in non_whatsapp_numbers:
            f.write(f"{number}\n")
    print("Non-WhatsApp numbers saved to 'non_whatsapp_numbers.csv'")
    # successfully send message to total
    print(f"Successfully sent message to {len(phone_numbers) - len(non_whatsapp_numbers)} numbers")
