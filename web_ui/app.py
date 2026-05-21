import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_expo_key'

def get_settings():
    settings_file = app.config.get('SETTINGS_FILE')
    if settings_file and os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    return {"refresh_interval": 30}

def save_settings(settings):
    settings_file = app.config.get('SETTINGS_FILE')
    if settings_file:
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

def get_usb_path():
    monitor = app.config.get('USB_MONITOR')
    if monitor:
        return monitor.get_current_usb_path()
    return None

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    usb_path = get_usb_path()
    images = []
    if usb_path and os.path.exists(usb_path):
        for f in os.listdir(usb_path):
            if allowed_file(f) and not f.startswith('.'):
                file_path = os.path.join(usb_path, f)
                # Getting file modification time for sorting/display
                mod_time = os.path.getmtime(file_path)
                images.append({
                    'filename': f,
                    'mtime': mod_time
                })
        # Sort by newest first
        images.sort(key=lambda x: x['mtime'], reverse=True)
    
    return render_template('gallery.html', images=images, usb_connected=bool(usb_path))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    usb_path = get_usb_path()
    
    if request.method == 'POST':
        if not usb_path:
            flash('No USB drive detected. Cannot upload files.', 'danger')
            return redirect(request.url)
            
        if 'files[]' not in request.files:
            flash('No files provided.', 'danger')
            return redirect(request.url)
            
        files = request.files.getlist('files[]')
        
        success_count = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(usb_path, filename)
                file.save(file_path)
                success_count += 1
                
        if success_count > 0:
            flash(f'Successfully uploaded {success_count} images!', 'success')
        else:
            flash('No valid images were uploaded. Please ensure they are JPG, PNG, or WEBP.', 'warning')
            
        return redirect(url_for('gallery'))
        
    return render_template('upload.html', usb_connected=bool(usb_path))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    usb_path = get_usb_path()
    if usb_path:
        file_path = os.path.join(usb_path, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                flash(f'Image {filename} deleted successfully.', 'success')
            except Exception as e:
                flash(f'Error deleting {filename}: {e}', 'danger')
        else:
            flash('File not found.', 'danger')
    else:
        flash('No USB drive detected.', 'danger')
        
    return redirect(url_for('gallery'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    current_settings = get_settings()
    
    if request.method == 'POST':
        try:
            interval = int(request.form.get('refresh_interval', 30))
            if interval < 5:
                interval = 5  # Minimum 5 seconds
            current_settings['refresh_interval'] = interval
            save_settings(current_settings)
            flash('Settings saved successfully! The slideshow will update immediately.', 'success')
        except ValueError:
            flash('Invalid interval value. Must be a number.', 'danger')
            
    return render_template('settings.html', settings=current_settings)

@app.route('/image/<filename>')
def serve_image(filename):
    usb_path = get_usb_path()
    if usb_path:
        return send_from_directory(usb_path, filename)
    return "Not Found", 404
