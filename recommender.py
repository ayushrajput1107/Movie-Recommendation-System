import pandas as pd
from textblob import TextBlob
from data_loader import load_data, DATA_FILE

class MovieRecommender:
    def __init__(self):
        self.df = load_data()

    def detect_mood(self, text):
        """Detects mood from text using TextBlob sentiment analysis."""
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        # Simple heuristic mapping sentiment to genres
        if polarity > 0.3:
            return "Happy", ["Comedy", "Action", "Adventure", "Family"]
        elif polarity < -0.1:
            return "Sad", ["Drama", "Romance", "Documentary"]
        else:
            return "Neutral", ["Sci-Fi", "Thriller", "Mystery", "Action", "Fantasy"]

    def recommend_movies(self, user_text="", max_duration=None, target_energy=None, top_n=5):
        """Filters movies based on user preferences and mood."""
        filtered_df = self.df.copy()
        
        # 1. Mood-Based Filtering
        mood, preferred_genres = ("Neutral", [])
        if user_text:
            mood, preferred_genres = self.detect_mood(user_text)
            # Filter where at least one preferred genre matches the movie's genres
            filtered_df = filtered_df[filtered_df['genres'].apply(
                lambda x: any(g in str(x) for g in preferred_genres)
            )]
            
        # 2. Duration Filtering
        if max_duration:
            filtered_df = filtered_df[filtered_df['duration'] <= max_duration]
            
        # 3. Energy-Level Filtering
        if target_energy and target_energy != "Any":
            filtered_df = filtered_df[filtered_df['energy_level'] == target_energy]
            
        # If no movies match criteria, fallback to default dataset (relaxed filters)
        if len(filtered_df) == 0:
            filtered_df = self.df.copy()

        # 4. Sort by RL user_score
        # Higher user score means more likely to be recommended
        # Add a little randomness for exploration
        filtered_df['final_score'] = filtered_df['user_score'] + (pd.Series([0.1]*len(filtered_df)).sample(frac=1).values * 0.5)
        
        recommendations = filtered_df.sort_values(by='final_score', ascending=False).head(top_n)
        
        return recommendations, mood

    def update_feedback(self, movie_id, feedback_type):
        """Reinforcement Learning Feedback: Adjusts the user_score based on feedback."""
        # Simple Multi-Arm Bandit approach equivalent:
        # We increase/decrease the base score of the movie globally for the user simulation.
        idx = self.df.index[self.df['movie_id'] == movie_id].tolist()
        if not idx:
            return False
            
        idx = idx[0]
        current_score = self.df.at[idx, 'user_score']
        
        if feedback_type == 'Like':
            self.df.at[idx, 'user_score'] = min(1.0, current_score + 0.2)
        elif feedback_type == 'Dislike':
            self.df.at[idx, 'user_score'] = max(0.0, current_score - 0.2)
        elif feedback_type == 'Not Interested':
            self.df.at[idx, 'user_score'] = max(0.0, current_score - 0.1)
            
        # Save updated data
        try:
            self.df.to_csv(DATA_FILE, index=False)
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def explain_recommendation(self, movie, mood, max_duration, target_energy):
        """Explainable AI: Creates a transparent string explaining the recommendation."""
        reasons = []
        if mood != "Neutral":
            reasons.append(f"It aligns with your '{mood}' mood based on its genres ({movie['genres']}).")
        
        if max_duration:
            reasons.append(f"It fits your time constraint ({movie['duration']} mins <= {max_duration} mins).")
        
        if target_energy and target_energy != "Any":
            reasons.append(f"It matches your desired '{target_energy}' energy level.")
            
        if movie.get('user_score', 0) > 0.5:
            reasons.append("It has a high preference score based on similar interactions.")
            
        if not reasons:
            return "This movie is generally highly rated and matches broad preferences."
            
        explanation = "We recommend this because:\n- " + "\n- ".join(reasons)
        return explanation
