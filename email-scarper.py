import argparse
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
from tqdm import tqdm

# Clean help message
parser = argparse.ArgumentParser(
    description="🔍 Lightweight Email Crawler",
    usage="python3 crawler.py -u <URL> [-m MAX_PAGES] [-t TIMEOUT]",
    add_help=True,  # Still allows -h / --help
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

# Argument parser setup
parser = argparse.ArgumentParser(description="Email Crawler Script")
parser.add_argument("-u", "--url", required=True, help="Target URL to scan")
parser.add_argument("-m", "--max-pages", type=int, default=100, help="Maximum number of pages to scan (default: 100)")
parser.add_argument("-t", "--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")

args = parser.parse_args()

# Initialization
user_url = args.url
max_pages = args.max_pages
timeout = args.timeout

urls = deque([user_url])
scraped_urls = set()
emails = set()

count = 0

try:
    with tqdm(total=max_pages, desc="Crawling Progress") as pbar:
        while urls and count < max_pages:
            url = urls.popleft()
            if url in scraped_urls:
                pbar.update(1)
                continue

            scraped_urls.add(url)
            count += 1

            parts = urllib.parse.urlsplit(url)
            base_url = f"{parts.scheme}://{parts.netloc}"
            path = url[:url.rfind('/') + 1] if '/' in parts.path else url

            try:
                response = requests.get(url, timeout=timeout)
            except (requests.exceptions.MissingSchema,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.InvalidSchema,
                    requests.exceptions.ReadTimeout):
                pbar.update(1)
                continue

            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
            emails.update(new_emails)

            soup = BeautifulSoup(response.text, features="lxml")

            for anchor in soup.find_all("a"):
                link = anchor.get("href", "")
                if not link or link.startswith(("javascript:", "mailto:")):
                    continue
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = urllib.parse.urljoin(path, link)
                if link not in urls and link not in scraped_urls:
                    urls.append(link)

            pbar.update(1)

except KeyboardInterrupt:
    print('\n[-] Interrupted by user!')

number = len(emails)
print(f"\n[+] Emails found:{number}")
for mail in sorted(emails):
    print(mail)
    
