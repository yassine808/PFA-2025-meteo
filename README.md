# Rabat Weather Dashboard

A Python project that scrapes weather data for **Rabat, Morocco** from [meteomaroc.com](https://www.meteomaroc.com) and presents it through an interactive **Streamlit** dashboard.

## Features

- **Current Weather** — Real-time temperature, conditions, wind speed, and precipitation
- **Hourly Temperature Chart** — Visualizes temperature throughout the day
- **15-Day Forecast** — Max/min temperatures and weather conditions for the next 15 days
- **Ideal Day Finder** — Analyzes the 15-day forecast and recommends the best day for outdoor activities based on a weighted quality score (temperature, wind, sunshine, precipitation)
- **UV Index Scraper** — Fetches the current UV index and safety advice
- **Beach/Marine Scraper** — Retrieves sea state, water temperature, wave height, and tide data for Rabat beach

## Project Structure

| File | Description |
|------|-------------|
| `inter.py` | Main Streamlit dashboard application |
| `scraper_current.py` | Scrapes current weather data |
| `scraper_wholeday.py` | Scrapes hourly weather for the full day |
| `scraper_15day.py` | Scrapes the 15-day weather forecast |
| `rabat_uv.py` | Scrapes the current UV index |
| `rabat_maire_current.py` | Scrapes beach and marine conditions |
| `rabat_maire_current.csv` | Sample output from the beach scraper |
| `requirements.txt` | Python dependencies |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the Dashboard

```bash
streamlit run inter.py
```

### Run Individual Scrapers

```bash
python scraper_current.py
python scraper_wholeday.py
python scraper_15day.py
python rabat_uv.py
python rabat_maire_current.py
```

Each scraper saves its data as a CSV file in the project directory, which the dashboard then reads and visualizes.

## How the Ideal Day Finder Works

The quality score (0–1) for each day is calculated using weighted factors:

- **Temperature (30%)** — Moderate temperatures score highest
- **Wind (20%)** — Calm conditions score highest
- **Sunshine (40%)** — Sunny days score highest
- **Dryness (10%)** — Days without precipitation score highest

The day with the highest combined score is recommended as the ideal day for outdoor activities.

## Technologies

- **Python 3**
- **Streamlit** — Interactive web dashboard
- **BeautifulSoup4** — Web scraping
- **Pandas** — Data manipulation
- **Matplotlib / Seaborn** — Data visualization
- **NumPy** — Numerical computations
- **Requests** — HTTP requests
