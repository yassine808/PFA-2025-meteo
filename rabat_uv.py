import os
import requests
from bs4 import BeautifulSoup
import csv

URL = "https://www.meteomaroc.com/meteo/rabat"

def clean_text(text):
    if not text:
        return "N/A"
    return ' '.join(text.replace('\n', ' ').replace('\r', '').strip().split())

def scrape_uv_index():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        uv_data = {}

        uv_section = soup.find("div", class_="style_Indice")
        if uv_section:
            date = uv_section.find("h6")
            level = uv_section.find("h5")
            value = uv_section.find("div", class_="value")
            note = uv_section.find("p")

            uv_data["Date"] = clean_text(date.text) if date else "N/A"
            uv_data["Niveau"] = clean_text(level.text) if level else "N/A"
            uv_data["Valeur"] = clean_text(value.text) if value else "N/A"
            uv_data["Conseils"] = clean_text(note.text) if note else "N/A"

        # Save to CSV
        script_dir = os.path.dirname(os.path.realpath(__file__))
        csv_file = os.path.join(script_dir, "rabat_UV.csv")

        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            f.write('sep=;\n')
            writer = csv.writer(f, delimiter=';')
            writer.writerow(uv_data.keys())
            writer.writerow(uv_data.values())

        print("UV data successfully scraped and saved to rabat_UV.csv")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scrape_uv_index()
