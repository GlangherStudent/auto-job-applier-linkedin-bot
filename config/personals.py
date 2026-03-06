'''
Configuration: personal data for job applications.
version: 2024.11.28.16.00
'''


###################################################### CONFIGURE YOUR TOOLS HERE ######################################################


# >>>>>>>>>>> Easy Apply Questions & Inputs <<<<<<<<<<<

# Your legal name (replace with your real details locally, do not commit them)
first_name = "YOUR_FIRST_NAME"        # Your first name in quotes, for example: "Alex"
middle_name = ""                      # Optional middle name, for example: "Lee", or "" to leave empty
last_name = "YOUR_LAST_NAME"         # Your last name in quotes, for example: "Smith"

# Phone number (required by many forms) – use your real number locally, but NEVER commit it.
phone_number = "+10000000000"        # Example format, replace with your real phone number locally

# What is your current city?
# IMPORTANT: For LinkedIn autocomplete fields (for example, "Location (city)"),
# the accepted value is usually in English and must be selected from the suggestions.
current_city = "Your City, Your Country"  # For example: "Berlin, Germany". Set your real city locally.
'''
Note: If left empty as "", the bot will try to use the job location, which can cause errors.
'''

# Address. Some applications make this required.
street = "Your Street and Number"
state = "Your State or Region"
zipcode = "000000"
country = "Your Country"

## US Equal Opportunity questions
# What is your ethnicity or race? If left empty as "", the tool will not answer the question.
ethnicity = "Decline"              # "Decline", "Hispanic/Latino", "American Indian or Alaska Native", "Asian", "Black or African American", "Native Hawaiian or Other Pacific Islander", "White", "Other"

# How do you identify yourself? If left empty as "", the tool will not answer the question.
gender = "Decline"                 # "Male", "Female", "Other", "Decline" or ""

# Are you physically disabled or have a history/record of having a disability?
disability_status = "Decline"      # "Yes", "No", "Decline"

veteran_status = "Decline"         # "Yes", "No", "Decline"
##


'''
For string variables followed by comments with options, only use the answers from given options.
Some valid examples are:
* variable1 = "option1"         # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#
* variable2 = ""                # "option1", "option2", "option3" or ("" to not select). Answers are case sensitive.#

Other variables are free text. No restrictions other than compulsory use of quotes.
Some valid examples are:
* variable3 = "Random Answer 5"         # Enter your answer. Eg: "Answer1", "Answer2"

Invalid inputs will result in an error!
'''

# JobMatcher: dictionary for text answers (used by modules/job_matcher.py)
_full_name = (first_name + " " + (middle_name + " " if middle_name else "") + last_name).replace("  ", " ").strip()
PERSONALS = {
    "city": current_city or "Your City, Your Country",
    "phone": phone_number,
    "first_name": first_name,
    "last_name": last_name,
    "full_name": _full_name,
}


############################################################################################################