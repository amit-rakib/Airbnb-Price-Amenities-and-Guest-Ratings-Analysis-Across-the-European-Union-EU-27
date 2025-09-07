import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options  

LOCATIONS = [
    # Sweden
    ("Sweden", "Stockholm"),
    ("Sweden", "Gothenburg"),
    ("Sweden", "Malmö"),
    ("Sweden", "Uppsala"),
    ("Sweden", "Lund"),

    # France
    ("France", "Paris"),
    ("France", "Lyon"),
    ("France", "Marseille"),
    ("France", "Nice"),
    ("France", "Bordeaux"),

    # Germany
    ("Germany", "Berlin"),
    ("Germany", "Munich"),
    ("Germany", "Hamburg"),
    ("Germany", "Cologne"),
    ("Germany", "Frankfurt"),

    # Italy
    ("Italy", "Rome"),
    ("Italy", "Milan"),
    ("Italy", "Naples"),
    ("Italy", "Turin"),
    ("Italy", "Florence"),

    # Spain
    ("Spain", "Madrid"),
    ("Spain", "Barcelona"),
    ("Spain", "Valencia"),
    ("Spain", "Seville"),
    ("Spain", "Bilbao"),

    # Netherlands
    ("Netherlands", "Amsterdam"),
    ("Netherlands", "Rotterdam"),
    ("Netherlands", "The Hague"),
    ("Netherlands", "Utrecht"),
    ("Netherlands", "Eindhoven"),

    # Belgium
    ("Belgium", "Brussels"),
    ("Belgium", "Antwerp"),
    ("Belgium", "Ghent"),
    ("Belgium", "Bruges"),
    ("Belgium", "Leuven"),

    # Denmark
    ("Denmark", "Copenhagen"),
    ("Denmark", "Aarhus"),
    ("Denmark", "Odense"),
    ("Denmark", "Aalborg"),
    ("Denmark", "Esbjerg"),

    # Norway
    ("Norway", "Oslo"),
    ("Norway", "Bergen"),
    ("Norway", "Trondheim"),
    ("Norway", "Stavanger"),
    ("Norway", "Tromsø"),

    # Finland
    ("Finland", "Helsinki"),
    ("Finland", "Espoo"),
    ("Finland", "Tampere"),
    ("Finland", "Oulu"),
    ("Finland", "Turku"),

    # Poland
    ("Poland", "Warsaw"),
    ("Poland", "Krakow"),
    ("Poland", "Gdansk"),
    ("Poland", "Wroclaw"),
    ("Poland", "Poznan"),

    # Czech Republic
    ("Czech Republic", "Prague"),
    ("Czech Republic", "Brno"),
    ("Czech Republic", "Ostrava"),
    ("Czech Republic", "Pilsen"),
    ("Czech Republic", "Olomouc"),

    # Austria
    ("Austria", "Vienna"),
    ("Austria", "Graz"),
    ("Austria", "Linz"),
    ("Austria", "Salzburg"),
    ("Austria", "Innsbruck"),

    # Switzerland
    ("Switzerland", "Zurich"),
    ("Switzerland", "Geneva"),
    ("Switzerland", "Basel"),
    ("Switzerland", "Bern"),
    ("Switzerland", "Lausanne"),

    # Portugal
    ("Portugal", "Lisbon"),
    ("Portugal", "Porto"),
    ("Portugal", "Braga"),
    ("Portugal", "Coimbra"),
    ("Portugal", "Faro"),

    # Ireland
    ("Ireland", "Dublin"),
    ("Ireland", "Cork"),
    ("Ireland", "Limerick"),
    ("Ireland", "Galway"),
    ("Ireland", "Waterford"),

    # United Kingdom
    ("United Kingdom", "London"),
    ("United Kingdom", "Manchester"),
    ("United Kingdom", "Birmingham"),
    ("United Kingdom", "Glasgow"),
    ("United Kingdom", "Edinburgh"),

    # Hungary
    ("Hungary", "Budapest"),
    ("Hungary", "Debrecen"),
    ("Hungary", "Szeged"),
    ("Hungary", "Miskolc"),
    ("Hungary", "Pecs"),

    # Greece
    ("Greece", "Athens"),
    ("Greece", "Thessaloniki"),
    ("Greece", "Patras"),
    ("Greece", "Heraklion"),
    ("Greece", "Larissa"),

    # Croatia
    ("Croatia", "Zagreb"),
    ("Croatia", "Split"),
    ("Croatia", "Rijeka"),
    ("Croatia", "Osijek"),
    ("Croatia", "Zadar"),

    # Romania
    ("Romania", "Bucharest"),
    ("Romania", "Cluj-Napoca"),
    ("Romania", "Timisoara"),
    ("Romania", "Iasi"),
    ("Romania", "Constanta"),

    # Bulgaria
    ("Bulgaria", "Sofia"),
    ("Bulgaria", "Plovdiv"),
    ("Bulgaria", "Varna"),
    ("Bulgaria", "Burgas"),
    ("Bulgaria", "Ruse"),

    # Slovakia
    ("Slovakia", "Bratislava"),
    ("Slovakia", "Kosice"),
    ("Slovakia", "Presov"),
    ("Slovakia", "Nitra"),
    ("Slovakia", "Zilina"),

    # Slovenia
    ("Slovenia", "Ljubljana"),
    ("Slovenia", "Maribor"),
    ("Slovenia", "Celje"),
    ("Slovenia", "Kranj"),
    ("Slovenia", "Velenje"),

    # Estonia
    ("Estonia", "Tallinn"),
    ("Estonia", "Tartu"),
    ("Estonia", "Narva"),
    ("Estonia", "Parnu"),
    ("Estonia", "Kohtla-Jarve"),

    # Latvia
    ("Latvia", "Riga"),
    ("Latvia", "Daugavpils"),
    ("Latvia", "Liepaja"),
    ("Latvia", "Jelgava"),
    ("Latvia", "Jurmala"),

    # Lithuania
    ("Lithuania", "Vilnius"),
    ("Lithuania", "Kaunas"),
    ("Lithuania", "Klaipeda"),
    ("Lithuania", "Siauliai"),
    ("Lithuania", "Panevezys"),

    # Luxembourg
    ("Luxembourg", "Luxembourg City"),
    ("Luxembourg", "Esch-sur-Alzette"),
    ("Luxembourg", "Differdange"),
    ("Luxembourg", "Dudelange"),
    ("Luxembourg", "Ettelbruck"),
]


PER_CITY_LIMIT = None

AMENITY_SECTIONS = [
    "Bathroom",
    "Bedroom and laundry",
    "Entertainment",
    "Heating and cooling",
    "Privacy and safety",
    "Internet and office",
    "Kitchen and dining",
    "Parking and facilities",
    "Services",
]

def get_listing_data(driver, country, city):
    row = {}
    try:
        row["Title"] = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
    except:
        row["Title"] = ""

    def grab(label):
        try:
            return driver.find_element(
                By.XPATH, f".//*[normalize-space()='{label}']/following::*[normalize-space(text())][1]"
            ).text
        except:
            return ""

    row["Cleanliness"]   = grab("Cleanliness")
    row["Accuracy"]      = grab("Accuracy")
    row["Check-in"]      = grab("Check-in")
    row["Communication"] = grab("Communication")
    row["Value"]         = grab("Value")

    row["Country"] = country
    row["City"]    = city

    try:
        price_text = driver.find_elements(By.CLASS_NAME, "umg93v9")[1].text
        row["Price"] = "".join(ch for ch in price_text if ch.isdigit())
    except:
        row["Price"] = ""

    for sec in AMENITY_SECTIONS:
        row[sec] = "0"

    try:
        show_all_btn = driver.find_element(By.XPATH, "//span[contains(.,'Show all')]/parent::button")
        driver.execute_script("arguments[0].click();", show_all_btn)
        time.sleep(2)

        sections = driver.find_elements(By.CSS_SELECTOR, "div._11jhslp")
        for section in sections:
            try:
                sec_title = section.find_element(By.TAG_NAME, "h2").text.strip()
            except:
                continue

            if sec_title in AMENITY_SECTIONS:
                try:
                    ul = section.find_element(By.CSS_SELECTOR, "ul._2f5j8p[role='list']")
                    items = [li.text.strip() for li in ul.find_elements(By.TAG_NAME, "li") if li.text.strip()]
                    items = [txt for txt in items if not txt.startswith("Unavailable") and "Lock on" not in txt]
                    row[sec_title] = ", ".join(items) if items else "0"
                except:
                    row[sec_title] = "0"

        try:
            driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
        except:
            pass
    except:
        pass

    return row

def main():
    opts = Options()
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-blink-features=AutomationControlled")
   
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    opts.add_argument("--window-size=800,900")


    driver = webdriver.Chrome(options=opts)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US','en'] });
        """
    })


    wait = WebDriverWait(driver, 10)

    all_data = []   

    for country, city in LOCATIONS:
        url = f"https://www.airbnb.com/s/{city}--{country}/homes"
        driver.get(url)

        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH,
                "//button[translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='got it']")))
            btn.click()
        except TimeoutException:
            pass

        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "c965t3n")))
        rooms = driver.find_elements(By.CLASS_NAME, "c965t3n")

        if PER_CITY_LIMIT is not None:
            rooms = rooms[:PER_CITY_LIMIT]

        for room in rooms:
            room.click()
            time.sleep(2)

            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
            time.sleep(2)

            try:
                svg_close = driver.find_element(By.XPATH, "//svg[@aria-hidden='true']//path[@d='m6 6 20 20M26 6 6 26']")
                driver.execute_script("arguments[0].click();", svg_close)
            except NoSuchElementException:
                pass

            row = get_listing_data(driver, country, city)
            all_data.append(row)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

    driver.quit()

    cols = ["Country","City","Title","Price",
            "Cleanliness","Accuracy","Check-in","Communication","Value"] + AMENITY_SECTIONS
    df = pd.DataFrame(all_data, columns=cols)

    df.to_csv("airbnb_listings_with_amenities.csv", index=False)
    print(f"Saved {len(df)} rows total")

if __name__ == "__main__":
    main()
