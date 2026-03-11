import uuid
import cloudscraper
import time
import random

class NGLWrapper:
    def __init__(self):
        self.s = cloudscraper.create_scraper()
        self.submit_url = "https://ngl.link/api/submit"
        self.username = None
        self.counter = 0
        
    def set_username(self, username):
        self.username = username
        
    def send_question(self, question):
        device_id = str(uuid.uuid4())
        data = {
            "username": self.username,
            "question": question,
            "deviceId": device_id,
            "gameSlug": "",
            "referrer": ""
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self.s.post(self.submit_url, data=data, timeout=10)
                
                if r.status_code == 200:
                    self.counter += 1
                    return True
                elif r.status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return False
                else:
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return False
        
        return False