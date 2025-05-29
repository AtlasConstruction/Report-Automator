# image_downloader.py (updated)
import os
import base64
from io import BytesIO
from PIL import Image
import imagehash
import hashlib
import uuid

class ImageDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        os.makedirs(self.download_folder, exist_ok=True)
        self.seen_hashes = {}  # {combined_hash: (best_path, best_size)}

    def _create_fingerprint(self, img_data):
        """Create multiple hashes for robust duplicate detection"""
        try:
            with Image.open(BytesIO(img_data)) as img:
                # Preprocess image
                img = img.convert('RGB')
                thumbnail = img.resize((128, 128), Image.LANCZOS)
                
                # Create multiple hashes
                phash = str(imagehash.phash(thumbnail))
                dhash = str(imagehash.dhash(thumbnail))
                grayscale_hash = hashlib.md5(thumbnail.tobytes()).hexdigest()
                
                return f"{phash}-{dhash}-{grayscale_hash}", img.size[0]*img.size[1]
        except Exception as e:
            print(f"Error creating fingerprint: {str(e)}")
            return str(uuid.uuid4()), 0  # Fallback to random UUID if image processing fails

    def save_images(self, image_data):
        saved_images = []
        
        for idx, item in enumerate(image_data):
            try:
                if 'dataUrl' not in item:
                    print(f"⚠️ Missing dataUrl for image {idx}")
                    continue

                # Extract and decode image
                header, encoded = item['dataUrl'].split(",", 1)
                img_data = base64.b64decode(encoded)
                
                # Create unique fingerprint
                combined_hash, resolution = self._create_fingerprint(img_data)
                
                # Check for duplicates
                duplicate = None
                for existing_hash in self.seen_hashes:
                    existing_phash, existing_dhash, _ = existing_hash.split('-')
                    current_phash, current_dhash, _ = combined_hash.split('-')
                    
                    # Compare multiple hash aspects
                    if (imagehash.hex_to_hash(existing_phash) - imagehash.hex_to_hash(current_phash) <= 2 and
                        imagehash.hex_to_hash(existing_dhash) - imagehash.hex_to_hash(current_dhash) <= 2):
                        duplicate = existing_hash
                        break

                if duplicate:
                    # Keep higher resolution version
                    if resolution > self.seen_hashes[duplicate][1]:
                        # Replace with better quality
                        old_path = self.seen_hashes[duplicate][0]
                        temp_path = old_path + ".old"
                        if os.path.exists(old_path):
                            os.rename(old_path, temp_path)
                        with open(old_path, 'wb') as f:
                            f.write(img_data)
                        self.seen_hashes[duplicate] = (old_path, resolution)
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        print(f"♻️ Replaced duplicate with better resolution: {old_path}")
                    continue

                # Generate filename based on content hash and blob URL
                blob_id = item.get('blobUrl', '').split('/')[-1][:8]  # Get last part of blob URL
                filename = f"whatsapp_{blob_id}_{combined_hash[:8]}.png"
                img_path = os.path.join(self.download_folder, filename)
                
                # Save only if file doesn't exist
                if not os.path.exists(img_path):
                    with open(img_path, 'wb') as f:
                        f.write(img_data)
                    self.seen_hashes[combined_hash] = (img_path, resolution)
                    saved_images.append({
                        'path': img_path,
                        'text': item.get('text', 'No text found'),
                        'blobUrl': item.get('blobUrl', '')
                    })

            except Exception as e:
                print(f"⚠️ Error processing image {idx}: {str(e)}")
        
        return saved_images