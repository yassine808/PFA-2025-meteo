import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

URL = "https://www.meteomaroc.com/meteo/rabat"

def clean_text(text):
    """Clean text by removing extra spaces, newlines, and special characters"""
    if not text:
        return "N/A"
    text = str(text)
    # Replace multiple spaces/newlines with single space
    return ' '.join(text.replace('\n', ' ').replace('\r', '').strip().split())

def extract_temperature(text):
    """Extract temperature value from text"""
    if not text:
        return "N/A"
    text = str(text)
    temp = ''.join(filter(lambda x: x.isdigit() or x == '.', text))
    return f"{temp}°" if temp else "N/A"

def scrape_rabat_weather():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, "html.parser")
        weather_data = {}
        
        # Extract date and time
        date_label = soup.find("label", class_="d-lg-block d-none")
        if date_label:
            date_time = clean_text(date_label.text).split("|")
            weather_data["Date"] = date_time[0] if len(date_time) > 0 else "N/A"
            weather_data["Heure"] = date_time[1] if len(date_time) > 1 else "N/A"
        
        # Current temperature
        temp_element = soup.find("div", class_="temp_selected_ville_part1")
        weather_data["Temperature"] = extract_temperature(temp_element.p.text if temp_element else None)
        
        # Weather condition (cleaned)
        condition_element = soup.find("div", class_="temp_selected_ville_part2")
        if condition_element and condition_element.p:
            condition_text = condition_element.p.get_text(" ", strip=True)
            # Extract just the condition without the feels-like temp
            weather_data["Conditions"] = condition_text.split('°')[0].strip()
        else:
            weather_data["Conditions"] = "N/A"
        
        # Feels-like temperature
        feels_like = soup.find("span", class_="temp_selected_ville_part2")
        weather_data["Ressentie"] = extract_temperature(feels_like.text if feels_like else None)
        
        # Max and min temperatures
        weather_data["Maximale"] = extract_temperature(soup.find("span", class_="hote-meteo"))
        weather_data["Minimale"] = extract_temperature(soup.find("span", class_="cooled-meteo"))
        
        # Additional weather info with improved cleaning
        info_items = soup.find_all("div", class_="item_info_ville_selected_part2")
        for item in info_items:
            img = item.find("img")
            if not img:
                continue
                
            info_text = item.find("div", class_="item_info_ville_selected_part2_text")
            if not info_text or not info_text.p:
                continue
                
            text_content = clean_text(info_text.p.text)
            
            if "umbrella" in img.get("src", ""):
                weather_data["Precipitations"] = extract_temperature(text_content)
            elif "wind.png" in img.get("src", ""):
                weather_data["Vitesse vent"] = text_content.replace("km/h", "").strip() + " km/h"
            elif "cloud" in img.get("src", ""):
                weather_data["Couverture nuageuse"] = text_content
            elif "winddirection" in img.get("src", ""):
                weather_data["Direction vent"] = text_content.split()[0]
            elif "sunrise" in img.get("src", ""):
                weather_data["Lever soleil"] = text_content.replace("AM", " AM").replace("AMLever du soleil", "AM")
            elif "sunset" in img.get("src", ""):
                weather_data["Coucher soleil"] = text_content.replace("PM", " PM").replace("PMCoucher du soleil", "PM")
        
        # Save to CSV with proper formatting
        script_dir = os.path.dirname(os.path.realpath(__file__))
        csv_file = os.path.join(script_dir, "rabat_weather_current.csv")
        
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            f.write('sep=;\n')
            writer = csv.writer(f, delimiter=';')
            writer.writerow(weather_data.keys())
            # Clean each value before writing
            cleaned_values = [clean_text(str(v)) for v in weather_data.values()]
            writer.writerow(cleaned_values)
        
        print("Weather data successfully scraped and cleaned:")
        for key, value in weather_data.items():
            print(f"{key}: {clean_text(str(value))}")
        print(f"\nData saved to {csv_file}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    scrape_rabat_weather()