import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageEventHandler(FileSystemEventHandler):
    def __init__(self, converter, pic_dir):
        super().__init__()
        self.converter = converter
        self.pic_dir = pic_dir
        self.valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')

    def is_valid_image(self, path):
        return path.lower().endswith(self.valid_extensions) and not os.path.basename(path).startswith('.')

    def on_created(self, event):
        if not event.is_directory and self.is_valid_image(event.src_path):
            file_name = os.path.basename(event.src_path)
            print(f"New file detected: {file_name}")
            # Add a small delay to ensure file is fully written before processing
            time.sleep(0.5)
            self.converter.process_single_image(file_name)

    def on_deleted(self, event):
        if not event.is_directory and self.is_valid_image(event.src_path):
            file_name = os.path.basename(event.src_path)
            pic_path = os.path.join(self.pic_dir, file_name)
            if os.path.exists(pic_path):
                print(f"File deleted: {file_name}, removing from local cache.")
                try:
                    os.remove(pic_path)
                except Exception as e:
                    print(f"Error deleting file {pic_path}: {e}")

class USBMonitor:
    def __init__(self, base_mount_path, converter, pic_dir):
        self.base_mount_path = base_mount_path
        self.converter = converter
        self.pic_dir = pic_dir
        self.current_usb_path = None
        self.observer = None
        self._thread = None
        self.stop_monitor = False

    def find_usb_drive(self):
        if not os.path.exists(self.base_mount_path):
            return None
        
        for item in os.listdir(self.base_mount_path):
            full_path = os.path.join(self.base_mount_path, item)
            if os.path.isdir(full_path):
                return full_path
        return None

    def start_observer(self, usb_path):
        self.observer = Observer()
        event_handler = ImageEventHandler(self.converter, self.pic_dir)
        self.observer.schedule(event_handler, usb_path, recursive=False)
        self.observer.start()
        print(f"Started monitoring USB path: {usb_path}")

    def stop_observer(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("Stopped monitoring USB path.")

    def monitor_loop(self):
        while not self.stop_monitor:
            usb_path = self.find_usb_drive()
            
            # If USB was added
            if usb_path and self.current_usb_path != usb_path:
                self.stop_observer()
                self.current_usb_path = usb_path
                self.converter.source_dir = usb_path
                
                # Process existing images first
                print(f"USB Drive detected at {usb_path}, processing existing images...")
                try:
                    self.converter.process_images()
                except Exception as e:
                    print(f"Error processing initial images: {e}")
                    
                self.start_observer(usb_path)

            # If USB was removed
            elif not usb_path and self.current_usb_path is not None:
                print("USB Drive removed.")
                self.stop_observer()
                self.current_usb_path = None
                self.converter.source_dir = None
                # Optionally clear pic_dir? The original code didn't specify, but it's probably good.
                for f in os.listdir(self.pic_dir):
                    try:
                        os.remove(os.path.join(self.pic_dir, f))
                    except:
                        pass
                
            time.sleep(2)

    def start(self):
        self.stop_monitor = False
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.stop_monitor = True
        if self._thread:
            self._thread.join()
        self.stop_observer()

    def get_current_usb_path(self):
        return self.current_usb_path
