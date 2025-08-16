from flask import Flask, jsonify, send_file
import random
import string
import os
import shutil
import zipfile
import tempfile

app = Flask(__name__)

def generate_random_password():
    full_width_letters = [f'\\uff{hex(0xFF21 + i)[2:].zfill(2)}' for i in range(26)]
    first_part = ''.join(random.choice(full_width_letters) for _ in range(7))
    separator = '\\u3164'
    second_part = ''.join(random.choice(full_width_letters) for _ in range(4))
    alphanumeric = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
    return f"{first_part}{separator}{second_part}_{alphanumeric}"

def generate_random_uid():
    return random.randint(1000000000, 9999999999)

def generate_guest_account():
    return {
        "guest_account_info": {
            "com.garena.msdk.guest_password": generate_random_password(),
            "com.garena.msdk.guest_uid": generate_random_uid()
        }
    }

def create_account_files(num, temp_dir):
    parent_folder_name = "NR_CODEX_OUTPUT"
    parent_folder_path = os.path.join(temp_dir, parent_folder_name)
    os.makedirs(parent_folder_path, exist_ok=True)
    
    for i in range(num):
        # Create a unique subfolder named NR_CODEX_GUEST_IDS_<number>
        account_folder_name = f"NR_CODEX_GUEST_IDS_{i + 1}"
        account_folder_path = os.path.join(parent_folder_path, account_folder_name)
        os.makedirs(account_folder_path, exist_ok=True)
        
        # Generate unique account info
        account = generate_guest_account()
        
        # Create .dat file named guest100067.dat in each subfolder
        file_name = "guest100067.dat"
        file_path = os.path.join(account_folder_path, file_name)
        with open(file_path, 'w') as f:
            f.write(str(account))
    
    return parent_folder_path, parent_folder_name

def create_zip_file(folder_path, folder_name):
    zip_path = f"{folder_path}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Maintain folder structure in zip
                arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                zipf.write(file_path, arcname)
    return zip_path

@app.route('/generate/<int:num>', methods=['GET'])
def generate_multiple_accounts(num):
    if num < 1 or num > 10000:
        return jsonify({"error": "Number of accounts must be between 1 and 10000"}), 400
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create account files and folder structure
        folder_path, folder_name = create_account_files(num, temp_dir)
        
        # Create zip file
        zip_path = create_zip_file(folder_path, folder_name)
        
        # Send zip file as response
        response = send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"{folder_name}.zip"
        )
        
        return response
    
    finally:
        # Cleanup: Remove temporary files and directories
        shutil.rmtree(temp_dir, ignore_errors=True)
        if 'zip_path' in locals() and os.path.exists(zip_path):
            os.remove(zip_path)

if __name__ == '__main__':
    app.run(debug=True)
