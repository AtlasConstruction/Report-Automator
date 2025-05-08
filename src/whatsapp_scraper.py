import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class WhatsAppScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = None
    
    def initialize_driver(self):
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(
            service=Service(self.driver_path), 
            options=options
        )
    
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
    
    def get_message_text(self, img_element):
        try:
            message_element = img_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'message')]")
            return message_element.text if message_element else "No text found"
        except Exception:
            return "No text found"
    
    def close(self):
        if self.driver:
            self.driver.quit()