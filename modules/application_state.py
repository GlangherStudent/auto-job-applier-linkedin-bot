'''
Application State Management - Thread-safe state tracking.
This module replaces global variables with proper class-based state management.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.09
'''

from dataclasses import dataclass
from typing import Set
from threading import Lock
import re
from config.constants import SalaryConversion


@dataclass
class PersonalInfo:
    """Centralized personal information"""
    first_name: str
    middle_name: str
    last_name: str
    phone_number: str
    current_city: str

    @property
    def full_name(self) -> str:
        """Returns properly formatted full name"""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


@dataclass
class SalaryInfo:
    """Salary and compensation information with conversions"""
    desired_salary: int
    desired_salary_max: int
    current_ctc: int

    @property
    def desired_salary_lakhs(self) -> str:
        """Salary in lakhs (Indian numbering system)"""
        return str(round(self.desired_salary / SalaryConversion.LAKH_FACTOR, 2))

    @property
    def desired_salary_monthly(self) -> str:
        """Monthly salary"""
        return str(int(self.desired_salary / SalaryConversion.MONTHLY_DIVISOR))

    @property
    def desired_salary_range(self) -> str:
        """Salary range as string"""
        return f"{self.desired_salary}-{self.desired_salary_max}"

    @property
    def current_ctc_lakhs(self) -> str:
        """Current CTC in lakhs"""
        return str(round(self.current_ctc / SalaryConversion.LAKH_FACTOR, 2))

    @property
    def current_ctc_monthly(self) -> str:
        """Current monthly CTC"""
        return str(int(self.current_ctc / SalaryConversion.MONTHLY_DIVISOR))


class ApplicationCounters:
    """Thread-safe counters for application tracking"""

    def __init__(self):
        self._lock = Lock()
        self._easy_applied = 0
        self._external_jobs = 0
        self._failed = 0
        self._skipped = 0
        self._tabs = 1

    @property
    def easy_applied_count(self) -> int:
        with self._lock:
            return self._easy_applied

    def increment_easy_applied(self) -> int:
        with self._lock:
            self._easy_applied += 1
            return self._easy_applied

    @property
    def external_jobs_count(self) -> int:
        with self._lock:
            return self._external_jobs

    def increment_external_jobs(self) -> int:
        with self._lock:
            self._external_jobs += 1
            return self._external_jobs

    @property
    def failed_count(self) -> int:
        with self._lock:
            return self._failed

    def increment_failed(self) -> int:
        with self._lock:
            self._failed += 1
            return self._failed

    @property
    def skipped_count(self) -> int:
        with self._lock:
            return self._skipped

    def increment_skipped(self) -> int:
        with self._lock:
            self._skipped += 1
            return self._skipped

    @property
    def tabs_count(self) -> int:
        with self._lock:
            return self._tabs

    def increment_tabs(self) -> int:
        with self._lock:
            self._tabs += 1
            return self._tabs

    def get_stats(self) -> dict:
        """Returns all counter statistics"""
        with self._lock:
            return {
                'easy_applied': self._easy_applied,
                'external_jobs': self._external_jobs,
                'failed': self._failed,
                'skipped': self._skipped,
                'tabs': self._tabs
            }


class PatternCache:
    """Compiled regex patterns cache"""

    def __init__(self):
        # Experience patterns
        self.re_experience = re.compile(
            r'(\d+)\s*(to|-)\s*(\d+)\s*years?', re.IGNORECASE
        )
        self.re_experience_abbrev = re.compile(
            r'(\d+)\s*\+?\s*(?:yrs?|years?)', re.IGNORECASE
        )
        self.re_experience_min = re.compile(
            r'minimum\s*(?:of\s*)?(\d+)\s*(?:yrs?|years?)', re.IGNORECASE
        )


class ApplicationState:
    """Main application state container"""

    def __init__(self, personal_info: PersonalInfo, salary_info: SalaryInfo):
        self.personal = personal_info
        self.salary = salary_info
        self.counters = ApplicationCounters()
        self.patterns = PatternCache()

        # Session flags
        self.use_new_resume = True
        self.daily_limit_reached = False

        # Question tracking
        self.randomly_answered_questions: Set[str] = set()

        # Module instances (initialized later)
        self.human_behavior = None
        self.session_manager = None
        self.error_recovery = None
        self.file_manager = None

    def initialize_modules(self, driver):
        """Initialize all module instances with WebDriver"""
        try:
            from modules.anti_detection import HumanBehaviorSimulator
            from modules.session_manager import SessionManager
            from modules.error_recovery import ErrorRecovery
            from modules.file_manager import FileManager
            from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(driver)
            self.human_behavior = HumanBehaviorSimulator(driver, actions)
            self.session_manager = SessionManager()
            self.error_recovery = ErrorRecovery(driver)
            self.file_manager = FileManager()

            print("[OK] All modules initialized successfully")
        except Exception as e:
            print(f"[WARNING] Failed to initialize some modules: {e}")


############################################################################################################
