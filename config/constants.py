'''
Configuration Constants - Centralized magic numbers and configuration values.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.09
'''


class SalaryConversion:
    """Constants for salary format conversions"""
    LAKH_FACTOR = 100000  # Indian numbering system: 1 lakh = 100,000
    MONTHLY_DIVISOR = 12  # Months in a year


class TimeConversion:
    """Constants for time period conversions"""
    DAYS_PER_MONTH = 30  # Approximate days in a month
    DAYS_PER_WEEK = 7    # Days in a week
    WEEKS_PER_MONTH = 4  # Approximate weeks in a month
    SECONDS_PER_DAY = 86400  # Seconds in a day


class CSVConstants:
    """Constants for CSV file operations"""
    MAX_FIELD_SIZE = 1_000_000  # 1MB maximum CSV field size
    MAX_ENTRY_LENGTH = 131_000  # Maximum length for CSV entry before truncation
    HEADER_SKIP_ROWS = 1        # Number of header rows to skip


class NetworkConstants:
    """Constants for network operations and recovery"""
    RECOVERY_WAIT_INTERVALS = [10, 20, 30, 60, 60, 60]  # Seconds between retry attempts
    MAX_RECOVERY_WAIT = 300  # 5 minutes maximum wait for recovery
    LINKEDIN_RATE_LIMIT_WAIT = 3600  # 1 hour wait if rate limited


class AntiDetectionConstants:
    """Constants for human behavior simulation"""
    BEZIER_CONTROL_POINTS = 3  # Number of control points for Bezier curves
    TYPING_ERROR_RATE = 0.08   # 8% chance of typing error
    MIN_TYPING_SPEED = 0.05    # Minimum seconds per character
    MAX_TYPING_SPEED = 0.20    # Maximum seconds per character
    HOVER_DELAY_MIN = 0.3      # Minimum hover delay in seconds
    HOVER_DELAY_MAX = 0.8      # Maximum hover delay in seconds
    MICRO_MOVEMENT_MIN = 200   # Minimum range for micro mouse movements
    MICRO_MOVEMENT_MAX = 1000  # Maximum range for micro mouse movements
    RANDOM_PAUSE_MIN = 0.5     # Minimum random pause in seconds
    RANDOM_PAUSE_MAX = 3.0     # Maximum random pause in seconds


class RetryConstants:
    """Constants for retry logic"""
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 2.0
    DEFAULT_BACKOFF_FACTOR = 2.0
    ELEMENT_WAIT_TIMEOUT = 10  # Seconds to wait for element
    PAGE_LOAD_TIMEOUT = 30     # Seconds to wait for page load


class DateConstants:
    """Constants for date handling"""
    DEFAULT_DATE_OF_BIRTH = "01.01.1985"
    DATE_FORMAT_ISO = "%Y-%m-%d"
    DATE_FORMAT_US = "%m/%d/%Y"
    DATE_FORMAT_EU = "%d.%m.%Y"


class LinkedInURLs:
    """LinkedIn URL constants"""
    LOGIN_URL = "https://www.linkedin.com/login"
    FEED_URL = "https://www.linkedin.com/feed/"
    JOBS_SEARCH_BASE = "https://www.linkedin.com/jobs/search/"


############################################################################################################
