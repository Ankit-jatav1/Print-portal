from flask import Flask, request, session, render_template, redirect, url_for
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a secure key

UPLOAD_FOLDER = 'uploads'
temp_storage = {}  # Temporary dictionary to store file data

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Admin login page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Change to secure credentials
            session['admin'] = True  # Set session flag for admin
            return redirect(url_for('admin_dashboard'))  # Redirect to dashboard
        else:
            return "Invalid credentials", 403
    return render_template('admin_login.html')  # Show login form

# Admin dashboard page (accessible only after login)
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin'):  # Check if admin is logged in
        return redirect(url_for('admin_login'))  # Redirect to login page if not logged in
    files = list(temp_storage.keys())  # Get the list of files from temp storage
    return render_template('admin_dashboard.html', files=files)  # Show files to admin

# Admin logout page
@app.route('/logout')
def logout():
    session.pop('admin', None)  # Clear the session
    return redirect(url_for('admin_login'))  # Redirect to login page after logout

# Customer upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        customer_name = request.form['customerName']
        category = request.form['category']
        files = request.files.getlist('files')
        for file in files:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            temp_storage[file.filename] = {
                "customer_name": customer_name,
                "category": category,
                "timestamp": time.time()  # Store timestamp of upload
            }
        return "Files uploaded successfully", 200
    return render_template('customer_upload.html')  # Show upload form to customer

# Function to delete old files after 4 hours
def delete_old_files():
    current_time = time.time()
    for file, details in list(temp_storage.items()):
        if current_time - details['timestamp'] > 14400:  # 4 hours (14400 seconds)
            os.remove(os.path.join(UPLOAD_FOLDER, file))  # Delete file
            del temp_storage[file]  # Remove file from temp storage

# Schedule the file deletion task every hour
scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_files, 'interval', hours=1)
scheduler.start()

# Test page (optional)
@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug=True)
