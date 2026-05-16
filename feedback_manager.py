import json
import os

PROFILE_PATH = "user_profile.json"

def load_profile():
    """Loads user profile weights from a local JSON file."""
    if os.path.exists(PROFILE_PATH):
        try:
            with open(PROFILE_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
            
    # Default profile weights
    return {
        "genre_weights": {},
        "energy_weights": {
            "High": 1.0,
            "Medium": 1.0,
            "Low": 1.0
        }
    }

def save_profile(profile):
    """Saves user profile locally."""
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profile, f, indent=4)

def update_weights(movie_genres, movie_energy, feedback_type):
    """
    Updates the RL weights based on explicit feedback.
    feedback_type: 'like', 'dislike', 'not_interested'
    """
    profile = load_profile()
    
    if feedback_type == 'like':
        weight_change = 0.2
    elif feedback_type == 'dislike':
        weight_change = -0.2
    elif feedback_type == 'not_interested':
        weight_change = -0.1
    else:
        return profile
        
    # Update energy weights
    if movie_energy in profile['energy_weights']:
        profile['energy_weights'][movie_energy] = max(0.1, profile['energy_weights'][movie_energy] + weight_change)
        
    # Update genre weights
    genres = movie_genres.split('|')
    for g in genres:
        current_weight = profile['genre_weights'].get(g, 1.0)
        profile['genre_weights'][g] = max(0.1, current_weight + weight_change)
        
    save_profile(profile)
    return profile
