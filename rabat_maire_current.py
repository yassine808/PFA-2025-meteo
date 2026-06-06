import os
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://www.meteomaroc.com/plage/rabat"

def clean_text(text):
    if not text:
        return "N/A"
    return ' '.join(text.replace('\n', ' ').replace('\r', '').strip().split())

def extract_temperature(text):
    if not text:
        return "N/A"
    text = str(text)
    digits = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
    return f"{digits}°" if digits else "N/A"

def scrape_rabat_maire_current():
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'fr-FR,fr;q=0.9'
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        data = {}

        # Date & Heure
        label = soup.select_one(".selected_ville_part1_top label.d-lg-block")
        if label:
            parts = clean_text(label.text).split("|")
            data["Date"] = parts[0].strip() if len(parts) > 0 else "N/A"
            data["Heure"] = parts[1].strip() if len(parts) > 1 else "N/A"

        # Températures
        max_span = soup.select_one(".selected_ville_max_and_min_temps .hote")
        min_span = soup.select_one(".selected_ville_max_and_min_temps .cooled")
        data["Temperature Max"] = extract_temperature(max_span.text if max_span else None)
        data["Temperature Min"] = extract_temperature(min_span.text if min_span else None)

        # Etat de la mer
        mer = soup.select_one(".plage_temp_and_stats_plage_goodorbad p img")
        data["Etat mer"] = clean_text(mer.find_next_sibling(text=True)) if mer else "N/A"

        # Baignade
        baignade = soup.select_one(".flag-green")
        data["Baignade"] = clean_text(baignade.text) if baignade else "N/A"

        # Infos météo bas
        infos = soup.select(".selected_ville_part1_bottom .item_info_ville_selected_part2")
        for info in infos:
            img = info.find("img")
            ps = info.find_all("p")
            alt = img.get("alt", "").lower() if img else ""

            if "pluie" in alt:
                data["Precipitations"] = clean_text(ps[0].text) if ps else "N/A"
            elif "vagues" in alt:
                data["Vagues"] = clean_text(ps[0].text) if ps else "N/A"
            elif "temperature mer" in alt:
                data["Temperature eau"] = clean_text(ps[0].text) if ps else "N/A"
            elif "vent" in alt and "direction" not in alt:
                data["Vent"] = clean_text(ps[0].text) if ps else "N/A"
            elif "basse" in alt:
                data["Maree basse"] = clean_text(ps[0].text) if ps else "N/A"
            elif "pleine" in alt:
                data["Maree haute 1"] = clean_text(ps[0].text) if len(ps) > 0 else "N/A"
                data["Maree haute 2"] = clean_text(ps[1].text) if len(ps) > 1 else "N/A"
            elif "sunrise" in alt:
                data["Lever soleil"] = clean_text(ps[0].text) if ps else "N/A"
            elif "sunset" in alt:
                data["Coucher soleil"] = clean_text(ps[0].text) if ps else "N/A"

        # Enregistrer CSV
        output_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "rabat_maire_current.csv")
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            f.write("sep=;\n")
            writer = csv.writer(f, delimiter=";")
            writer.writerow(data.keys())
            writer.writerow(data.values())

        print("Data scraped and saved to rabat_maire_current.csv")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scrape_rabat_maire_current()
