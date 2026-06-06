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

def extract_temperature(text):
    """Extract temperature value from text"""
    text = clean_text(text)
    if not text:
        return ""
    temp = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
    return f"{temp}°" if temp else ""

def get_weather_condition(icon_class):
    """Determine weather condition from icon class"""
    if not icon_class:
        return "N/A"
    if "weathericon113" in icon_class:
        return "Ensoleillé" if "jour" in icon_class else "Clair"
    elif "weathericon116" in icon_class:
        return "Nuageux"
    return "N/A"

def scrape_rabat_hourly_weather():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        hourly_items = soup.find_all("div", class_="item_selected_ville_hourly_weather_slider")

        hourly_data = {}
        for item in hourly_items:
            # Extract time
            time_label = item.find("label", class_="time-small")
            time = clean_text(time_label.text) if time_label else ""
            if ":" in time:
                time = time.replace(":00", "h")
            elif time and not time.endswith("h"):
                time = f"{time}h"
            
            # Temperature
            temp = extract_temperature(item.find("p").text if item.find("p") else "")
            
            # Condition
            weather_icon = item.find("div", class_=lambda x: x and "weathericon-med" in x)
            condition = get_weather_condition(weather_icon.get("class", [])) if weather_icon else "N/A"
            
            # Other metrics
            precip = "N/A"
            wind_speed = "N/A"
            wind_dir = "N/A"
            cloud_cover = "N/A"

            info_blocks = item.find_all("div", class_="item_info_ville_selected_part2")
            for block in info_blocks:
                img = block.find("img")
                if not img:
                    continue
                
                img_src = img.get("src", "")
                text = clean_text(block.find("p").text) if block.find("p") else ""
                
                if "umbrella" in img_src:
                    precip = text if text else "0%"
                elif "wind.png" in img_src:
                    wind_speed = text if text else "N/A"
                elif "winddirection" in img_src:
                    wind_dir = text.split()[0] if text else "N/A"
                elif "cloud" in img_src:
                    cloud_cover = text if text else "0%"

            # Overwrite only if data is complete
            if temp != "N/A" and precip != "N/A" and wind_speed != "N/A" and wind_dir != "N/A" and cloud_cover != "N/A":
                hourly_data[time] = {
                    "Heure": time,
                    "Temperature": temp,
                    "Conditions": condition,
                    "Precipitations": precip,
                    "Vitesse vent": wind_speed,
                    "Direction vent": wind_dir,
                    "Couverture nuageuse": cloud_cover
                }

        # Sort hours
        sorted_hours = sorted(hourly_data.keys(), key=lambda h: int(h.replace("h", "")))

        script_dir = os.path.dirname(os.path.realpath(__file__))
        csv_file = os.path.join(script_dir, f"rabat_whole_current_day.csv")

        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            f.write('sep=;\n')
            writer = csv.DictWriter(f, fieldnames=[
                "Heure", "Temperature", "Conditions",
                "Precipitations", "Vitesse vent",
                "Direction vent", "Couverture nuageuse"
            ], delimiter=';')
            writer.writeheader()
            for hour in sorted_hours:
                writer.writerow(hourly_data[hour])
        
        print(f"Successfully scraped {len(hourly_data)} complete hourly records")
        print(f"Data saved to: {csv_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scrape_rabat_hourly_weather()
