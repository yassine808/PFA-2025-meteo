# inter.py - Complete Weather Dashboard
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import io

# Set page configuration
st.set_page_config(
    page_title="Rabat Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-container {
        background-color: #0E1117;
        color: white;
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1F2730;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .recommendation-card {
        padding: 20px;
        border-radius: 10px;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    .temperature-display {
        color: white !important;
        font-size: 42px;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 28px;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
    }
    .section-header {
        color: #4CAF50;
        font-size: 24px;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 8px;
        margin: 25px 0 15px 0;
    }
    .chart-container {
        background-color: #1F2730;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .error-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #f44336;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Load data with robust error handling
        forecast = pd.read_csv("rabat_next_15days.csv", sep=";", skiprows=1)
        current = pd.read_csv("rabat_weather_current.csv", sep=";", skiprows=1)
        hourly = pd.read_csv("rabat_whole_current_day.csv", sep=";", skiprows=1)
        
        # Clean and standardize data
        forecast = forecast.drop_duplicates().fillna(0)
        current = current.fillna(0)
        hourly = hourly.fillna(0)
        
        # Convert temperature columns
        for df in [forecast, current, hourly]:
            if 'Température' in df.columns:
                df['Temperature'] = df['Température'].str.replace('°', '').astype(float)
            if 'Température max' in df.columns:
                df['Temperature max'] = df['Température max'].str.replace('°', '').astype(float)
            if 'Température min' in df.columns:
                df['Temperature min'] = df['Température min'].str.replace('°', '').astype(float)
        
        return forecast, current, hourly
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def normalize_manual(series):
    """Robust MinMax scaling with edge case handling"""
    series = pd.to_numeric(series, errors='coerce').fillna(0)
    if series.nunique() == 1:  # All values same
        return pd.Series([0.5]*len(series))
    return (series - series.min()) / (series.max() - series.min())

# Load data
forecast, current, hourly = load_data()

# Main app
st.title("🌤️ Rabat Weather Dashboard")

if current is None or forecast is None or hourly is None:
    st.error("Failed to load weather data. Please check your CSV files.")
    st.stop()

try:
    # ======================
    # CURRENT WEATHER SECTION
    # ======================
    st.markdown('<div class="section-header">Current Weather</div>', unsafe_allow_html=True)
    
    # Extract current weather data
    current_data = {
        'temp': current.iloc[0].get('Temperature', 0),
        'conditions': current.iloc[0].get('Conditions', 'N/A'),
        'wind': current.iloc[0].get('Vitesse vent', 'N/A'),
        'precip': current.iloc[0].get('Precipitations', '0 mm')
    }
    
    # Display current weather metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card">'
            f'<h1 class="temperature-display">{current_data["temp"]}°C</h1>'
            f'<p>{current_data["conditions"]}</p>'
            f'</div>', 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3>Wind</h3>'
            f'<p>{current_data["wind"]}</p>'
            f'</div>', 
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<h3>Precipitation</h3>'
            f'<p>{current_data["precip"]}</p>'
            f'</div>', 
            unsafe_allow_html=True
        )

    # ======================
    # HOURLY TEMPERATURE CHART
    # ======================
    st.markdown('<div class="section-header">Hourly Temperature</div>', unsafe_allow_html=True)
    
    hourly['Temperature'] = pd.to_numeric(hourly['Temperature'].str.replace('°', ''), errors='coerce').fillna(0)
    
    with st.container():
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot hourly temperature
        sns.lineplot(
            data=hourly, 
            x='Heure', 
            y='Temperature', 
            color='#FF5733',
            linewidth=3,
            marker='o',
            markersize=10,
            markeredgecolor='white',
            markeredgewidth=1.5
        )
        
        # Add value labels
        for x, y in zip(hourly['Heure'], hourly['Temperature']):
            ax.text(
                x, y + 0.5, f'{int(y)}°',
                ha='center', va='bottom',
                color='white',
                fontsize=10,
                bbox=dict(facecolor='#1F2730', edgecolor='#FF5733', boxstyle='round,pad=0.3')
            )
        
        # Customize chart
        ax.set_title("Temperature Throughout the Day", color='white', pad=20)
        ax.set_ylabel("Temperature (°C)", color='white')
        ax.set_xlabel("Hour of Day", color='white')
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_facecolor('#1F2730')
        fig.patch.set_facecolor('#1F2730')
        ax.tick_params(colors='white', which='both')
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # 15-DAY FORECAST
    # ======================
    st.markdown('<div class="section-header">15-Day Forecast</div>', unsafe_allow_html=True)
    
    # Prepare forecast data
    forecast['Temperature max'] = pd.to_numeric(forecast['Temperature max'].str.replace('°', ''), errors='coerce').fillna(0)
    forecast['Temperature min'] = pd.to_numeric(forecast['Temperature min'].str.replace('°', ''), errors='coerce').fillna(0)
    forecast['Temperature range'] = forecast['Temperature max'] - forecast['Temperature min']
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Temperature Forecast", "Weather Conditions"])
    
    with tab1:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Plot temperature range
            forecast.plot(
                x='Jour',
                y=['Temperature max', 'Temperature min'],
                color=['#FF5733', '#3498db'],
                linewidth=2.5,
                marker='o',
                ax=ax
            )
            
            ax.set_title("15-Day Temperature Forecast", color='white', pad=15)
            ax.set_ylabel("Temperature (°C)", color='white')
            ax.set_xlabel("Day", color='white')
            ax.legend(["Max Temperature", "Min Temperature"], facecolor='#1F2730')
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_facecolor('#1F2730')
            fig.patch.set_facecolor('#1F2730')
            ax.tick_params(colors='white', which='both')
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Plot weather conditions
            condition_counts = forecast['Conditions'].value_counts()
            colors = ['#4CAF50', '#2196F3', '#9C27B0', '#FF9800']
            condition_counts.plot(
                kind='bar',
                color=colors[:len(condition_counts)],
                ax=ax
            )
            
            ax.set_title("Weather Conditions Frequency", color='white', pad=15)
            ax.set_ylabel("Number of Days", color='white')
            ax.set_xlabel("", color='white')
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_facecolor('#1F2730')
            fig.patch.set_facecolor('#1F2730')
            ax.tick_params(colors='white', which='both')
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
            st.markdown('</div>', unsafe_allow_html=True)

    # ======================
    # IDEAL DAY FINDER
    # ======================
    st.markdown('<div class="section-header">Ideal Day Finder</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="margin-bottom: 20px;">
        This feature analyzes the next 15 days of weather data to recommend 
        the best day for outdoor activities based on temperature, wind, 
        precipitation, and weather conditions.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Find Best Day for Outdoor Activities", key="ideal_day_button"):
        with st.spinner('Analyzing weather data...'):
            try:
                # Prepare data with robust type handling
                forecast['Wind max'] = (
                    forecast['Vent']
                    .astype(str)
                    .str.extract(r'(\d+)\s*-')[0]
                    .astype(float)
                    .fillna(0)
                )
                forecast['Precipitation'] = (
                    forecast['Precipitations']
                    .astype(str)
                    .str.replace(' mm', '')
                    .replace('', '0')
                    .astype(float)
                )
                
                # Handle weather conditions
                forecast['Conditions'] = forecast['Conditions'].fillna('Unknown')
                
                # Calculate scores (0-1 scale, higher is better)
                scores = {
                    'Temperature': 1 - normalize_manual(forecast['Temperature max']),
                    'Wind': 1 - normalize_manual(forecast['Wind max']),
                    'Sunny': forecast['Conditions'].apply(
                        lambda x: 1 if isinstance(x, str) and 'Ensoleillé' in x 
                        else 0.7 if isinstance(x, str) and 'Nuageux' in x 
                        else 0.4
                    ),
                    'Dry': 1 - normalize_manual(forecast['Precipitation'])
                }
                
                # Weighted overall score
                weights = {
                    'Temperature': 0.3,  # Moderate temperatures preferred
                    'Wind': 0.2,         # Calm wind preferred
                    'Sunny': 0.4,        # Sunny conditions preferred
                    'Dry': 0.1           # No precipitation preferred
                }
                
                forecast['Overall_score'] = sum(
                    scores[factor] * weight 
                    for factor, weight in weights.items()
                )
                
                # Find and display best day
                if forecast['Overall_score'].notna().any():
                    best_day = forecast.loc[forecast['Overall_score'].idxmax()]
                    
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h2>🌟 Recommended Day: {best_day['Jour']}</h2>
                        <p><strong>Weather:</strong> {best_day['Conditions']}</p>
                        <p><strong>Temperature:</strong> {best_day['Temperature max']}°C (max) / {best_day['Temperature min']}°C (min)</p>
                        <p><strong>Wind:</strong> {best_day['Vent']}</p>
                        <p><strong>Precipitation:</strong> {best_day['Precipitations']}</p>
                        <p><strong>Quality Score:</strong> {best_day['Overall_score']:.2f}/1.00</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show scoring visualization
                    with st.container():
                        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                        fig, ax = plt.subplots(figsize=(14, 6))
                        
                        # Prepare scores for visualization
                        score_columns = ['Temperature', 'Wind', 'Sunny', 'Dry']
                        score_data = forecast.set_index('Jour')[score_columns]
                        
                        # Plot stacked bar chart
                        score_data.plot(
                            kind='bar',
                            stacked=True,
                            color=['#FF7043', '#5C6BC0', '#66BB6A', '#26C6DA'],
                            ax=ax
                        )
                        
                        ax.set_title("Daily Weather Quality Scores", color='white', pad=15)
                        ax.set_ylabel("Score (0-1)", color='white')
                        ax.set_xlabel("Day", color='white')
                        ax.legend(
                            ["Temperature", "Wind", "Sunny", "Dry"],
                            facecolor='#1F2730'
                        )
                        ax.grid(True, linestyle='--', alpha=0.3)
                        ax.set_facecolor('#1F2730')
                        fig.patch.set_facecolor('#1F2730')
                        ax.tick_params(colors='white', which='both')
                        plt.xticks(rotation=45)
                        
                        st.pyplot(fig)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("Could not determine ideal day - insufficient weather data")
                    
            except Exception as e:
                st.markdown('<div class="error-box">Failed to analyze ideal day</div>', unsafe_allow_html=True)
                st.error(str(e))
                st.write("Debug data:", forecast[['Jour', 'Conditions', 'Temperature max', 'Vent', 'Precipitations']])

except Exception as e:
    st.markdown('<div class="error-box">Error processing weather data</div>', unsafe_allow_html=True)
    st.error(str(e))
    st.write("Debug info - Current data columns:", current.columns.tolist())
    st.write("Debug info - Forecast data columns:", forecast.columns.tolist())