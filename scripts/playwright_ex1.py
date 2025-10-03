from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.bazaraki.com/real-estate-to-rent/apartments-flats/")

    time.sleep(10)
    if page.get_by_role("button", name="Согласиться").is_visible():
        page.get_by_role("button", name="Согласиться").click()
    time.sleep(10)

    links = page.eval_on_selector_all(
        "a.js-advert",  # все теги <a class="mask js-advert">
        "elements => elements.map(el => el.href)"
    )

    # приводим к полным ссылкам
    full_links = [f"https://www.bazaraki.com{l}" if l.startswith("/") else l for l in links]

    print(full_links)
    print(len(full_links))

    browser.close()
