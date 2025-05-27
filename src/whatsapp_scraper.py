import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller-created temp folder
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

class WhatsAppScraper:
    def __init__(self, driver_path):
        self.driver_path =  get_resource_path('drivers/chromedriver.exe')
        self.driver = None
    
    def initialize_driver(self):
        options = Options()
    
        # Essential arguments to prevent crashes
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")
        
        # For headless operation (optional)
        # options.add_argument("--headless=new")
        
        # Fix for PyInstaller temp directory
        options.add_argument(f"--user-data-dir={os.path.join(os.getcwd(), 'chrome_profile')}")
        
        # Disable extensions and other potential issues
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-setuid-sandbox")
        
        service = Service(executable_path=self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
    
    def open_whatsapp_web(self):
        self.driver.get("https://web.whatsapp.com")
        input("📱 Scan QR, open the chat and scroll to load all images. Then press ENTER...")
        time.sleep(5)
    
    def extract_blob_images(self):
        js_code = """
        const getBase64FromImage = (img) => {
            return new Promise((resolve, reject) => {
                try {
                    let canvas = document.createElement('canvas');
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    let ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/png'));
                } catch (e) {
                    reject(e);
                }
            });
        };

        const allImages = Array.from(document.querySelectorAll('img[src^="blob:"]'));
        const promises = allImages.map(img => getBase64FromImage(img));
        return Promise.all(promises).then(results => results);
        """
        
        self.driver.execute_script(js_code)
        time.sleep(5)
        return self.driver.execute_script("""
            return (async () => {
                return await Promise.all(
                    Array.from(document.querySelectorAll('img[src^="blob:"]'))
                    .map(img => {
                        return new Promise((resolve) => {
                            let canvas = document.createElement('canvas');
                            canvas.width = img.naturalWidth;
                            canvas.height = img.naturalHeight;
                            let ctx = canvas.getContext('2d');
                            ctx.drawImage(img, 0, 0);
                            resolve({
                                dataUrl: canvas.toDataURL('image/png'),
                                element: img
                            });
                        });
                    })
                );
            })();
        """)
    
    def extract_images_with_text(self):
        return self.driver.execute_script("""
        function getFollowingText(imgElement) {
            // Walk through DOM to find the associated text
            let container = imgElement.closest('.copyable-text');
            if (!container) return "No text found";
            
            // Look for text in known WhatsApp structures
            let textElement = container.querySelector('[data-testid="text"]') || 
                            container.querySelector('.selectable-text') ||
                            container.querySelector('.message-text');
            
            return textElement ? textElement.innerText : "No text found";
        }

        return Array.from(document.querySelectorAll('img[src^="blob:"]')).map(img => {
            // Convert blob image to base64
            let canvas = document.createElement('canvas');
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            let ctx = canvas.getContext('2d');
            ctx.drawImage(img, 0, 0);
            
            return {
                dataUrl: canvas.toDataURL('image/png'),
                text: getFollowingText(img),
                element: img  // Include the actual DOM element
            };
        });
        """)

    def get_message_text(self, img_element):
        try:
            # Use JavaScript to get text since Selenium might have stale references
            return self.driver.execute_script("""
                function getText(img) {
                    let container = img.closest('.copyable-text');
                    if (!container) return "No text found";
                    
                    let textElement = container.querySelector('[data-testid="text"]') || 
                                    container.querySelector('.selectable-text') ||
                                    container.querySelector('.message-text');
                    
                    return textElement ? textElement.innerText : "No text found";
                }
                return getText(arguments[0]);
            """, img_element)
        except Exception:
            return "No text found" 

    
    def close(self):
        if self.driver:
            self.driver.quit()