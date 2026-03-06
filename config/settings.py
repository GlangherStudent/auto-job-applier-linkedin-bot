'''
Global bot settings.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''


###################################################### CONFIGURE YOUR BOT HERE ######################################################

# >>>>>>>>>>> LinkedIn Settings <<<<<<<<<<<

# Keep the External Application tabs open?
close_tabs = False                  # True or False, Note: True or False are case-sensitive
'''
Note: RECOMMENDED TO LEAVE IT AS `True`, if you set it `False`, be sure to CLOSE ALL TABS BEFORE CLOSING THE BROWSER!!!
'''

# Follow easy applied companies
follow_companies = False            # True or False, Note: True or False are case-sensitive

# Do you want the program to run continuously until you stop it? (Beta)
run_non_stop = True                 # True or False, Note: True or False are case-sensitive - Enabled to maximize applications until the daily limit
'''
Note: Will be treated as False if `run_in_background = True`
'''
alternate_sortby = True             # True or False, Note: True or False are case-sensitive
cycle_date_posted = True            # True or False, Note: True or False are case-sensitive
stop_date_cycle_at_24hr = True      # True or False, Note: True or False are case-sensitive





# >>>>>>>>>>> RESUME GENERATOR (Experimental & In Development) <<<<<<<<<<<

# Give the path to the folder where all the generated resumes are to be stored
generated_resume_path = "all resumes/" # (In Development)





# >>>>>>>>>>> Global Settings <<<<<<<<<<<

# Directory and name of the files where history of applied jobs is saved (Sentence after the last "/" will be considered as the file name).
file_name = "all excels/all_applied_applications_history.csv"
failed_file_name = "all excels/all_failed_applications_history.csv"
logs_folder_path = "logs/"

# Set the maximum amount of time allowed to wait between each click in secs
click_gap = 3                       # Enter the maximum allowed seconds to wait approximately (only non-negative integers, for example 0, 1, 2, 3). Optimized for natural anti-detection behavior.

# If you want to see Chrome running then set run_in_background as False (May reduce performance). 
run_in_background = False           # True or False, Note: True or False are case-sensitive ,   If True, this will make pause_at_failed_question, pause_before_submit and run_in_background as False

# If you want to disable extensions then set disable_extensions as True (Better for performance)
disable_extensions = False          # True or False, Note: True or False are case-sensitive

# Run in safe mode. Set this True if Chrome is taking too long to open or if you have multiple profiles in the browser. This will open Chrome in a guest profile.
safe_mode = False                   # True or False, Note: True or False are case-sensitive - Set to False to use your existing Chrome profile

# Do you want scrolling to be smooth or instantaneous? (Can reduce performance if True)
smooth_scroll = False               # True or False, Note: True or False are case-sensitive

# If enabled (True), the program keeps your screen active and prevents the PC from sleeping. Instead, you can disable this feature (set it to False) and adjust your OS sleep settings.
keep_screen_awake = True            # True or False, Note: True or False are case-sensitive (temporarily deactivates when dialogs are present, for example Pause before submit or Help needed for a question)

# Run in undetected mode to bypass anti-bot protections (Preview Feature, UNSTABLE. Recommended to leave it as False)
stealth_mode = False                # True or False, Note: True or False are case-sensitive

# Do you want to get alerts on errors?
showErrorAlerts = False              # True or False - Disabled (errors are written only to logs)

##> ------ Enhanced by AI Audit - Session Management Settings ------
# Session management and anti-detection settings
enable_anti_detection = True         # Enable human behavior simulation
daily_application_limit = 100        # Maximum applications per day (LinkedIn limit is typically around 100–150)
session_length_minutes = 45          # Minutes of activity before a break (30–60 is a good range for longer, natural sessions)
enable_session_breaks = True         # Enable automatic short breaks for anti-detection
enable_workday_simulation = False    # Simulate realistic work hours (for example, 8 AM–8 PM). Disabled here to maximize applications.
##<












############################################################################################################