'''
Main LinkedIn Easy Apply bot entrypoint.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''


# Imports
import os
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
import csv
import re
import time
import pyautogui

# Set CSV field size limit to prevent field size errors
csv.field_size_limit(CSVConstants.MAX_FIELD_SIZE)  # Set to 1MB instead of default 131KB

from random import choice, shuffle, randint, random
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    NoSuchElementException, ElementClickInterceptedException,
    NoSuchWindowException, ElementNotInteractableException,
    WebDriverException, TimeoutException, StaleElementReferenceException
)

from config.personals import (
    first_name, last_name, middle_name, phone_number,
    current_city, street, state, zipcode, country,
    ethnicity, gender, disability_status, veteran_status,
    PERSONALS
)
from config.questions import (
    desired_salary, desired_salary_max, current_ctc,
    years_of_experience, notice_period, education,
    require_visa, us_citizenship,
    cover_letter, default_resume_path, resume_cv_folder,
    pause_before_submit, pause_at_failed_question,
    QUESTIONS_PERSONAL, availability_start,
    overwrite_previous_answers, recent_employer,
    linkedin_summary, linkedin_headline,
    linkedIn, website, confidence_level
)
from config.search import (
    search_terms, search_location, switch_number,
    sort_by, date_posted, salary, easy_apply_only,
    experience_level, job_type, on_site,
    companies, location, industry, job_function,
    about_company_bad_words, bad_words, security_clearance,
    did_masters, current_experience,
    onsite_locations, remote_locations, enable_location_filtering,
    strict_location_filter, allowed_work_locations,
    randomize_search_order,
    under_10_applicants, in_your_network, fair_chance_employer,
    job_titles, benefits, commitments, about_company_good_words,
    pause_after_filters
)
from config.secrets import username, password
from config.settings import (
    close_tabs, follow_companies, run_non_stop,
    alternate_sortby, cycle_date_posted, stop_date_cycle_at_24hr,
    file_name, failed_file_name, logs_folder_path,
    click_gap, run_in_background, disable_extensions,
    safe_mode, smooth_scroll, keep_screen_awake,
    stealth_mode, showErrorAlerts,
    enable_anti_detection, daily_application_limit,
    session_length_minutes, enable_session_breaks,
    enable_workday_simulation
)

##> ------ Enhanced by AI Audit - Robust Modules ------
try:
    from modules.anti_detection import HumanBehaviorSimulator, smart_buffer, get_random_delay
except ImportError as e:
    HumanBehaviorSimulator = None
    smart_buffer = None
    get_random_delay = None
    print(f"[WARNING] Anti-detection module not available: {e}")

try:
    from modules.session_manager import SessionManager, WorkdayScheduler
except ImportError as e:
    SessionManager = None
    WorkdayScheduler = None
    print(f"[WARNING] Session manager module not available: {e}")

try:
    from modules.error_recovery import ErrorRecovery, retry_on_exception, safe_execute
except ImportError as e:
    ErrorRecovery = None
    retry_on_exception = None
    safe_execute = None
    print(f"[WARNING] Error recovery module not available: {e}")

try:
    from modules.file_manager import FileManager
except ImportError as e:
    FileManager = None
    print(f"[WARNING] File manager module not available: {e}")

try:
    from modules.smart_answers import (
        smart_match_question, get_contextual_answer, match_select_option,
        intelligent_yes_no_answer, detect_yes_no_options, KEYWORD_GROUPS
    )
except ImportError as e:
    smart_match_question = None
    get_contextual_answer = None
    match_select_option = None
    intelligent_yes_no_answer = None
    detect_yes_no_options = None
    print(f"[WARNING] Smart answers module not available: {e}")

try:
    from modules.job_matcher import smart_text_answer, job_matcher
    JOB_MATCHER_AVAILABLE = job_matcher is not None
    if JOB_MATCHER_AVAILABLE:
        print("[OK] JobMatcher loaded")
except Exception as e:
    job_matcher = None
    smart_text_answer = None
    JOB_MATCHER_AVAILABLE = False
    print(f"[WARNING] JobMatcher not available: {e}")

try:
    from modules.cv_selector import get_resume_path_for_job
except ImportError:
    get_resume_path_for_job = None

try:
    from modules.llm_field_helper import ask_llm_for_field
except ImportError:
    ask_llm_for_field = None
##<

# Note: availability_start already imported from config.questions (line 55)
# Note: onsite_locations, remote_locations, enable_location_filtering already imported from config.search (line 66)

from modules.open_chrome import driver, actions, wait
from modules.helpers import (
    critical_error_log, print_lg, buffer, manual_login_retry,
    calculate_date_posted, truncate_for_csv, sleep
)
from modules.clickers_and_finders import (
    wait_span_click, boolean_button_click, find_by_class,
    scroll_to_view, text_input_by_ID, try_xp, try_linkText,
    try_find_by_classes, text_input, multi_sel_noWait
)
from selenium.webdriver.common.keys import Keys
from modules.validator import validate_config
from modules.application_state import ApplicationState, PersonalInfo, SalaryInfo
from modules.csv_manager import CachedCSVManager

from typing import Literal


pyautogui.FAILSAFE = False


#< Global Variables and logics

if run_in_background == True:
    pause_at_failed_question = False
    pause_before_submit = False
    run_non_stop = False

##> ------ Enhanced by AI Audit - Application State Management ------
# Initialize personal information
personal_info = PersonalInfo(
    first_name=first_name.strip(),
    middle_name=middle_name.strip(),
    last_name=last_name.strip(),
    phone_number=phone_number,
    current_city=current_city
)

# Import desired_salary_max if exists, otherwise use desired_salary
try:
    from config.questions import desired_salary_max
except ImportError:
    desired_salary_max = desired_salary

# Initialize salary information
salary_info = SalaryInfo(
    desired_salary=desired_salary,
    desired_salary_max=desired_salary_max,
    current_ctc=current_ctc
)

# Initialize application state (thread-safe)
app_state = ApplicationState(personal_info, salary_info)

# Backward compatibility - create convenient aliases
full_name = personal_info.full_name
desired_salary_lakhs = salary_info.desired_salary_lakhs
desired_salary_monthly = salary_info.desired_salary_monthly
desired_salary_range = salary_info.desired_salary_range
current_ctc_lakhs = salary_info.current_ctc_lakhs
current_ctc_monthly = salary_info.current_ctc_monthly
desired_salary_str = str(desired_salary)
current_ctc_str = str(current_ctc)

notice_period_months = str(notice_period // TimeConversion.DAYS_PER_MONTH)
notice_period_weeks = str(notice_period // TimeConversion.DAYS_PER_WEEK)
notice_period = str(notice_period)
##<

##> ------ Enhanced by AI Audit - Global Instances (Robust & Stable) ------
human_behavior = None  # HumanBehaviorSimulator instance
session_manager = None  # SessionManager instance
error_recovery = None  # ErrorRecovery instance
file_manager = None  # FileManager instance
##<

#>


def _is_external_ats_context() -> bool:
    """
    Detect whether the current form is served by an external ATS
    (Workable, SmartRecruiters, Greenhouse, etc.), in which case the
    buttons and flow may differ significantly from LinkedIn’s standard Easy Apply.
    """
    try:
        url = driver.current_url.lower()
    except Exception:
        url = ""

    ats_keywords = [
        "workable.com",
        "smartrecruiters.com",
        "greenhouse.io",
        "myworkdayjobs.com",
        "bamboohr.com",
        "recruitee.com",
    ]
    if any(k in url for k in ats_keywords):
        return True

    # As a fallback, detect generic “powered by” texts in the form footer
    try:
        footer_text = driver.find_element(
            By.XPATH,
            "//*[contains(normalize-space(.), 'Application powered by') or "
            "contains(normalize-space(.), 'powered by Workable') or "
            "contains(normalize-space(.), 'powered by SmartRecruiters')]",
        ).text.lower()
        if "powered by" in footer_text or "application powered by" in footer_text:
            return True
    except Exception:
        pass

    return False


# Helper to inspect Easy Apply form state (validation + final submit)
def _find_form_validation_errors(modal: WebElement) -> list[str]:
    """
    Look for validation messages inside the Easy Apply form.
    Return a list of non-empty validation messages that were found.
    """
    messages: list[str] = []
    try:
        error_elements = modal.find_elements(
            By.XPATH,
            ".//*[contains(@class,'artdeco-inline-feedback') "
            "or contains(@class,'artdeco-inline-feedback__message') "
            "or @data-test-form-element-error-message='true']",
        )
        for el in error_elements:
            try:
                txt = el.text.strip()
            except Exception:
                txt = ""
            if txt:
                messages.append(txt)
    except Exception:
        return messages

    if messages:
        print_lg("⚠️ Form validation errors detected before Submit:")
        for msg in messages:
            print_lg(f"   - {msg}")
    return messages


def _click_final_submit_button(modal: WebElement) -> bool:
    """
    Try to submit the application using multiple strategies:
    - classic texts such as 'Submit application' / 'Submit' / 'Send application'
    - the primary (non-secondary, non-disabled) button from the modal footer.

    Return True if a Submit-style button was successfully clicked.
    """
    # 1) Standard attempt on known button texts (scope limited to the modal)
    for label in ("Submit application", "Submit", "Send application"):
        try:
            if wait_span_click(modal, label, 2, scrollTop=True):
                return True
        except Exception:
            continue

    # 2) Generic search for the primary button in the footer
    footer = None
    try:
        footer = modal.find_element(
            By.XPATH,
            ".//footer[contains(@class,'jobs-easy-apply-modal__footer') "
            "or contains(@class,'artdeco-modal__actionbar')]",
        )
    except Exception:
        # If we do not find an explicit footer, search the whole modal
        footer = modal

    try:
        buttons = footer.find_elements(By.XPATH, ".//button[not(@disabled)]")
    except Exception:
        buttons = []

    for btn in buttons:
        try:
            text = (btn.text or "").strip().lower()
            aria = (btn.get_attribute("aria-label") or "").strip().lower()
            data_control = (btn.get_attribute("data-control-name") or "").strip().lower()
            classes = (btn.get_attribute("class") or "").strip().lower()

            # Skip secondary/cancel buttons
            if "secondary" in classes or "cancel" in text or "back" in text:
                continue

            looks_like_submit = any(
                kw in text or kw in aria or kw in data_control
                for kw in ("submit", "send application", "send", "apply")
            ) or "submit_unify" in data_control

            if not looks_like_submit:
                continue

            scroll_to_view(driver, btn, True)
            try:
                actions.move_to_element(btn).click().perform()
            except Exception:
                try:
                    btn.click()
                except Exception:
                    continue
            buffer(click_gap)
            print_lg("✅ Clicked primary Submit button via generic selector")
            return True
        except Exception:
            continue

    return False


#< Login Functions
def is_logged_in_LN() -> bool:
    '''
    Function to check if user is logged-in in LinkedIn
    * Returns: `True` if user is logged-in or `False` if not
    '''
    if driver.current_url == LinkedInURLs.FEED_URL: return True
    if try_linkText(driver, "Sign in"): return False
    if try_xp(driver, '//button[@type="submit" and contains(text(), "Sign in")]'):  return False
    if try_linkText(driver, "Join now"): return False
    print_lg("Didn't find Sign in link, so assuming user is logged in!")
    return True


def login_LN() -> None:
    '''
    Function to login for LinkedIn
    * Tries to login using given `username` and `password` from `secrets.py`
    * If failed, tries to login using saved LinkedIn profile button if available
    * If both failed, asks user to login manually
    '''
    # Find the username and password fields and fill them with user credentials
    driver.get(LinkedInURLs.LOGIN_URL)
    # If username or password not configured, fall back to saved browser profile / manual login
    if not username or not password:
        ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
        print_lg("⚠️ User did not configure LINKEDIN_USERNAME and LINKEDIN_PASSWORD in .env!")
        print_lg("Attempting to login with saved browser profile...")
        ##<
        manual_login_retry(is_logged_in_LN, 2)
        return
    try:
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        try:
            text_input_by_ID(driver, "username", username, 1)
        except Exception as e:
            print_lg("Couldn't find username field.")
            # print_lg(e)
        try:
            text_input_by_ID(driver, "password", password, 1)
        except Exception as e:
            print_lg("Couldn't find password field.")
            # print_lg(e)
        # Find the login submit button and click it
        driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
    except Exception as e1:
        try:
            profile_button = find_by_class(driver, "profile__details")
            profile_button.click()
        except Exception as e2:
            # print_lg(e1, e2)
            print_lg("Couldn't Login!")

    try:
        # Wait until successful redirect, indicating successful login
        wait.until(EC.url_to_be(LinkedInURLs.FEED_URL)) # wait.until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space(.)="Start a post"]')))
        return print_lg("Login successful!")
    except Exception as e:
        print_lg("Seems like login attempt failed! Possibly due to wrong credentials or already logged in! Try logging in manually!")
        # print_lg(e)
        manual_login_retry(is_logged_in_LN, 2)
#>



##> ------ Enhanced by AI Audit - CSV Manager with Caching ------
# Initialize cached CSV manager (5 minute cache)
csv_manager = CachedCSVManager(file_name, cache_ttl_seconds=300)
failed_csv_manager = CachedCSVManager(failed_file_name, cache_ttl_seconds=300)
##<

def get_applied_job_ids() -> set[str]:
    '''
    Function to get a `set` of applied job's Job IDs
    * Returns a set of Job IDs from existing applied jobs history csv file
    * Now uses thread-safe CSV manager with caching
    '''
    try:
        return csv_manager.get_column_as_set_cached(column_index=0, skip_header=True)
    except Exception as e:
        print_lg(f"[WARNING] Error reading applied job IDs: {e}")
        return set()


def navigate_to_jobs_search_human_like(search_term: str) -> bool:
    '''
    Full user-like flow: Search bar → Jobs → Easy Apply.
    Simulates: type in search → Enter → click Jobs → click Easy Apply.
    Returns True if it succeeds, False for a fallback to the direct URL.
    '''
    try:
        # 1. Make sure we are on the feed/home or jobs page
        if "feed" not in driver.current_url and "jobs" not in driver.current_url:
            driver.get(LinkedInURLs.FEED_URL)
            buffer(3)
        
        # 2. Find and click the global search bar
        search_selectors = [
            "//input[contains(@placeholder, 'Search')]",
            "//input[@aria-label='Search']",
            "//input[contains(@class, 'search')]",
            "//header//input[@type='text']",
        ]
        search_input = None
        for xpath in search_selectors:
            try:
                search_input = driver.find_element(By.XPATH, xpath)
                if search_input.is_displayed():
                    break
            except Exception:
                continue
        
        if not search_input:
            print_lg("⚠️ Search bar not found, using direct URL...")
            return False
        
        # 3. Click, clear, type search term (like a user), then press Enter
        scroll_to_view(driver, search_input)
        buffer(1)
        search_input.click()
        buffer(1)
        search_input.clear()
        buffer(0.5)
        # The user types the desired role (for example, "logistics manager") – Easy Apply is handled later
        text_input(actions, search_input, search_term, "Search")
        buffer(1)
        search_input.send_keys(Keys.ENTER)
        buffer(3)
        
        # 4. Click the "Jobs" filter in the search results
        jobs_clicked = False
        for xpath in [
            "//button[.//span[normalize-space()='Jobs']]",
            "//span[normalize-space()='Jobs']/ancestor::button",
            "//a[contains(@href, '/search/results')]//span[contains(text(), 'Jobs')]",
            "//*[contains(@class, 'search-reusables__filter')]//span[normalize-space()='Jobs']",
        ]:
            try:
                jobs_btn = driver.find_element(By.XPATH, xpath)
                if jobs_btn.is_displayed():
                    scroll_to_view(driver, jobs_btn)
                    buffer(1)
                    jobs_btn.click()
                    jobs_clicked = True
                    print_lg("✅ Clicked Jobs filter")
                    break
            except Exception:
                continue
        
        if not jobs_clicked:
            # We might already be on the Jobs page after search – check the URL
            if "/jobs/" in driver.current_url:
                jobs_clicked = True
            else:
                print_lg("⚠️ Jobs button not found, using direct URL...")
                return False
        
        buffer(3)
        
        # 5. Easy Apply will be handled in apply_filters(); at this point we are on the Jobs page
        print_lg("✅ Human-like flow: Search → Jobs (Easy Apply will be handled in apply_filters)")
        return True
        
    except Exception as e:
        print_lg(f"⚠️ Human-like flow failed: {e}")
        return False


def apply_easy_apply_direct() -> bool:
    '''
    Try to click the Easy Apply button directly from the filter bar
    (without opening All filters).
    Returns True if it succeeds, False otherwise.
    '''
    if not easy_apply_only:
        return True
    try:
        # Wait for the filter bar to appear in the DOM (All filters button present)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))
            )
            buffer(1)
        except Exception:
            pass
        # Selectors for the Easy Apply button in the Jobs filter bar (multiple LinkedIn variants)
        selectors = [
            "//button[.//span[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'easy apply')]]",
            "//button[contains(., 'Easy Apply')]",
            "//span[normalize-space()='Easy Apply']/ancestor::button",
            "//*[@role='button'][.//span[contains(text(), 'Easy Apply')]]",
            "//*[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'easy apply')]",
            "//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'easy apply')]",
            "//li[.//span[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'easy apply')]]//button",
            "//*[@role='button'][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'easy apply')]",
        ]
        for xpath in selectors:
            try:
                btn = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, xpath)))
                if btn and btn.is_displayed() and btn.is_enabled():
                    scroll_to_view(driver, btn)
                    buffer(1)
                    btn.click()
                    buffer(1)
                    print_lg("✅ Easy Apply activated directly (without All filters)")
                    return True
            except Exception:
                continue
    except Exception as e:
        print_lg(f"Easy Apply direct not found: {e}")
    return False


def set_search_location() -> None:
    '''
    Function to set search location
    '''
    if search_location.strip():
        try:
            print_lg(f'Setting search location as: "{search_location.strip()}"')
            search_location_ele = try_xp(driver, ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", False) #  and not(@aria-hidden='true')]")
            text_input(actions, search_location_ele, search_location, "Search Location")
        except ElementNotInteractableException:
            try_xp(driver, ".//label[@class='jobs-search-box__input-icon jobs-search-box__keywords-label']")
            actions.send_keys(Keys.TAB, Keys.TAB).perform()
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(search_location.strip()).perform()
            sleep(2)
            actions.send_keys(Keys.ENTER).perform()
            try_xp(driver, ".//button[@aria-label='Cancel']")
        except Exception as e:
            try_xp(driver, ".//button[@aria-label='Cancel']")
            print_lg("Failed to update search location, continuing with default location!", e)


def apply_filters() -> None:
    '''
    Function to apply job search filters
    '''
    set_search_location()

    try:
        recommended_wait = 1 if click_gap < 1 else 0

        # Open the All filters dialog
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[normalize-space()="All filters"]')
            )
        ).click()
        buffer(recommended_wait)

        # 1) Sort by = Most recent
        wait_span_click(driver, "Most recent")
        buffer(recommended_wait)

        # 2) Easy Apply = ON
        boolean_button_click(driver, actions, "Easy Apply")
        buffer(recommended_wait)

        # 3) Click "Show results" button to apply filters
        show_results_button: WebElement = driver.find_element(
            By.XPATH,
            '//button[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "apply current filters to show")]',
        )
        show_results_button.click()

        global pause_after_filters
        if pause_after_filters:
            print_lg("Pause after filters enabled. Continuing in 5s...")
            sleep(5)

    except Exception as e:
        print_lg("Setting the preferences failed!")
        print_lg(f"Error: {e}")



def get_page_info() -> tuple[WebElement | None, int | None]:
    '''
    Function to get pagination element and current page number
    '''
    try:
        pagination_element = try_find_by_classes(driver, ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"])
        scroll_to_view(driver, pagination_element)
        current_page = int(pagination_element.find_element(By.XPATH, "//button[contains(@class, 'active')]").text)
    except Exception as e:
        print_lg("Failed to find Pagination element, hence couldn't scroll till end!")
        pagination_element = None
        current_page = None
        print_lg(e)
    return pagination_element, current_page



def get_job_main_details(job: WebElement, blacklisted_companies: set, rejected_jobs: set) -> tuple[str, str, str, str, str, bool]:
    '''
    # Function to get job main details.
    Returns a tuple of (job_id, title, company, work_location, work_style, skip)
    * job_id: Job ID
    * title: Job title
    * company: Company name
    * work_location: Work location of this job
    * work_style: Work style of this job (Remote, On-site, Hybrid)
    * skip: A boolean flag to skip this job
    '''
    skip = False
    job_details_button = job.find_element(By.TAG_NAME, 'a')  # job.find_element(By.CLASS_NAME, "job-card-list__title")  # Problem in India
    scroll_to_view(driver, job_details_button, True)
    job_id = job.get_dom_attribute('data-occludable-job-id')
    title = job_details_button.text
    if "\n" in title:
        title = title.split("\n")[0]
    other_details = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
    index = other_details.find(' · ')
    if index == -1:
        company = other_details.strip()
        work_location = ""
        work_style = ""
    else:
        company = other_details[:index]
        work_location = other_details[index+3:]
        paren_start = work_location.rfind('(')
        paren_end = work_location.rfind(')')
        if paren_start != -1 and paren_end != -1 and paren_end > paren_start:
            work_style = work_location[paren_start+1:paren_end]
            work_location = work_location[:paren_start].strip()
        else:
            work_style = ""
            work_location = work_location.strip()

    # Fallback: when location is only in caption (e.g. "Bucharest, Romania (Remote)" in metadata)
    if not work_location or not work_location.strip():
        try:
            caption_el = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__caption')
            metadata = caption_el.find_elements(By.CSS_SELECTOR, '.job-card-container__metadata-wrapper li')
            if metadata:
                caption_text = metadata[0].text.strip()
                if caption_text:
                    paren_start = caption_text.rfind('(')
                    paren_end = caption_text.rfind(')')
                    if paren_start != -1 and paren_end != -1 and paren_end > paren_start:
                        work_style = caption_text[paren_start+1:paren_end].strip()
                        work_location = caption_text[:paren_start].strip()
                    else:
                        work_location = caption_text
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
            pass

    # Skip if previously rejected due to blacklist or already applied
    if company in blacklisted_companies:
        print_lg(f'Skipping "{title} | {company}" job (Blacklisted Company). Job ID: {job_id}!')
        skip = True
    elif job_id in rejected_jobs: 
        print_lg(f'Skipping previously rejected "{title} | {company}" job. Job ID: {job_id}!')
        skip = True

    # Strict location filter: accept only jobs whose displayed work location is in the allowed list
    if not skip and strict_location_filter:
        w = ' '.join(work_location.strip().lower().split())
        location_ok = False
        if w:
            for loc in allowed_work_locations:
                loc_norm = loc.strip().lower()
                if w == loc_norm or loc_norm in w or w.startswith(loc_norm):
                    location_ok = True
                    break
        if not location_ok:
            print_lg(f'Skipping "{title} | {company}" job (location "{work_location}" not in allowed set). Job ID: {job_id}!')
            skip = True
    
    # Check location filtering based on work style
    if not skip and enable_location_filtering:
        location_accepted = False
        if work_style.lower() == "remote":
            # For remote jobs, check against remote_locations
            for accepted_location in remote_locations:
                if accepted_location.lower() in work_location.lower():
                    location_accepted = True
                    break
            if not location_accepted:
                print_lg(f'Skipping "{title} | {company}" job (Remote location "{work_location}" not in accepted remote locations). Job ID: {job_id}!')
                skip = True
        elif work_style.lower() in ["on-site", "hybrid"]:
            # For on-site/hybrid jobs, check against onsite_locations
            for accepted_location in onsite_locations:
                if accepted_location.lower() in work_location.lower():
                    location_accepted = True
                    break
            if not location_accepted:
                print_lg(f'Skipping "{title} | {company}" job (On-site/Hybrid location "{work_location}" not in accepted locations). Job ID: {job_id}!')
                skip = True
    try:
        if job.find_element(By.CLASS_NAME, "job-card-container__footer-job-state").text == "Applied":
            skip = True
            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
    except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
        pass
    try:
        if not skip:
            job_details_button.click()
    except Exception as e:
        # Retry with ActionChains (element might be covered or need scroll-into-view)
        try:
            scroll_to_view(driver, job_details_button, True)
            buffer(0.5)
            actions.move_to_element(job_details_button).click().perform()
        except Exception:
            print_lg(f'Failed to click "{title} | {company}" job on details button. Job ID: {job_id}!')
            discard_job()
            job_details_button.click()  # To pass the error outside
    buffer(click_gap)
    return (job_id,title,company,work_location,work_style,skip)


# Function to check for Blacklisted words in About Company
def check_blacklist(rejected_jobs: set, job_id: str, company: str, blacklisted_companies: set) -> tuple[set, set, WebElement]:
    jobs_top_card = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description","jobs-unified-top-card__primary-description","jobs-details__main-content"])
    about_company_org = find_by_class(driver, "jobs-company__box")
    scroll_to_view(driver, about_company_org)
    about_company_org = about_company_org.text
    about_company = about_company_org.lower()
    skip_checking = False
    for word in about_company_good_words:
        if word.lower() in about_company:
            print_lg(f'Found the word "{word}". So, skipped checking for blacklist words.')
            skip_checking = True
            break
    if not skip_checking:
        for word in about_company_bad_words: 
            if word.lower() in about_company: 
                rejected_jobs.add(job_id)
                blacklisted_companies.add(company)
                raise ValueError(f'\n"{about_company_org}"\n\nContains "{word}".')
    buffer(click_gap)
    scroll_to_view(driver, jobs_top_card)
    return rejected_jobs, blacklisted_companies, jobs_top_card



# Function to extract years of experience required from About Job
def extract_years_of_experience(text: str) -> int:
    # Extract all patterns: '10+ years', '5 years', '3-5 years', '5-y experience min', 'min. 5 years', etc.
    matches = list(re.findall(app_state.patterns.re_experience, text))
    matches += list(re.findall(app_state.patterns.re_experience_abbrev, text))
    matches += list(re.findall(app_state.patterns.re_experience_min, text))
    if len(matches) == 0:
        print_lg(f'\n{text}\n\nCouldn\'t find experience requirement in About the Job!')
        return 0
    filtered = [int(match) for match in matches if int(match) <= 12]
    if not filtered:
        print_lg("All experience matches exceeded 12 years cap, defaulting to 0")
        return 0
    return max(filtered)



def get_job_description(
) -> tuple[
    str | Literal['Unknown'],
    int | Literal['Unknown'],
    bool,
    str | None,
    str | None
    ]:
    '''
    # Job Description
    Function to extract job description from About the Job.
    ### Returns:
    - `jobDescription: str | 'Unknown'`
    - `experience_required: int | 'Unknown'`
    - `skip: bool`
    - `skipReason: str | None`
    - `skipMessage: str | None`
    '''
    jobDescription = "Unknown"
    experience_required = "Unknown"
    skip = False
    skipReason = None
    skipMessage = None
    try:
        found_masters = 0
        jobDescription = find_by_class(driver, "jobs-box__html-content").text
        jobDescriptionLow = jobDescription.lower()
        for word in bad_words:
            if word.lower() in jobDescriptionLow:
                skipMessage = f'\n{jobDescription}\n\nContains bad word "{word}". Skipping this job!\n'
                skipReason = "Found a Bad Word in About Job"
                skip = True
                break
        if not skip and security_clearance == False and ('polygraph' in jobDescriptionLow or 'clearance' in jobDescriptionLow or 'secret' in jobDescriptionLow):
            skipMessage = f'\n{jobDescription}\n\nFound "Clearance" or "Polygraph". Skipping this job!\n'
            skipReason = "Asking for Security clearance"
            skip = True
        if not skip:
            if did_masters and 'master' in jobDescriptionLow:
                print_lg(f'Found the word "master" in \n{jobDescription}')
                found_masters = 2
            experience_required = extract_years_of_experience(jobDescription)
            if current_experience > -1 and experience_required > current_experience + found_masters:
                skipMessage = f'\n{jobDescription}\n\nExperience required {experience_required} > Current Experience {current_experience + found_masters}. Skipping this job!\n'
                skipReason = "Required experience is high"
                skip = True
    except Exception as e:
        if jobDescription == "Unknown":
            print_lg("Unable to extract job description!")
        else:
            experience_required = "Error in extraction"
            print_lg("Unable to extract years of experience required!")
    return jobDescription, experience_required, skip, skipReason, skipMessage
        


# Function to select the correct resume already uploaded on LinkedIn
def upload_resume(modal: WebElement, resume: str) -> tuple[bool, str]:
    """
    In noul flux NU mai uploadam fisiere locale in LinkedIn.
    Toate CV-urile sunt deja incarcate in profil, iar fisierele de pe LinkedIn
    au exact aceleasi nume ca fisierele locale din `all resumes/cv`.

    Aceasta functie:
    - primeste `resume` (path local sau nume de fisier),
    - extrage numele fisierului,
    - cauta in modalul Easy Apply optiunea care afiseaza acest nume
      (lista de CV-uri deja urcate) si o selecteaza.

    Daca nu gaseste un match sigur, NU incearca niciun upload de fisier si
    lasa LinkedIn sa foloseasca "Previous resume".
    """
    try:
        target_name = os.path.basename(resume).strip()
        if not target_name:
            print_lg("⚠️ upload_resume called with empty resume name, keeping previous resume on LinkedIn.")
            return False, "Previous resume"

        print_lg(f'🔍 Trying to select existing LinkedIn resume: "{target_name}"')

        # 1. Incearca sa deschida dropdown-ul / sectiunea de CV, daca exista
        try:
            resume_triggers = modal.find_elements(
                By.XPATH,
                ".//button[contains(@aria-label, 'Resume') or "
                "contains(translate(normalize-space(.), 'RESUMECV', 'resumecv'), 'resume')]"
            )
            for btn in resume_triggers:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        buffer(click_gap)
                        break
                except Exception:
                    continue
        except Exception:
            # Daca nu exista un astfel de buton, continuam — lista poate fi deja vizibila.
            pass

        # 2. Cauta elementul care contine numele complet de fisier
        #    si urca la un ancestor "clickable" (button / label / [role=radio]).
        xpath = (
            ".//*[not(self::input or self::textarea)]"
            f"[contains(normalize-space(.), '{target_name}')]"
        )
        candidates = modal.find_elements(By.XPATH, xpath)

        if not candidates:
            print_lg(f'⚠️ No DOM elements found containing resume name "{target_name}". Using previous resume on LinkedIn.')
            return False, "Previous resume"

        for el in candidates:
            try:
                if not el.is_displayed():
                    continue

                clickable = el
                try:
                    clickable = el.find_element(
                        By.XPATH,
                        "ancestor-or-self::button | ancestor-or-self::*[@role='radio'] | ancestor-or-self::label"
                    )
                except Exception:
                    clickable = el

                if not clickable.is_displayed() or not clickable.is_enabled():
                    continue

                clickable.click()
                print_lg(f'📄 Selected existing LinkedIn resume: {target_name}')
                return True, target_name
            except Exception as click_err:
                print_lg(f"⚠️ Failed to click candidate for resume '{target_name}': {click_err}")
                continue

        # 3. Daca nu am gasit nicio optiune cu acel nume, nu facem upload si
        # ramane "Previous resume".
        print_lg(f'⚠️ Could not find a matching uploaded resume for "{target_name}". Using previous resume on LinkedIn.')
        return False, "Previous resume"

    except Exception as e:
        print_lg(f"⚠️ Error while selecting existing LinkedIn resume: {e}")
        return False, "Previous resume"

# Function to answer common questions for Easy Apply
def answer_common_questions(label: str, answer: str) -> str:
    label_lower = label.lower()

    # Sponsorship / visa questions (Yes/No)
    if 'sponsorship' in label_lower or 'visa' in label_lower:
        return require_visa

    # Language proficiency (radio buttons)
    # Examples from attached forms:
    # "What is your proficiency in Romanian?"
    # "What is your proficiency in English?"
    if 'proficiency in romanian' in label_lower:
        # Match exact visible option text as in the form
        return 'Native/ Bilingual Proficiency'
    if 'proficiency in english' in label_lower:
        return 'Full Professional Proficiency'

    return answer


##> ------ Enhanced by AI Audit - Numeric Field Helpers ------
def extract_number_from_text(text: str) -> str:
    '''
    Extract the first integer number from a text.
    Example: "17 years in relevant field" → "17"
    Example: "I have 5+ years of experience" → "5"
    '''
    import re
    # Look for the first number in the text
    match = re.search(r'\d+', str(text))
    if match:
        return match.group(0)
    return ""

def detect_numeric_field_requirements(field_element, question_label: str = "") -> dict:
    '''
    Detect whether a field expects numeric input and infer basic bounds.
    Returns a dict with 'is_numeric', 'min', 'max', 'is_decimal'.
    '''
    try:
        # 1. PROACTIVE: check question text for numeric indicators (before validation)
        if question_label:
            label_lower = question_label.lower()
            # Keywords that indicate numeric questions
            numeric_keywords = [
                'how many years', 'how many months', 'how many',
                'number of years', 'years of experience',
                'años de experiencia', 'anni di esperienza',  # Spanish, Italian
                'jahre erfahrung',  # German
            ]
            
            if any(kw in label_lower for kw in numeric_keywords):
                # The question clearly expects a number → use a generic 0–99 range for years of experience
                return {
                    'is_numeric': True,
                    'min': 0,
                    'max': 99,
                    'is_decimal': False
                }
            
            # Detection for "notice period" style fields that may require a number,
            # even when the question wording allows free text.
            notice_period_keywords = [
                'notice period',
                'notice',
                'available to start',
                'when can you start',
                'start date',
                'availability',
                'notice days',
                'days of notice',
            ]
            if any(kw in label_lower for kw in notice_period_keywords):
                # For notice/availability we always use an integer number of days
                # (many forms accept values like 14 / 30 more reliably than fractions).
                return {
                    'is_numeric': True,
                    'min': 0,
                    'max': 365,
                    'is_decimal': False,
                }
        
        # 2. Check for validation messages in the parent element (after validation)
        try:
            parent = field_element.find_element(By.XPATH, "./..")
            validation_text = parent.text.lower()
            
            # Detect messages that request a "decimal number" or "number larger than 0.0"
            if 'decimal number' in validation_text or 'number larger than' in validation_text:
                import re
                # Extract range pentru numere zecimale
                decimal_match = re.search(r'larger than\s+([\d.]+)', validation_text)
                min_decimal = float(decimal_match.group(1)) if decimal_match else 0.0
                
                return {
                    'is_numeric': True,
                    'min': 0,
                    'max': 999,
                    'is_decimal': True,
                    'min_decimal': min_decimal
                }
            
            # Look for messages such as "Enter a whole number between X and Y"
            if 'whole number' in validation_text or 'number between' in validation_text:
                import re
                # Extract range: "between 0 and 99" sau "0-99"
                range_match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', validation_text)
                if not range_match:
                    range_match = re.search(r'(\d+)\s*-\s*(\d+)', validation_text)
                
                if range_match:
                    return {
                        'is_numeric': True,
                        'min': int(range_match.group(1)),
                        'max': int(range_match.group(2)),
                        'is_decimal': False
                    }
                return {'is_numeric': True, 'min': 0, 'max': 999, 'is_decimal': False}
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
            pass
        
        input_type = field_element.get_attribute("type")
        input_mode = field_element.get_attribute("inputmode")
        
        if input_type == "number" or input_mode == "numeric":
            min_val = field_element.get_attribute("min")
            max_val = field_element.get_attribute("max")
            step = field_element.get_attribute("step")
            is_decimal = step and '.' in str(step)
            
            return {
                'is_numeric': True,
                'min': int(min_val) if min_val and min_val.replace('.', '').replace('-', '').isdigit() else 0,
                'max': int(max_val) if max_val and max_val.replace('.', '').isdigit() else 999,
                'is_decimal': is_decimal
            }
    except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
        pass
    
    return {'is_numeric': False, 'min': None, 'max': None, 'is_decimal': False}

def sanitize_numeric_answer(answer: str, min_val: int = 0, max_val: int = 999, is_decimal: bool = False, question_label: str = "") -> str:
    '''
    Extract a number from the answer and clamp it within the given limits.
    Also supports conversion for notice periods (for example: "2 weeks" → 0.5 or 2).
    '''
    import re
    
    # For notice-period style fields, convert the text to a numeric value
    if question_label and ('notice' in question_label.lower() or 'available to start' in question_label.lower()):
        answer_lower = str(answer).lower()
        
        # Detect "weeks" and convert to months (decimal).
        # Example: "2 weeks" → 0.5 months, "4 weeks" → 1 month.
        weeks_match = re.search(r'(\d+)\s*(?:week)', answer_lower)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            months = weeks / 4.0  # Convert weeks to months (decimal)
            if is_decimal:
                return f"{months:.2f}".rstrip('0').rstrip('.')  # Remove trailing zeros
            else:
                return str(int(months) if months >= 1 else 0)
        
        # Detect "months" and convert appropriately
        months_match = re.search(r'(\d+)\s*(?:month)', answer_lower)
        if months_match:
            months = int(months_match.group(1))
            if is_decimal:
                return f"{months:.1f}".rstrip('0').rstrip('.')
            else:
                return str(months)
        
        # Detect "immediately" or "available now" → 0
        if 'immediately' in answer_lower or 'available now' in answer_lower or 'now' in answer_lower:
            return "0" if not is_decimal else "0.0"
    
    # Extract the numeric portion (supports decimals)
    if is_decimal:
        # Look for a decimal number
        decimal_match = re.search(r'(\d+\.?\d*)', str(answer))
        if decimal_match:
            number_str = decimal_match.group(1)
        else:
            # Fallback: look for an integer
            number_str = extract_number_from_text(answer)
    else:
        # Look only for an integer
        number_str = extract_number_from_text(answer)
    
    if not number_str:
        # If no number is found, fall back to the configured years_of_experience
        number_str = extract_number_from_text(years_of_experience)
    
    if not number_str:
        # Final fallback: use the middle of the allowed range
        if is_decimal:
            return f"{(min_val + max_val) / 2:.1f}".rstrip('0').rstrip('.')
        else:
            return str((min_val + max_val) // 2)
    
    # Validate and clamp to limits
    try:
        if is_decimal:
            number = float(number_str)
            min_decimal = float(min_val)
            max_decimal = float(max_val)
            
            if number < min_decimal:
                return f"{min_decimal:.1f}".rstrip('0').rstrip('.')
            elif number > max_decimal:
                return f"{max_decimal:.1f}".rstrip('0').rstrip('.')
            else:
                return f"{number:.2f}".rstrip('0').rstrip('.')  # Format with at most 2 decimals
        else:
            number = int(number_str)
            if number < min_val:
                return str(min_val)
            elif number > max_val:
                return str(max_val)
            else:
                return str(number)
    except ValueError:
        # If conversion fails, return the default value
        if is_decimal:
            return f"{(min_val + max_val) / 2:.1f}".rstrip('0').rstrip('.')
        else:
            return str((min_val + max_val) // 2)
##<

##> ------ Enhanced by AI Audit - Text Answer Fallback Function ------
def _get_text_answer_fallback(label: str) -> str:
    '''
    Fallback logic for text answers when smart matching not available.
    '''
    answer = ""
    
    # Before "years" – exclude "grade point average" (contains "grade", not "years" of experience)
    if ('grade' in label or 'gpa' in label or 'point average' in label) and 'experience' not in label:
        try:
            from config.questions import grade_point_average
            answer = str(grade_point_average)
        except ImportError:
            answer = "8.5"
    elif 'language' in label or 'lingua' in label or 'limb' in label:
        try:
            from config.questions import languages_spoken
            answer = languages_spoken or "English, Romanian"
        except ImportError:
            answer = "English, Romanian"
    elif 'date of birth' in label or 'birth' in label or 'mm.dd.yyyy' in label or 'birthday' in label:
        try:
            from config.questions import date_of_birth
            answer = date_of_birth or DateConstants.DEFAULT_DATE_OF_BIRTH
        except ImportError:
            answer = DateConstants.DEFAULT_DATE_OF_BIRTH
    elif 'university' in label and ('name' in label or 'insert' in label or 'not included' in label):
        try:
            from config.questions import university_name
            answer = university_name or "N/A"
        except ImportError:
            answer = "N/A"
    elif 'experience' in label or 'years' in label: 
        answer = years_of_experience
    elif 'phone' in label or 'mobile' in label: 
        answer = phone_number
    elif 'street' in label: 
        answer = street
    elif 'city' in label or 'location' in label or 'address' in label:
        answer = current_city if current_city else "Bucharest, Romania"
    elif 'signature' in label: 
        answer = full_name
    elif 'name' in label:
        if 'full' in label: answer = full_name
        elif 'first' in label and 'last' not in label: answer = first_name
        elif 'middle' in label and 'last' not in label: answer = middle_name
        elif 'last' in label and 'first' not in label: answer = last_name
        elif 'employer' in label: answer = recent_employer
        else: answer = full_name
    elif 'notice' in label:
        if 'month' in label: answer = notice_period_months
        elif 'week' in label: answer = notice_period_weeks
        else: answer = notice_period
    elif 'salary' in label or 'compensation' in label or 'ctc' in label or 'pay' in label:
        if 'current' in label or 'present' in label:
            if 'month' in label: answer = current_ctc_monthly
            elif 'lakh' in label: answer = current_ctc_lakhs
            else: answer = current_ctc_str
        else:
            if 'month' in label: answer = desired_salary_monthly
            elif 'lakh' in label: answer = desired_salary_lakhs
            else: answer = desired_salary_str
    elif 'linkedin' in label: answer = linkedIn
    elif 'website' in label or 'blog' in label or 'portfolio' in label or 'link' in label: answer = website
    elif 'scale of 1-10' in label: answer = confidence_level
    elif 'headline' in label: answer = linkedin_headline
    elif ('hear' in label or 'come across' in label) and 'this' in label and ('job' in label or 'position' in label): answer = "LinkedIn"
    elif 'state' in label or 'province' in label: answer = state
    elif 'zip' in label or 'postal' in label or 'code' in label: answer = zipcode
    elif 'country' in label: answer = country

    return answer if answer else ""


# Function to answer the questions for Easy Apply
def answer_questions(modal: WebElement, questions_list: set, work_location: str, job_description: str | None = None ) -> set:
    # Get all questions from the page
     
    all_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")

    for Question in all_questions:
        # Check if it's a select Question
        select = try_xp(Question, ".//select", False)
        if select:
            label_org = "Unknown"
            try:
                label = Question.find_element(By.TAG_NAME, "label")
                label_org = label.find_element(By.TAG_NAME, "span").text
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            answer = 'Yes'
            label = label_org.lower()
            select = Select(select)
            selected_option = select.first_selected_option.text.strip()
            optionsText = []
            options = '"List of phone country codes"'
            if label != "phone country code":
                optionsText = [option.text for option in select.options]
                options = "".join([f' "{option}",' for option in optionsText])
            prev_answer = selected_option
            # Detect implicit "Select an option" style placeholders in multiple languages
            default_placeholders = {
                "select an option",
                "select",
                "choose",
                "option auswählen",   # German
                "bitte auswählen",
                "auswählen",
            }
            is_default_selection = (
                not selected_option
                or selected_option.strip().lower() in default_placeholders
            )
            if overwrite_previous_answers or is_default_selection:
                ##> ------ Enhanced by AI Audit - Intelligent Yes/No Detection ------
                # NEW: Detect if this is a Yes/No dropdown and use intelligent answering
                is_yes_no_question = detect_yes_no_options(optionsText) if detect_yes_no_options else False
                
                if is_yes_no_question and intelligent_yes_no_answer:
                    # Use intelligent strategy-based answering for Yes/No questions
                    answer = intelligent_yes_no_answer(label, optionsText)
                    print_lg(f"🎯 Intelligent Yes/No: '{label_org}' → {answer}")
                ##<
                ##> ------ Enhanced by AI Audit - Smart Answer Matching ------
                # Use extended keywords for better matching
                elif smart_match_question:
                    answer_type, confidence = smart_match_question(label)
                    
                    if confidence == 'high':
                        answer = get_contextual_answer(label, answer_type, 'select')
                    else:
                        # Fallback to old logic
                        if 'email' in label or 'phone' in label: 
                            answer = prev_answer
                        elif 'gender' in label or 'sex' in label: 
                            answer = gender
                        elif 'disability' in label: 
                            answer = disability_status
                        elif 'proficiency' in label: 
                            answer = 'Professional'
                        else: 
                            answer = answer_common_questions(label, answer)
                else:
                    # Fallback to original logic if smart_answers not available
                    if 'email' in label or 'phone' in label: 
                        answer = prev_answer
                    elif 'gender' in label or 'sex' in label: 
                        answer = gender
                    elif 'disability' in label: 
                        answer = disability_status
                    else: 
                        answer = answer_common_questions(label,answer)
                ##<
                ##> ------ Enhanced by AI Audit - Smart Option Matching ------
                # Try smart matching first (for non-Yes/No questions)
                if match_select_option and optionsText:
                    answer = match_select_option(label, optionsText, answer)
                ##<
                
                try: 
                    select.select_by_visible_text(answer)
                except NoSuchElementException as e:
                    # Define similar phrases for common answers
                    possible_answer_phrases = []
                    if answer == 'Decline':
                        possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                    elif 'yes' in answer.lower():
                        possible_answer_phrases = ["Yes", "Agree", "I do", "I have"]
                    elif 'no' in answer.lower():
                        possible_answer_phrases = ["No", "Disagree", "I don't", "I do not"]
                    else:
                        # Try partial matching for any answer
                        possible_answer_phrases = [answer]
                        # Add lowercase and uppercase variants
                        possible_answer_phrases.append(answer.lower())
                        possible_answer_phrases.append(answer.upper())
                        # Try without special characters
                        possible_answer_phrases.append(''.join(c for c in answer if c.isalnum()))
                    ##<
                    foundOption = False
                    for phrase in possible_answer_phrases:
                        for option in optionsText:
                            # Check if phrase is in option or option is in phrase (bidirectional matching)
                            if phrase.lower() in option.lower() or option.lower() in phrase.lower():
                                select.select_by_visible_text(option)
                                answer = option
                                foundOption = True
                                break
                    if not foundOption and ask_llm_for_field and job_description and optionsText:
                        llm_ans = ask_llm_for_field(label_org, "select", options=optionsText, job_description=job_description)
                        if llm_ans:
                            for opt in optionsText:
                                if opt.strip().lower() == llm_ans.strip().lower() or llm_ans.strip().lower() in opt.strip().lower():
                                    select.select_by_visible_text(opt)
                                    answer = opt
                                    foundOption = True
                                    print_lg(f'🤖 LLM answered select: "{label_org}" → {opt}')
                                    break
                    if not foundOption:
                        print_lg(f'⚠️ RANDOM ANSWER: Failed to match "{answer}" for question "{label_org}", selecting random option!')
                        select.select_by_index(randint(1, len(select.options)-1))
                        answer = select.first_selected_option.text
                        app_state.randomly_answered_questions.add((f'{label_org} [ {options} ]',"select"))
            questions_list.add((f'{label_org} [ {options} ]', answer, "select", prev_answer))
            continue
        
        # Check if it's a radio Question
        radio = try_xp(Question, './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', False)
        if radio:
            prev_answer = None
            label = try_xp(radio, './/span[@data-test-form-builder-radio-button-form-component__title]', False)
            try: label = find_by_class(label, "visually-hidden", 2.0)
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            label_org = label.text if label else "Unknown"
            answer = 'Yes'
            label = label_org.lower()

            label_org += ' [ '
            options = radio.find_elements(By.TAG_NAME, 'input')
            options_labels = []
            
            for option in options:
                id = option.get_attribute("id")
                option_label = try_xp(radio, f'.//label[@for="{id}"]', False)
                options_labels.append( f'"{option_label.text if option_label else "Unknown"}"<{option.get_attribute("value")}>' ) # Saving option as "label <value>"
                if option.is_selected(): prev_answer = options_labels[-1]
                label_org += f' {options_labels[-1]},'

            if overwrite_previous_answers or prev_answer is None:
                ##> ------ Enhanced by AI Audit - Smart Answer Matching ------
                # Use extended keywords for better matching
                if smart_match_question:
                    answer_type, confidence = smart_match_question(label)
                    
                    if confidence == 'high':
                        answer = get_contextual_answer(label, answer_type, 'radio')
                    else:
                        # Fallback to specific checks
                        if 'citizenship' in label or 'employment eligibility' in label: 
                            answer = us_citizenship
                        elif 'veteran' in label or 'protected' in label: 
                            answer = veteran_status
                        elif 'disability' in label or 'handicapped' in label: 
                            answer = disability_status
                        else: 
                            answer = answer_common_questions(label, answer)
                else:
                    # Original logic
                    if 'citizenship' in label: answer = us_citizenship
                    elif 'veteran' in label: answer = veteran_status
                    elif 'disability' in label: answer = disability_status
                    else: answer = answer_common_questions(label,answer)
                ##<
                foundOption = try_xp(radio, f".//label[normalize-space()='{answer}']", False)
                if foundOption: 
                    actions.move_to_element(foundOption).click().perform()
                else:
                    if ask_llm_for_field and job_description:
                        visible_labels = [o.split('<')[0].strip().strip('"') for o in options_labels]
                        llm_ans = ask_llm_for_field(label_org, "radio", options=visible_labels, job_description=job_description)
                        if llm_ans:
                            for i, lbl in enumerate(visible_labels):
                                if lbl.strip().lower() == llm_ans.strip().lower() or llm_ans.strip().lower() in lbl.strip().lower():
                                    foundOption = options[i]
                                    actions.move_to_element(foundOption).click().perform()
                                    answer = options_labels[i]
                                    print_lg(f'🤖 LLM answered radio: "{label_org}" → {lbl}')
                                    break
                    if not foundOption:
                        possible_answer_phrases = ["Decline", "not wish", "don't wish", "Prefer not", "not want"] if answer == 'Decline' else [answer]
                        ele = options[0]
                        answer = options_labels[0]
                        for phrase in possible_answer_phrases:
                            for i, option_label in enumerate(options_labels):
                                if phrase in option_label:
                                    foundOption = options[i]
                                    ele = foundOption
                                    answer = f'Decline ({option_label})' if len(possible_answer_phrases) > 1 else option_label
                                    break
                            if foundOption: break
                        actions.move_to_element(ele).click().perform()
                        if not foundOption: app_state.randomly_answered_questions.add((f'{label_org} ]',"radio"))
            else: answer = prev_answer
            questions_list.add((f"{label_org} ]", answer, "radio", prev_answer))
            buffer(randint(1, 3))  # Pause after radio button selection to simulate real user
            continue
        
        # Check for large text areas (ex. Message to employer, cover letter, motivation)
        textarea = try_xp(Question, ".//textarea", False)
        if textarea:
            label_org = "Unknown"
            try:
                label_el = Question.find_element(By.TAG_NAME, "label")
                spans = label_el.find_elements(By.TAG_NAME, "span")
                if spans:
                    label_org = spans[0].text.strip() or label_el.text.strip() or "Unknown"
                else:
                    label_org = label_el.text.strip() or "Unknown"
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass

            current_value = textarea.get_attribute("value") or ""
            label_lower = label_org.lower()

            should_fill = overwrite_previous_answers or not current_value.strip()
            is_message_field = any(
                kw in label_lower
                for kw in ("message", "motiv", "motivation", "cover letter", "top choice")
            )

            if should_fill and is_message_field:
                answer_text = None

                # 1) Try LLM if available, cu context de job description
                if ask_llm_for_field and job_description:
                    try:
                        answer_text = ask_llm_for_field(
                            label_org,
                            "text",
                            options=None,
                            job_description=job_description,
                        )
                        if answer_text:
                            print_lg(f'🤖 LLM filled textarea: "{label_org}"')
                    except Exception:
                        answer_text = None

                # 2) Static professional fallback if LLM not available / failed
                if not answer_text:
                    answer_text = (
                        "I am highly interested in this opportunity and I believe my background and skills "
                        "are a strong match for the role. I would welcome the chance to further discuss how "
                        "I can contribute to your team and projects."
                    )

                try:
                    textarea.clear()
                except Exception:
                    pass
                try:
                    textarea.send_keys(answer_text)
                    questions_list.add((label_org, answer_text, "text", current_value))
                except Exception:
                    print_lg(f'⚠️ Failed to fill textarea for "{label_org}"')

            continue
        
        # Check if it's a text question
        text = try_xp(Question, ".//input[@type='text']", False)
        if text: 
            do_actions = False
            label = try_xp(Question, ".//label[@for]", False)
            try: label = label.find_element(By.CLASS_NAME,'visually-hidden')
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass
            label_org = label.text if label else "Unknown"
            answer = "" # years_of_experience
            label = label_org.lower()

            prev_answer = text.get_attribute("value")
            if not prev_answer or overwrite_previous_answers:
                ##> ------ JobMatcher (Option A) + Smart Text Matching ------
                answer = ""
                if job_matcher and smart_text_answer:
                    answer = smart_text_answer(label_org, job_matcher)
                    if answer and ('city' in label or 'location' in label):
                        do_actions = True
                if answer is None or answer == "":
                    if smart_match_question:
                        answer_type, confidence = smart_match_question(label)
                        if confidence == 'high':
                            answer = get_contextual_answer(label, answer_type, 'text')
                            if answer_type == 'city':
                                do_actions = True
                        else:
                            if ask_llm_for_field and job_description:
                                llm_ans = ask_llm_for_field(label_org, "text", job_description=job_description)
                                if llm_ans:
                                    answer = llm_ans
                                    print_lg(f'🤖 LLM answered text: "{label_org}" → {llm_ans[:50]}...')
                            if not answer:
                                answer = _get_text_answer_fallback(label)
                    else:
                        if ask_llm_for_field and job_description:
                            llm_ans = ask_llm_for_field(label_org, "text", job_description=job_description)
                            if llm_ans:
                                answer = llm_ans
                                print_lg(f'🤖 LLM answered text: "{label_org}" → {llm_ans[:50]}...')
                        if not answer:
                            answer = _get_text_answer_fallback(label)
                ##<
                # CRITICAL: answer can be None from smart_text_answer/get_contextual_answer
                if answer is None or answer == "":
                    if answer == "":
                        app_state.randomly_answered_questions.add((label_org, "text"))
                    if ask_llm_for_field and job_description:
                        llm_ans = ask_llm_for_field(label_org, "text", job_description=job_description)
                        if llm_ans:
                            answer = llm_ans
                            print_lg(f'🤖 LLM answered text: "{label_org}" → {llm_ans[:50]}...')
                    if not answer:
                        fb = _get_text_answer_fallback(label)
                        answer = fb if fb else years_of_experience
                ##<
                
                ##> ------ Enhanced by AI Audit - Numeric Field Detection ------
                # Check if this is a numeric-only field (pass question label for proactive detection)
                numeric_requirements = detect_numeric_field_requirements(text, label_org)
                
                if numeric_requirements['is_numeric']:
                    # Extract number from answer and validate range
                    original_answer = answer
                    answer = sanitize_numeric_answer(
                        answer,
                        numeric_requirements['min'],
                        numeric_requirements['max'],
                        numeric_requirements.get('is_decimal', False),
                        label_org,
                    )
                    print_lg(f'🔢 Numeric field detected: "{label_org}" | Range: {numeric_requirements["min"]}-{numeric_requirements["max"]} | Decimal: {numeric_requirements.get("is_decimal", False)} | Answer: {original_answer} → {answer}')
                ##<
                
                ##> ------ Enhanced by AI Audit - Smart Field Validation & Retry ------
                # Check maxlength attribute and truncate answer if needed
                max_length = text.get_attribute("maxlength")
                if max_length and max_length.isdigit():
                    max_len = int(max_length)
                    if len(str(answer)) > max_len:
                        answer = str(answer)[:max_len]
                        print_lg(f'Text truncated to {max_len} characters for field: {label_org}')
                
                # Try to input the answer with validation check
                # CRITICAL: send_keys fails with 'NoneType' object is not iterable if answer is None
                answer = answer if answer is not None else ""
                try:
                    def _select_city_autocomplete(input_ele, typed: str = "Bucharest", pick: str = "Bucharest, Romania") -> bool:
                        """
                        LinkedIn 'Location (city)' is an autocomplete: you must type and select a suggestion.
                        Returns True if a suggestion was selected, otherwise False.
                        """
                        try:
                            input_ele.clear()
                        except Exception:
                            pass
                        input_ele.send_keys(typed)

                        # Wait for the suggestions dropdown and pick the exact match when available
                        for _ in range(3):
                            try:
                                sleep(0.6)
                                option = driver.find_element(
                                    By.XPATH,
                                    f"//div[@role='listbox']//div[@role='option'][.//*[normalize-space()='{pick}'] or normalize-space(.)='{pick}']"
                                    f" | //div[@role='listbox']//li[.//*[normalize-space()='{pick}'] or normalize-space(.)='{pick}']"
                                )
                                try:
                                    actions.move_to_element(option).click().perform()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", option)
                                return True
                            except Exception:
                                # Fallback: if no exact match is found, try keyboard navigation
                                try:
                                    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
                                    return True
                                except Exception:
                                    continue
                        return False

                    # Special-case: Location (city) / city fields that need autocomplete selection
                    if ('location (city)' in label) or (('location' in label or 'city' in label) and do_actions):
                        # Example behaviour: type "Bucharest" and select "Bucharest, Romania"
                        if not _select_city_autocomplete(text):
                            # If the autocomplete did not appear, fall back to simple text input
                            text.clear()
                            text.send_keys("Bucharest, Romania")
                    else:
                        text.clear()
                        text.send_keys(str(answer))
                    
                    # Verify if validation error appears (for all text fields)
                    sleep(0.5)  # Wait for validation
                    
                    try:
                        parent = text.find_element(By.XPATH, "./..")
                        error_elements = parent.find_elements(By.XPATH, ".//*[contains(@class, 'error') or contains(@class, 'invalid') or contains(@class, 'validation')]")
                        
                        for error_msg in error_elements:
                            if error_msg.is_displayed():
                                error_text = error_msg.text.lower()
                                
                                # Detect validation errors that require a "decimal number" or "number larger than 0.0"
                                if 'decimal number' in error_text or 'number larger than' in error_text or 'enter a number' in error_text:
                                    print_lg(f'⚠️ Field "{label_org}" requires numeric input. Error: {error_msg.text}')
                                    
                                    # Re-detect numeric field requirements now that we have the error text
                                    numeric_requirements = detect_numeric_field_requirements(text, label_org)
                                    
                                    if not numeric_requirements['is_numeric']:
                                        # Force the field to be treated as numeric if the error explicitly demands a number
                                        numeric_requirements = {
                                            'is_numeric': True,
                                            'min': 0,
                                            'max': 999,
                                            'is_decimal': 'decimal' in error_text or 'larger than' in error_text
                                        }
                                    
                                    # Re-convert the answer into a numeric value
                                    original_answer = answer
                                    answer = sanitize_numeric_answer(
                                        original_answer,
                                        numeric_requirements['min'],
                                        numeric_requirements['max'],
                                        numeric_requirements.get('is_decimal', False),
                                        label_org
                                    )
                                    
                                    # Retry with the converted numeric answer
                                    text.clear()
                                    text.send_keys(str(answer))
                                    sleep(0.5)
                                    
                                    # Check again whether the validation error has disappeared
                                    try:
                                        error_check = parent.find_element(By.XPATH, ".//*[contains(@class, 'error') or contains(@class, 'invalid')]")
                                        if error_check.is_displayed():
                                            print_lg(f'⚠️ Still showing error after numeric conversion. Original: "{original_answer}" → Numeric: "{answer}"')
                                        else:
                                            print_lg(f'✅ Successfully converted to numeric: "{original_answer}" → "{answer}"')
                                    except (NoSuchElementException, TimeoutException):
                                        # No error found, numeric conversion worked
                                        print_lg(f'✅ Successfully converted to numeric: "{original_answer}" → "{answer}"')
                                    
                                    break  # We have processed this error, no need to inspect additional ones
                                
                                # For salary fields, verify if validation error appears
                                elif 'salary' in label.lower() or 'compensation' in label.lower():
                                    # Validation failed, try fallback
                                    print_lg(f'⚠️ Salary validation failed with "{answer}", trying fallback...')
                                    
                                    # Clear and try with minimum value only
                                    text.clear()
                                    fallback_answer = desired_salary_str  # Just the minimum
                                    text.send_keys(fallback_answer)
                                    sleep(0.5)
                                    
                                    # Check again
                                    try:
                                        error_msg2 = parent.find_element(By.XPATH, ".//*[contains(@class, 'error') or contains(@class, 'invalid')]")
                                        if error_msg2 and error_msg2.is_displayed():
                                            # Still failing, leave empty
                                            print_lg(f'⚠️ Fallback also failed, leaving salary field empty')
                                            text.clear()
                                            answer = ""
                                        else:
                                            answer = fallback_answer
                                            print_lg(f'✅ Fallback successful with: {fallback_answer}')
                                    except (NoSuchElementException, TimeoutException):
                                        # No error found, fallback worked
                                        answer = fallback_answer
                                        print_lg(f'✅ Fallback successful with: {fallback_answer}')
                                    break
                    except (NoSuchElementException, TimeoutException):
                        # No validation error element found, input is good
                        pass
                    
                    if do_actions:
                        sleep(2)
                        actions.send_keys(Keys.ARROW_DOWN)
                        actions.send_keys(Keys.ENTER).perform()
                        
                except Exception as e:
                    print_lg(f'⚠️ Failed to input text for "{label_org}": {e}')
                    # Continue anyway
                ##<
                
            questions_list.add((label, text.get_attribute("value"), "text", prev_answer))
            buffer(randint(2, 5))  # Pause after text input to simulate real user typing
            continue

        # Check if it's a textarea question (multi-line text, often required)
        text_area = try_xp(Question, ".//textarea", False)
        if text_area:
            do_actions = False
            label = try_xp(Question, ".//label[@for]", False)
            try:
                # Prefer visually-hidden span if present (similar la input text)
                label = label.find_element(By.CLASS_NAME, "visually-hidden") if label else label
            except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                pass

            # Some external ATS systems integrated into Easy Apply (for example Workable, SmartRecruiters)
            # do not put the classic label in a <label> tag, but use aria-label or placeholder instead.
            # To avoid leaving "Headline" / "Summary" fields empty, combine all available text sources.
            label_text_parts = []
            if label and label.text:
                label_text_parts.append(label.text)
            try:
                placeholder = text_area.get_attribute("placeholder") or ""
                if placeholder:
                    label_text_parts.append(placeholder)
            except Exception:
                placeholder = ""
            try:
                aria_label = text_area.get_attribute("aria-label") or ""
                if aria_label:
                    label_text_parts.append(aria_label)
            except Exception:
                aria_label = ""

            label_org = " ".join(label_text_parts).strip() or "Unknown"
            label = label_org.lower()
            answer = ""
            prev_answer = text_area.get_attribute("value")

            if not prev_answer or overwrite_previous_answers:
                # 1) First try well-known special fields
                #    (including Workable/ATS fields that may have "Headline" or "Summary" in label/placeholder)
                if 'headline' in label:
                    answer = linkedin_headline
                elif 'summary' in label:
                    answer = linkedin_summary
                elif 'cover' in label:
                    answer = cover_letter

                # 2) If we still do not have an answer, reuse the smart-text logic from input[type=text]
                if not answer:
                    # JobMatcher / Smart text answers
                    if job_matcher and smart_text_answer:
                        a = smart_text_answer(label_org, job_matcher)
                        if a:
                            answer = a

                if not answer:
                    if smart_match_question:
                        answer_type, confidence = smart_match_question(label)
                        if confidence == 'high':
                            answer = get_contextual_answer(label, answer_type, 'textarea')

                # 3) Generic fallback for free-text answers
                if not answer:
                    fb = _get_text_answer_fallback(label)
                    if fb:
                        answer = fb

                # 4) Simple heuristics for the most common items
                if not answer:
                    if 'year' in label or 'years' in label:
                        answer = str(years_of_experience)
                    elif 'country' in label or 'countries' in label:
                        answer = "Romania"

                # 5) LLM fallback for unknown fields
                if not answer and ask_llm_for_field and job_description:
                    llm_ans = ask_llm_for_field(label_org, "text", job_description=job_description)
                    if llm_ans:
                        answer = llm_ans
                        print_lg(f'🤖 LLM answered textarea: "{label_org}" → {llm_ans[:50]}...')

                # 6) Final fallback: neutral text so that required fields are not left empty
                if not answer:
                    app_state.randomly_answered_questions.add((label_org, "textarea"))
                    answer = "N/A"

            # Check maxlength attribute and truncate answer if needed
            max_length = text_area.get_attribute("maxlength")
            if max_length and max_length.isdigit():
                max_len = int(max_length)
                if len(str(answer)) > max_len:
                    answer = str(answer)[:max_len]
                    print_lg(f'Textarea truncated to {max_len} characters for field: {label_org}')

            try:
                text_area.clear()
            except Exception:
                pass
            text_area.send_keys(str(answer))

            if do_actions:
                sleep(2)
                actions.send_keys(Keys.ARROW_DOWN)
                actions.send_keys(Keys.ENTER).perform()

            questions_list.add((label, text_area.get_attribute("value"), "textarea", prev_answer))
            buffer(randint(3, 7))  # Pause after textarea input to simulate real user typing
            continue

        # Check if it's a checkbox question
        checkbox = try_xp(Question, ".//input[@type='checkbox']", False)
        if checkbox:
            label = try_xp(Question, ".//span[@class='visually-hidden']", False)
            label_org = label.text if label else "Unknown"
            label = label_org.lower()
            answer = try_xp(Question, ".//label[@for]", False)  # Sometimes multiple checkboxes are given for 1 question, Not accounted for that yet
            answer = answer.text if answer else "Unknown"
            prev_answer = checkbox.is_selected()
            checked = prev_answer
            if not prev_answer:
                try:
                    actions.move_to_element(checkbox).click().perform()
                    checked = True
                except Exception as e: 
                    print_lg("Checkbox click failed!", e)
                    pass
            questions_list.add((f'{label} ([X] {answer})', checked, "checkbox", prev_answer))
            buffer(randint(1, 2))  # Pause after checkbox selection to simulate real user
            continue


    # Select todays date
    try_xp(driver, "//button[contains(@aria-label, 'This is today')]")

    # Collect important skills
    # if 'do you have' in label and 'experience' in label and ' in ' in label -> Get word (skill) after ' in ' from label
    # if 'how many years of experience do you have in ' in label -> Get word (skill) after ' in '

    return questions_list




def external_apply(pagination_element: WebElement, job_id: str, job_link: str, resume: str, date_listed, application_link: str, screenshot_name: str) -> tuple[bool, str, int]:
    '''
    Function to open new tab and save external job application links
    '''
    if easy_apply_only:
        try:
            if "exceeded the daily application limit" in driver.find_element(By.CLASS_NAME, "artdeco-inline-feedback__message").text: app_state.daily_limit_reached = True
        except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
            pass
        print_lg("Easy apply failed I guess!")
        if pagination_element != None: return True, application_link, app_state.counters.tabs_count
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3')]"))).click() # './/button[contains(span, "Apply") and not(span[contains(@class, "disabled")])]'
        wait_span_click(driver, "Continue", 1, True, False)
        windows = driver.window_handles
        current_tabs = app_state.counters.increment_tabs()
        driver.switch_to.window(windows[-1])
        application_link = driver.current_url
        print_lg('Got the external application link "{}"'.format(application_link))
        if close_tabs and driver.current_window_handle != linkedIn_tab: driver.close()
        driver.switch_to.window(linkedIn_tab)
        return False, application_link, current_tabs
    except Exception as e:
        # print_lg(e)
        print_lg("Failed to apply!")
        failed_job(job_id, job_link, resume, date_listed, "Probably didn't find Apply button or unable to switch tabs.", e, application_link, screenshot_name)
        app_state.counters.increment_failed()
        return True, application_link, app_state.counters.tabs_count



def follow_company(modal=None) -> None:
    '''
    Function to follow or un-follow easy applied companies based on `follow_companies`
    Ensures the checkbox is UNCHECKED if follow_companies = False
    '''
    if modal is None:
        modal = driver
    try:
        follow_checkbox_input = try_xp(modal, ".//input[@id='follow-company-checkbox' and @type='checkbox']", False)
        if follow_checkbox_input:
            is_currently_checked = follow_checkbox_input.is_selected()
            if is_currently_checked != follow_companies:
                try_xp(modal, ".//label[@for='follow-company-checkbox']")
                print_lg(f'Follow company checkbox {"unchecked" if follow_companies == False else "checked"}')
    except Exception as e:
        print_lg("Failed to update follow companies checkbox!", e)


def _click_primary_easy_apply_footer_button(modal: WebElement) -> bool:
    """
    Many Easy Apply flows use different button texts (or no span text at all).
    This clicks the primary enabled footer button inside the modal (Next/Review/Submit/etc.).
    Returns True if a button was clicked.
    """
    try:
        # Prefer enabled primary button
        buttons = modal.find_elements(By.XPATH, ".//footer//button[not(@disabled)]")
        primary = []
        fallback = []
        for b in buttons:
            try:
                if not b.is_displayed() or not b.is_enabled():
                    continue
            except Exception:
                continue
            cls = (b.get_attribute("class") or "").lower()
            if "artdeco-button--primary" in cls or "primary" in cls:
                primary.append(b)
            else:
                fallback.append(b)
        candidates = primary + fallback
        for b in candidates:
            try:
                b.click()
                buffer(click_gap)
                return True
            except ElementClickInterceptedException:
                try:
                    driver.execute_script("arguments[0].click();", b)
                    buffer(click_gap)
                    return True
                except Exception:
                    continue
            except Exception:
                continue
        return False
    except Exception:
        return False
    


#< Failed attempts logging
def failed_job(job_id: str, job_link: str, resume: str, date_listed, error: str, exception: Exception, application_link: str, screenshot_name: str) -> None:
    '''
    Function to update failed jobs list in excel
    ##> ------ Enhanced by AI Audit - Using CSV Manager ------
    '''
    try:
        fieldnames = ['Job ID', 'Job Link', 'Resume Tried', 'Date listed', 'Date Tried', 'Assumed Reason', 'Stack Trace', 'External Job link', 'Screenshot Name']

        row_data = {
            'Job ID': truncate_for_csv(job_id),
            'Job Link': truncate_for_csv(job_link),
            'Resume Tried': truncate_for_csv(resume),
            'Date listed': truncate_for_csv(date_listed),
            'Date Tried': datetime.now(),
            'Assumed Reason': truncate_for_csv(error),
            'Stack Trace': truncate_for_csv(exception),
            'External Job link': truncate_for_csv(application_link),
            'Screenshot Name': truncate_for_csv(screenshot_name)
        }

        success = failed_csv_manager.append_row(row_data, fieldnames)
        if not success:
            print_lg("[WARNING] Failed to save failed job to CSV (file locked or error)")
    except Exception as e:
        print_lg(f"[WARNING] Failed to update failed jobs list: {e}")
        print_lg("Possible reasons: File is open, permission denied, or file not found")
        print_lg("Continuing without saving this failure...")
    ##<


def screenshot(driver: WebDriver, job_id: str, failedAt: str) -> str:
    '''
    Function to to take screenshot for debugging
    - Returns screenshot name as String
    '''
    screenshot_name = "{} - {} - {}.png".format( job_id, failedAt, str(datetime.now()) )
    path = logs_folder_path+f"/screenshots/{screenshot_name}".replace(":",".")
    driver.save_screenshot(path.replace("//","/"))
    return screenshot_name
#>



def submitted_jobs(job_id: str, title: str, company: str, work_location: str, work_style: str, description: str, experience_required: int | Literal['Unknown', 'Error in extraction'],
                   skills: list[str] | Literal['In Development'], hr_name: str | Literal['Unknown'], hr_link: str | Literal['Unknown'], resume: str,
                   reposted: bool, date_listed: datetime | Literal['Unknown'], date_applied:  datetime | Literal['Pending'], job_link: str, application_link: str,
                   questions_list: set | None, connect_request: Literal['In Development']) -> None:
    '''
    Function to create or update the Applied jobs CSV file, once the application is submitted successfully
    ##> ------ Enhanced by AI Audit - Using CSV Manager ------
    '''
    try:
        fieldnames = ['Job ID', 'Title', 'Company', 'Work Location', 'Work Style', 'About Job', 'Experience required', 'Skills required', 'HR Name', 'HR Link', 'Resume', 'Re-posted', 'Date Posted', 'Date Applied', 'Job Link', 'External Job link', 'Questions Found', 'Connect Request']

        row_data = {
            'Job ID': truncate_for_csv(job_id),
            'Title': truncate_for_csv(title),
            'Company': truncate_for_csv(company),
            'Work Location': truncate_for_csv(work_location),
            'Work Style': truncate_for_csv(work_style),
            'About Job': truncate_for_csv(description),
            'Experience required': truncate_for_csv(experience_required),
            'Skills required': truncate_for_csv(skills),
            'HR Name': truncate_for_csv(hr_name),
            'HR Link': truncate_for_csv(hr_link),
            'Resume': truncate_for_csv(resume),
            'Re-posted': truncate_for_csv(reposted),
            'Date Posted': truncate_for_csv(date_listed),
            'Date Applied': truncate_for_csv(date_applied),
            'Job Link': truncate_for_csv(job_link),
            'External Job link': truncate_for_csv(application_link),
            'Questions Found': truncate_for_csv(questions_list),
            'Connect Request': truncate_for_csv(connect_request)
        }

        success = csv_manager.append_row(row_data, fieldnames)
        if not success:
            print_lg("[WARNING] Failed to save application to CSV (file locked or error)")
    except Exception as e:
        print_lg(f"[WARNING] Failed to update submitted jobs list: {e}")
        print_lg("Possible reasons: File is open, permission denied, or file not found")
        print_lg("Continuing without saving this application...")
    ##<



# Function to discard the job application
def discard_job() -> None:
    """
    Best-effort cleanup for Easy Apply modals.
    Tries multiple UI paths (ESC, Close/Dismiss, Discard confirmations).
    Never raises – failures should not crash the main loop.
    """
    try:
        actions.send_keys(Keys.ESCAPE).perform()
    except Exception:
        pass

    # Common: close current focus (dropdowns) then discard
    try:
        actions.send_keys(Keys.ESCAPE).perform()
    except Exception:
        pass

    # Try discard buttons (various labels)
    try:
        if wait_span_click(driver, "Discard", 1, scroll=False, click=True):
            return
        if wait_span_click(driver, "Discard application", 1, scroll=False, click=True):
            return
    except Exception:
        pass

    # Try closing/dismissing the modal (X button), then discard confirmation if it appears
    dismiss_xpaths = [
        "//button[contains(@aria-label,'Dismiss')]",
        "//button[contains(@aria-label,'Close')]",
        "//button[contains(@class,'artdeco-modal__dismiss')]",
        "//button[contains(@data-control-name,'dismiss')]",
    ]
    for xp in dismiss_xpaths:
        try:
            if try_xp(driver, xp, True):
                break
        except Exception:
            continue

    # After closing, LinkedIn often shows a confirmation sheet
    try:
        wait_span_click(driver, "Discard", 1, scroll=False, click=True)
    except Exception:
        pass






# Function to apply to jobs
def apply_to_jobs(search_terms: list[str]) -> None:
    applied_jobs = get_applied_job_ids()
    rejected_jobs = set()
    blacklisted_companies = set()
    global current_city, pause_before_submit, pause_at_failed_question
    current_city = current_city.strip()

    if randomize_search_order:  shuffle(search_terms)
    
    try:
        from config.search import use_human_like_flow
    except ImportError:
        use_human_like_flow = False
    
    for searchTerm in search_terms:
        ##> ------ Flow: Human-like sau URL direct ------
        if use_human_like_flow:
            if not navigate_to_jobs_search_human_like(searchTerm):
                # Fallback la URL direct
                driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
        else:
            driver.get(f"https://www.linkedin.com/jobs/search/?keywords={searchTerm}")
        ##<
        
        print_lg("\n________________________________________________________________________________________________________________________\n")
        print_lg(f'\n>>>> Now searching for "{searchTerm}" <<<<\n\n')

        apply_filters()

        current_count = 0
        try:
            # Continue applying until:
            # 1. switch_number is reached (very high, effectively "infinite" per term)
            # 2. there are no more jobs available (pagination finished)
            # 3. the daily limit is reached
            while current_count < switch_number:
                # Check daily limit at start of each iteration
                if session_manager and session_manager.check_daily_limit_reached():
                    print_lg(f"\n🛑 Daily limit reached ({session_manager.applications_today}/{session_manager.daily_limit})")
                    print_lg(f"✅ Stopping search term: '{searchTerm}' after {current_count} applications")
                    return
                # Wait until job listings are loaded
                wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))

                pagination_element, current_page = get_page_info()

                # Find all job listings in current page
                buffer(3)
                job_listings = driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")  

            
                for job in job_listings:
                    if keep_screen_awake: pyautogui.press('shiftright')
                    if current_count >= switch_number: break
                    
                    ##> ------ Enhanced by AI Audit - Periodic Health Check ------
                    # Check for CAPTCHA every 10 jobs (not at start)
                    if current_count > 0 and current_count % 10 == 0:
                        if error_recovery and error_recovery.detect_captcha():
                            print_lg("🚨 CAPTCHA detected after applying! Stopping to avoid ban.")
                            print_lg("💡 Solve CAPTCHA in browser and restart bot to continue.")
                            return  # Exit function gracefully
                    ##<
                    
                    print_lg("\n-@-\n")

                    job_id,title,company,work_location,work_style,skip = get_job_main_details(job, blacklisted_companies, rejected_jobs)

                    # Skip jobs already processed in a previous run (checkpoint resume)
                    if session_manager and session_manager.is_job_processed(job_id):
                        print_lg(f'Skipping already processed job from checkpoint. Job ID: {job_id}!')
                        continue
                    
                    if skip: continue
                    
                    # NEW RULE: Detect LinkedIn's "We limit daily submissions..." message
                    # If present, this usually means Easy Apply is disabled for the day → full stop.
                    try:
                        limit_msg_el = driver.find_element(
                            By.XPATH,
                            "//*[contains(normalize-space(), 'We limit daily submissions') "
                            "or contains(normalize-space(), 'limit daily submissions to maintain quality')]"
                        )
                        if limit_msg_el and limit_msg_el.is_displayed():
                            print_lg("🛑 LinkedIn daily submissions limit message detected for this job.")
                            print_lg("ℹ️ Message: 'We limit daily submissions to maintain quality and prevent bots, helping each application get the right attention. Save this job and apply tomorrow.'")
                            app_state.daily_limit_reached = True
                            return
                    except (NoSuchElementException, ElementNotInteractableException, TimeoutException, StaleElementReferenceException, ElementClickInterceptedException):
                        # No such message → continue normally
                        pass
                    
                    # Simulate time for a real user to read the job posting
                    ##> ------ Enhanced by AI Audit - Natural Reading Simulation ------
                    if human_behavior:
                        try:
                            jobs_top_card_element = try_find_by_classes(driver, ["job-details-jobs-unified-top-card__primary-description-container","job-details-jobs-unified-top-card__primary-description"])
                            human_behavior.simulate_reading(jobs_top_card_element, text_length=len(title) + 500)
                        except (NoSuchElementException, AttributeError):
                            reading_time = randint(5, 15)
                            print_lg(f"Reading job details for {reading_time} seconds...")
                            buffer(reading_time)
                    else:
                        reading_time = randint(5, 15)
                        print_lg(f"Reading job details for {reading_time} seconds...")
                        buffer(reading_time)
                    ##<
                    
                    # Redundant fail safe check for applied jobs!
                    try:
                        if job_id in applied_jobs or find_by_class(driver, "jobs-s-apply__application-link", 2):
                            print_lg(f'Already applied to "{title} | {company}" job. Job ID: {job_id}!')
                            continue
                    except Exception as e:
                        print_lg(f'Trying to Apply to "{title} | {company}" job. Job ID: {job_id}')

                    job_link = f"https://www.linkedin.com/jobs/view/{job_id}"
                    application_link = "Easy Applied"
                    date_applied = "Pending"
                    hr_link = "Unknown"
                    hr_name = "Unknown"
                    connect_request = "In Development" # Still in development
                    date_listed = "Unknown"
                    skills = "Needs an AI" # Still in development
                    resume = "Pending"
                    reposted = False
                    questions_list = None
                    screenshot_name = "Not Available"

                    try:
                        rejected_jobs, blacklisted_companies, jobs_top_card = check_blacklist(rejected_jobs,job_id,company,blacklisted_companies)
                    except ValueError as e:
                        print_lg(e, 'Skipping this job!\n')
                        failed_job(job_id, job_link, resume, date_listed, "Found Blacklisted words in About Company", e, "Skipped", screenshot_name)
                        app_state.counters.increment_skipped()
                        continue
                    except Exception as e:
                        print_lg("Failed to scroll to About Company!")
                        # print_lg(e)



                    # Hiring Manager info
                    try:
                        hr_info_card = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, "hirer-card__hirer-information")))
                        hr_link = hr_info_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                        hr_name = hr_info_card.find_element(By.TAG_NAME, "span").text
                    except Exception as e:
                        print_lg(f'HR info was not given for "{title}" with Job ID: {job_id}!')
                        # print_lg(e)


                    # Calculation of date posted
                    try:
                        # except: 
                        time_posted_text = jobs_top_card.find_element(By.XPATH, './/span[contains(normalize-space(), " ago")]').text
                        print(f"Time Posted: {time_posted_text}")
                        if time_posted_text.__contains__("Reposted"):
                            reposted = True
                            time_posted_text = time_posted_text.replace("Reposted", "")
                        date_listed = calculate_date_posted(time_posted_text.strip())
                    except Exception as e:
                        print_lg("Failed to calculate the date posted!",e)


                    description, experience_required, skip, reason, message = get_job_description()
                    if skip:
                        print_lg(message)
                        failed_job(job_id, job_link, resume, date_listed, reason, message, "Skipped", screenshot_name)
                        rejected_jobs.add(job_id)
                        app_state.counters.increment_skipped()
                        continue
                    
                    skills = "Not extracted"

                    uploaded = False
                    # Case 1: Easy Apply Button
                    if try_xp(driver, ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]"):
                        try: 
                            try:
                                errored = ""
                                modal = find_by_class(driver, "jobs-easy-apply-modal")
                                resume = "Previous resume"
                                resume_path = default_resume_path
                                if get_resume_path_for_job:
                                    try:
                                        resume_path = get_resume_path_for_job(
                                            description, resume_cv_folder, default_resume_path
                                        )
                                        if resume_path and os.path.exists(resume_path):
                                            print_lg(f'📄 Selected CV: {os.path.basename(resume_path)}')
                                        else:
                                            print_lg("⚠️ CV selector returned path that does not exist on disk, using previous LinkedIn resume.")
                                    except Exception as e:
                                        resume_path = default_resume_path
                                        print_lg(f'⚠️ CV selector failed, using default: {e}')
                                next_button = True
                                questions_list = set()
                                next_counter = 0
                                while next_button:
                                    next_counter += 1
                                    # Check if modal is still visible
                                    try:
                                        if not modal.is_displayed():
                                            print_lg("⚠️ Easy Apply modal disappeared, skipping...")
                                            errored = "modal_gone"
                                            break
                                    except (StaleElementReferenceException, NoSuchElementException):
                                        print_lg("⚠️ Easy Apply modal no longer accessible, skipping...")
                                        errored = "modal_gone"
                                        break
                                    if next_counter >= 15:
                                        ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
                                        print_lg("⚠️ Stuck in question loop, attempting to continue anyway...")
                                        screenshot(driver, job_id, "Stuck at questions")
                                        # Skip this job and continue
                                        ##<
                                        if questions_list: print_lg("Stuck for one or some of the following questions...", questions_list)
                                        screenshot_name = screenshot(driver, job_id, "Failed at questions")
                                        errored = "stuck"
                                        raise Exception("Seems like stuck in a continuous loop of next, probably because of new questions.")
                                    questions_list = answer_questions(modal, questions_list, work_location, job_description=description)
                                    ##> ------ Enhanced by AI Audit - CV Default LinkedIn ------
                                    # In noul flux incercam INTOTDEAUNA sa selectam CV-ul corect
                                    # deja urcat in LinkedIn, daca avem un `resume_path` valid
                                    # si inca nu am facut selectia in acest formular.
                                    if not uploaded and resume_path:
                                        uploaded, resume = upload_resume(modal, resume_path)
                                    ##<
                                    # Strategy: try multiple navigation buttons (Review/Next/Continue).
                                    # If still can't progress, skip this form by raising (handled below).
                                    clicked = False
                                    # Re-acquire modal in case DOM refreshed
                                    try:
                                        modal = find_by_class(driver, "jobs-easy-apply-modal", 2.0)
                                    except Exception:
                                        pass
                                    for btn_text in ("Review", "Next", "Continue"):
                                        try:
                                            if wait_span_click(modal, btn_text, 1.5, scrollTop=True):
                                                clicked = True
                                                break
                                        except Exception:
                                            continue
                                    # Fallback: click primary footer button regardless of text
                                    if not clicked:
                                        try:
                                            clicked = _click_primary_easy_apply_footer_button(modal)
                                        except Exception:
                                            clicked = False
                                    if not clicked:
                                        # Last resort: sometimes we're already on submit screen
                                        for btn_text in ("Submit application", "Submit", "Send application"):
                                            try:
                                                if wait_span_click(modal, btn_text, 1.0, scrollTop=True):
                                                    clicked = True
                                                    break
                                            except Exception:
                                                continue
                                    # Final fallback: primary footer button again (submit screens often have only one)
                                    if not clicked:
                                        try:
                                            clicked = _click_primary_easy_apply_footer_button(modal)
                                        except Exception:
                                            clicked = False
                                    if not clicked:
                                        raise Exception("Unable to progress Easy Apply (no Review/Next/Submit button)")
                                    buffer(click_gap)

                            except NoSuchElementException: errored = "nose"
                            finally:
                                if questions_list and errored != "stuck": 
                                    print_lg("Answered the following questions...", questions_list)
                                    print("\n\n" + "\n".join(str(question) for question in questions_list) + "\n\n")
                                # Ensure we're on the review step before submitting (try modal first, then page)
                                try:
                                    wait_span_click(modal, "Review", 1, scrollTop=True)
                                except Exception:
                                    pass
                                wait_span_click(driver, "Review", 1, scrollTop=True)
                                ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
                                # Eliminat: pause_before_submit confirmation
                                print_lg("✅ Ready to submit application (no pause, automatic flow)")
                                ##<

                                # If the Easy Apply modal is gone, we most likely ended up on an external ATS
                                try:
                                    modal_still_there = find_by_class(driver, "jobs-easy-apply-modal", 2.0)
                                except Exception:
                                    modal_still_there = None

                                if not modal_still_there and _is_external_ats_context():
                                    print_lg("⚠️ Detected external ATS context after questions. Skipping automatic Submit for safety.")
                                    errored = "ats_external"
                                    raise Exception("Unsupported external ATS flow – manual review recommended.")

                                follow_company(modal)
                                # Strategy: more robust Submit logic:
                                # 1) try known button texts limited to the modal
                                # 2) if that fails, search for the primary Submit button in the footer
                                submitted = _click_final_submit_button(modal)
                                if submitted:
                                    date_applied = datetime.now()
                                    if not (wait_span_click(driver, "Done", 2) or wait_span_click(driver, "Finish", 1.5)):
                                        try:
                                            actions.send_keys(Keys.ESCAPE).perform()
                                        except Exception:
                                            pass
                                else:
                                    ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
                                    # Before giving up, inspect potential validation errors
                                    errors = _find_form_validation_errors(modal)
                                    if not errors:
                                        print_lg("⚠️ Failed to find Submit button, discarding application...")
                                    else:
                                        print_lg("⚠️ Submit blocked by validation errors, discarding application...")
                                    ##<
                                    print_lg("Since, Submit Application failed, discarding the job application...")
                                    if errored == "nose": raise Exception("Failed to click Submit application 😑")


                        except Exception as e:
                            print_lg("Failed to Easy apply!")
                            # print_lg(e)
                            critical_error_log("Somewhere in Easy Apply process",e)
                            failed_job(job_id, job_link, resume, date_listed, "Problem in Easy Applying", e, application_link, screenshot_name)
                            app_state.counters.increment_failed()

                            # If ErrorRecovery is enabled, try to recover the WebDriver session.
                            # If the internal attempt limit is reached, stop the main loop.
                            if error_recovery:
                                try:
                                    ok = error_recovery.recover_webdriver_session()
                                    if not ok:
                                        print_lg("🛑 Hard stop: WebDriver recovery failed too many times. Exiting main loop.")
                                        return
                                except Exception:
                                    pass

                            discard_job()
                            continue
                    else:
                        # Case 2: Apply externally
                        skip, application_link, tabs_count = external_apply(pagination_element, job_id, job_link, resume, date_listed, application_link, screenshot_name)
                        if app_state.daily_limit_reached:
                            print_lg("\n###############  Daily application limit for Easy Apply is reached!  ###############\n")
                            return
                        if skip: continue

                    submitted_jobs(job_id, title, company, work_location, work_style, description, experience_required, skills, hr_name, hr_link, resume, reposted, date_listed, date_applied, job_link, application_link, questions_list, connect_request)
                    if uploaded:   app_state.use_new_resume = False

                    print_lg(f'✅ Successfully saved "{title} | {company}" job. Job ID: {job_id}')
                    current_count += 1
                    if application_link == "Easy Applied": app_state.counters.increment_easy_applied()
                    else:   app_state.counters.increment_external_jobs()
                    applied_jobs.add(job_id)
                    
                    ##> ------ Enhanced by AI Audit - Save Checkpoint ------
                    # Save progress checkpoint for resume capability
                    if session_manager:
                        session_manager.save_checkpoint(searchTerm, current_page, job_id)
                    ##<
                    
                    ##> ------ Enhanced by AI Audit - Session Management & Natural Delays ------
                    # Record application in session manager
                    if session_manager:
                        can_continue = session_manager.record_application()
                        
                        if not can_continue:
                            print_lg("\n" + "="*70)
                            print_lg("🛑 DAILY LIMIT REACHED!")
                            print_lg("="*70)
                            return
                        
                        # Check if need break
                        should_break, break_reason, break_duration = session_manager.should_take_break()
                        if should_break and enable_session_breaks:
                            if break_duration > 0:
                                session_manager.take_break(break_duration, break_reason)
                            else:
                                print_lg(f"\n🛑 {break_reason}")
                                return
                        
                        # Get natural delay
                        wait_time = session_manager.get_inter_application_delay()
                    else:
                        wait_time = randint(30, 60)
                    
                    print_lg(f"⏸️  Pausing for {wait_time:.1f} seconds before next application...")
                    
                    # Use smart buffer with normal distribution
                    if enable_anti_detection:
                        smart_buffer(wait_time, variance=0.3, distribution='normal')
                    else:
                        buffer(int(wait_time))
                    
                    # Random distraction simulation
                    if human_behavior and random() < 0.05:  # 5% chance
                        human_behavior.simulate_distraction()
                    ##<



                # Switching to the next page
                # Continue to iterate pages until there are no jobs left or the daily limit is reached
                if pagination_element == None:
                    print_lg("Couldn't find pagination element, probably at the end page of results!")
                    print_lg(f"✅ Finished all pages for search term: '{searchTerm}' ({current_count} applications)")
                    break
                try:
                    # Check the daily limit before switching pages
                    if session_manager and session_manager.check_daily_limit_reached():
                        print_lg("\n🛑 Daily limit reached - stopping pagination")
                        return
                    
                    pagination_element.find_element(By.XPATH, f"//button[@aria-label='Page {current_page+1}']").click()
                    print_lg(f"\n>-> Now on Page {current_page+1} \n")
                    
                    # Simulate page loading time for realistic user behaviour (tuned for anti-detection)
                    page_load_time = randint(8, 15)  # Slightly reduced for efficiency while staying natural
                    print_lg(f"Waiting {page_load_time} seconds for page to load...")
                    buffer(page_load_time)
                except NoSuchElementException:
                    print_lg(f"\n>-> Didn't find Page {current_page+1}. Probably at the end page of results!\n")
                    print_lg(f"✅ Finished all pages for search term: '{searchTerm}' ({current_count} applications)")
                    break

        except ElementClickInterceptedException as e:
            # Recoverable in many cases: usually a modal/overlay left open.
            print_lg("⚠️ Click intercepted at page level. Attempting recovery and continuing...", e)
            try:
                discard_job()
            except Exception:
                pass
            try:
                actions.send_keys(Keys.ESCAPE).perform()
            except Exception:
                pass
            buffer(2)
            continue
        except (NoSuchWindowException, WebDriverException) as e:
            print_lg("Browser window closed or session is invalid. Ending application process.", e)
            raise e # Re-raise to be caught by main
        except Exception as e:
            print_lg("Failed to find Job listings!")
            critical_error_log("In Applier", e)
            try:
                print_lg(driver.page_source, pretty=True)
            except Exception as page_source_error:
                print_lg(f"Failed to get page source, browser might have crashed. {page_source_error}")
            # print_lg(e)

        
def run(total_runs: int) -> int:
    if app_state.daily_limit_reached:
        return total_runs
    
    ##> ------ Enhanced by AI Audit - Enhanced Run with Health Checks ------
    print_lg("\n" + "="*100)
    print_lg(f"🚀 CYCLE #{total_runs} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_lg(f"📅 Looking for: '{date_posted}' | Sort by: '{sort_by}'")
    print_lg("="*100 + "\n")

    apply_to_jobs(search_terms)
    
    # Checkpoint cleanup at end of successful run
    if session_manager and session_manager.check_daily_limit_reached():
        session_manager.clear_checkpoint()
        print_lg("✅ Daily limit reached - checkpoint cleared")
    
    print_lg("\n" + "="*100)
    print_lg(f"✅ CYCLE #{total_runs} COMPLETE")
    print_lg("="*100 + "\n")

    if not app_state.daily_limit_reached:
        # Shorter pause between cycles for higher throughput, while keeping behaviour natural
        print_lg("⏸️  Sleeping for 5 minutes before next cycle...")
        sleep(180)  # 3 minutes
        print_lg("⏳ 2 more minutes...")
        sleep(120)  # 2 minutes
    
    buffer(3)
    ##<
    return total_runs + 1



linkedIn_tab = False

def main() -> None:
    total_runs = 1
    tabs_count = 0  # Initialize to prevent UnboundLocalError in finally block
    try:
        global linkedIn_tab, human_behavior, session_manager, error_recovery, file_manager
        alert_title = "Error Occurred. Closing Browser!"
        validate_config()
        
        ##> ------ Enhanced by AI Audit - Initialize Robust Modules ------
        print_lg("\n" + "="*70)
        print_lg("🚀 INITIALIZING ULTRA-ROBUST BOT")
        print_lg("="*70)
        
        # Initialize File Manager
        if FileManager:
            try:
                file_manager = FileManager(
                    logs_folder=logs_folder_path,
                    max_log_size_mb=10,
                    max_screenshots=50
                )
                print_lg("✅ File manager initialized")
                
                # Perform maintenance
                file_manager.perform_maintenance()
                
            except Exception as e:
                print_lg(f"⚠️ Failed to initialize file manager: {e}")
                file_manager = None
        
        # Initialize Error Recovery
        if ErrorRecovery:
            try:
                error_recovery = ErrorRecovery(driver)
                print_lg("✅ Error recovery & retry logic initialized")
            except Exception as e:
                print_lg(f"⚠️ Failed to initialize error recovery: {e}")
                error_recovery = None
        
        # Initialize Human Behavior Simulator
        if enable_anti_detection and HumanBehaviorSimulator:
            try:
                human_behavior = HumanBehaviorSimulator(driver, actions)
                print_lg("✅ Anti-detection (natural behavior) initialized")
            except Exception as e:
                print_lg(f"⚠️ Failed to initialize anti-detection: {e}")
                human_behavior = None
        
        # Initialize Session Manager
        if SessionManager:
            try:
                session_manager = SessionManager(
                    daily_limit=daily_application_limit,
                    session_length=session_length_minutes,
                    logs_folder=logs_folder_path
                )
                print_lg("✅ Session manager (checkpoints & breaks) initialized")
                
                # Show session stats
                stats = session_manager.get_session_stats()
                print_lg(f"📊 Applications today: {stats['applications_today']}/{stats['daily_limit']}")
                
                if session_manager.check_daily_limit_reached():
                    print_lg("\n⚠️ DAILY LIMIT ALREADY REACHED!")
                    print_lg("The bot will not apply to any jobs today.")
                    print_lg("Come back tomorrow for fresh 100 applications!")
                    return
                    
            except Exception as e:
                print_lg(f"⚠️ Failed to initialize session manager: {e}")
                session_manager = None
        
        print_lg("="*70 + "\n")
        print_lg("✅ ALL SYSTEMS READY - Starting autonomous operation...")
        print_lg("💡 You can leave now - bot will handle everything!\n")
        ##<

        # Verificare CV-uri locale:
        # - daca lipseste default_resume_path DAR exista CV-uri in `resume_cv_folder`
        #   (DOCX/DOC/PDF), continuam cu selectia dinamica;
        # - doar daca nu exista niciun CV local, ne bazam exclusiv pe „Previous resume”.
        cv_folder = resume_cv_folder
        has_local_cvs = os.path.isdir(cv_folder) and any(
            os.path.isfile(os.path.join(cv_folder, f))
            and os.path.splitext(f)[1].lower() in {".docx", ".doc", ".pdf"}
            for f in os.listdir(cv_folder)
        )

        if not os.path.exists(default_resume_path):
            if has_local_cvs:
                print_lg(f'⚠️ Default resume "{default_resume_path}" is missing, but CV variants exist in "{cv_folder}".')
                print_lg("ℹ️ Will use dynamic CV selection based on job description and existing LinkedIn uploads.")
            else:
                print_lg(f'⚠️ Default resume "{default_resume_path}" is missing and no local CVs were found in "{cv_folder}".')
                print_lg("Continuing with previous upload from LinkedIn for all applications (no CV switching possible).")
                app_state.use_new_resume = False

        # Login to LinkedIn
        tabs_count = len(driver.window_handles)
        driver.get(LinkedInURLs.LOGIN_URL)
        if not is_logged_in_LN(): login_LN()
        
        linkedIn_tab = driver.current_window_handle

        if app_state.use_new_resume:
            print_lg("✅ Using dynamic CV selection: local DOCX files mapped to existing LinkedIn resumes by filename.")
        else:
            print_lg("✅ Using previously selected default CV from LinkedIn (no local CV switching).")

        # Start applying to jobs
        driver.switch_to.window(linkedIn_tab)
        total_runs = run(total_runs)
        while(run_non_stop):
            if cycle_date_posted:
                date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
                global date_posted
                current_idx = date_options.index(date_posted) if date_posted in date_options else 0
                next_idx = current_idx + 1
                if stop_date_cycle_at_24hr:
                    date_posted = date_options[next_idx] if next_idx < len(date_options) else date_options[-1]
                else:
                    date_posted = date_options[next_idx % len(date_options)]
            if alternate_sortby:
                global sort_by
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
                total_runs = run(total_runs)
                sort_by = "Most recent" if sort_by == "Most relevant" else "Most relevant"
            total_runs = run(total_runs)
            if app_state.daily_limit_reached:
                break
        

    except (NoSuchWindowException, WebDriverException) as e:
        print_lg("Browser window closed or session is invalid. Exiting.", e)
    except Exception as e:
        ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
        critical_error_log("In Applier Main", e)
        print_lg(f"⚠️ Critical error occurred: {e}")
        print_lg("Check logs/log.txt for details")
        ##<
    finally:
        stats = app_state.counters.get_stats()
        summary = "Total runs: {}\nJobs Easy Applied: {}\nExternal job links collected: {}\nTotal applied or collected: {}\nFailed jobs: {}\nIrrelevant jobs skipped: {}\n".format(total_runs, stats['easy_applied'], stats['external_jobs'], stats['easy_applied'] + stats['external_jobs'], stats['failed'], stats['skipped'])
        print_lg(summary)
        print_lg(f"\n\nTotal runs:                     {total_runs}")
        print_lg(f"Jobs Easy Applied:              {stats['easy_applied']}")
        print_lg(f"External job links collected:   {stats['external_jobs']}")
        print_lg("                              ----------")
        print_lg("Total applied or collected:     {}".format(stats['easy_applied'] + stats['external_jobs']))
        print_lg(f"\nFailed jobs:                    {stats['failed']}")
        print_lg("Irrelevant jobs skipped:        {}\n".format(stats['skipped']))
        if app_state.randomly_answered_questions: print_lg("\n\nQuestions randomly answered:\n  {}  \n\n".format(";\n".join(str(question) for question in app_state.randomly_answered_questions)))
        quotes = choice([
            "Success is not final, failure is not fatal, It is the courage to continue that counts. - Winston Churchill",
            "Believe in yourself and all that you are. Know that there is something inside you that is greater than any obstacle. - Christian D. Larson",
            "Every job is a self-portrait of the person who does it. Autograph your work with excellence. - Jessica Guidobono",
            "The only way to do great work is to love what you do. If you haven't found it yet, keep looking. Don't settle. - Steve Jobs",
            "Opportunities don't happen, you create them. - Chris Grosser",
            "The road to success and the road to failure are almost exactly the same. The difference is perseverance. - Colin R. Davis",
            "Obstacles are those frightful things you see when you take your eyes off your goal. - Henry Ford",
            "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
            ])
        stats = app_state.counters.get_stats()
        timeSaved = (stats['easy_applied'] * 80) + (stats['external_jobs'] * 20) + (stats['skipped'] * 10)
        timeSavedMsg = ""
        if timeSaved > 0:
            timeSaved += 60
            timeSavedMsg = f"In this run, you saved approx {round(timeSaved/60)} mins ({timeSaved} secs) compared to manual applying."
        msg = f"{quotes}\n\n\n{timeSavedMsg}\n\nSummary:\n{summary}"
        ##> ------ Enhanced by AI Audit - Auto-flow without alerts ------
        print_lg("\n" + "="*70)
        print_lg(msg)
        print_lg("="*70)
        print_lg("Closing the browser...")
        if tabs_count >= 10:
            msg = "NOTE: IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM!\n\nOr it's highly likely that application will just open browser and not do anything next time!" 
            print_lg(f"\n⚠️ {msg}")
        ##<
        try:
            if driver:
                driver.quit()
        except WebDriverException as e:
            print_lg("Browser already closed.", e)
        except Exception as e: 
            critical_error_log("When quitting...", e)


if __name__ == "__main__":
    main()
