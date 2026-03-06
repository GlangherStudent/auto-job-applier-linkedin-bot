'''
Smart answer matching module for select/radio/checkbox questions.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.02.10
'''

from typing import Tuple
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs


# Extended keyword lists for better question matching
KEYWORD_GROUPS = {
    'first_name': [
        'first name', 'given name', 'forename', 'christian name',
        'nombre', 'prénom', 'vorname'
    ],
    
    'last_name': [
        'last name', 'surname', 'family name', 'apellido',
        'nom de famille', 'nachname', 'cognome'
    ],
    
    'full_name': [
        'full name', 'complete name', 'legal name', 'name in full',
        'your name', 'applicant name', 'candidate name'
    ],
    
    'phone': [
        'phone', 'mobile', 'telephone', 'cell', 'contact number',
        'phone number', 'mobile number', 'tel', 'telefon'
    ],
    
    'email': [
        'email', 'e-mail', 'email address', 'electronic mail',
        'mail', 'correo', 'courriel'
    ],
    
    'city': [
        'city', 'town', 'location', 'locality', 'ciudad',
        'ville', 'città', 'stad', 'current city',
        'where are you located', 'where do you live',
        'your location', 'based in',
        # Permanent/work location variants (common in Greenhouse/Lever)
        'permanent', 'work location', 'permanent work location',
        'city, state', 'city state'
    ],
    
    'address': [
        'address', 'street address', 'street', 'home address',
        'residential address', 'dirección', 'adresse'
    ],
    
    'state': [
        'state', 'province', 'region', 'county', 'estado',
        'région', 'bundesland'
    ],
    
    'country': [
        'country', 'nation', 'país', 'pays', 'land'
    ],
    
    'zipcode': [
        'zip', 'postal', 'postcode', 'zip code', 'postal code',
        'código postal', 'code postal', 'plz'
    ],
    
    'salary': [
        'salary', 'compensation', 'pay', 'wage', 'ctc', 'package',
        'remuneration', 'earnings', 'income', 'salario',
        'how much', 'expected pay', 'desired salary',
        'salary expectation', 'compensation expectation'
    ],
    
    'current_salary': [
        'current salary', 'current ctc', 'current compensation',
        'current pay', 'present salary', 'existing salary',
        'how much do you earn', 'current earnings'
    ],
    
    'date_of_birth': [
        'date of birth', 'birth', 'birthday', 'mm.dd.yyyy',
        'date of birth (mm.dd.yyyy)', 'dob'
    ],
    
    'grade_point_average': [
        'grade', 'gpa', 'grade point average', 'point average',
        'grade average', 'baccalaureate grade'
    ],
    
    'languages': [
        'language', 'languages', 'speak', 'lingua', 'limb',
        'type in a language', 'languages you speak'
    ],
    
    'experience': [
        'experience', 'years of experience', 'work experience',
        'professional experience', 'how many years',
        'years in', 'experiencia', 'expérience'
    ],
    
    'notice_period': [
        'notice period', 'notice', 'availability', 'joining',
        'how soon', 'when can you start', 'start date',
        'available to join', 'earliest start'
    ],
    
    'visa': [
        'visa', 'sponsorship', 'work authorization', 'work permit',
        'authorized to work', 'legal to work', 'right to work',
        # Extra common phrasings
        'legally authorized', 'legally eligible',
        'require sponsorship', 'need sponsorship',
        'employment visa', 'h-1b', 'h1b', 'h1-b',
        'in the united states', 'work in the united states', 'us work authorization'
    ],
    
    'linkedin': [
        'linkedin', 'linkedin profile', 'linkedin url',
        'linkedin page', 'linkedin link'
    ],
    
    'website': [
        'website', 'portfolio', 'personal website', 'blog',
        'url', 'web page', 'online portfolio', 'github'
    ],
    
    'gender': [
        'gender', 'sex', 'male/female', 'identify as',
        'gender identity'
    ],
    
    'ethnicity': [
        'ethnicity', 'race', 'ethnic background', 'ethnic origin',
        'racial background'
    ],
    
    'disability': [
        'disability', 'disabled', 'handicap', 'physical disability',
        'mental disability', 'impairment'
    ],
    
    'veteran': [
        'veteran', 'military', 'armed forces', 'protected veteran',
        'military service'
    ],
    
    'citizenship': [
        'citizenship', 'citizen', 'nationality', 'employment eligibility',
        'authorized to work', 'us citizen', 'work status'
    ],
    
    'employer': [
        'employer', 'company', 'current employer', 'current company',
        'where do you work', 'organization'
    ],
    
    'degree': [
        'degree', 'education', 'qualification', 'diploma',
        'bachelor', 'master', 'phd', 'university'
    ],
    
    'start_date': [
        'start', 'begin', 'commence', 'available', 'joining date',
        'when can you start', 'availability', 'earliest start'
    ],
    
    'referral': [
        'referral', 'referred', 'who referred', 'employee referral',
        'how did you hear', 'how did you find', 'source'
    ],
    
    'cover_letter': [
        'cover letter', 'motivation', 'why do you want',
        'why are you interested', 'tell us about yourself'
    ],
    
    'linkedin_headline': [
        'headline', 'professional headline', 'linkedin headline',
        'job title', 'current role'
    ],
}


# Keywords for “have you worked at [company]?” – checked first so they are not confused with employer/company questions
WORKED_AT_COMPANY_KEYWORDS = [
    'worked at', 'have you worked at', 'have you ever worked at', 'ever worked at',
    'employed by', 'employed at', 'previous employment at', 'worked for this company',
    'worked for us', 'worked here', 'experience at this company',
    'lucrat la', 'ai lucrat la', 'ai lucrat', 'ai mai lucrat',
    'have you previously worked', 'prior employment at',
]


def smart_match_question(label: str) -> Tuple[str, str]:
    '''
    Matches question label to answer type using extended keywords.
    Returns (answer_type, confidence) tuple.
    
    Args:
        label: Question label text (lowercase)
    
    Returns:
        (answer_type, confidence): 
        - answer_type: Type of answer needed ('first_name', 'salary', etc.)
        - confidence: 'high' or 'low'
    '''
    label = label.lower().strip()
    
    # Priority: questions like “have you worked at this company?” → always answer "No" (not current employer)
    for keyword in WORKED_AT_COMPANY_KEYWORDS:
        if keyword in label:
            return ('worked_at_company', 'high')
    
    # Check each keyword group
    for answer_type, keywords in KEYWORD_GROUPS.items():
        for keyword in keywords:
            if keyword in label:
                # High confidence if exact keyword match
                return (answer_type, 'high')
    
    # No match found
    return ('unknown', 'low')


def get_contextual_answer(label: str, answer_type: str, field_type: str = 'text') -> str:
    '''
    Gets contextual answer with additional logic.
    
    Args:
        label: Question label
        answer_type: Type from smart_match_question
        field_type: 'text', 'select', 'radio', 'textarea'
    
    Returns:
        Answer string or empty string
    '''
    # Import variabile personale din config.personals
    from config.personals import (
        first_name, middle_name, last_name, phone_number,
        current_city, street, state, zipcode, country,
        gender, ethnicity, disability_status, veteran_status
    )
    # Import question-related variables from config.questions
    from config.questions import (
        years_of_experience, desired_salary, current_ctc,
        notice_period, require_visa, linkedIn, website,
        linkedin_headline, linkedin_summary, cover_letter,
        recent_employer
    )
    try:
        from config.questions import date_of_birth, grade_point_average, languages_spoken, university_name
    except ImportError:
        date_of_birth = DateConstants.DEFAULT_DATE_OF_BIRTH
        grade_point_average = "8.5"
        languages_spoken = "English, Romanian"
        university_name = "N/A"
    
    # Map answer types to actual values
    answer_map = {
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"{first_name} {middle_name} {last_name}".replace('  ', ' ').strip(),
        'phone': phone_number,
        'email': '',  # Usually auto-filled by LinkedIn
        'city': current_city if current_city else "Bucharest, Romania",
        'address': street,
        'state': state,
        'country': country,
        'zipcode': zipcode,
        'salary': str(int(desired_salary)),
        'current_salary': str(int(current_ctc)),
        'experience': years_of_experience,
        'notice_period': str(notice_period),
        'visa': require_visa,
        'linkedin': linkedIn,
        'website': website,
        'gender': gender,
        'ethnicity': ethnicity,
        'disability': disability_status,
        'veteran': veteran_status,
        'citizenship': 'Other',  # Default safe answer
        'employer': recent_employer,
        'worked_at_company': 'No',
        'start_date': 'Immediately',
        'cover_letter': cover_letter,
        'linkedin_headline': linkedin_headline,
        'degree': '',  # Usually specific to question
        'referral': '',  # Leave empty usually
        'date_of_birth': date_of_birth,
        'grade_point_average': str(grade_point_average) if grade_point_average else '8.5',
        'languages': languages_spoken or 'English, Romanian',
        'language': languages_spoken or 'English, Romanian',
        'university_name': university_name or 'N/A',
    }
    
    return answer_map.get(answer_type, '')


def match_select_option(label: str, options: list, answer: str) -> str:
    '''
    Matches answer to available select options using fuzzy logic.
    
    Args:
        label: Question label
        options: List of available options
        answer: Desired answer
    
    Returns:
        Best matching option or first option
    '''
    if not options:
        return answer
    
    answer_lower = answer.lower()
    
    # Exact match
    for option in options:
        if option.lower() == answer_lower:
            return option
    
    # Partial match
    for option in options:
        if answer_lower in option.lower() or option.lower() in answer_lower:
            return option
    
    # Common answer variations (including variants that indicate you have NOT worked at the company)
    if answer.lower() in ['yes', 'no', 'decline']:
        variations = {
            'yes': ['yes', 'agree', 'i do', 'i have', 'affirmative'],
            'no': ['no', 'disagree', "i don't", 'i do not', 'negative', 'never', 'have not worked', 'not worked', 'never worked', 'do not have', "haven't"],
            'decline': ['decline', 'prefer not', 'not wish', "don't wish"]
        }
        
        for option in options:
            option_lower = option.lower()
            for variant in variations.get(answer.lower(), []):
                if variant in option_lower:
                    return option
    
    # No good match, return first non-default option
    if len(options) > 1 and options[0].lower() in ['select an option', 'select', 'choose']:
        return options[1]
    
    return options[0] if options else answer


##> ------ Enhanced by AI Audit - Intelligent Yes/No Answering ------
def intelligent_yes_no_answer(label: str, options: list) -> str:
    '''
    Answer Yes/No dropdown questions intelligently using the configured strategy.
    
    Args:
        label: The question text (lowercased for matching).
        options: List of available options.
    
    Returns:
        "Yes" or "No" based on the configured strategy.
    '''
    try:
        from config.questions import (
            dropdown_answer_strategy, 
            my_skills_and_certifications, 
            my_experience_years,
            custom_dropdown_answers
        )
    except ImportError:
        # Fallback if configuration does not exist
        return "Yes"
    
    label_lower = label.lower()
    
    # 1. Check custom overrides FIRST (highest priority)
    for keyword, custom_answer in custom_dropdown_answers.items():
        if keyword.lower() in label_lower:
            return custom_answer
    
    # 2. Strategy: conservative → answer "No" for uncertain cases
    if dropdown_answer_strategy == "conservative":
        # Keywords where we answer "Yes" only when there is a clear match
        safe_keywords = ["authorized to work", "legally eligible", "over 18", "background check"]
        for safe in safe_keywords:
            if safe in label_lower:
                return "Yes"
        # For anything else in conservative mode, answer "No"
        return "No"
    
    # 3. Strategy: realistic → check skills and experience
    if dropdown_answer_strategy == "realistic":
        # A. Check questions about years of experience (for example, "10+ years in X")
        import re
        years_match = re.search(r'(\d+)\s*\+?\s*(or more)?\s*years?', label_lower)
        if years_match:
            required_years = int(years_match.group(1))
            # Check whether we have enough experience in the requested domain
            for domain, my_years in my_experience_years.items():
                if domain in label_lower and my_years >= required_years:
                    return "Yes"
            # If there is no specific domain match, check total experience
            if my_experience_years.get("total_experience", 0) >= required_years:
                return "Yes"
            else:
                return "No"
        
        # B. Check questions about specific skills/certifications/experience
        # Example: "Do you have experience with SAP?", "Are you proficient in ITAR?"
        for skill in my_skills_and_certifications:
            if skill.lower() in label_lower:
                return "Yes"
        
        # C. If nothing matches our skills → "No" (realistic approach)
        # EXCEPTION: general eligibility/background check questions etc.
        generic_yes_keywords = [
            "authorized to work", "legally eligible", "over 18", "background check",
            "drug test", "willing to", "able to", "available to", "interested in"
        ]
        for keyword in generic_yes_keywords:
            if keyword in label_lower:
                return "Yes"
        
        # Default for realistic: if we are not sure, answer "No"
        return "No"
    
    # 4. Strategy: optimistic (default) → answer "Yes" for almost everything
    # EXCEPTION: questions where "No" is clearly safer (for example, criminal record, visa needs)
    negative_keywords = [
        "criminal", "convicted", "felony", "misdemeanor", 
        "dismissed", "terminated", "fired"
    ]
    for neg in negative_keywords:
        if neg in label_lower:
            return "No"
    
    # Default optimistic: "Yes"
    return "Yes"


def detect_yes_no_options(options: list) -> bool:
    '''
    Detect whether a dropdown represents a Yes/No choice.
    
    Args:
        options: List of available options.
    
    Returns:
        True if it looks like a Yes/No dropdown, False otherwise.
    '''
    if len(options) < 2:
        return False
    
    options_lower = [opt.lower() for opt in options]
    # Include more real-world variants seen in application forms
    yes_indicators = [
        'yes', 'y', 'i do', 'i have', 'agree', 'affirmative',
        'authorized', 'eligible', 'i am', "i'm", 'true'
    ]
    no_indicators = [
        'no', 'n', "i don't", "i do not", 'disagree', 'negative',
        'not authorized', 'not eligible', 'false'
    ]
    
    has_yes = any(yes_ind in opt for opt in options_lower for yes_ind in yes_indicators)
    has_no = any(no_ind in opt for opt in options_lower for no_ind in no_indicators)
    
    return has_yes and has_no
##<
