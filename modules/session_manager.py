'''
Session management module (breaks, daily limits, checkpoints).
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''

import time
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from modules.helpers import print_lg


class SessionManager:
    '''
    Manages application sessions, breaks, and daily limits to avoid detection.
    Enhanced with progress checkpointing and auto-resume capability.
    '''
    
    def __init__(self, daily_limit: int = 100, session_length: int = 20, logs_folder: str = None):
        '''
        Initialize session manager.
        - daily_limit: Maximum applications per day
        - session_length: Minutes of activity before break
        - logs_folder: Folder for session_state.json and checkpoint.json (default from config.settings)
        '''
        self.daily_limit = daily_limit
        self.session_length = session_length  # minutes
        if logs_folder is None:
            try:
                from config.settings import logs_folder_path
                logs_folder = logs_folder_path
            except ImportError:
                logs_folder = "logs"
        logs_path = Path(logs_folder)
        self.session_file = logs_path / "session_state.json"
        self.checkpoint_file = logs_path / "checkpoint.json"
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.session_start = datetime.now()
        self.applications_this_session = 0
        self.applications_today = 0
        self.last_break = datetime.now()
        
        ##> ------ Enhanced by AI Audit - Checkpoint Tracking ------
        self.current_search_term = None
        self.current_page = 1
        self.processed_job_ids = set()
        ##<
        
        # Load previous session data
        self._load_session_state()
        self._load_checkpoint()
    
    
    def _load_session_state(self) -> None:
        '''
        Loads previous session state if exists and is from today.
        '''
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if data is from today
                last_date = datetime.fromisoformat(data.get('date', '2000-01-01'))
                if last_date.date() == datetime.now().date():
                    self.applications_today = data.get('applications_today', 0)
                    print_lg(f"Resumed session: {self.applications_today} applications already done today")
                else:
                    print_lg("New day, resetting counters")
                    self.applications_today = 0
            else:
                print_lg("Starting fresh session")
                
        except Exception as e:
            print_lg(f"Failed to load session state: {e}")
            self.applications_today = 0
    
    
    def _save_session_state(self) -> None:
        '''
        Saves current session state to file.
        '''
        try:
            data = {
                'date': datetime.now().isoformat(),
                'applications_today': self.applications_today,
                'session_start': self.session_start.isoformat(),
                'last_break': self.last_break.isoformat()
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print_lg(f"Failed to save session state: {e}")
    
    
    def record_application(self) -> bool:
        '''
        Records a new application. Returns False if daily limit reached.
        '''
        self.applications_this_session += 1
        self.applications_today += 1
        self._save_session_state()
        
        print_lg(f"Applications: Session={self.applications_this_session}, Today={self.applications_today}/{self.daily_limit}")
        
        return self.applications_today < self.daily_limit
    
    
    def should_take_break(self) -> tuple[bool, str, int]:
        '''
        Determines if a break is needed.
        Returns (should_break, reason, duration_seconds)
        '''
        current_time = datetime.now()
        
        # Check daily limit
        if self.applications_today >= self.daily_limit:
            return (True, "Daily limit reached", 0)
        
        # Warning at 80% of daily limit
        if self.applications_today >= int(self.daily_limit * 0.8):
            print_lg(f"⚠️ WARNING: Approaching daily limit ({self.applications_today}/{self.daily_limit})")
        
        # Check session length (every 15-25 applications)
        if self.applications_this_session >= random.randint(15, 25):
            duration = random.randint(300, 600)  # 5-10 minutes
            return (True, "Session break (natural rhythm)", duration)
        
        # Check time since session start (20-40 minutes of activity)
        session_duration = (current_time - self.session_start).seconds / 60
        if session_duration >= random.randint(20, 40):
            duration = random.randint(600, 1800)  # 10-30 minutes
            return (True, "Extended break (session timeout)", duration)
        
        # Check time since last break
        time_since_break = (current_time - self.last_break).seconds / 60
        if time_since_break >= random.randint(30, 45):
            duration = random.randint(180, 420)  # 3-7 minutes
            return (True, "Regular break", duration)
        
        # Small random break (5% chance)
        if random.random() < 0.05:
            duration = random.randint(60, 180)  # 1-3 minutes
            return (True, "Random micro-break", duration)
        
        return (False, "", 0)
    
    
    def take_break(self, duration: int, reason: str) -> None:
        '''
        Takes a break for specified duration.
        '''
        print_lg(f"\n{'='*60}")
        print_lg(f"☕ TAKING BREAK: {reason}")
        print_lg(f"⏰ Duration: {duration // 60} minutes {duration % 60} seconds")
        print_lg(f"⏸️  Break started at: {datetime.now().strftime('%H:%M:%S')}")
        print_lg(f"▶️  Will resume at: {(datetime.now() + timedelta(seconds=duration)).strftime('%H:%M:%S')}")
        print_lg(f"{'='*60}\n")
        
        # Split break into chunks to show progress
        chunks = min(10, duration // 10)
        chunk_duration = duration / chunks
        
        for i in range(chunks):
            time.sleep(chunk_duration)
            progress = ((i + 1) / chunks) * 100
            remaining = duration - ((i + 1) * chunk_duration)
            if i % 3 == 0:  # Print every 3rd chunk
                print_lg(f"Break progress: {progress:.0f}% - {remaining:.0f}s remaining")
        
        # Update tracking
        self.last_break = datetime.now()
        self.applications_this_session = 0
        self.session_start = datetime.now()
        
        print_lg(f"✅ Break finished. Resuming applications...\n")
    
    
    def get_inter_application_delay(self) -> float:
        '''
        Returns recommended delay between applications (in seconds).
        Uses normal distribution for natural variation.
        Optimized for a high number of applications while keeping anti-detection behaviour.
        '''
        # Base delay: 25-50 seconds (high volume, but still natural)
        mean = 35
        std = 8
        delay = max(20, min(70, random.gauss(mean, std)))
        
        # Increase delay if approaching daily limit (pentru anti-detection)
        if self.applications_today >= int(self.daily_limit * 0.8):
            delay *= random.uniform(1.3, 1.8)
            print_lg(f"⚠️ Increased delay (approaching limit): {delay:.1f}s")
        
        return delay
    
    
    def get_reading_time(self, text_length: int) -> float:
        '''
        Calculates natural reading time based on text length.
        Returns time in seconds.
        '''
        # Average reading speed: 200-250 words per minute
        words = text_length / 5  # Rough estimate
        base_time = (words / 225) * 60
        
        # Add variation
        variation = random.uniform(0.8, 1.3)
        reading_time = base_time * variation
        
        # Clamp between 3-45 seconds
        return max(3, min(45, reading_time))
    
    
    def check_daily_limit_reached(self) -> bool:
        '''
        Returns True if daily limit has been reached.
        '''
        return self.applications_today >= self.daily_limit
    
    
    def get_session_stats(self) -> dict:
        '''
        Returns current session statistics.
        '''
        return {
            'applications_today': self.applications_today,
            'daily_limit': self.daily_limit,
            'applications_this_session': self.applications_this_session,
            'session_duration_minutes': (datetime.now() - self.session_start).seconds / 60,
            'time_since_last_break_minutes': (datetime.now() - self.last_break).seconds / 60,
            'percentage_of_limit': (self.applications_today / self.daily_limit) * 100
        }
    
    
    def should_slow_down(self) -> bool:
        '''
        Returns True if bot should slow down (approaching limits).
        '''
        return self.applications_today >= int(self.daily_limit * 0.7)
    
    
    def reset_daily_stats(self) -> None:
        '''
        Resets daily statistics (for testing or manual reset).
        '''
        print_lg("Resetting daily statistics...")
        self.applications_today = 0
        self._save_session_state()
    
    
    ##> ------ Enhanced by AI Audit - Checkpoint Methods ------
    def _load_checkpoint(self) -> None:
        '''
        Load checkpoint for resume capability.
        '''
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if checkpoint is recent (last 6 hours)
                checkpoint_time = datetime.fromisoformat(data.get('timestamp', '2000-01-01'))
                if (datetime.now() - checkpoint_time).seconds < 21600:  # 6 hours
                    self.current_search_term = data.get('current_search_term')
                    self.current_page = data.get('current_page', 1)
                    self.processed_job_ids = set(data.get('processed_job_ids', []))
                    
                    if self.processed_job_ids:
                        print_lg(f"📍 Checkpoint found: {len(self.processed_job_ids)} jobs already processed")
                        print_lg(f"   Last search: {self.current_search_term}, Page: {self.current_page}")
                        
        except Exception as e:
            print_lg(f"⚠️ Failed to load checkpoint: {e}")
    
    
    def save_checkpoint(self, search_term: str, page: int, job_id: str) -> None:
        '''
        Save progress checkpoint.
        '''
        try:
            self.current_search_term = search_term
            self.current_page = page
            self.processed_job_ids.add(job_id)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'current_search_term': self.current_search_term,
                'current_page': self.current_page,
                'processed_job_ids': list(self.processed_job_ids)
            }

            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                    
        except Exception as e:
            print_lg(f"⚠️ Failed to save checkpoint: {e}")
    
    
    def is_job_processed(self, job_id: str) -> bool:
        '''
        Check if job was already processed in this session.
        '''
        return job_id in self.processed_job_ids
    
    
    def clear_checkpoint(self) -> None:
        '''
        Clear checkpoint (call at successful completion).
        '''
        try:
            if self.checkpoint_file.exists():
                self.checkpoint_file.unlink()
                print_lg("✅ Checkpoint cleared")
        except Exception as e:
            print_lg(f"⚠️ Failed to clear checkpoint: {e}")
    ##<


class WorkdayScheduler:
    '''
    Simulates realistic working hours and patterns.
    '''
    
    def __init__(self):
        self.work_start_hour = random.randint(8, 10)  # 8-10 AM
        self.work_end_hour = random.randint(17, 20)   # 5-8 PM
        self.lunch_start_hour = random.randint(12, 13)  # 12-1 PM
        self.lunch_duration = random.randint(30, 60)  # 30-60 minutes
    
    
    def is_working_hours(self) -> bool:
        '''
        Checks if current time is within working hours.
        '''
        current_hour = datetime.now().hour
        
        # Check if during work hours
        if current_hour < self.work_start_hour or current_hour >= self.work_end_hour:
            return False
        
        # Check if during lunch
        if current_hour == self.lunch_start_hour:
            return False
        
        return True
    
    
    def get_time_until_work_hours(self) -> int:
        '''
        Returns seconds until next work period starts.
        '''
        current_time = datetime.now()
        current_hour = current_time.hour
        
        if current_hour < self.work_start_hour:
            # Before work starts
            next_work = current_time.replace(hour=self.work_start_hour, minute=0, second=0)
            return (next_work - current_time).seconds
        
        elif current_hour == self.lunch_start_hour:
            # During lunch
            return self.lunch_duration * 60
        
        else:
            # After work, wait until tomorrow
            next_work = (current_time + timedelta(days=1)).replace(
                hour=self.work_start_hour, minute=0, second=0
            )
            return (next_work - current_time).seconds
    
    
    def should_work_today(self) -> bool:
        '''
        Decides if should work today (not every day, to be more realistic).
        '''
        # 85% chance of working today (realistic)
        return random.random() < 0.85


##<
