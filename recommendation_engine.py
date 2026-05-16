import pandas as pd

def rank_movies(df, mood, max_duration, target_energy, user_profile, chatbot_filters=None):
    """
    Ranks movies based on multiple dimensions and returns sorted results.
    """
    chatbot_filters = chatbot_filters or {}
    
    # 1. Filter by Hard Constraints
    filtered_df = df.copy()
    
    # Duration Filter
    if max_duration:
        filtered_df = filtered_df[filtered_df['runtime_minutes'] <= max_duration]
    
    # Chatbot Genre Filters
    if chatbot_filters.get('genres'):
        target_genres = [g.capitalize() for g in chatbot_filters['genres']]
        
        def has_target_genre(genre_str):
            movie_genres = [g.strip() for g in genre_str.split('|')]
            return any(tg in movie_genres for tg in target_genres)
            
        filtered_df = filtered_df[filtered_df['genres'].apply(has_target_genre)]
        
    if filtered_df.empty:
        return []
        
    # 2. Score remaining movies
    scored_movies = []
    for _, row in filtered_df.iterrows():
        score = row['base_rating'] # Base score 5.0 - 9.5
        explanation = []
        
        # RL Weights from profile
        movie_genres = [g.strip() for g in row['genres'].split('|')]
        genre_multiplier = sum(user_profile.get('genre_weights', {}).get(g, 1.0) for g in movie_genres) / len(movie_genres)
        score *= genre_multiplier
        
        energy_multiplier = user_profile.get('energy_weights', {}).get(row['energy_level'], 1.0)
        score *= energy_multiplier
        
        if genre_multiplier > 1.2:
            explanation.append(f"Highly matches your historical genre preferences.")
            
        # Match Energy
        if target_energy != "Any":
            if row['energy_level'] == target_energy:
                score += 5.0
                explanation.append(f"Matches your '{target_energy}' energy preference.")
            else:
                score -= 2.0
        
        # Match Mood
        if mood and mood != "Neutral":
            if row['mood_tags'] == mood:
                score += 5.0
                explanation.append(f"Perfectly suits your '{mood}' mood.")
            else:
                score -= 1.0
                
        # Generate base explanation if empty
        if not explanation:
            explanation.append("A solid generic recommendation based on ratings.")
            
        # Combine explanation into a readable string
        reasoning = " | ".join(explanation) + f" (Score: {score:.1f})"
        
        movie_dict = row.to_dict()
        movie_dict['final_score'] = score
        movie_dict['explanation'] = reasoning
        scored_movies.append(movie_dict)
        
    # Sort by final score descending
    scored_movies.sort(key=lambda x: x['final_score'], reverse=True)
    return scored_movies
