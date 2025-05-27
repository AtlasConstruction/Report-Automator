# main.py
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import base64
import os
import io
from PIL import Image
from src.whatsapp_scraper import WhatsAppScraper
from src.docx_writer import DocxWriter
from gui.resource import setIcon

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WhatsApp Image Scraper")
        self.geometry("500x300")
        self.resizable(False, False)
        
        self.scraper = None
        self.scraping = False
        
        # Output Path
        tk.Label(self, text="Save to DOCX File:").pack(pady=(20, 5))
        self.output_entry = tk.Entry(self, width=50)
        self.output_entry.pack()
        tk.Button(self, text="Browse", command=self.browse_file).pack(pady=5)

        # Chromedriver Path
        tk.Label(self, text="Chromedriver Path:").pack(pady=(10, 5))
        self.driver_entry = tk.Entry(self, width=50)
        self.driver_entry.insert(0, "drivers/chromedriver.exe")
        self.driver_entry.pack()

        # Status Frame
        self.status_frame = tk.Frame(self)
        self.status_frame.pack(pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Status: Ready")
        self.status_label.pack(side=tk.LEFT)
        
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        
        # Action Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=15)
        
        self.start_button = tk.Button(
            self.button_frame, 
            text="Start WhatsApp", 
            command=self.start_whatsapp,
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.download_button = tk.Button(
            self.button_frame, 
            text="Download Images", 
            command=self.download_images,
            bg="#2196F3",
            fg="white",
            width=15,
            # state=tk.DISABLED
        )
        self.download_button.pack(side=tk.LEFT, padx=5)

    def browse_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")]
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)

    def start_whatsapp(self):
        driver_path = self.driver_entry.get()
        
        if not driver_path:
            messagebox.showwarning("Input Required", "Please specify the ChromeDriver path.")
            return
            
        try:
            self.scraper = WhatsAppScraper(driver_path)
            self.scraper.initialize_driver()
            self.start_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Opening WhatsApp...")
            self.progress.pack(side=tk.LEFT, padx=5)
            self.progress.start()
            
            self.after(100, lambda: self._complete_whatsapp_start())
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            if self.scraper:
                self.scraper.close()
            self._reset_ui()

    def _complete_whatsapp_start(self):
        try:
            success = self.scraper.open_whatsapp_web()
            if success:
                self.status_label.config(text="Status: WhatsApp ready - scan QR code")
                self.download_button.config(state=tk.NORMAL)
                messagebox.showinfo("Ready", "WhatsApp Web is open. Please scan the QR code and navigate to the desired chat.")
            else:
                messagebox.showerror("Error", "Failed to open WhatsApp Web")
                self._reset_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._reset_ui()
        finally:
            self.progress.stop()
            self.progress.pack_forget()

    def download_images(self):
        output_path = self.output_entry.get()
        
        if not output_path:
            messagebox.showwarning("Input Required", "Please specify an output file path.")
            return
            
        try:
            self.status_label.config(text="Status: Downloading images...")
            self.progress.pack(side=tk.LEFT, padx=5)
            self.progress.start()
            self.download_button.config(state=tk.DISABLED)
            
            self.after(100, lambda: self._perform_download(output_path))
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._reset_ui()

    def _perform_download(self, output_path):
        try:
            results = self.scraper.extract_images_with_text()

            if not results:
                messagebox.showinfo("No Images", "No WhatsApp images were found.")
                return

            doc_writer = DocxWriter()
            data = []

            temp_folder = "output/temp_images"
            os.makedirs(temp_folder, exist_ok=True)

            for i, item in enumerate(results):
                base64_data = item["dataUrl"].split(',')[1]
                image_data = base64.b64decode(base64_data)
                image_path = os.path.join(temp_folder, f"image_{i}.png")

                image = Image.open(io.BytesIO(image_data))
                image.save(image_path)

                data.append({
                    'path': image_path,
                    'text': item['text']
                })

            doc_writer.create_table(data)
            doc_writer.save(output_path)

            messagebox.showinfo("Success", f"Scraping complete.\nFile saved to:\n{output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._reset_ui()
            if self.scraper:
                self.scraper.close()

    def _reset_ui(self):
        self.status_label.config(text="Status: Ready")
        self.progress.stop()
        self.progress.pack_forget()
        self.start_button.config(state=tk.NORMAL)
        self.download_button.config(state=tk.DISABLED)

    def on_closing(self):
        if self.scraper:
            self.scraper.close()
        self.destroy()

if __name__ == "__main__":
    app = MainWindow()
    setIcon(app)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    app.mainloop()  