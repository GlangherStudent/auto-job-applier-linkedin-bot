'''
Selenium click and find helpers for the LinkedIn bot.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''

from config.settings import click_gap, smooth_scroll
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
from modules.helpers import buffer, print_lg, sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)

# Click Functions
def wait_span_click(driver: WebDriver, text: str, time: float=5.0, click: bool=True, scroll: bool=True, scrollTop: bool=False) -> WebElement | bool:
    '''
    Finds the span element with the given `text`.
    - Returns `WebElement` if found, else `False` if not found.
    - Clicks on it if `click = True`.
    - Will spend a max of `time` seconds in searching for each element.
    - Will scroll to the element if `scroll = True`.
    - Will scroll to the top if `scrollTop = True`.
    - Tries multiple selectors (span, button containing text, aria-label) for robustness (e.g. Next/Review).
    '''
    if not text:
        return False
    # Selectors: exact span first, then button with span/text, then aria-label (LinkedIn may use different structure)
    xpaths = [
        './/span[normalize-space(.)="' + text + '"]',
        './/button[.//span[normalize-space(.)="' + text + '"]]',
        './/button[contains(normalize-space(.), "' + text + '")]',
        './/*[@aria-label="' + text + '"]',
        './/*[contains(@aria-label, "' + text + '") and (@role="button" or name()="button")]',
        './/*[@role="button" and contains(translate(., "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "' + text.lower() + '")]',
    ]
    for i, xpath in enumerate(xpaths):
        try:
            wait_time = time if i == 0 else min(1, time)
            button = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, xpath)))
            if button and button.is_displayed() and button.is_enabled():
                if scroll:
                    scroll_to_view(driver, button, scrollTop)
                if click:
                    try:
                        button.click()
                    except ElementClickInterceptedException:
                        # LinkedIn often has temporary overlays/labels that intercept clicks.
                        # JS click is a practical fallback (still may fail if element truly not interactable).
                        try:
                            driver.execute_script("arguments[0].click();", button)
                        except Exception:
                            raise
                    buffer(click_gap)
                return button
        except Exception:
            continue
    print_lg(f"Click Failed! Didn't find '{text}" + "'")
    return False

def multi_sel(driver: WebDriver, texts: list, time: float=5.0) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that text.
    - Will spend a max of `time` seconds in searching for each element.
    '''
    for text in texts:
        ##> ------ Dheeraj Deshwal : dheeraj20194@iiitd.ac.in/dheerajdeshwal9811@gmail.com - Bug fix ------
        wait_span_click(driver, text, time, False)
        ##<
        try:
            button = WebDriverWait(driver,time).until(EC.presence_of_element_located((By.XPATH, './/span[normalize-space(.)="'+text+'"]')))
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            print_lg(f"Click Failed! Didn't find '{text}"+"'")
            # print_lg(e)

def multi_sel_noWait(driver: WebDriver, texts: list, actions: ActionChains = None) -> None:
    '''
    - For each text in the `texts`, tries to find and click `span` element with that class.
    - If `actions` is provided, bot tries to search and Add the `text` to this filters list section.
    - Won't wait to search for each element, assumes that element is rendered.
    '''
    for text in texts:
        try:
            button = driver.find_element(By.XPATH, './/span[normalize-space(.)="'+text+'"]')
            scroll_to_view(driver, button)
            button.click()
            buffer(click_gap)
        except Exception as e:
            if actions: company_search_click(driver,actions,text)
            else:   print_lg(f"Click Failed! Didn't find '{text}"+"'")
            # print_lg(e)

def boolean_button_click(driver: WebDriver, actions: ActionChains, text: str) -> None:
    '''
    Tries to click on the boolean button with the given `text` text.
    '''
    try:
        list_container = driver.find_element(By.XPATH, './/h3[normalize-space()="'+text+'"]/ancestor::fieldset')
        button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
        scroll_to_view(driver, button)
        actions.move_to_element(button).click().perform()
        buffer(click_gap)
    except Exception as e:
        print_lg(f"Click Failed! Didn't find '{text}"+"'")
        # print_lg(e)

# Find functions
def find_by_class(driver: WebDriver, class_name: str, time: float=5.0) -> WebElement | Exception:
    '''
    Waits for a max of `time` seconds for element to be found, and returns `WebElement` if found, else `Exception` if not found.
    '''
    return WebDriverWait(driver, time).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

# Scroll functions
def scroll_to_view(driver: WebDriver, element: WebElement, top: bool = False, smooth_scroll: bool = smooth_scroll) -> None:
    '''
    Scrolls the `element` to view.
    - `smooth_scroll` will scroll with smooth behavior.
    - `top` will scroll to the `element` to top of the view.
    '''
    if top:
        return driver.execute_script('arguments[0].scrollIntoView();', element)
    behavior = "smooth" if smooth_scroll else "instant"
    return driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "'+behavior+'" });', element)

# Enter input text functions
def text_input_by_ID(driver: WebDriver, id: str, value: str, time: float=5.0) -> None | Exception:
    '''
    Enters `value` into the input field with the given `id` if found, else throws NotFoundException.
    - `time` is the max time to wait for the element to be found.
    '''
    username_field = WebDriverWait(driver, time).until(EC.presence_of_element_located((By.ID, id)))
    username_field.send_keys(Keys.CONTROL + "a")
    username_field.send_keys(value)

def try_xp(driver: WebDriver, xpath: str, click: bool=True) -> WebElement | bool:
    try:
        if not click:
            return driver.find_element(By.XPATH, xpath)

        # Click path (more robust than a raw .click())
        ele = driver.find_element(By.XPATH, xpath)
        try:
            scroll_to_view(driver, ele)
        except Exception:
            pass

        try:
            ele.click()
            return True
        except ElementClickInterceptedException:
            # Common in LinkedIn when an overlay/label temporarily blocks clicks.
            # Try JS click as a safe fallback; if it still fails, treat as not found/clickable.
            try:
                driver.execute_script("arguments[0].click();", ele)
                return True
            except Exception:
                return False
    except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
        # Selector not found or not clickable – fail silently to avoid noisy logs.
        return False

def try_linkText(driver: WebDriver, linkText: str) -> WebElement | bool:
    try:
        return driver.find_element(By.LINK_TEXT, linkText)
    except (NoSuchElementException, ElementNotInteractableException, TimeoutException):
        # Link not found is expected in many flows – no need to log every attempt.
        return False

def try_find_by_classes(driver: WebDriver, classes: list[str]) -> WebElement | ValueError:
    for cla in classes:
        try:    return driver.find_element(By.CLASS_NAME, cla)
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
            pass
    raise ValueError("Failed to find an element with given classes")

def company_search_click(driver: WebDriver, actions: ActionChains, companyName: str) -> None:
    '''
    Tries to search and Add the company to company filters list.
    '''
    wait_span_click(driver,"Add a company",1)
    search = driver.find_element(By.XPATH,"(.//input[@placeholder='Add a company'])[1]")
    search.send_keys(Keys.CONTROL + "a")
    search.send_keys(companyName)
    buffer(3)
    actions.send_keys(Keys.DOWN).perform()
    actions.send_keys(Keys.ENTER).perform()
    print_lg(f'Tried searching and adding "{companyName}"')

def text_input(actions: ActionChains, textInputEle: WebElement | bool, value: str, textFieldName: str = "Text") -> None | Exception:
    if textInputEle:
        sleep(1)
        # actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
        textInputEle.clear()
        textInputEle.send_keys(value.strip())
        sleep(2)
        actions.send_keys(Keys.ENTER).perform()
    else:
        print_lg(f'{textFieldName} input was not given!')