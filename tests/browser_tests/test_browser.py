import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class TestSeleniumBrowser:
    """Test Selenium headless browser functionality for system testing"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Create a headless Chrome WebDriver instance"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Create WebDriver with automatic ChromeDriver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        # Clean up
        driver.quit()
    
    def test_basic_webpage_loading(self, driver):
        """Test basic webpage loading and title verification"""
        # Navigate to a simple test page
        driver.get("https://httpbin.org/")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Verify page title
        assert "httpbin" in driver.title.lower()
        
        # Verify page loaded successfully
        assert driver.current_url == "https://httpbin.org/"
        
        # Check that some content is present
        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert len(body_text) > 0
        
        # Verify HTTP status (should be 200)
        # Note: Selenium doesn't give direct access to HTTP status codes
        # but we can verify the page loaded successfully
        
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page source length: {len(driver.page_source)}")
    
    def test_form_interaction_and_validation(self, driver):
        """Test form interaction and basic validation"""
        # Navigate to a form test page
        driver.get("https://httpbin.org/forms/post")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Find form elements
        customer_name_input = driver.find_element(By.NAME, "custname")
        telephone_input = driver.find_element(By.NAME, "custtel")
        email_input = driver.find_element(By.NAME, "custemail")
        size_select = driver.find_element(By.NAME, "size")
        toppings_checkboxes = driver.find_elements(By.NAME, "topping")
        delivery_time_input = driver.find_element(By.NAME, "delivery")
        comments_textarea = driver.find_element(By.NAME, "comments")
        
        # Fill out the form
        customer_name_input.send_keys("John Do")
        telephone_input.send_keys("555-123-4567")
        email_input.send_keys("john.doe@example.com")
        
        # Select size
        size_select.click()
        size_option = driver.find_element(By.CSS_SELECTOR, "input[value='medium']")
        size_option.click()
        size_select = size_option.get_attribute("value")
        
        # Select toppings
        for checkbox in toppings_checkboxes[:2]:  # Select first 2 toppings
            if not checkbox.is_selected():
                checkbox.click()
        
        # Set delivery time
        delivery_time_input.send_keys("12:30P")
        
        
        # Add comments
        comments_textarea.click()
        comments_textarea.send_keys("Please deliver to the back door")
        # Verify form data was entered correctly
        assert customer_name_input.get_attribute("value") == "John Doe"
        assert telephone_input.get_attribute("value") == "555-123-4567"
        assert email_input.get_attribute("value") == "john.doe@example.com"
        assert size_select == "medium"
        assert delivery_time_input.get_attribute("value") == "12:30"
        assert comments_textarea.get_attribute("value") == "Please deliver to the back door"
        
        # Verify toppings were selected
        selected_toppings = [cb for cb in toppings_checkboxes if cb.is_selected()]
        assert len(selected_toppings) >= 2
        
        print(f"Form filled successfully")
        print(f"Customer name: {customer_name_input.get_attribute('value')}")
        print(f"Size selected: {size_select}")
        print(f"Toppings selected: {len(selected_toppings)}")
