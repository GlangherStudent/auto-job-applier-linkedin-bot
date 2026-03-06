'''
Error recovery & retry logic module.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.02.10
'''

import time
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
from functools import wraps
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
    WebDriverException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from modules.helpers import print_lg


def retry_on_exception(max_retries: int = 3, delay: float = 2.0, backoff: float = 2.0, exceptions: tuple = None):
    '''
    Decorator for automatic retry with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch (default: common Selenium exceptions)
    '''
    if exceptions is None:
        exceptions = (
            NoSuchElementException,
            TimeoutException,
            StaleElementReferenceException,
            ElementNotInteractableException,
            ElementClickInterceptedException
        )
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        print_lg(f"⚠️ Retry {attempt + 1}/{max_retries} for {func.__name__}: {type(e).__name__}")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print_lg(f"❌ All retries exhausted for {func.__name__}")
                        raise last_exception
            
            return None
        return wrapper
    return decorator


class ErrorRecovery:
    '''
    Handles error recovery and self-healing for the bot.
    '''
    
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
    
    
    def recover_from_stuck_modal(self) -> bool:
        '''
        Attempts to close stuck modals/dialogs.
        Returns True if recovery successful.
        '''
        try:
            print_lg("🔧 Attempting to close stuck modal...")
            
            # Try ESC key multiple times
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            for _ in range(3):
                actions.send_keys(Keys.ESCAPE).perform()
                time.sleep(0.5)
            
            print_lg("✅ Modal closed with ESC")
            return True
            
        except Exception as e:
            print_lg(f"⚠️ Modal recovery failed: {e}")
            return False
    
    
    def recover_from_page_error(self) -> bool:
        '''
        Attempts to recover from page errors by refreshing.
        Returns True if recovery successful.
        '''
        try:
            print_lg("🔧 Attempting page refresh...")
            self.driver.refresh()
            time.sleep(3)
            print_lg("✅ Page refreshed successfully")
            return True
        except Exception as e:
            print_lg(f"⚠️ Page refresh failed: {e}")
            return False
    
    
    def check_linkedin_accessible(self) -> bool:
        '''
        Checks if LinkedIn is accessible.
        Returns True if accessible.
        '''
        try:
            current_url = self.driver.current_url
            if 'linkedin.com' in current_url:
                return True
            else:
                print_lg(f"⚠️ Not on LinkedIn: {current_url}")
                return False
        except Exception as e:
            print_lg(f"⚠️ Cannot check URL: {e}")
            return False
    
    
    def detect_rate_limiting(self) -> bool:
        '''
        Detects if LinkedIn is rate limiting ONLY on job search/application pages.
        Returns True if rate limiting detected.
        ##> ------ Enhanced by AI Audit - More Specific Rate Limit Detection ------
        '''
        try:
            current_url = self.driver.current_url
            
            # Check on job-related pages and any LinkedIn page with errors
            if not any(x in current_url for x in ['/jobs/', '/feed/', 'linkedin.com']):
                return False  # Not on LinkedIn, skip check
            
            # Look for SPECIFIC rate limit messages in visible elements only
            try:
                # Check for visible error messages
                error_elements = self.driver.find_elements(By.XPATH, 
                    "//*[contains(@class, 'error') or contains(@class, 'alert') or contains(@class, 'warning')]")
                
                for element in error_elements:
                    if element.is_displayed():
                        text = element.text.lower()
                        
                        # Very specific rate limit phrases
                        if any(phrase in text for phrase in [
                            'exceeded the daily application limit',
                            'too many applications',
                            'reached the limit',
                            'apply limit reached'
                        ]):
                            print_lg(f"⚠️ Rate limiting detected: '{text[:50]}'")
                            return True
                
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            
            return False
            
        except Exception as e:
            print_lg(f"⚠️ Cannot detect rate limiting: {e}")
            return False
    
    
    def detect_captcha(self) -> bool:
        '''
        Detects if CAPTCHA is present and VISIBLE.
        Returns True only if CAPTCHA is actively blocking.
        ##> ------ Enhanced by AI Audit - More Specific CAPTCHA Detection ------
        '''
        try:
            # Check for actual CAPTCHA elements that are visible
            try:
                # Look for visible reCAPTCHA iframe
                captcha_iframe = self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha') or contains(@title, 'reCAPTCHA')]")
                if captcha_iframe and captcha_iframe.is_displayed():
                    # Check if it's actually blocking (not just present in background)
                    size = captcha_iframe.size
                    if size['width'] > 100 and size['height'] > 100:  # Visible size
                        print_lg(f"🚨 Active CAPTCHA detected (visible and blocking)!")
                        return True
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            
            # Check for LinkedIn security challenge page
            try:
                current_url = self.driver.current_url
                if 'checkpoint/challenge' in current_url or 'security/verify' in current_url:
                    print_lg(f"🚨 LinkedIn security challenge detected!")
                    return True
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            
            return False
            
        except Exception:
            return False
    
    
    def safe_click(self, element, max_retries: int = 3) -> bool:
        '''
        Safely clicks element with retry logic.
        Returns True if successful.
        '''
        for attempt in range(max_retries):
            try:
                element.click()
                return True
            except ElementClickInterceptedException:
                if attempt < max_retries - 1:
                    print_lg(f"⚠️ Click intercepted, retry {attempt + 1}/{max_retries}")
                    time.sleep(1)
                    # Try to scroll element into view
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
            except Exception as e:
                if attempt < max_retries - 1:
                    print_lg(f"⚠️ Click error: {type(e).__name__}, retry {attempt + 1}/{max_retries}")
                    time.sleep(1)
        
        return False
    
    
    def handle_network_error(self, max_wait: int = 300) -> bool:
        '''
        Handles network errors by waiting and retrying.
        Returns True if network recovered.
        '''
        print_lg("🌐 Network error detected, waiting for recovery...")
        
        wait_intervals = [10, 20, 30, 60, 60, 60]  # Progressive waiting
        
        for i, interval in enumerate(wait_intervals):
            if i * 60 > max_wait:
                break
            
            print_lg(f"⏳ Waiting {interval}s (attempt {i + 1}/{len(wait_intervals)})...")
            time.sleep(interval)
            
            try:
                # Try to access LinkedIn
                self.driver.get(LinkedInURLs.FEED_URL)
                time.sleep(3)
                if self.check_linkedin_accessible():
                    print_lg("✅ Network recovered!")
                    return True
            except (NoSuchElementException, TimeoutException) as e:
                continue
        
        print_lg("❌ Network recovery failed")
        return False


    def recover_webdriver_session(self) -> bool:
        """
        Try to recover a WebDriver session that appears to be broken
        (for example HTTPConnectionPool / target machine actively refused it).
        Note: this method cannot recreate the driver automatically, but
        it provides a single log point and a recommendation to restart.
        """
        self.recovery_attempts += 1
        print_lg(
            f"⚠️ WebDriver connection appears broken "
            f"(attempt {self.recovery_attempts}/{self.max_recovery_attempts})."
        )

        # Quick check to see if we can still access current_url
        try:
            _ = self.driver.current_url
            print_lg("✅ WebDriver still responds to current_url – no hard reset performed.")
            return True
        except Exception as e:
            print_lg(f"⚠️ WebDriver current_url failed: {type(e).__name__} - {str(e)[:120]}")

        if self.recovery_attempts >= self.max_recovery_attempts:
            print_lg(
                "🛑 Maximum WebDriver recovery attempts reached. "
                "Please restart the bot or the browser session manually."
            )
            return False

        # Try a simple refresh as a last soft fallback
        try:
            print_lg("🔧 Trying soft WebDriver refresh on last known page...")
            self.driver.refresh()
            time.sleep(3)
            print_lg("✅ Soft refresh executed, continuing with caution.")
            return True
        except Exception as e:
            print_lg(f"❌ WebDriver refresh also failed: {type(e).__name__} - {str(e)[:120]}")
            return False


def safe_execute(func):
    '''
    Decorator that wraps function in try-except and logs errors.
    Function continues even if exception occurs.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print_lg(f"⚠️ Error in {func.__name__}: {type(e).__name__} - {str(e)}")
            return None
    return wrapper


##<
