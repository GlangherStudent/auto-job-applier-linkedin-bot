'''
Configuration: Easy Apply questions & inputs.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''


###################################################### APPLICATION INPUTS ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Give a relative path of your default resume. If the file is not found, the bot will continue
# using your previously uploaded resume in LinkedIn.
# IMPORTANT: In this project resumes are expected in DOCX format only,
# both locally (in `all resumes/cv`) and in the LinkedIn application section.
# The bot does NOT upload new files to LinkedIn; it only selects the correct resume
# based on the file name (the local file name must match the one already stored in LinkedIn).
default_resume_path = "all resumes/default/resume.docx"      # Example path – create this locally with your own CV.

# Folder with multiple CVs for AI-driven selection (for example, `all resumes/cv` with DOCX files)
resume_cv_folder = "all resumes/cv"

# What do you want to answer for questions that ask about years of experience you have?
# This is different from current_experience in the search configuration.
years_of_experience = "5"          # A number in quotes, for example: "0","1","2","3","4"

# Do you need visa sponsorship now or in future?
require_visa = "No"               # "Yes" or "No"

# What is the link to your portfolio website? Leave it empty as "" if you want to skip this question.
website = ""                        # Example: "https://your-portfolio.example" or "" to leave unanswered

# Please provide the link to your LinkedIn profile.
# Recommended: full URL with https:// for maximum compatibility with application forms.
linkedIn = ""       # Example: "https://www.linkedin.com/in/YOUR_USERNAME" or "" to leave unanswered

# What is the status of your citizenship?
# If left empty as "", the tool will not answer the question. However, some companies require an answer.
# Valid options are: "U.S. Citizen/Permanent Resident", "Non-citizen allowed to work for any employer", "Non-citizen allowed to work for current employer", "Non-citizen seeking work authorization", "Canadian Citizen/Permanent Resident" or "Other"
us_citizenship = "Other"



## SOME ANNOYING QUESTIONS BY COMPANIES 🫠 ##

# What to enter in your desired salary question (American and European), or expected CTC (other regions).
# UNIT: adapt these values to your own market and currency; only numbers are allowed in many forms.
desired_salary = 50000          # Example numeric value (do NOT use quotes)
desired_salary_max = 70000      # Example maximum value for ranges
'''
Note: If question has the word "lakhs" in it (Example: What is your expected CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
And if asked in months, then it will divide by 12 and answer. Examples:
* 2400000 will be answered as "200000"
* 850000 will be answered as "70833"
'''

# What is your current CTC? Some companies make this compulsory and numeric.
current_ctc = 0                 # Example annual value; set to 0 if you prefer not to share.
'''
Note: If question has the word "lakhs" in it (Example: What is your current CTC in lakhs), 
then it will add '.' before last 5 digits and answer. Examples: 
* 2400000 will be answered as "24.00"
* 850000 will be answered as "8.50"
# And if asked in months, then it will divide by 12 and answer. Examples:
# * 2400000 will be answered as "200000"
# * 850000 will be answered as "70833"
'''

# (In Development) # Currency of salaries you mentioned. Companies that allow string inputs will add this tag to the end of numbers. Eg: 
# currency = "INR"                 # "USD", "INR", "EUR", etc.

# What is your notice period in days?
notice_period = 30                   # Any number >= 0 without quotes, for example: 0, 7, 15, 30, 45
'''
Note: If question has 'month' or 'week' in it (Example: What is your notice period in months), 
then it will divide by 30 or 7 and answer respectively. Examples:
* For notice_period = 66:
  - "66" OR "2" if asked in months OR "9" if asked in weeks
* For notice_period = 15:"
  - "15" OR "0" if asked in months OR "2" if asked in weeks
* For notice_period = 0:
  - "0" OR "0" if asked in months OR "0" if asked in weeks
'''

# Your LinkedIn headline in quotes, for example:
# "Software Engineer @ Example, Masters in Computer Science"
linkedin_headline = "YOUR_LINKEDIN_HEADLINE"  # Or "" to leave this question unanswered

# Your summary in quotes. Use \n to add line breaks if using single quotes "Summary".
# You can skip \n when using triple quotes """Summary""" as below.
linkedin_summary = """
YOUR_LINKEDIN_SUMMARY
"""

'''
Note: If left empty as "", the tool will not answer the question. However, some companies require a summary. Use \n to add line breaks.
''' 

# Your cover letter in quotes. Use \n to add line breaks if using single quotes "Cover Letter".
# You can skip \n when using triple quotes """Cover Letter""" as below.
cover_letter = """
YOUR_COVER_LETTER
"""
'''
Note: If left empty as "", the tool will not answer the question. However, some companies require a cover letter. Use \n to add line breaks.
''' 

# Name of your most recent employer (optional)
recent_employer = "YOUR_PREVIOUS_EMPLOYER"  # For example: "Sample Company", or "" to leave unanswered

# Example question: "On a scale of 1-10 how much experience do you have building web or mobile applications?"
confidence_level = "5"             # Any number between "1" and "10", in quotes

# When can you start? / What is your availability?
availability_start = "Immediately"  # "Immediately", "Within 1 week", "Within 2 weeks", "Within 1 month", "More than 1 month", or a number of days like "20"

# Education (used by JobMatcher for "highest degree" / "education level" fields)
education = "Bachelor's degree or equivalent"

# Additional fields for complex forms (for example, Roland Berger style forms)
# Date of birth (format MM.DD.YYYY)
date_of_birth = "01.01.1990"
# Grade point average (example: 8.5 on a 1–10 scale, or 3.5 GPA)
grade_point_average = "8.5"
# Languages spoken (comma-separated)
languages_spoken = "English"
# University name (if not in a predefined list)
university_name = "Your University Name"

# JobMatcher: data from questions used to build text answers (merged with config.personals.PERSONALS)
QUESTIONS_PERSONAL = {
    "desired_salary": str(int(desired_salary)),
    "years_of_experience": str(years_of_experience) if years_of_experience else "5",
    "education": education,
    "date_of_birth": date_of_birth,
    "grade_point_average": grade_point_average,
    "languages_spoken": languages_spoken,
    "university_name": university_name,
}


##> ------ Enhanced by AI Audit - Yes/No Dropdown Strategy ------
# Strategy for answering Yes/No questions in dropdowns.
# Options: "optimistic", "realistic", "conservative"
# - "optimistic": Answer "Yes" to most questions (maximizes applications, but may lead to mismatches)
# - "realistic": Answer "Yes" only when the question matches your declared skills/experience
# - "conservative": Answer "No" for uncertain questions, "Yes" only when you are sure
dropdown_answer_strategy = "optimistic"  # Default: "optimistic"

# Skills and certifications you actually have (used for the "realistic" strategy).
# The bot will answer "Yes" ONLY if the question matches one of these keywords.
my_skills_and_certifications = [
    # Supply Chain & Operations
    "supply chain", "operations", "procurement", "logistics", "inventory", "warehouse",
    "vendor management", "supplier management", "category management", "sourcing",
    
    # Project management
    "project management", "program management", "pmp", "prince2", "agile", "scrum",
    
    # Industry experience  
    "automotive", "energy", "retail", "manufacturing", "distribution", "oil & gas",
    "petrom", "omv", "toyota", "metro",
    
    # Technical skills
    "sap", "erp", "wms", "power bi", "excel", "data analysis", "process improvement",
    "lean", "six sigma", "kaizen", "5s",
    
    # Management & leadership
    "team management", "budget management", "kpi", "cost reduction", "efficiency",
    "continuous improvement", "change management", "digital transformation",
    
    # Certifications & standards (add yours here)
    # "iso 9001", "iso 14001", "as9100",  # Aerospace standard – uncomment if you have it
    # "itar", "ear",  # US export control – uncomment if you have experience
]

# Years of experience for different domains (used for the "realistic" strategy).
# When a question asks for "10+ years in X", the bot checks these values.
my_experience_years = {
    "total_experience": 5,  # Total professional experience in years
    "supply_chain": 3,
    "operations": 3,
    "procurement": 2,
    "logistics": 2,
    "project_management": 2,
    "team_management": 2,
}

# Custom answers for specific questions (override the configured strategy).
# Use this dict for very specific questions where you want full control.
# Key = keywords from the question (lowercase, partial match is OK)
# Value = "Yes" or "No" (you can also use variables such as `require_visa`)
custom_dropdown_answers = {
    # Example: "willing to relocate" → "No"
    # "relocate": "No",
    # "travel 50%": "No",
    # "clearance": "No",   # Nu am US security clearance

    # Questions like “have you worked at [this company]?” → default answer is No
    "worked at": "No",
    "have you worked at": "No",
    "have you ever worked at": "No",
    "ever worked at": "No",
    "employed by": "No",
    "employed at": "No",
    "previous employment at": "No",
    "worked for this company": "No",
    "worked for us": "No",
    "worked here": "No",
    "experience at this company": "No",
    "have you previously worked": "No",
    "prior employment at": "No",

    # Questions such as:
    # "Do you now, or will you in the future, require sponsorship for employment visa status (e.g. H-1B)...?"
    # These should answer using the value configured in `require_visa` (default "No").
    "require sponsorship": require_visa,
    "visa sponsorship": require_visa,
    "sponsorship for employment visa": require_visa,
    "employment visa status": require_visa,
    "h-1b": require_visa,
    "h1b": require_visa,
    "h1-b": require_visa,
    "work visa": require_visa,
}
##<
##



# >>>>>>>>>>> RELATED SETTINGS <<<<<<<<<<<

## Allow Manual Inputs
# Should the tool pause before every submit application during easy apply to let you check the information?
pause_before_submit = False         # True or False - DEZACTIVAT pentru flux continuu automat
'''
Note: Will be treated as False if `run_in_background = True`
'''

# Should the tool pause if it needs help in answering questions during easy apply?
# Note: If set as False will answer randomly...
pause_at_failed_question = False    # True or False - DEZACTIVAT pentru flux continuu automat
'''
Note: Will be treated as False if `run_in_background = True`
'''
##

# Do you want to overwrite previous answers?
overwrite_previous_answers = False # True or False, Note: True or False are case-sensitive







############################################################################################################