'''
Anti-detection module: human-like behavior simulation for LinkedIn bot.
License:    GNU Affero General Public License - https://www.gnu.org/licenses/agpl-3.0.en.html
version:    26.01.20.5.08
'''

import time
from config.constants import SalaryConversion, TimeConversion, CSVConstants, NetworkConstants, AntiDetectionConstants, RetryConstants, DateConstants, LinkedInURLs
import random

try:
    import numpy as np
except ImportError:
    np = None  # Fallback fara numpy

import pyautogui
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from modules.helpers import print_lg, buffer

# Disable pyautogui failsafe for controlled movements
pyautogui.FAILSAFE = False


class HumanBehaviorSimulator:
    '''
    Simulates human-like behavior to avoid LinkedIn bot detection.
    '''
    
    def __init__(self, driver: WebDriver, actions: ActionChains):
        self.driver = driver
        self.actions = actions
        self.typing_speed_base = 0.1  # Base typing speed in seconds
        self.error_rate = 0.08  # 8% chance of typo
        
    
    def generate_bezier_curve(self, start: tuple, end: tuple, control_points: int = 3) -> list:
        '''
        Generates a Bezier curve path between start and end points.
        Returns list of (x, y) coordinates.
        '''
        # Generate random control points (foloseste numpy daca e disponibil, altfel fallback simplu)
        if np is not None:
            t_values = np.linspace(0, 1, 20)
        else:
            # Fallback: lista echidistanta fara numpy
            steps = 20
            t_values = [i / (steps - 1) for i in range(steps)]
        
        # Create control points with some randomness
        control = []
        for i in range(control_points):
            t = (i + 1) / (control_points + 1)
            x = start[0] + t * (end[0] - start[0]) + random.randint(-50, 50)
            y = start[1] + t * (end[1] - start[1]) + random.randint(-50, 50)
            control.append((x, y))
        
        # Full points list
        points = [start] + control + [end]
        
        # Calculate Bezier curve
        curve_points = []
        for t in t_values:
            point = self._bezier_point(points, t)
            curve_points.append(point)
        
        return curve_points
    
    
    def _bezier_point(self, points: list, t: float) -> tuple:
        '''
        Calculate a point on Bezier curve at parameter t.
        '''
        n = len(points) - 1
        x = sum(self._bernstein(n, i, t) * points[i][0] for i in range(n + 1))
        y = sum(self._bernstein(n, i, t) * points[i][1] for i in range(n + 1))
        return (int(x), int(y))
    
    
    def _bernstein(self, n: int, i: int, t: float) -> float:
        '''
        Bernstein polynomial.
        '''
        from math import factorial
        return factorial(n) / (factorial(i) * factorial(n - i)) * (t ** i) * ((1 - t) ** (n - i))
    
    
    def move_mouse_naturally(self, element: WebElement = None, x: int = None, y: int = None) -> None:
        '''
        Moves mouse to element or coordinates using natural Bezier curve.
        '''
        try:
            # Get current mouse position
            current_pos = pyautogui.position()
            
            # Determine target position
            if element:
                location = element.location
                size = element.size
                target_x = location['x'] + size['width'] // 2 + random.randint(-10, 10)
                target_y = location['y'] + size['height'] // 2 + random.randint(-10, 10)
            else:
                target_x = x if x else random.randint(100, 800)
                target_y = y if y else random.randint(100, 600)
            
            # Generate curve path
            curve = self.generate_bezier_curve(
                (current_pos.x, current_pos.y),
                (target_x, target_y),
                control_points=random.randint(2, 4)
            )
            
            # Move along curve
            duration = random.uniform(0.3, 0.8)
            step_delay = duration / len(curve)
            
            for point in curve:
                pyautogui.moveTo(point[0], point[1], duration=step_delay, tween=pyautogui.easeInOutQuad)
                
        except Exception as e:
            print_lg(f"Mouse movement failed: {e}")
    
    
    def random_mouse_movement(self) -> None:
        '''
        Performs random mouse movement to simulate user distraction.
        '''
        if random.random() < 0.15:  # 15% chance
            target_x = random.randint(200, 1000)
            target_y = random.randint(100, 700)
            self.move_mouse_naturally(x=target_x, y=target_y)
            time.sleep(random.uniform(0.2, 0.5))
    
    
    def hover_element(self, element: WebElement, duration: float = None) -> None:
        '''
        Hovers over an element naturally before clicking.
        '''
        try:
            self.move_mouse_naturally(element)
            hover_time = duration if duration else random.uniform(0.3, 0.8)
            time.sleep(hover_time)
        except Exception as e:
            print_lg(f"Hover failed: {e}")
    
    
    def natural_click(self, element: WebElement, double: bool = False) -> None:
        '''
        Clicks element with natural mouse movement and timing.
        '''
        try:
            # Move to element naturally
            self.move_mouse_naturally(element)
            
            # Small pause before click
            time.sleep(random.uniform(0.1, 0.3))
            
            # Perform click
            if double:
                pyautogui.doubleClick()
            else:
                pyautogui.click()
            
            # Small pause after click
            time.sleep(random.uniform(0.1, 0.2))
            
        except Exception as e:
            print_lg(f"Natural click failed, using fallback: {e}")
            element.click()  # Fallback to Selenium click
    
    
    def natural_typing(self, text: str, element: WebElement = None) -> str:
        '''
        Types text with human-like speed, mistakes, and corrections.
        Returns the final typed text.
        '''
        if not text:
            return ""
        
        try:
            typed_text = ""
            i = 0
            
            while i < len(text):
                char = text[i]
                
                # Typing speed variation
                char_delay = self.typing_speed_base * random.uniform(0.5, 2.0)
                
                # Pause at spaces and punctuation (thinking)
                if char in [' ', ',', '.', '!', '?']:
                    char_delay *= random.uniform(1.5, 3.0)
                
                # Occasional typo
                if random.random() < self.error_rate and char.isalnum():
                    # Type wrong character
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    pyautogui.write(wrong_char, interval=char_delay)
                    typed_text += wrong_char
                    time.sleep(random.uniform(0.1, 0.3))
                    
                    # Backspace to correct
                    pyautogui.press('backspace')
                    typed_text = typed_text[:-1]
                    time.sleep(random.uniform(0.1, 0.2))
                
                # Type correct character
                pyautogui.write(char, interval=char_delay)
                typed_text += char
                
                # Occasional longer pause (thinking/distraction)
                if random.random() < 0.05:  # 5% chance
                    time.sleep(random.uniform(0.5, 1.5))
                
                i += 1
            
            return typed_text
            
        except Exception as e:
            print_lg(f"Natural typing failed, using fallback: {e}")
            if element:
                element.send_keys(text)
            return text
    
    
    def simulate_reading(self, element: WebElement, text_length: int = None) -> None:
        '''
        Simulates reading behavior with natural scrolling and pauses.
        '''
        try:
            # Calculate reading time based on text length
            if text_length:
                # Average reading speed: 200-250 words per minute
                words = text_length / 5  # Rough estimate: 5 chars per word
                reading_time = (words / 225) * 60  # seconds
                reading_time = max(3, min(reading_time, 30))  # Between 3-30 seconds
            else:
                reading_time = random.uniform(5, 15)
            
            print_lg(f"Simulating reading for {reading_time:.1f} seconds...")
            
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Read in chunks with scroll
            chunks = random.randint(3, 6)
            chunk_time = reading_time / chunks
            
            for i in range(chunks):
                # Pause (reading)
                time.sleep(chunk_time * random.uniform(0.8, 1.2))
                
                # Small scroll down
                if i < chunks - 1:
                    scroll_amount = random.randint(50, 150)
                    self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    time.sleep(random.uniform(0.2, 0.5))
                
                # Random mouse movement while reading
                if random.random() < 0.3:
                    self.random_mouse_movement()
            
            # Occasionally scroll back up to re-read
            if random.random() < 0.2:  # 20% chance
                print_lg("Re-reading section...")
                scroll_amount = random.randint(-100, -50)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(1.0, 2.0))
                
        except Exception as e:
            print_lg(f"Reading simulation failed: {e}")
            time.sleep(random.uniform(3, 8))  # Fallback delay
    
    
    def simulate_form_thinking(self, question_complexity: str = 'simple') -> None:
        '''
        Simulates thinking time before answering form questions.
        - simple: Yes/No, Select options
        - medium: Short text answers
        - complex: Paragraphs, difficult questions
        '''
        thinking_times = {
            'simple': (1, 3),
            'medium': (2, 5),
            'complex': (3, 8)
        }
        
        min_time, max_time = thinking_times.get(question_complexity, (1, 3))
        thinking_time = random.uniform(min_time, max_time)
        
        print_lg(f"Thinking for {thinking_time:.1f} seconds...")
        
        # Split thinking time into segments with micro-movements
        segments = random.randint(2, 4)
        for _ in range(segments):
            time.sleep(thinking_time / segments)
            if random.random() < 0.4:  # 40% chance of mouse movement
                self.random_mouse_movement()
    
    
    def random_scroll_behavior(self) -> None:
        '''
        Performs random scrolling to simulate browsing.
        '''
        if random.random() < 0.25:  # 25% chance
            scroll_direction = random.choice([-1, 1])
            scroll_amount = random.randint(100, 300) * scroll_direction
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.3, 0.8))
    
    
    def simulate_distraction(self) -> None:
        '''
        Simulates user distraction (looking away, checking phone, etc.)
        '''
        if random.random() < 0.1:  # 10% chance
            distraction_time = random.uniform(3, 10)
            print_lg(f"Simulating distraction for {distraction_time:.1f} seconds...")
            time.sleep(distraction_time)
    
    
    def page_load_wait(self) -> None:
        '''
        Waits for page load with natural variation.
        '''
        wait_time = random.uniform(2, 5)
        time.sleep(wait_time)
        
        # Random scroll after load
        if random.random() < 0.6:  # 60% chance
            self.random_scroll_behavior()


def get_random_delay(min_seconds: float, max_seconds: float, distribution: str = 'normal') -> float:
    '''
    Returns a random delay with specified distribution.
    - distribution: 'uniform', 'normal', 'exponential'
    '''
    if distribution == 'normal':
        # Normal distribution centered between min and max
        mean = (min_seconds + max_seconds) / 2
        std = (max_seconds - min_seconds) / 4
        delay = np.random.normal(mean, std)
        # Clamp to min-max range
        return max(min_seconds, min(max_seconds, delay))
    
    elif distribution == 'exponential':
        # Exponential distribution (more short delays, fewer long ones)
        scale = (max_seconds - min_seconds) / 3
        delay = min_seconds + np.random.exponential(scale)
        return min(max_seconds, delay)
    
    else:  # uniform
        return random.uniform(min_seconds, max_seconds)


def smart_buffer(base_delay: float, variance: float = 0.3, distribution: str = 'normal') -> None:
    '''
    Advanced buffer with natural variation.
    - base_delay: base time in seconds
    - variance: percentage variation (0.3 = 30%)
    - distribution: delay distribution type
    '''
    min_delay = base_delay * (1 - variance)
    max_delay = base_delay * (1 + variance)
    delay = get_random_delay(min_delay, max_delay, distribution)
    time.sleep(delay)


##<
