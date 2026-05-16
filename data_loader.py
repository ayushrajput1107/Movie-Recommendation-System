import pandas as pd
import numpy as np
import os

DATA_FILE = 'movies.csv'
TMDB_URL = 'https://raw.githubusercontent.com/rashida048/Some-NLP-Projects/master/movie_dataset.csv'

def fetch_and_prepare_real_data():
    """Downloads the TMDB dataset, cleans it, and prepares required columns."""
    print("Downloading real movie dataset... This might take a few seconds.")
    try:
        # Load the external dataset
        raw_df = pd.read_csv(TMDB_URL)
        
        # We only need specific columns for our recommender
        # 'runtime' in TMDB -> 'duration', 'overview' -> 'overview', 'genres' -> 'genres'
        cols_to_keep = ['title', 'genres', 'overview', 'runtime', 'id']
        df = raw_df[cols_to_keep].copy()
        
        # Rename runtime and id to match our Recommender's expectations
        df.rename(columns={'runtime': 'duration', 'id': 'movie_id'}, inplace=True)
        
        # Clean missing data
        df.dropna(subset=['title', 'genres', 'overview', 'duration'], inplace=True)
        
        # Filter out movies with 0 duration (bad data point in TMDB)
        df = df[df['duration'] > 0]

        # Ensure genres is a clean string (TMDB format is space separated string in this specific wrapper dataset)
        # E.g., "Action Adventure Fantasy Science Fiction"
        df['genres'] = df['genres'].astype(str)

        df = assign_energy_levels(df)
        
        # Add User Score for RL
        df["user_score"] = np.random.uniform(0.0, 0.5, len(df)) # start slightly lower
        
        # Reset index
        df.reset_index(drop=True, inplace=True)
        
        df.to_csv(DATA_FILE, index=False)
        print(f"Successfully processed and saved {len(df)} real movies!")
        return df

    except Exception as e:
        print(f"Error fetching real data: {e}")
        return None

def assign_energy_levels(df):
    """Heuristically assigns energy levels based on genre tags."""
    def get_energy(genres_str):
        g = genres_str.lower()
        if any(x in g for x in ['action', 'thriller', 'adventure', 'horror', 'science fiction']):
            return 'High'
        elif any(x in g for x in ['drama', 'romance', 'documentary', 'history']):
            return 'Low'
        else:
            return 'Medium'
            
    df['energy_level'] = df['genres'].apply(get_energy)
    return df

def load_data():
    """Loads the dataset. Downloads the real dataset if it doesn't exist."""
    if not os.path.exists(DATA_FILE):
        return fetch_and_prepare_real_data()
    
    # Validation step to ensure existing movies.csv is the real one, not the 100-row mock one.
    try:
        df = pd.read_csv(DATA_FILE)
        # If it's too small, it's the old mock dataset. Regenerate.
        if len(df) < 500: 
             print("Old mock dataset detected. Upgrading to real dataset...")
             return fetch_and_prepare_real_data()
        return df
    except Exception:
        return fetch_and_prepare_real_data()


if __name__ == "__main__":
    import os
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE) # Force fresh download for testing
    df = load_data()
    if df is not None:
        print(df.head())
