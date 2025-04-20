
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from appium.options.android import UiAutomator2Options
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def measure_time(task_name):
    """Decorator to measure execution time of a function."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start_time = time.time()
            result = func(self, *args, **kwargs)
            end_time = time.time()
            response_time = end_time - start_time
            self.response_times[task_name] = response_time
            logger.info(f"{task_name} took {response_time:.2f} seconds")
            return result
        return wrapper
    return decorator

class AmazonAppAutomation:
    def __init__(self):
        options = UiAutomator2Options()
        options.platform_name = 'Android'
        options.platform_version = '16.0'  # Change to your Android version
        options.device_name = 'emulator-5554'  # From `adb devices`
        options.app_package = 'in.amazon.mShop.android.shopping'
        options.app_activity = 'com.amazon.mShop.home.HomeActivity'
        options.automation_name = 'UiAutomator2'
        options.no_reset = False
        options.full_reset = False
        options.auto_grant_permissions = True

        try:
            self.driver = webdriver.Remote(
                command_executor='http://127.0.0.1:4723',
                options=options
            )
            self.wait = WebDriverWait(self.driver, 30)
            self.response_times = {}
            logger.info("Appium driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Appium driver: {str(e)}")
            raise

    def skip_login(self):
        window_size = self.driver.get_window_size()
        x = int(window_size['width'] * 0.27)
        y = int(window_size['height'] * 0.18)
        self.driver.tap([(x, y)], 100)

        language_btn = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'English')]")
            ))
        language_btn.click()

        skip_btn = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Skip')]")
            ))
        skip_btn.click()

    @measure_time("Homepage Load Time")
    def load_homepage(self):
        """Measure homepage load time."""
        try:
            logger.info("Waiting for homepage to load...")
            home_element = self.wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//*[contains(@text, 'Search') or contains(@content-desc, 'Search') or contains(@resource-id, 'search')]")
            ))
            logger.info("Homepage loaded successfully")
        except Exception as e:
            logger.error(f"Error in load_homepage: {str(e)}")
            raise

    @measure_time("Search Wireless Headphones")
    def search_headphones(self):
        """Search for 'wireless headphones'."""
        try:
            # Try multiple ways to find and click search
            search_box = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Search') or contains(@content-desc, 'Search') or contains(@resource-id, 'search')]")
            ))
            search_box.click()
            
            # Wait for search input to be active
            search_input = self.wait.until(EC.presence_of_element_located(
                (AppiumBy.CLASS_NAME, "android.widget.EditText")
            ))
            search_input.clear()
            search_input.send_keys("wireless headphones")
            
            # Press Enter
            self.driver.press_keycode(66)
            
            # Wait for results
            self.wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//*[contains(@text, 'Results') or contains(@text, 'results')]")
            ))
            logger.info("Search completed successfully")
        except Exception as e:
            logger.error(f"Error in search_headphones: {str(e)}")
            raise

    @measure_time("Sort by Price and Retrieve Lowest Priced Item")
    def sort_by_price(self):
        try:
            # Click on the filters button
            filter_btn = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Sort') or contains(@content-desc, 'Sort') or "
                                "contains(@text, 'Filter') or contains(@content-desc, 'Filter')]")
            ))
            filter_btn.click()

            window_size = self.driver.get_window_size()
            start_x = window_size['width'] // 6
            start_y = int(window_size['height'] * 0.8)
            end_y = int(window_size['height'] * 0.2)
            self.driver.swipe(start_x, start_y, start_x, end_y, 100)

            # Click on Sort by option
            sort_btn = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Sort by')]")
            ))
            sort_btn.click()

            # Tap on "Price: Low to High"
            x = int(window_size['width'] * 0.68)
            y = int(window_size['height'] * 0.24)
            self.driver.tap([(x, y)], 100)
            time.sleep(2)

            # Tap on "Apply" or "Show results" button
            x = int(window_size['width'] * 0.90)
            y = int(window_size['height'] * 0.944)
            self.driver.tap([(x, y)], 100)

            time.sleep(3)


            lowprice_name = "yo"
            lowprice_price = "yo"
            flag=0
            name = []
            price = []

            # Find all clickable elements on screen
            elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().clickable(true)")
            for el in elements:
                try:
                    text = el.text.strip()
                    if text:
                        continue
                    else:
                        # Try to explore child elements inside if no direct text
                        children = el.find_elements(By.XPATH, ".//*")
                        for child in children:
                            child_text = child.text.strip()
                            if  "Headphone" in child_text: 
                                name.append(child_text)
                            if "₹" in child_text:
                                price.append(child_text)

                except Exception as e:
                    print(f"Error reading element: {e}")

            print(f"Lowest price headphone: {name[0]}\nPrice: {price[2]}")
            return name[0], price[2]


        except Exception as e:
            logger.error(f"Error in sort_by_price: {str(e)}")
            self.driver.save_screenshot("sort_by_price_error.png")
            raise


    @measure_time("Sort by Rating")
    def sort_by_rating(self):
        """Sort by rating and return top item details."""
        try:
            # Click on filter/sort button
            sort_button = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Filter') or contains(@content-desc, 'Filter')]")
            ))
            sort_button.click()
            
            # Select "Avg. Customer Review"
            rating_option = self.wait.until(EC.element_to_be_clickable(
                (AppiumBy.XPATH, "//*[contains(@text, 'Avg. Customer Review')]")
            ))
            rating_option.click()

            time.sleep(2)



            window_size = self.driver.get_window_size()
            start_x = window_size['width'] // 6
            start_y = int(window_size['height'] * 0.8)
            end_y = int(window_size['height'] * 0.2)

            

            x = int(window_size['width'] * 0.90)
            y = int(window_size['height'] * 0.944)
            self.driver.tap([(x, y)], 100)

            time.sleep(3)


            highreview_name = ""
            highreview_price = ""
            flag=0
            name = []
            price = []

            # Find all clickable elements on screen
            elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().clickable(true)")
            for el in elements:
                try:
                    text = el.text.strip()
                    if text:
                        continue
                    else:
                        # Try to explore child elements inside if no direct text
                        children = el.find_elements(By.XPATH, ".//*")
                        for child in children:
                            child_text = child.text.strip()
                            if  "Headphone" in child_text:
                                name.append(child_text)
                            if "₹" in child_text:
                                price.append(child_text)

                except Exception as e:
                    print(f"Error reading element: {e}")

            print("\n")
            print(f"Highest rated headphone: {name[0]}\nPrice: {price[2]}")
            return name[0],price[2]


        except Exception as e:
            logger.error(f"Error in sort_by_price: {str(e)}")
            self.driver.save_screenshot("sort_by_price_error.png")
            raise


    def run_automation(self):
        """Execute all tasks and log response times."""
        try:

            self.skip_login()

            self.load_homepage()
            self.search_headphones()
            
            # Sort by price and get item details
            price_item_name, price_item_price = self.sort_by_price()            
            # Sort by rating and get item details
            rated_item_name = self.sort_by_rating()
            
            # Add the top rated item to cart

            start_e = time.time()
            add_to_cart_button = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("Add to cart").instance(0)')
            add_to_cart_button.click()
            end_e = time.time()
            time.sleep(3)
            print(f"Add to Cart Response time: {end_e - start_e:.2f}s")

            
            
            # logger.info("\n=== RESPONSE TIMES ===")
            # for task, time_taken in self.response_times.items():
            #     logger.info(f"{task}: {time_taken:.2f} seconds")
                
        except Exception as e:
            logger.error(f"Automation failed: {str(e)}")
            self.driver.save_screenshot("automation_error.png")
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()

if __name__ == "__main__":
    try:
        automation = AmazonAppAutomation()
        automation.run_automation()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

