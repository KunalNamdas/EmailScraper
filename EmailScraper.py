import os
import sys
import time
import platform
import random
import logging
import requests
from bs4 import BeautifulSoup
import re
import tldextract
from collections import deque
import signal
from fake_useragent import UserAgent
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(filename='program.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Attempt to import colorama, install it if not available
try:
    from colorama import Style, Fore, Back
except ModuleNotFoundError:
    logging.error("colorama module not found. Installing...")
    os.system("pip install colorama")
    from colorama import Style, Fore, Back

# Define color configurations
all_col = [
    Style.BRIGHT + Fore.RED,
    Style.BRIGHT + Fore.CYAN,
    Style.BRIGHT + Fore.LIGHTCYAN_EX,
    Style.BRIGHT + Fore.LIGHTBLUE_EX,
    Style.BRIGHT + Fore.LIGHTMAGENTA_EX,
    Style.BRIGHT + Fore.LIGHTYELLOW_EX,
]

all_DARKCOLORS = [
    Style.BRIGHT + Fore.CYAN,
    Style.BRIGHT + Fore.GREEN,
    Style.BRIGHT + Fore.RED,
    Style.BRIGHT + Fore.YELLOW,
    Style.BRIGHT + Fore.BLUE,
    Style.BRIGHT + Fore.WHITE,
]

ran = random.choice(all_DARKCOLORS)
ran2 = random.choice(all_col)

# Define specific colors
lg = Style.BRIGHT + Fore.LIGHTGREEN_EX
g = Style.BRIGHT + Fore.GREEN
lc = Style.BRIGHT + Fore.LIGHTCYAN_EX
c = Style.BRIGHT + Fore.CYAN
ly = Style.BRIGHT + Fore.LIGHTYELLOW_EX
y = Style.BRIGHT + Fore.YELLOW
r = Style.BRIGHT + Fore.RED
lr = Style.BRIGHT + Fore.LIGHTRED_EX
b = Style.BRIGHT + Fore.BLUE
w = Style.BRIGHT + Fore.LIGHTWHITE_EX

# Define the logo with ASCII art
logo = f"""
   ▄████████   ▄▄▄▄███▄▄▄▄      ▄████████  ▄█   ▄█               ▄████████  ▄████████    ▄████████    ▄████████    ▄███████▄    ▄████████    ▄████████ 
  ███    ███ ▄██▀▀▀███▀▀▀██▄   ███    ███ ███  ███              ███    ███ ███    ███   ███    ███   ███    ███   ███    ███   ███    ███   ███    ███ 
  ███    █▀  ███   ███   ███   ███    ███ ███▌ ███              ███    █▀  ███    █▀    ███    ███   ███    ███   ███    ███   ███    █▀    ███    ███ 
 ▄███▄▄▄     ███   ███   ███   ███    ███ ███▌ ███              ███        ███         ▄███▄▄▄▄██▀   ███    ███   ███    ███  ▄███▄▄▄      ▄███▄▄▄▄██▀ 
▀▀███▀▀▀     ███   ███   ███ ▀███████████ ███▌ ███            ▀███████████ ███        ▀▀███▀▀▀▀▀   ▀███████████ ▀█████████▀  ▀▀███▀▀▀     ▀▀███▀▀▀▀▀   
  ███    █▄  ███   ███   ███   ███    ███ ███  ███                     ███ ███    █▄  ▀███████████   ███    ███   ███          ███    █▄  ▀███████████ 
  ███    ███ ███   ███   ███   ███    ███ ███  ███▌    ▄         ▄█    ███ ███    ███   ███    ███   ███    ███   ███          ███    ███   ███    ███ 
  ██████████  ▀█   ███   █▀    ███    █▀  █▀   █████▄▄██       ▄████████▀  ████████▀    ███    ███   ███    █▀   ▄████▀        ██████████   ███    ███ 
                                               ▀                                        ███    ███                                          ███    ███ 
                                                                                                                                                                                                                                           
                                                        
            </> Author: Kunal-Namdas    
            </> GitHub : @kunalnamdas                                                                                                      
"""

# Function to print the banner with the logo
def banner():
    print(ran + logo)

# Function to get random user agent
def get_random_user_agent():
    ua = UserAgent()
    return ua.random

# Function to extract emails from a webpage
def extract_emails_from_page(content):
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
    return emails

# Function to handle graceful termination
def signal_handler(sig, frame):
    logging.info('Program terminated successfully.')
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Function to crawl and extract emails
def crawl_website(start_url, delay):
    visited = set()
    queue = deque([start_url])
    all_emails = set()

    while queue:
        url = queue.popleft()
        if url in visited:
            continue

        visited.add(url)
        print(f'[+] Crawling URL: {url}')

        headers = {'User-Agent': get_random_user_agent()}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            content = response.text
        except RequestException as e:
            logging.error(f'Request failed: {e}')
            continue

        try:
            emails = extract_emails_from_page(content)
            all_emails.update(emails)
        except re.error as e:
            logging.error(f'Regex error: {e}')
            continue

        soup = BeautifulSoup(content, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if href.startswith('/'):
                href = start_url + href
            elif href.startswith('http'):
                ext = tldextract.extract(href)
                base_ext = tldextract.extract(start_url)
                if ext.domain == base_ext.domain:
                    queue.append(href)
                    time.sleep(delay)  # Delay between requests to avoid detection

    return all_emails

# Main function
def main():
    try:
        os.system("cls")
        banner()
       
        domain = input("Enter the domain to scrape: ").strip()
        delay = float(input("Enter the delay between requests (in seconds): ").strip())

        if not domain:
            logging.error("Domain cannot be empty")
            return

        start_url = f'http://{domain}'
        
        emails = crawl_website(start_url, delay)

        logging.info(f'Found emails: {emails}')

        with open('emails.txt', 'w') as f:
            for email in emails:
                f.write(f'{email}\n')

        logging.info('Emails saved to emails.txt')
        print("Emails saved successfully!")

    except KeyboardInterrupt:
        logging.info('Program terminated successfully.')

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')

if __name__ == "__main__":
    main()
