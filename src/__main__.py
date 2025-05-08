import os
import logging
from datetime import datetime
from whatsapp_scraper import WhatsAppScraper
from image_downloader import ImageDownloader
from docx_writer import DocxWriter

# Configure logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), '../logs/app.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        # Initialize paths
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        driver_path = os.path.join(base_dir, 'drivers/chromedriver.exe')
        images_dir = os.path.join(base_dir, 'assets/images')
        output_dir = os.path.join(base_dir, 'output')
        
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f'whatsapp_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx')
        
        # Initialize components
        scraper = WhatsAppScraper(driver_path)
        scraper.initialize_driver()
        scraper.open_whatsapp_web()
        
        # Extract image data
        image_data = scraper.extract_blob_images()
        
        # Process images and text
        processed_data = []
        for idx, item in enumerate(image_data):
            text = scraper.get_message_text(item['element'])
            processed_data.append({
                'dataUrl': item['dataUrl'],
                'text': text
            })
            logging.info(f"Processed image {idx+1} with text: {text[:50]}...")
        
        # Download images
        downloader = ImageDownloader(images_dir)
        saved_images = downloader.save_images(processed_data)
        
        # Create Word document
        writer = DocxWriter()
        writer.create_table(saved_images)
        writer.save(output_file)
        
        logging.info(f"✅ Document successfully saved at {output_file}")
        print(f"✅ Document successfully saved at {output_file}")
        
    except Exception as e:
        logging.error(f"❌ Error in main execution: {str(e)}", exc_info=True)
        print(f"❌ An error occurred: {str(e)}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()