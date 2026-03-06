'''
Configuration validator for all config/*.py modules.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''




# from config.XdepricatedX import *

__validation_file_path = ""

def check_int(var: int, var_name: str, min_value: int=0) -> bool | TypeError | ValueError:
    if not isinstance(var, int): raise TypeError(f'The variable "{var_name}" in "{__validation_file_path}" must be an Integer!\nReceived "{var}" of type "{type(var)}" instead!\n\nSolution:\nPlease open "{__validation_file_path}" and update "{var_name}" to be an Integer.\nExample: `{var_name} = 10`\n\nNOTE: Do NOT surround Integer values in quotes ("10")X !\n\n')
    if var < min_value: raise ValueError(f'The variable "{var_name}" in "{__validation_file_path}" expects an Integer greater than or equal to `{min_value}`! Received `{var}` instead!\n\nSolution:\nPlease open "{__validation_file_path}" and update "{var_name}" accordingly.')
    return True

def check_boolean(var: bool, var_name: str) -> bool | ValueError:
    if var == True or var == False: return True
    raise ValueError(f'The variable "{var_name}" in "{__validation_file_path}" expects a Boolean input `True` or `False`, not "{var}" of type "{type(var)}" instead!\n\nSolution:\nPlease open "{__validation_file_path}" and update "{var_name}" to either `True` or `False` (case-sensitive, T and F must be CAPITAL/uppercase).\nExample: `{var_name} = True`\n\nNOTE: Do NOT surround Boolean values in quotes ("True")X !\n\n')

def check_string(var: str, var_name: str, options: list=[], min_length: int=0) -> bool | TypeError | ValueError:
    if not isinstance(var, str): raise TypeError(f'Invalid input for {var_name}. Expecting a String!')
    if min_length > 0 and len(var) < min_length: raise ValueError(f'Invalid input for {var_name}. Expecting a String of length at least {min_length}!')
    if len(options) > 0 and var not in options: raise ValueError(f'Invalid input for {var_name}. Expecting a value from {options}, not {var}!')
    return True

def check_list(var: list, var_name: str, options: list=[], min_length: int=0) -> bool | TypeError | ValueError:
    if not isinstance(var, list):
        raise TypeError(f'Invalid input for {var_name}. Expecting a List!')
    if len(var) < min_length: raise ValueError(f'Invalid input for {var_name}. Expecting a List of length at least {min_length}!')
    for element in var:
        if not isinstance(element, str): raise TypeError(f'Invalid input for {var_name}. All elements in the list must be strings!')
        if len(options) > 0 and element not in options: raise ValueError(f'Invalid input for {var_name}. Expecting all elements to be values from {options}. This "{element}" is NOT in options!')
    return True


# Enhanced validation functions (Phase 2)
def validate_phone_number(phone: str) -> tuple[bool, str]:
    """Validate phone number format (international)"""
    import re

    # Pattern: +CountryCode followed by 6-15 digits
    pattern = r'^\+\d{1,3}\d{6,15}$'

    if not isinstance(phone, str):
        return False, "Phone must be string"

    # Remove spaces, dashes, parentheses
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')

    if re.match(pattern, cleaned):
        return True, cleaned
    return False, "Invalid phone format (use: +CountryCode1234567890)"


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    import re

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not isinstance(email, str):
        return False, "Email must be string"

    if re.match(pattern, email.strip()):
        return True, email.strip().lower()
    return False, "Invalid email format"


def validate_resume_path(path: str) -> tuple[bool, str]:
    """Validate resume file exists and is in a supported format (DOCX/PDF)."""
    from pathlib import Path

    resume_path = Path(path)

    if not resume_path.exists():
        return False, f"Resume file not found: {path}"

    # Prefer DOCX (format used in `all resumes/cv` and in LinkedIn),
    # but keep support for PDF if needed in other flows.
    if resume_path.suffix.lower() not in {'.docx', '.doc', '.pdf'}:
        return False, "Resume must be DOCX, DOC or PDF format"

    if resume_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
        return False, "Resume file too large (max 10MB)"

    return True, str(resume_path.absolute())



from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs

from config.personals import (
    first_name, last_name, middle_name, phone_number,
    current_city, street, state, zipcode, country,
    ethnicity, gender, disability_status, veteran_status,
    PERSONALS
)
def validate_personals() -> None | ValueError | TypeError:
    '''
    Validates all variables in the `/config/personals.py` file.
    '''
    global __validation_file_path
    __validation_file_path = "config/personals.py"

    check_string(first_name, "first_name", min_length=1)
    check_string(middle_name, "middle_name")
    check_string(last_name, "last_name", min_length=1)

    check_string(phone_number, "phone_number", min_length=10)

    check_string(current_city, "current_city")
    
    check_string(street, "street")
    check_string(state, "state")
    check_string(zipcode, "zipcode")
    check_string(country, "country")
    
    check_string(ethnicity, "ethnicity", ["Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other"],  min_length=0)
    check_string(gender, "gender", ["Male", "Female", "Other", "Decline", ""])
    check_string(disability_status, "disability_status", ["Yes", "No", "Decline"])
    check_string(veteran_status, "veteran_status", ["Yes", "No", "Decline"])



from config.questions import (
    desired_salary, desired_salary_max, current_ctc,
    years_of_experience, notice_period, education,
    require_visa, us_citizenship,
    cover_letter,
    pause_before_submit, pause_at_failed_question,
    QUESTIONS_PERSONAL, availability_start
)
def validate_questions() -> None | ValueError | TypeError:
    '''
    Validates all variables in the `/config/questions.py` file.
    '''
    global __validation_file_path
    __validation_file_path = "config/questions.py"

    # check_string(default_resume_path, "default_resume_path")  # Variable doesn't exist
    check_string(years_of_experience, "years_of_experience")
    check_string(require_visa, "require_visa", ["Yes", "No"])
    # check_string(website, "website")  # Variable doesn't exist
    # check_string(linkedIn, "linkedIn")  # Variable doesn't exist
    check_int(desired_salary, "desired_salary")
    check_string(us_citizenship, "us_citizenship", ["U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident", "Other"])
    # check_string(linkedin_headline, "linkedin_headline")  # Variable doesn't exist
    check_int(notice_period, "notice_period")
    check_int(current_ctc, "current_ctc")
    # check_string(linkedin_summary, "linkedin_summary")  # Variable doesn't exist
    check_string(cover_letter, "cover_letter")
    # check_string(recent_employer, "recent_employer")  # Variable doesn't exist
    # check_string(confidence_level, "confidence_level")  # Variable doesn't exist

    check_boolean(pause_before_submit, "pause_before_submit")
    check_boolean(pause_at_failed_question, "pause_at_failed_question")
    # check_boolean(overwrite_previous_answers, "overwrite_previous_answers")  # Variable doesn't exist

    ##> ------ Enhanced by AI Audit - CV Matching Validation ------
    # check_boolean(enable_cv_matching, "enable_cv_matching")  # Variable doesn't exist
    # if enable_cv_matching:
    #     # Check if cv_variants is a list
    #     if not isinstance(cv_variants, list):
    #         raise TypeError(f'cv_variants must be a list, got {type(cv_variants)}')
    #     if len(cv_variants) < 1:
    #         raise ValueError(f'cv_variants must have at least 1 CV')
    #     # Check each CV entry
    #     for i, cv in enumerate(cv_variants):
    #         if not isinstance(cv, dict):
    #             raise TypeError(f'CV variant #{i+1} must be a dictionary, got {type(cv)}')
    #         if 'file' not in cv:
    #             raise ValueError(f'CV variant #{i+1} missing "file" key')
    #         if not isinstance(cv['file'], str):
    #             raise TypeError(f'CV variant #{i+1} "file" must be a string, got {type(cv["file"])}')
    ##<


from config.search import (
    search_terms, search_location, switch_number,
    randomize_search_order,
    sort_by, date_posted, salary, easy_apply_only,
    experience_level, job_type, on_site,
    companies, location, industry, job_function,
    job_titles, benefits, commitments,
    under_10_applicants, in_your_network, fair_chance_employer,
    about_company_bad_words, about_company_good_words, bad_words, security_clearance,
    did_masters, current_experience,
    onsite_locations, remote_locations, enable_location_filtering,
    pause_after_filters
)
def validate_search() -> None | ValueError | TypeError:
    '''
    Validates all variables in the `/config/search.py` file.
    '''
    global __validation_file_path
    __validation_file_path = "config/search.py"

    check_list(search_terms, "search_terms", min_length=1)
    check_string(search_location, "search_location")
    check_int(switch_number, "switch_number", 1)
    check_boolean(randomize_search_order, "randomize_search_order")

    check_string(sort_by, "sort_by", ["", "Most recent", "Most relevant"])
    check_string(date_posted, "date_posted", ["", "Any time", "Past month", "Past week", "Past 24 hours"])
    check_string(salary, "salary")

    check_boolean(easy_apply_only, "easy_apply_only")

    check_list(experience_level, "experience_level", ["Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"])
    check_list(job_type, "job_type", ["Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"])
    check_list(on_site, "on_site", ["On-site", "Remote", "Hybrid"])

    check_list(companies, "companies")
    check_list(location, "location")
    check_list(industry, "industry")
    check_list(job_function, "job_function")
    check_list(job_titles, "job_titles")
    check_list(benefits, "benefits")
    check_list(commitments, "commitments")

    check_boolean(under_10_applicants, "under_10_applicants")
    check_boolean(in_your_network, "in_your_network")
    check_boolean(fair_chance_employer, "fair_chance_employer")

    check_boolean(pause_after_filters, "pause_after_filters")

    check_list(about_company_bad_words, "about_company_bad_words")
    check_list(about_company_good_words, "about_company_good_words")
    check_list(bad_words, "bad_words")
    check_boolean(security_clearance, "security_clearance")
    check_boolean(did_masters, "did_masters")
    check_int(current_experience, "current_experience", -1)




from config.secrets import (
    username, password
)
def validate_secrets() -> None | ValueError | TypeError:
    '''
    Validates all variables in the `/config/secrets.py` file.
    '''
    global __validation_file_path
    __validation_file_path = "config/secrets.py"

    check_string(username, "username", min_length=5)
    check_string(password, "password", min_length=5)



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
def validate_settings() -> None | ValueError | TypeError:
    '''
    Validates all variables in the `/config/settings.py` file.
    '''
    global __validation_file_path
    __validation_file_path = "config/settings.py"

    check_boolean(close_tabs, "close_tabs")
    check_boolean(follow_companies, "follow_companies")

    check_boolean(run_non_stop, "run_non_stop")
    check_boolean(alternate_sortby, "alternate_sortby")
    check_boolean(cycle_date_posted, "cycle_date_posted")
    check_boolean(stop_date_cycle_at_24hr, "stop_date_cycle_at_24hr")
    

    check_string(file_name, "file_name", min_length=1)
    check_string(failed_file_name, "failed_file_name", min_length=1)
    check_string(logs_folder_path, "logs_folder_path", min_length=1)

    check_int(click_gap, "click_gap", 0)

    check_boolean(run_in_background, "run_in_background")
    check_boolean(disable_extensions, "disable_extensions")
    check_boolean(safe_mode, "safe_mode")
    check_boolean(smooth_scroll, "smooth_scroll")
    check_boolean(keep_screen_awake, "keep_screen_awake")
    check_boolean(stealth_mode, "stealth_mode")
    
    ##> ------ Enhanced by AI Audit - Session Management Validation ------
    check_boolean(enable_anti_detection, "enable_anti_detection")
    check_int(daily_application_limit, "daily_application_limit", 1)
    check_int(session_length_minutes, "session_length_minutes", 5)
    check_boolean(enable_session_breaks, "enable_session_breaks")
    check_boolean(enable_workday_simulation, "enable_workday_simulation")
    ##<




def validate_config() -> bool | ValueError | TypeError:
    '''
    Runs all validation functions to validate all variables in the config files.
    '''
    validate_personals()
    validate_questions()
    validate_search()
    validate_secrets()
    validate_settings()

    # validate_String(chatGPT_username, "chatGPT_username")
    # validate_String(chatGPT_password, "chatGPT_password")
    # validate_String(chatGPT_resume_chat_title, "chatGPT_resume_chat_title")
    return True

