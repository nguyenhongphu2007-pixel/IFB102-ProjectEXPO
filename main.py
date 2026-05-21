import os
import sys
import json
import threading
import shutil

# Local imports
from slideshow.display_manager import DisplayManager
from slideshow.image_converter import ImageConverter
from slideshow.usb_monitor import USBMonitor
from web_ui.app import app, get_settings

def setup_environment():
    # Setup paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pic_dir = os.path.join(base_dir, 'pic')
    config_dir = os.path.join(base_dir, 'config')
    settings_file = os.path.join(config_dir, 'settings.json')
    
    # Clean and create pic directory
    if os.path.exists(pic_dir):
        shutil.rmtree(pic_dir)
    os.makedirs(pic_dir)
    
    # Ensure config directory and settings exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    if not os.path.exists(settings_file):
        with open(settings_file, 'w') as f:
            json.dump({"refresh_interval": 30}, f)

    return base_dir, pic_dir, settings_file

def main():
    print("Starting E-Ink Slideshow Service...")
    base_dir, pic_dir, settings_file = setup_environment()
    
    # Find the correct base mount point for USB drives
    if os.name == 'nt':
        # Windows environment testing
        base_mount_path = os.path.join(base_dir, "mock_usb_mount")
        mock_usb = os.path.join(base_mount_path, "TEST_USB")
        if not os.path.exists(mock_usb):
            os.makedirs(mock_usb)
        print(f"Windows environment detected. Using {mock_usb} as fake USB drive for testing.")
    else:
        # Linux / Raspberry Pi environment
        username = os.getenv("SUDO_USER") or os.getenv("USER") or "pi"
        base_mount_path = f"/media/{username}"
        if not os.path.exists(base_mount_path):
            base_mount_path = "/media/pi"

    # Initialize components
    app.config['SETTINGS_FILE'] = settings_file
    
    # We use a lambda to always fetch the latest refresh time from settings.json
    def get_refresh_cb():
        return get_settings().get('refresh_interval', 30)

    display_manager = DisplayManager(image_folder=pic_dir, get_refresh_time_cb=get_refresh_cb)
    
    image_converter = ImageConverter(source_dir=None, output_dir=pic_dir)
    
    usb_monitor = USBMonitor(base_mount_path=base_mount_path, converter=image_converter, pic_dir=pic_dir)
    
    # Share monitor with flask app
    app.config['USB_MONITOR'] = usb_monitor
    
    # Show startup message
    try:
        display_manager.display_message('start.jpg')
    except Exception as e:
        print(f"Startup display message failed: {e}")

    # Start background threads
    print("Starting background threads...")
    display_manager.start()
    usb_monitor.start()

    # Start Flask Web UI on main thread
    print("Starting Web Dashboard on port 5000...")
    try:
        # Use host='0.0.0.0' to allow access from local network
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\nShutting down services...")
    finally:
        usb_monitor.stop()
        display_manager.stop()
        print("Shutdown complete.")

if __name__ == '__main__':
    main()
