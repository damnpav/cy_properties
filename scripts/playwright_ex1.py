from playwright.sync_api import sync_playwright
import time


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.bazaraki.com/real-estate-to-rent/apartments-flats/")
    time.sleep(5)

    # Принимаем cookies
    try:
        page.get_by_role("button", name="Согласиться").click(timeout=5000)
    except:
        pass
    time.sleep(2)

    links = page.eval_on_selector_all(
        "a[href*='/adv/']",
        "els => els.map(el => el.href)"
    )

    print(f'write links from page 1')
    with open(f'links_buf1.txt', 'w') as file:
        file.write('\n'.join(links))

    time.sleep(2)
    print(f'go to page 2')
    page.get_by_role("link", name="2", exact=True).click()
    time.sleep(10)
    links = page.eval_on_selector_all(
        "a[href*='/adv/']",
        "els => els.map(el => el.href)"
    )

    print(f'write links from page 2')
    with open(f'links_buf2.txt', 'w') as file:
        file.write('\n'.join(links))

    browser.close()
