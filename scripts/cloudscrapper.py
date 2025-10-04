import cloudscraper

scraper = cloudscraper.create_scraper()  # имитирует браузер
url = "https://www.bazaraki.com/ajax-items-list/?page=1&c=5270&rubric=3529"
resp = scraper.get(url)

print(resp.status_code)
print(resp.text[:10000])
