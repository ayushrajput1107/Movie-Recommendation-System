import re

class MovieChatbot:
    def __init__(self):
        # Basic intent matching using simple keywords
        self.energy_keywords = {
            "High": ["exciting", "fast", "action", "energetic", "thrilling", "pumped"],
            "Medium": ["balanced", "steady", "average", "normal"],
            "Low": ["chill", "relaxing", "slow", "calm", "sad", "peaceful", "quiet"]
        }
        
    def parse_query(self, query):
        """
        Parses a natural language query extracting explicitly mentioned filters:
        - duration (e.g., "under 120 mins", "less than 2 hours")
        - energy level
        """
        query = query.lower()
        
        # 1. Parse Duration (looking for numbers preceding min, hr, etc.)
        max_duration = None
        duration_match = re.search(r'under\s+(\d+)\s*(min|hour|hr)', query)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            max_duration = value * 60 if 'hour' in unit or 'hr' in unit else value
        else:
            duration_match = re.search(r'less than\s+(\d+)\s*(min|hour|hr)', query)
            if duration_match:
                value = int(duration_match.group(1))
                unit = duration_match.group(2)
                max_duration = value * 60 if 'hour' in unit or 'hr' in unit else value
            else:
                 # look for "about x hours" or "around x mins" as fallback
                 duration_match = re.search(r'(about|around)\s+(\d+)\s*(min|hour|hr)', query)
                 if duration_match:
                    value = int(duration_match.group(2))
                    unit = duration_match.group(3)
                    max_duration = value * 60 if 'hour' in unit or 'hr' in unit else value

        # 2. Parse Energy level
        target_energy = "Any"
        for level, words in self.energy_keywords.items():
            if any(word in query for word in words):
                target_energy = level
                break

        return max_duration, target_energy

    def get_response(self, recommender, query):
        """Conversational pipeline: Parses query, gets recommendations, returning a conversational string and the dataframe"""
        
        max_duration, target_energy = self.parse_query(query)
        
        # Pass the full query to recommender for mood detection as well
        recommendations, mood = recommender.recommend_movies(
            user_text=query,
            max_duration=max_duration,
            target_energy=target_energy,
            top_n=3
        )

        response_text = f"I sense you are feeling '{mood}'. "
        if target_energy != "Any":
             response_text += f"You're looking for something with {target_energy} energy. "
        if max_duration:
             response_text += f"I kept it under {max_duration} minutes. "
             
        response_text += "Here is what I found for you:\n\n"
        
        if len(recommendations) == 0:
            return "Actually, I couldn't find anything matching all those criteria right now. Try adjusting your preferences!", None

        for _, row in recommendations.iterrows():
            response_text += f"🎬 **{row['title']}** ({row['duration']} min | {row['energy_level']} energy | {row['genres']})\n"

        return response_text, recommendations, mood, max_duration, target_energy
