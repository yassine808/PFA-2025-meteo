import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

URL = "https://www.meteomaroc.com/meteo/rabat"

def clean_text(text):
    """Clean text by removing extra spaces and newlines"""
    if text is None:
        return ""
    return ' '.join(str(text).strip().split())

def get_weather_condition(icon_class):
    """Determine weather condition from icon class"""
    if not icon_class:
        return "N/A"
    if "weathericon113" in icon_class:
        return "Ensoleillé"
    elif "weathericon116" in icon_class:
        return "Nuageux"
    return "N/A"

def scrape_rabat_15_days_weather():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    try:
        # Fetch the page
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # This will raise an error if the request fails
        soup = BeautifulSoup(response.text, "html.parser")

        # Parse forecast data
        forecast_items = soup.find_all("div", class_="item_previsionsjours_slider")
        forecast_data = []

        for item in forecast_items:
            label = item.find("label")
            day = clean_text(label.text) if label else "N/A"

            # Ensure we get the correct class for the icon
            icon_div = item.find("div", class_=lambda x: x and "weathericon-med" in x)
            if icon_div:
                icon_class = icon_div.get("class", [])
                condition = get_weather_condition(icon_class)
            else:
                condition = "N/A"

            # Handle temperatures
            temps = item.find_all("span")
            temp_max = clean_text(temps[0].text) if len(temps) > 0 else "N/A"
            temp_min = clean_text(temps[1].text) if len(temps) > 1 else "N/A"

            # Handle precipitation and wind
            p_tags = item.find_all("p", class_="rain")
            precip = clean_text(p_tags[0].text.replace("mm", "").strip()) + " mm" if len(p_tags) > 0 else "N/A"
            wind = clean_text(p_tags[1].text.replace("km/h", "").strip()) + " km/h" if len(p_tags) > 1 else "N/A"

            # Add to data
            forecast_data.append({
                "Jour": day,
                "Temperature max": temp_max,
                "Temperature min": temp_min,
                "Conditions": condition,
                "Precipitations": precip,
                "Vent": wind
            })

        # Save the data to CSV
        script_dir = os.path.dirname(os.path.realpath(__file__))
        csv_file = os.path.join(script_dir, "rabat_next_15days.csv")

        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            f.write("sep=;\n")  # Set separator for CSV
            writer = csv.DictWriter(f, fieldnames=[
                "Jour", "Temperature max", "Temperature min",
                "Conditions", "Precipitations", "Vent"
            ], delimiter=';')
            writer.writeheader()
            writer.writerows(forecast_data)

        print(f"Successfully scraped {len(forecast_data)} forecast records")
        print(f"Data saved to: {csv_file}")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scrape_rabat_15_days_weather()
