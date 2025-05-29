# whatsapp_scraper.py (updated)
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller-created temp folder
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)

class WhatsAppScraper:
    def __init__(self, driver_path):
        self.driver_path = get_resource_path('drivers/chromedriver.exe')
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
        self.driver.maximize_window()
    
    def open_whatsapp_web(self):
        self.driver.get("https://web.whatsapp.com")
        input("📱 Scan QR, open the chat and scroll to load all images. Then press ENTER...")
        time.sleep(5)
        return True
    
    def extract_images_with_text(self):
        """Extract all blob images with their associated text"""
        try:
            # Wait for at least one image to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'img[src^="blob:"]'))
            )
            
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

                // Get all blob images
                const blobImages = Array.from(document.querySelectorAll('img[src^="blob:"]'));
                
                // Process each image
                return blobImages.map(img => {
                    try {
                        // Convert blob image to base64
                        const canvas = document.createElement('canvas');
                        canvas.width = img.naturalWidth;
                        canvas.height = img.naturalHeight;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        
                        return {
                            dataUrl: canvas.toDataURL('image/png'),
                            text: getFollowingText(img),
                            element: img,  // Include the actual DOM element
                            blobUrl: img.src  // Keep the original blob URL
                        };
                    } catch (e) {
                        console.error('Error processing image:', e);
                        return {
                            dataUrl: '',
                            text: 'Error processing image',
                            element: img,
                            blobUrl: img.src
                        };
                    }
                }).filter(img => img.dataUrl);  // Filter out failed conversions
            """)
        except Exception as e:
            print(f"Error extracting images: {str(e)}")
            return []
    
    def close(self):
        if self.driver:
            self.driver.quit()