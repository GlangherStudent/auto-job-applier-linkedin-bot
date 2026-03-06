'''
File management module for logs, CSVs and screenshots.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.02.10
'''

import os
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
from pathlib import Path
from datetime import datetime, timedelta
from modules.helpers import print_lg


class FileManager:
    '''
    Manages log files, CSV files, and screenshots with automatic cleanup.
    '''
    
    def __init__(self, logs_folder: str = "logs/", max_log_size_mb: int = 10, max_screenshots: int = 50):
        self.logs_folder = Path(logs_folder)
        self.max_log_size = max_log_size_mb * 1024 * 1024  # Convert to bytes
        self.max_screenshots = max_screenshots
    
    
    def cleanup_old_screenshots(self) -> None:
        '''
        Keeps only the most recent screenshots, deletes older ones.
        '''
        try:
            screenshots_dir = self.logs_folder / "screenshots"
            if not screenshots_dir.exists():
                return
            
            # Get all screenshots
            screenshots = list(screenshots_dir.glob("*.png"))
            
            if len(screenshots) > self.max_screenshots:
                # Sort by modification time
                screenshots.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Delete old ones
                for screenshot in screenshots[self.max_screenshots:]:
                    try:
                        screenshot.unlink()
                    except Exception as e:
                        print_lg(f"⚠️ Failed to delete screenshot {screenshot.name}: {e}")
                
                deleted_count = len(screenshots) - self.max_screenshots
                print_lg(f"🧹 Cleanup: Deleted {deleted_count} old screenshots")
                
        except Exception as e:
            print_lg(f"⚠️ Screenshot cleanup failed: {e}")
    
    
    def rotate_log_if_needed(self, log_file: str = "log.txt") -> None:
        '''
        Rotates log file if it exceeds maximum size.
        '''
        try:
            log_path = self.logs_folder / log_file
            
            if not log_path.exists():
                return
            
            file_size = log_path.stat().st_size
            
            if file_size > self.max_log_size:
                # Rotate log
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archived_name = f"log_{timestamp}.txt"
                archived_path = self.logs_folder / archived_name
                
                log_path.rename(archived_path)
                print_lg(f"🔄 Log rotated: {log_file} → {archived_name} ({file_size / 1024 / 1024:.1f} MB)")
                
                # Keep only last 3 archived logs
                self._cleanup_archived_logs()
                
        except Exception as e:
            print_lg(f"⚠️ Log rotation failed: {e}")
    
    
    def _cleanup_archived_logs(self) -> None:
        '''
        Keeps only the 3 most recent archived log files.
        '''
        try:
            archived_logs = list(self.logs_folder.glob("log_*.txt"))
            
            if len(archived_logs) > 3:
                # Sort by modification time
                archived_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                # Delete old archived logs
                for log in archived_logs[3:]:
                    try:
                        log.unlink()
                        print_lg(f"🧹 Deleted old archived log: {log.name}")
                    except Exception as e:
                        print_lg(f"⚠️ Failed to delete log {log.name}: {e}")
                        
        except Exception as e:
            print_lg(f"⚠️ Archived log cleanup failed: {e}")
    
    
    def cleanup_old_csv_entries(self, csv_file: str, days_to_keep: int = 30) -> None:
        '''
        Removes CSV entries older than specified days to prevent file growth.
        '''
        try:
            csv_path = Path(csv_file)
            
            if not csv_path.exists():
                return
            
            import csv
            from datetime import datetime
            
            # Read current CSV
            rows_to_keep = []
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                for row in reader:
                    try:
                        # Check Date Applied
                        date_str = row.get('Date Applied', '')
                        if date_str and date_str != 'Pending':
                            date_applied = datetime.fromisoformat(date_str.split('.')[0])
                            if date_applied > cutoff_date:
                                rows_to_keep.append(row)
                            else:
                                removed_count += 1
                        else:
                            rows_to_keep.append(row)
                    except:
                        rows_to_keep.append(row)  # Keep if can't parse date
            
            # Write back if any removed
            if removed_count > 0:
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows_to_keep)
                
                print_lg(f"🧹 CSV cleanup: Removed {removed_count} entries older than {days_to_keep} days")
                
        except Exception as e:
            print_lg(f"⚠️ CSV cleanup failed: {e}")
    
    
    def perform_maintenance(self) -> None:
        '''
        Performs all file maintenance tasks.
        '''
        print_lg("\n🧹 Performing file maintenance...")
        self.rotate_log_if_needed()
        self.cleanup_old_screenshots()
        # CSV cleanup se face mai rar (nu la fiecare rulare)
        print_lg("✅ Maintenance complete\n")


##<
