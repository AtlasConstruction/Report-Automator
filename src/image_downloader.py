import os
import base64
import time
from typing import List, Dict

class ImageDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        os.makedirs(self.download_folder, exist_ok=True)
    
    def save_images(self, image_data):
        saved_images = []
        for idx, item in enumerate(image_data):
            try:
                # Verify required keys exist
                if 'dataUrl' not in item:
                    raise ValueError("Missing 'dataUrl' in image data")
                
                # Extract base64 data
                header, encoded = item['dataUrl'].split(",", 1)
                img_data = base64.b64decode(encoded)
                
                # Create filename - use timestamp if available, otherwise use index
                timestamp = item.get('timestamp', time.strftime("%Y%m%d_%H%M%S"))
                img_path = os.path.join(
                    self.download_folder, 
                    f"whatsapp_img_{timestamp}_{idx}.png"
                )
                
                # Save image
                with open(img_path, "wb") as f:
                    f.write(img_data)
                
                saved_images.append({
                    'path': img_path,
                    'text': item.get('text', 'No text found')
                })
                
            except Exception as e:
                print(f"Error saving image {idx}: {str(e)}")
                continue  # Skip to next image if error occurs
        
        return saved_images
    # def save_images(self, image_data: List[Dict]) -> List[Dict]:
    #     saved_images = []
    #     for idx, item in enumerate(image_data):
    #         try:
    #             data_url = item['dataUrl']
    #             header, encoded = data_url.split(",", 1)
    #             img_data = base64.b64decode(encoded)
    #             img_path = os.path.join(
    #                 self.download_folder, 
    #                 f"whatsapp_image_{idx+1}.png"
    #             )
                
    #             with open(img_path, "wb") as f:
    #                 f.write(img_data)
                
    #             saved_images.append({
    #                 'path': img_path,
    #                 'text': item['text']
    #             })
                
    #         except Exception as e:
    #             print(f"❌ Error saving image {idx+1}: {e}")
        
    #     return saved_images