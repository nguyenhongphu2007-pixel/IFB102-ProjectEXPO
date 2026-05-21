import os
import sys
import time
import random
from PIL import Image
from lib.waveshare_epd import epd7in3f

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_PATH = os.path.join(SCRIPT_DIR, 'lib')
sys.path.append(LIB_PATH)
import threading

class DisplayManager:
    """
    Class to manage the display of images on the e-Paper screen.
    """

    # Initializes the display using the epd7in3f library.
    # Sets the rotation and refresh time callback for the display.
    # Initializes the last display time and selected image to None.
    def __init__(self, image_folder, get_refresh_time_cb):
        self.last_display_time = time.time()
        self.last_selected_image = None
        self.image_folder = image_folder
        self.rotation = 0
        self.get_refresh_time_cb = get_refresh_time_cb
        self.epd = epd7in3f.EPD()
        self.epd.init()
        self.stop_display = False
        self._thread = None

    # Fetches the image files from the specified folder.
    def fetch_image_files(self):
        return [f for f in os.listdir(self.image_folder)]


    # Selects a random image from the list of images.
    def select_random_image(self, images):
        # If one image or less
        if len(images) <= 1:
            return images[0]
        
        # Select a random image unless it was previously selected
        random_image = random.choice([img for img in images if img != self.last_selected_image])
        
        return random_image


    # Continuously loop to display a random image from the specified folder at the specified refresh time.
    def display_images(self):
        self.stop_display = False

        images = self.fetch_image_files()

        if not images:
            print("No images found, displaying default image.")
            self.display_message('no_valid_images.jpg')
            return

        random_image = self.select_random_image(images)
        self.last_selected_image = random_image
            
        # Open and display the image
        with Image.open(os.path.join(self.image_folder, random_image)) as pic:
            pic = pic.rotate(self.rotation)
            self.epd.display(self.epd.getbuffer(pic))
            self.last_display_time = time.time()

        while not self.stop_display:
            current_time = time.time()
            elapsed_time = current_time - self.last_display_time
            refresh_time = self.get_refresh_time_cb()
            
            if elapsed_time >= refresh_time:
                images = self.fetch_image_files()
                if images:
                    random_image = self.select_random_image(images)
                    self.last_selected_image = random_image

                    # Open and display the image
                    with Image.open(os.path.join(self.image_folder, random_image)) as pic:
                        print(f"Displaying new image: {random_image}")
                        pic = pic.rotate(self.rotation)
                        self.epd.display(self.epd.getbuffer(pic))
                self.last_display_time = time.time()
            
            time.sleep(1) # Prevent 100% CPU usage
            
    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.display_images, daemon=True)
            self._thread.start()

    def stop(self):
        self.stop_display = True
        if self._thread:
            self._thread.join()
    

    def display_message(self, message_file):
        with Image.open(os.path.join(SCRIPT_DIR, f"messages/{message_file}")) as img_start:
                img_start = img_start.rotate(self.rotation)
                self.epd.display(self.epd.getbuffer(img_start))

