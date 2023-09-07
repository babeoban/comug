import os
import getpass
from cryptography.fernet import Fernet
import time

FOLDER_NAME = 'comug'
USER_HOME = os.path.expanduser("~")
FOLDER_PATH = os.path.join(USER_HOME, FOLDER_NAME)
PASSWORD_FILE = os.path.join(FOLDER_PATH, 'password.txt')
KEY_FILE = os.path.join(FOLDER_PATH, 'key.key')
LIST_FILE = os.path.join(FOLDER_PATH, 'list.txt')

isExist = os.path.exists(FOLDER_PATH)
if not isExist:
   os.makedirs(FOLDER_PATH)

def generate_key():
    return Fernet.generate_key()

def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            return key_file.read()
    else:
        return None

def save_key(key):
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    with open(file_path, 'wb') as file:
        file.write(encrypted_data)

def decrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(data)
    with open(file_path, 'wb') as file:
        file.write(decrypted_data)

def create_or_reset_password():
    new_password = getpass.getpass("Create a new password: ")
    password = getpass.getpass("Confirm the password: ")
    if new_password != password:
        print("Passwords do not match. Exiting...")
        time.sleep(3)
        exit(1)

    key = generate_key()
    save_key(key)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(new_password.encode())
    os.makedirs(FOLDER_PATH, exist_ok=True)

    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'ab') as password_file:  # Open in append mode
            password_file.write(encrypted_password)
    else:
        with open(PASSWORD_FILE, 'wb') as password_file:
            password_file.write(encrypted_password)

    print("Password changed successfully.")

def load_encoded_files_list():
    encoded_files = set()
    if os.path.exists(LIST_FILE):
        with open(LIST_FILE, 'r') as list_file:
            for line in list_file:
                encoded_files.add(line.strip())
    return encoded_files

def save_encoded_files_list(encoded_files):
    with open(LIST_FILE, 'w') as list_file:
        for file in encoded_files:
            list_file.write(file + '\n')

def change_password():
    old_password = getpass.getpass("Enter the old password: ")
    saved_password = create_or_load_password()

    if old_password != saved_password:
        print("Old password is incorrect. Exiting...")
        time.sleep(3)
        exit(1)

    new_password = getpass.getpass("Enter the new password: ")
    confirm_password = getpass.getpass("Confirm the new password: ")

    if new_password != confirm_password:
        print("Passwords do not match. Exiting...")
        time.sleep(3)
        exit(1)

    key = load_key()
    fernet = Fernet(key)
    encrypted_old_password = fernet.encrypt(old_password.encode())
    encrypted_new_password = fernet.encrypt(new_password.encode())

    with open(PASSWORD_FILE, 'wb') as password_file:
        password_file.write(encrypted_new_password)

    print("Password changed successfully.")

def create_or_load_password():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'rb') as password_file:
            encrypted_password = password_file.read()
        key = load_key()
        if key is None:
            print("Password file exists, but encryption key is missing. Resetting the password...")
            create_or_reset_password()
            return create_or_load_password()  # Retry after resetting password

        fernet = Fernet(key)
        try:
            decrypted_password = fernet.decrypt(encrypted_password).decode()
            return decrypted_password
        except:
            print("Password decryption failed. Resetting the password...")
            create_or_reset_password()
            return create_or_load_password()  # Retry after resetting password
    else:
        create_or_reset_password()
        return create_or_load_password()

def main():
    folder_path = os.getcwd()
    key = load_key()
    encoded_files = load_encoded_files_list()
    saved_password = create_or_load_password()  # Moved this line to the beginning

    entered_password = getpass.getpass("Enter the password: ")

    if entered_password != saved_password:
        print("Wrong password. Exiting...")
        time.sleep(3)
        exit(1)

    while True:
        print("1: Encode")
        print("2: Decode")
        print("3: Change Password")
        print("4: Exit")
        choice = input("Choose an option (1/2/3/4): ")

        if choice == '1':
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in encoded_files and file not in ['comug.py', 'comug.exe']:
                        encrypt_file(file_path, key)
                        encoded_files.add(file_path)
            save_encoded_files_list(encoded_files)
            print("Encryption complete.")
        elif choice == '2':
            files_to_remove = []
            for file_path in encoded_files.copy():
                if os.path.exists(file_path) and file_path not in ['comug.py', 'comug.exe']:
                    decrypt_file(file_path, key)
                    files_to_remove.append(file_path)
            for file_path in files_to_remove:
                encoded_files.remove(file_path)
            save_encoded_files_list(encoded_files)
            print("Decryption complete.")
        elif choice == '3':
            change_password()
        elif choice == '4':
            exit(1)
        else:
            print("Invalid choice. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()