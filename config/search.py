'''
Configuration: LinkedIn search preferences & filters.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''


###################################################### LINKEDIN SEARCH PREFERENCES ######################################################

# These Sentences are Searched in LinkedIn
# Enter your search terms inside '[ ]' with quotes ' "searching title" ' for each search followed by comma ', ' Eg: ["Software Engineer", "Software Developer", "Selenium Developer"]
search_terms = ["Operations Manager", "Supply Chain Manager", "Program Manager", "Head of Operations", "Logistics Manager", "Senior Project Manager", "Operational Excellence Lead", "Director Operatiuni", "Director Logistica", "Head of Supply Chain", "PMO Manager", "PMO Lead", "Transformation Manager", "Continuous Improvement Manager", "Logistics Operations Manager", "Distribution Manager", "Warehouse Manager", "Demand Planning Manager", "Strategic Sourcing Manager", "Procurement Manager", "Transport Manager", "Plant Manager, Director de Fabrica", "Factory Manager", "Production Manager", "Manufacturing Manager", "Site Manager", "Unit Manager", "Area Manager, Operatiuni", "Digital Transformation Manager", "Digital Operations Lead", "IT Project Manager", "Process Automation Manager", "ERP Implementation Manager", "WMS Project Manager", "Industry 4.0 Manager", "Innovation Manager", "Business Project Manager", "Implementation Manager", "Change Manager", "Portfolio Manager", "Business Analyst Lead", "Operational Director", "Chief Operating Officer (COO)", "Vice President (VP) of Operations", "Vice President (VP) of Supply Chain", "General Manager (GM)", "Director General"]

# Search location, this will be filled in "City, state, or zip code" search box. If left empty as "", tool will not fill it.
search_location = "Bucharest, Romania"            # Valid format: "City, Country" - LinkedIn requires proper location format

# After how many applications in the current search should the bot switch to the next search term?
##> ------ Enhanced by AI Audit - Maximum Applications Strategy ------
switch_number = 1000                # Very high number to apply to all available jobs for each term
'''
MAXIMUM APPLICATIONS STRATEGY:
- switch_number = 1000 → the bot keeps applying until:
  * there are no more jobs available (pagination finished)
  * the daily limit is reached
  * LinkedIn explicitly asks you to stop
- The bot walks through all pages for each search term.
- Maximises the number of applications within LinkedIn’s daily limits.
- Randomisation ensures diversity in search terms.
'''
##<

# Do you want to randomize the search order for search_terms?
randomize_search_order = True     # True or False, Note: True or False are case-sensitive – enabled for better coverage and anti-detection.


# >>>>>>>>>>> Job Search Filters <<<<<<<<<<<
''' 
You could set your preferences or leave them as empty to not select options except for 'True or False' options. Below are some valid examples for leaving them empty:
This is below format: QUESTION = VALID_ANSWER

## Examples of how to leave them empty. Note that True or False options cannot be left empty! 
* question_1 = ""                    # answer1, answer2, answer3, etc.
* question_2 = []                    # (multiple select)
* question_3 = []                    # (dynamic multiple select)

## Some valid examples of how to answer questions:
* question_1 = "answer1"                  # "answer1", "answer2", "answer3" or ("" to not select). Answers are case sensitive.
* question_2 = ["answer1", "answer2"]     # (multiple select) "answer1", "answer2", "answer3" or ([] to not select). Note that answers must be in [] and are case sensitive.
* question_3 = ["answer1", "Random AnswER"]     # (dynamic multiple select) "answer1", "answer2", "answer3" or ([] to not select). Note that answers must be in [] and need not match the available options.

'''

sort_by = ""                       # "Most recent", "Most relevant" or ("" to not select)
##> ------ Enhanced by AI Audit - Date Posted Filter Disabled ------
date_posted = ""                   # Disabled to find more jobs (including older postings).
# Valid values: "Any time", "Past month", "Past week", "Past 24 hours" or ("" to not select)
##<
salary = ""                        # "$40,000+", "$60,000+", "$80,000+", "$100,000+", "$120,000+", "$140,000+", "$160,000+", "$180,000+", "$200,000+"

easy_apply_only = True             # True or False, Note: True or False are case-sensitive

experience_level = ["Mid-Senior level", "Director", "Executive"]              # (multiple select) "Internship", "Entry level", "Associate", "Mid-Senior level", "Director", "Executive"
job_type = ["Full-time", "Part-time", "Contract", "Temporary"]                      # (multiple select) "Full-time", "Part-time", "Contract", "Temporary", "Volunteer", "Internship", "Other"
on_site = ["On-site", "Remote", "Hybrid"]                       # (multiple select) "On-site", "Remote", "Hybrid"

companies = []                     # (dynamic multiple select) make sure the name you type in list exactly matches with the company name you're looking for, including capitals. 
                                   # Eg: "7-eleven", "Google","X, the moonshot factory","YouTube","CapitalG","Adometry (acquired by Google)","Meta","Apple","Byte Dance","Netflix", "Snowflake","Mineral.ai","Microsoft","JP Morgan","Barclays","Visa","American Express", "Snap Inc", "JPMorgan Chase & Co.", "Tata Consultancy Services", "Recruiting from Scratch", "Epic", and so on...
location = ["Bucharest"]  # (dynamic multiple select) – example location; adjust to your preferences
industry = []                      # (dynamic multiple select)
job_function = []                  # (dynamic multiple select)
job_titles = []                    # (dynamic multiple select)
benefits = []                      # (dynamic multiple select)
commitments = []                   # (dynamic multiple select)

under_10_applicants = False        # True or False, Note: True or False are case-sensitive
in_your_network = False            # True or False, Note: True or False are case-sensitive
fair_chance_employer = False       # True or False, Note: True or False are case-sensitive


## >>>>>>>>>>> RELATED SETTING <<<<<<<<<<<

# Pause after applying filters to let you manually adjust search results and filters?
pause_after_filters = False         # True or False – disabled for fully automatic flow

##> ------ Flow Options (Analysis Recommendations) ------
# Easy Apply direct: click the Easy Apply button in the filter bar (without All filters).
# True = faster, simpler, similar to the manual flow.
use_easy_apply_direct = True        # True = direct | False = prin All filters (vechi)

# Full user-like flow: Search bar → Jobs → Easy Apply.
# True = highest similarity with manual behaviour (search → Jobs → Easy Apply).
# False = direct jobs URL (faster, default).
use_human_like_flow = False         # True = user-like flow | False = direct URL (faster)
##<

##




## >>>>>>>>>>> SKIP IRRELEVANT JOBS <<<<<<<<<<<
 
# Avoid applying to these companies, and companies with these bad words in their 'About Company' section...
about_company_bad_words = ["Crossover"]       # (dynamic multiple search) or leave empty as []. Ex: ["Staffing", "Recruiting", "Name of Company you don't want to apply to"]

# Skip checking for `about_company_bad_words` for these companies if they have these good words in their 'About Company' section... [Exceptions, For example, I want to apply to "Robert Half" although it's a staffing company]
about_company_good_words = []      # (dynamic multiple search) or leave empty as []. Ex: ["Robert Half", "Dice"]

# Avoid applying to these companies if they have these bad words in their 'Job Description' section...  (In development)
bad_words = ["US Citizen","USA Citizen","No C2C", "No Corp2Corp", ".NET", "Embedded Programming", "PHP", "Ruby", "CNC"]                     # (dynamic multiple search) or leave empty as []. Case Insensitive. Ex: ["word_1", "phrase 1", "word word", "polygraph", "US Citizenship", "Security Clearance"]

# Do you have an active Security Clearance? (True for Yes and False for No)
security_clearance = False         # True or False, Note: True or False are case-sensitive

# Do you have a Masters degree? (True for Yes and False for No). If True, the tool will apply to jobs
# containing the word 'master' in their job description when experience requirements match.
did_masters = True                 # True or False, Note: True or False are case-sensitive

# Avoid applying to jobs if their required experience is above your current_experience.
# Set value as -1 if you want to apply to all jobs regardless of required experience.
##> ------ Enhanced by AI Audit - Apply to All Jobs ------
current_experience = -1             # -1 = apply to all jobs, ignore required experience
##<

# Location filters based on work style (on-site vs remote)
# For ON-SITE and HYBRID jobs, only apply to these locations:
onsite_locations = ["Bucharest", "Ilfov"]  # List of acceptable cities/regions for on-site work

# For REMOTE jobs, only apply to these countries/regions:
remote_locations = ["Romania", "Germany", "Netherlands", "Austria", "Poland", "Belgium", "France", "Spain", "Italy", "Portugal", "Czech Republic", "Hungary", "United Kingdom", "Ireland", "Sweden", "Denmark", "Finland", "Norway", "Switzerland"]  # European countries
# Note: LinkedIn doesn't have a general "Europe" filter, so we list major European countries

# Enable location filtering based on work style?
##> ------ Enhanced by AI Audit - Accept All Locations ------
enable_location_filtering = False   # Disabled – accept all locations for more jobs
##<

##> ------ Strict job location filter (example: only Bucharest) ------
# If True, ONLY jobs whose displayed location matches the list below are accepted.
# Any other location (including broad regions such as Europe/EMEA/EU) is ignored.
strict_location_filter = True
# Accepted locations exactly (they may appear with extra text, for example "Bucharest, Romania (Hybrid)").
allowed_work_locations = [
    "Bucharest, Romania",
    "Bucharest, Bucharest, Romania",
    "Bucharest Metropolitan Area",
    "Romania",
]
##<
##






############################################################################################################