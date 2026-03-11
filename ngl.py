import uuid
import requests
import time
import random
import json

class NGLWrapper:
    def __init__(self):
        # Use regular requests instead of cloudscraper (lighter for Vercel)
        self.session = requests.Session()
        self.submit_url = "https://ngl.link/api/submit"
        self.username = None
        self.counter = 0
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ngl.link',
            'Connection': 'keep-alive',
            'Referer': 'https://ngl.link/'
        })
        
    def set_username(self, username):
        self.username = username
        # Update referer with username
        self.session.headers.update({
            'Referer': f'https://ngl.link/{username}'
        })
        
    def send_question(self, question):
        """Send a question to NGL"""
        if not self.username:
            return False
            
        # Generate device ID
        device_id = str(uuid.uuid4())
        
        # Prepare data
        data = {
            "username": self.username,
            "question": question,
            "deviceId": device_id,
            "gameSlug": "",
            "referrer": ""
        }
        
        # Try to send with retries
        max_retries = 2  # Reduced for Vercel timeout
        
        for attempt in range(max_retries):
            try:
                # Send POST request
                response = self.session.post(
                    self.submit_url,
                    data=data,
                    timeout=3  # Shorter timeout for Vercel (3 seconds max)
                )
                
                # Check response
                if response.status_code == 200:
                    self.counter += 1
                    return True
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    if attempt < max_retries - 1:
                        time.sleep(0.5)  # Short wait
                        continue
                    return False
                else:
                    # Try to parse response
                    try:
                        result = response.json()
                        if result.get('success') == True:
                            self.counter += 1
                            return True
                    except:
                        pass
                    return False
                    
            except requests.exceptions.Timeout:
                # Timeout - try again once
                if attempt < max_retries - 1:
                    continue
                return False
            except requests.exceptions.ConnectionError:
                # Connection error - try again
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return False
            except Exception as e:
                # Other errors
                print(f"NGL Error: {e}")
                return False
        
        return False
    
    def send_bulk(self, questions):
        """Send multiple questions (limited for Vercel)"""
        results = []
        for question in questions[:5]:  # Max 5 messages per request (Vercel timeout)
            result = self.send_question(question)
            results.append(result)
            if result:
                time.sleep(0.3)  # Small delay between messages
        return results
    
    def get_status(self):
        """Get wrapper status"""
        return {
            'username': self.username,
            'messages_sent': self.counter
        }

# Simplified version without cloudscraper (lighter for Vercel)
class SimpleNGL:
    """Even simpler NGL sender - use this if the above still has issues"""
    
    def __init__(self):
        self.submit_url = "https://ngl.link/api/submit"
        
    def send(self, username, question):
        """Send a single message - simplest possible version"""
        try:
            device_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))
            
            data = {
                "username": username,
                "question": question,
                "deviceId": device_id,
                "gameSlug": "",
                "referrer": ""
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            response = requests.post(
                self.submit_url,
                data=data,
                headers=headers,
                timeout=3
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error: {e}")
            return False

# For Vercel, use this lightweight version
def send_ngl_message(username, question):
    """Standalone function to send NGL message (no class overhead)"""
    try:
        device_id = str(uuid.uuid4())
        
        data = {
            "username": username,
            "question": question,
            "deviceId": device_id,
            "gameSlug": "",
            "referrer": ""
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://ngl.link',
            'Referer': f'https://ngl.link/{username}'
        }
        
        response = requests.post(
            'https://ngl.link/api/submit',
            data=data,
            headers=headers,
            timeout=3
        )
        
        return response.status_code == 200
        
    except Exception as e:
        return False