import pandas as pd
import os

# Path to CSV file
csv_file = "articles.csv"

# Create the CSV file if it doesn't exist
def create_table():
    if not os.path.exists(csv_file):
        # Create a DataFrame with the column names
        columns = ['id', 'titre', 'url', 'date', 'categorie', 'contenu']
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, index=False)  # Save empty file with headers
        print(f"CSV file '{csv_file}' created.")

# Get all articles from the CSV
def get_all_articles():
    # Check if CSV exists
    if not os.path.exists(csv_file):
        print("CSV file not found!")
        return []

    # Load the data from the CSV into a DataFrame
    df = pd.read_csv(csv_file)
    articles = df.sort_values(by='date', ascending=False).to_dict(orient='records')  # Sort by date (desc)
    return articles

# Insert a new article into the CSV
def ajouter_article(titre, url, date, categorie, contenu):
    # Load the existing data from the CSV
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
    else:
        # Create an empty DataFrame if CSV doesn't exist
        df = pd.DataFrame(columns=['id', 'titre', 'url', 'date', 'categorie', 'contenu'])
    
    # Get the next id (if the file isn't empty)
    next_id = df['id'].max() + 1 if not df.empty else 1
    
    # Create a new row for the article
    new_article = pd.DataFrame([{
        'id': next_id,
        'titre': titre,
        'url': url,
        'date': date,
        'categorie': categorie,
        'contenu': contenu
    }])
    
    # Append the new article to the DataFrame
    df = pd.concat([df, new_article], ignore_index=True)

    # Save the updated DataFrame back to the CSV
    df.to_csv(csv_file, index=False)
    print(f"Article '{titre}' added successfully!")

# Test the functions
if __name__ == "__main__":
    # Create table (CSV file) if not exists
    create_table()

    # Adding a new article
    ajouter_article(
        titre="How to Use CSV with Python",
        url="https://example.com/csv-python",
        date="2025-06-27",
        categorie="Python",
        contenu="This article explains how to work with CSV files in Python."
    )

    # Get all articles
    articles = get_all_articles()
    print("All articles:")
    for article in articles:
        print(article)
