import os
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

# URL de la page météo de Casablanca
URL = "https://www.meteomaroc.com/plage/casablanca"

def normalize_text(text):
    """ Normalise le texte en supprimant les espaces superflus et en uniformisant les caractères """
    if text:
        return ' '.join(text.strip().split())
    return ""

def scrape_meteo_casablanca():
    # Chemin du fichier CSV
    script_dir = os.path.dirname(os.path.realpath(__file__))
    csv_file_path = os.path.join(script_dir, "meteo_casablanca.csv")
    
    # En-têtes pour contourner les restrictions éventuelles
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Requête HTTP
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # Vérifie que la requête a réussi
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Ouvrir le fichier CSV
        with open(csv_file_path, "w", newline="", encoding="utf-8-sig") as file:
            file.write('sep=;\n')
            writer = csv.writer(file, delimiter=';')
            
            # En-têtes du CSV
            writer.writerow(["Date", "Heure", "Température", "Conditions", "Vent", "Humidité"])
            
            # Trouver le conteneur principal des prévisions
            forecast_container = soup.find("div", class_="forecast-container")
            
            if forecast_container:
                # Extraire les jours de prévision
                days = forecast_container.find_all("div", class_="forecast-day")
                
                for day in days:
                    # Date du jour
                    date_element = day.find("div", class_="forecast-day-date")
                    date = normalize_text(date_element.text) if date_element else "N/A"
                    
                    # Heures de prévision
                    hours = day.find_all("div", class_="forecast-hour")
                    
                    for hour in hours:
                        # Heure
                        time_element = hour.find("div", class_="forecast-hour-time")
                        time = normalize_text(time_element.text) if time_element else "N/A"
                        
                        # Température
                        temp_element = hour.find("div", class_="forecast-hour-temp")
                        temperature = normalize_text(temp_element.text) if temp_element else "N/A"
                        
                        # Conditions
                        condition_element = hour.find("div", class_="forecast-hour-condition")
                        condition = normalize_text(condition_element.text) if condition_element else "N/A"
                        
                        # Vent
                        wind_element = hour.find("div", class_="forecast-hour-wind")
                        wind = normalize_text(wind_element.text) if wind_element else "N/A"
                        
                        # Humidité
                        humidity_element = hour.find("div", class_="forecast-hour-humidity")
                        humidity = normalize_text(humidity_element.text) if humidity_element else "N/A"
                        
                        # Écrire dans le CSV
                        writer.writerow([date, time, temperature, condition, wind, humidity])
            
        print(f"Scraping terminé! Données sauvegardées dans '{csv_file_path}'")
    
    except Exception as e:
        print(f"Une erreur est survenue: {str(e)}")

if __name__ == "__main__":
    scrape_meteo_casablanca()