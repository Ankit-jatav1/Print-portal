from flask import Flask, request, session, render_template, redirect, url_for
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
temp_storage = {}  # Temporary dictionary to store file data

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
                "timestamp": time.time()
            }
        return "Files uploaded successfully", 200
    print("Templates folder exists:", os.path.exists(os.path.join(os.getcwd(), 'templates')))
    return render_template('customer_upload.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))
    files = list(temp_storage.keys())
    return render_template('admin_dashboard.html', files=files)

def delete_old_files():
    current_time = time.time()
    for file, details in list(temp_storage.items()):
        if current_time - details['timestamp'] > 14400:  # 4 hours
            os.remove(os.path.join(UPLOAD_FOLDER, file))
            del temp_storage[file]

scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_files, 'interval', hours=1)
scheduler.start()

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':  # Change these to be secure
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials", 403
    return render_template('admin_login.html')

@app.route('/test')
def test():
    return render_template('test.html')

import os
print("Current working directory:", os.getcwd())


if __name__ == '__main__':
    app.run(debug=True)
