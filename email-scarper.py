from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
from tqdm import tqdm

user_url = str(input('[+] Enter Target URL To Scan: '))
urls = deque([user_url])

scraped_urls = set()
emails = set()

count = 0
max_pages = 100  # Change this to scan more or fewer pages

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
                response = requests.get(url, timeout=5)
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

print("\n[+] Emails found:")
for mail in sorted(emails):
    print(mail)
