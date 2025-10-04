import random
import time
from tqdm import tqdm
import sqlite3
from datetime import datetime
from playwright.sync_api import sync_playwright

# === CONFIG ===
BASE_URL = "https://www.bazaraki.com/real-estate-to-rent/apartments-flats/"
TOTAL_PAGES = 88
DB_FILE = "bazaraki_links.db"

# === INIT DATABASE ===
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    report_dt TEXT NOT NULL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL
)
""")
conn.commit()


def log(level, message):
    """Write logs both to console and database."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {level.upper()}: {message}")
    cur.execute("INSERT INTO logs (ts, level, message) VALUES (?, ?, ?)", (ts, level, message))
    conn.commit()


def save_links(links):
    """Save links to database with current datetime."""
    report_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    unique_links = list(set(links))
    cur.executemany("INSERT INTO links (url, report_dt) VALUES (?, ?)", [(l, report_dt) for l in unique_links])
    conn.commit()
    log("info", f"Saved {len(unique_links)} unique links.")


def random_delay(min_sec=0, max_sec=3):
    delay = random.uniform(min_sec, max_sec)
    log("debug", f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    log("info", f"Navigating to {BASE_URL}")
    page.goto(BASE_URL, timeout=60000)

    time.sleep(5)

    # Try to accept cookies
    try:
        page.get_by_role("button", name="Согласиться").click(timeout=3000)
        log("info", "Accepted cookies.")
    except Exception:
        log("warning", "No cookie consent button found.")

    # Loop through pages
    for page_num in tqdm(range(1, TOTAL_PAGES + 1)):
        try:
            log("info", f"Processing page {page_num}/{TOTAL_PAGES}")
            url = f"{BASE_URL}?page={page_num}"
            page.goto(url, timeout=60000)
            time.sleep(5)

            links = page.eval_on_selector_all(
                "a[href*='/adv/']",
                "els => els.map(el => el.href)"
            )
            log("info", f"Found {len(links)} links on page {page_num}.")

            save_links(links)

            random_delay(0, 3)

        except Exception as e:
            log("error", f"Error on page {page_num}: {e}")
            random_delay(3, 6)
            continue

    browser.close()
    conn.close()
    log("info", "Scraping completed successfully.")
