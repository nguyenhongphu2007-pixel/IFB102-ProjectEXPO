# E-Ink Slideshow Project

A production-ready e-ink photo frame application designed for the Raspberry Pi with a Waveshare 7.3-inch display. 

This project displays a continuous slideshow of images loaded directly from a USB drive and features a built-in web dashboard for easy management.

## Features

- **E-Ink Display Optimization:** Automatically resizes, crops, and enhances images for the Waveshare display.
- **Web Dashboard:** Access a clean, professional web UI from any browser on the local network.
- **Image Management:** Upload new images (drag & drop) or delete existing ones directly through the dashboard.
- **Real-time File Synchronization:** Uses filesystem monitoring (`watchdog`) to automatically detect USB changes and update the slideshow without restarting.
- **USB Auto-Detection:** Automatically locates inserted USB drives without hardcoding mount paths.
- **Dynamic Settings:** Change the refresh interval via the web dashboard with immediate effect.

## Project Structure

```
project/
├── main.py                     # Entry point for the application
├── web_ui/                     # Flask web application
│   ├── app.py                  # Web server routes and logic
│   └── templates/              # HTML interfaces (Bootstrap 5)
├── slideshow/                  # E-Ink display logic
│   ├── display_manager.py      # Background thread for e-ink updates
│   ├── image_converter.py      # Image processing (crop/resize/enhance)
│   └── usb_monitor.py          # Watchdog and USB detection
├── config/                     # Configuration files
│   └── settings.json           # Stores user preferences
├── requirements.txt            # Python dependencies
└── setup.sh                    # Automated systemd setup script
```

## Hardware Requirements

- Raspberry Pi 4 (or similar) running Raspberry Pi OS (Bookworm).
- Waveshare 7.3-inch 6-color E-Paper Display.
- USB Flash Drive (formatted as FAT32 or exFAT).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nguyenhongphu2007-pixel/IFB102-ProjectEXPO.git
   cd IFB102-ProjectEXPO
   ```

2. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
   *(Note: On newer Raspberry Pi OS versions, you may need to use a virtual environment or run `pip3 install --break-system-packages -r requirements.txt` if permitted by your setup.)*

3. **Install the Service (Optional but Recommended):**
   To make the project run automatically on boot:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   Follow the prompt to reboot the Raspberry Pi.

## Running the Application Manually

To run the application from the terminal:
```bash
python3 main.py
```

## USB Setup

1. Format a USB drive to FAT32 or exFAT.
2. Insert the USB drive into the Raspberry Pi.
3. The application will automatically detect the drive, process any existing images, and begin the slideshow.

## Dashboard Usage

Once the application is running, open a web browser on any device connected to the same network.

Navigate to:
```
http://raspberrypi.local:5000
```
*(Or replace `raspberrypi.local` with the actual IP address of your Raspberry Pi).*

From the dashboard, you can:
- **Gallery:** View all currently uploaded images and delete unwanted ones.
- **Upload:** Drag and drop new JPG, PNG, or WEBP images directly to the USB drive.
- **Settings:** Change the slideshow refresh interval.

## Troubleshooting

- **No Images Displaying:** Ensure your USB drive is inserted and properly mounted by the Raspberry Pi OS. Check the dashboard gallery to verify images were detected.
- **Service Not Starting:** Check systemd logs using `sudo journalctl -u epaper.service -e`.
- **Web Dashboard Unreachable:** Ensure you are on the same local network as the Raspberry Pi and that no firewall is blocking port 5000.
