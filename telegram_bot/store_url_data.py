import json
import os
import time
from urllib.parse import urlparse, urlunparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def normalize_url(url):
    """Normalize URLs by removing query params, fragments, and trailing slashes."""
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, "", "", ""))
    return cleaned_url.rstrip("/")

def scrape_url_playwright(url):
    """Scrape full page text using Playwright and return plain text."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        html_content = page.content()
        browser.close()

    soup = BeautifulSoup(html_content, "html.parser")
    text = " ".join([tag.text for tag in soup.find_all(["p", "h1", "h2", "h3", "li", "span", "div"])])
    return text

def save_url_data(url, content):
    """Save scraped content into knowledge.json under normalized URL."""
    data = {}

    if os.path.exists("knowledge.json"):
        with open("knowledge.json", "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Warning: knowledge.json is corrupted. Creating a fresh file.")

    clean_url = normalize_url(url)
    data[clean_url] = content

    with open("knowledge.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Data saved for {clean_url}")

def read_urls_from_txt(file_path="links.txt"):
    """Read and return list of URLs from a plain text file (one per line)."""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return []

    with open(file_path, "r") as f:
        urls = [line.strip() for line in f if line.strip().startswith("http")]

    return urls

def main():
    urls = read_urls_from_txt("links.txt")
    if not urls:
        print("⚠️ No valid URLs found in links.txt")
        return

    print(f"🔗 Found {len(urls)} URLs in links.txt. Starting scraping...")

    for url in urls:
        print(f"📄 Scraping: {url}")
        try:
            content = scrape_url_playwright(url)
            save_url_data(url, content)
            time.sleep(2)  # Prevent overloading the server
        except Exception as e:
            print(f"⚠️ Failed to scrape {url}: {e}")

    print("✅ All data from links.txt stored in knowledge.json!")

if __name__ == "__main__":
    main()









