import os
from logger import Logger
from datetime import datetime
from whatsapp_scraper import WhatsAppScraper
from image_downloader import ImageDownloader
from docx_writer import DocxWriter

# Configure logging


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
        # *** Remove this *** image_data = scraper.extract_blob_images()
        image_data = scraper.extract_images_with_text()
        
        # Process images and text
        processed_data = []
        for idx, item in enumerate(image_data):
     
            text = scraper.get_message_text(item['element'])
            processed_data.append({
                'dataUrl': item['dataUrl'],
                'text': text
            })
            Logger.info(f"Processed image {idx+1} with text: {text[:50]}...")
        
        # Download images
        downloader = ImageDownloader(images_dir)
        saved_images = downloader.save_images(processed_data)
        
        # Create Word document
        writer = DocxWriter()
        writer.create_table(saved_images)
        writer.save(output_file)
        
        Logger.info(f"✅ Document successfully saved at {output_file}")
        print(f"✅ Document successfully saved at {output_file}")
        
    except Exception as e:
        Logger.error(f"❌ Error in main execution: {str(e)}", exc_info=True)
        print(f"❌ An error occurred: {str(e)}")
        
    finally:

        scraper.close()
                # Delete all images in the images directory
        try:
            for file in os.listdir(images_dir):
                file_path = os.path.join(images_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            Logger.info("🧹 All images in the assets/images directory have been deleted.")
        except Exception as cleanup_error:
            Logger.error(f"⚠️ Error while cleaning up images: {str(cleanup_error)}")

if __name__ == "__main__":
    Logger.start_logger()
    Logger.info("Application started")
    main()