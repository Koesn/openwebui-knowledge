#!/usr/bin/env python3

import os
import requests
import argparse
import json
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv(".env")
except ImportError:
    print("dotenv not installed, skipping...")

# Konfigurasi
WEBUI_URL = os.getenv("WEBUI_URL", "https://your-open-webui-url.com") 
TOKEN = os.getenv("TOKEN", "your-open-webui-account-api-key-JWT-token")
LOG_FILE = "record.json"

# Fungsi untuk menulis log ke file JSON
def write_to_log(file_path, file_id):
    log_entry = {
        "file_id": file_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_name": Path(file_path).name,
        "file_extension": Path(file_path).suffix,
        "file_size": os.path.getsize(file_path),
        "file_path": file_path
    }
    
    # Baca log yang sudah ada
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='r') as file:
            log_data = json.load(file)
    else:
        log_data = []
        
    # Tambahkan entri baru
    log_data.append(log_entry)
    
    # Tulis kembali ke file
    with open(LOG_FILE, mode='w') as file:
        json.dump(log_data, file, indent=4)

def remove_from_log(file_id):
    if not os.path.exists(LOG_FILE):
        print(f"Record file '{LOG_FILE}' not found.")
        return
    
    try:
        # Baca log yang sudah ada
        with open(LOG_FILE, mode='r') as file:
            log_data = json.load(file)
            
        # Cari dan hapus entri dengan file_id yang sesuai
        new_log_data = [entry for entry in log_data if entry["file_id"] != file_id]
        
        # Tulis kembali ke file
        with open(LOG_FILE, mode='w') as file:
            json.dump(new_log_data, file, indent=4)
            
        print(f"File with ID '{file_id}' successfully removed from record.")
        
    except FileNotFoundError:
        print(f"Record File '{LOG_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Record file '{LOG_FILE}' invalid or empty.")
        return

# Fungsi untuk menghapus log dari file record
def remove_file_from_knowledge(knowledge_id, file_id, file_path):
    url = f'{WEBUI_URL}/api/v1/knowledge/{knowledge_id}/file/remove'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"File '{file_path}' successfully removed from knowledge.")
        return True
    else:
        print(f"Failed to remove file '{file_path}'. Status code: {response.status_code}, Response: {response.text}")
        return False
    
# Fungsi untuk Memproses Penghapusan Iteratif
def process_removal(knowledge_id):
    if not os.path.exists(LOG_FILE):
        print(f"Record file '{LOG_FILE}' not found.")
        return
    
    while True:
        # Buka file log
        with open(LOG_FILE, mode='r') as file:
            log_data = json.load(file)
            
        # Jika tidak ada record lagi, hentikan proses
        if not log_data:
            #print("Semua file berhasil dihapus dari knowledge.")
            break
        
        # Ambil record pertama
        entry = log_data[0]
        file_id = entry["file_id"]
        file_path = entry["file_path"]
        
        # Hapus dari knowledge base
        if remove_file_from_knowledge(knowledge_id, file_id, file_path):
            
            # Hapus record pertama dari log
            log_data.pop(0)  # Hapus record pertama dari list
            
            # Tulis kembali file log tanpa record yang dihapus
            with open(LOG_FILE, mode='w') as file:
                json.dump(log_data, file, indent=4)
                
                #print(f"File dengan ID '{file_id}' berhasil dihapus dari log.")
        else:
            print(f"Failed to remove file '{file_path}'. Process stopped.")
            break

# Fungsi untuk mengunggah file
def upload_file(file_path):
    url = f'{WEBUI_URL}/api/v1/files/'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Accept': 'application/json'
    }
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()

# Fungsi untuk menambahkan file ke knowledge
def add_file_to_knowledge(knowledge_id, file_id):
    url = f'{WEBUI_URL}/api/v1/knowledge/{knowledge_id}/file/add'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'file_id': file_id}
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# Fungsi untuk mencari ID file berdasarkan path dalam log
def find_file_ids_by_path(file_path):
    if not os.path.exists(LOG_FILE):
        print("Record file not found.")
        return []
    
    file_ids = []
    with open(LOG_FILE, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Lewati header
        for row in reader:
            if len(row) >= 6 and row[5] == file_path:
                file_ids.append(row[0])  # Kolom pertama adalah file ID

    if not file_ids:
        print(f"No ID file found for path '{file_path}' in record.")
        
    return file_ids

# Fungsi untuk memproses file atau folder
def process_files(knowledge_id, path, action):
    # Baca log yang sudah ada
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='r') as file:
            log_data = json.load(file)
    else:
        log_data = []
        
    # Buat set dari file_path yang sudah ada di log
    existing_files = {entry["file_path"] for entry in log_data}
    
    if action == "add":
        if os.path.isfile(path):
            # Cek apakah file sudah ada di log
            if path in existing_files:
                print(f"File '{path}' already exist in the knowledge.")
            else:
                uploaded_file = upload_file(path)
                if 'id' in uploaded_file:
                    file_id = uploaded_file['id']
                    add_file_to_knowledge(knowledge_id, file_id)
                    write_to_log(path, file_id)
                    print(f"File '{path}' succesfully added to knowledge with ID '{file_id}'.")
                else:
                    print(f"Failed to upload file '{path}'. Response: {uploaded_file}")
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    # Cek apakah file sudah ada di log
                    if file_path in existing_files:
                        print(f"File '{file_path}' already exist in the knowledge.")
                    else:
                        uploaded_file = upload_file(file_path)
                        if 'id' in uploaded_file:
                            file_id = uploaded_file['id']
                            add_file_to_knowledge(knowledge_id, file_id)
                            write_to_log(file_path, file_id)
                            print(f"File '{file_path}' succesfully added to knowledge with ID '{file_id}'.")
                        else:
                            print(f"Failed to upload file '{file_path}'. Response: {uploaded_file}")
        else:
            print(f"Path '{path}' invalid.")
    elif action == "remove":
        process_removal(knowledge_id)

# Main script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to add/remove knowledge from Open WebUI.")
    
    # Tambahkan argumen opsional untuk --add dan --remove
    parser.add_argument('--add', help='File(s) to upload and added to knowledge')
    parser.add_argument('--remove', help='File(s) to remove from knowledge')
    parser.add_argument('--id', required=True, help='Knowledge ID')
    
    args = parser.parse_args()
    
    # Validasi argumen
    if args.add and args.remove:
        print("Error: Choose only one action (--add or --remove).")
        exit(1)
    elif not args.add and not args.remove:
        print("Error: Choose only one action (--add atau --remove).")
        exit(1)
        
    # Tentukan aksi dan target
    if args.add:
        action = "add"
        target = args.add
    elif args.remove:
        action = "remove"
        target = args.remove
        
    # Proses file
    process_files(args.id, target, action)
    
