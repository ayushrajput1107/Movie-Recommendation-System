import streamlit as st
import pandas as pd
from recommender import MovieRecommender
from chatbot import MovieChatbot
import time

# --- Page Config ---
st.set_page_config(
    page_title="AI Movie Compass",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Global Styles */
    body {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F8B400; /* Aesthetic Gold */
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#F8B400, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
    }
    
    /* Movie Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(248, 180, 0, 0.3);
    }
    
    .movie-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-bottom: 5px;
    }
    
    .movie-meta {
        font-size: 0.9rem;
        color: #A0AEC0;
        margin-bottom: 10px;
    }
    
    .movie-desc {
        font-size: 1rem;
        color: #E2E8F0;
        line-height: 1.5;
        margin-bottom: 15px;
    }
    
    .explanation-box {
        background-color: rgba(66, 153, 225, 0.1);
        border-left: 4px solid #4299E1;
        padding: 10px 15px;
        border-radius: 0 8px 8px 0;
        font-size: 0.9rem;
        color: #bee3f8;
        font-style: italic;
    }
    
    /* Chatbot styling */
    .chat-msg-user {
        background-color: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        text-align: right;
        color: white;
    }
    .chat-msg-bot {
        background-color: rgba(248, 180, 0, 0.1);
        border-left: 3px solid #F8B400;
        padding: 10px;
        border-radius: 0 8px 8px 0;
        margin: 5px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- App State & Initialization ---
@st.cache_resource
def get_recommender():
    return MovieRecommender()

@st.cache_resource
def get_chatbot():
    return MovieChatbot()

recommender = get_recommender()
chatbot = get_chatbot()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Helper Functions ---
def render_movie_card(row, explanation, key_suffix, include_feedback=True):
    st.markdown(f"""
    <div class="movie-card">
        <div class="movie-title">{row['title']}</div>
        <div class="movie-meta">⏱️ {row['duration']} mins | ⚡ Energy: {row['energy_level']} | 🎭 Genres: {row['genres']}</div>
        <div class="movie-desc">{row['overview']}</div>
        <div class="explanation-box">🧠 <b>AI Reason:</b><br/>{explanation.replace(chr(10), '<br/>')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if include_feedback:
        col1, col2, col3 = st.columns([1,1,3])
        with col1:
            if st.button("👍 Like", key=f"like_{row['movie_id']}_{key_suffix}"):
                if recommender.update_feedback(row['movie_id'], 'Like'):
                    st.toast(f"Liked {row['title']}!", icon="✅")
        with col2:
            if st.button("👎 Dislike", key=f"dislike_{row['movie_id']}_{key_suffix}"):
                if recommender.update_feedback(row['movie_id'], 'Dislike'):
                    st.toast(f"Disliked {row['title']}.", icon="❌")
        with col3:
             if st.button("⏭️ Not Interested", key=f"skip_{row['movie_id']}_{key_suffix}"):
                if recommender.update_feedback(row['movie_id'], 'Not Interested'):
                    st.toast(f"Skipped {row['title']}.", icon="⏭️")

# --- UI Layout ---
st.markdown("<h1>🎦 AI Movie Compass</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0AEC0; margin-top: -15px; margin-bottom: 30px;'>Discover movies tailored exactly to your mood, time, and vibe.</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎯 Precision Discovery", "💬 Chat Recommendations"])

# --- TAB 1: Precision Discovery ---
with tab1:
    col_filters, col_results = st.columns([1, 2.5])
    
    with col_filters:
        st.markdown("### 🎛️ Customize Your Filters", unsafe_allow_html=True)
        
        # Mood Input
        st.markdown("**How are you feeling right now?**")
        user_mood_text = st.text_area("Express your mood (e.g., 'I had a fantastic day!', 'Just feeling sad and tired.')", height=100)
        
        # Duration Filter
        st.markdown("**How much time do you have?**")
        max_duration = st.slider("Max Duration (mins)", min_value=60, max_value=240, value=120, step=10)
        
        # Energy Filter
        st.markdown("**What energy level are you looking for?**")
        target_energy = st.select_slider("Energy Output", options=["Low", "Medium", "High", "Any"], value="Any")
        
        find_btn = st.button("Find Movies! 🚀", use_container_width=True, type="primary")
        
    with col_results:
        if find_btn:
            with st.spinner("Analyzing your preferences... 🧠"):
                time.sleep(1) # Artificial delay for effect
                recs, detected_mood = recommender.recommend_movies(
                    user_text=user_mood_text, 
                    max_duration=max_duration, 
                    target_energy=target_energy
                )
                
                if user_mood_text:
                    st.info(f"🎭 **Detected Mood:** {detected_mood} (Guides genre selection)")
                
                st.markdown("### ✨ Your Top Recommendations")
                
                if len(recs) == 0:
                    st.warning("No movies perfectly matched all your criteria, however we expanded the search!")
                    recs, _ = recommender.recommend_movies(top_n=3)
                
                for idx, (_, row) in enumerate(recs.iterrows()):
                    explanation = recommender.explain_recommendation(row, detected_mood, max_duration, target_energy)
                    render_movie_card(row, explanation, key_suffix=f"tab1_idx{idx}")
        elif st.session_state.get('initial_load', True):
            st.info("👈 Set your mood, time constraints, and desired energy level on the left to get starting recommendations.")

# --- TAB 2: Chatbot ---
with tab2:
    st.markdown("### 💬 Chat with the AI Movie Guide")
    st.markdown("Try asking: *'I want to watch something exciting and high energy under 2 hours. I am feeling great!'*")
    
    # Render Chat History
    for chat in st.session_state.chat_history:
        if chat['role'] == 'user':
            st.markdown(f"<div class='chat-msg-user'>👤 <b>You:</b> {chat['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-msg-bot'>🤖 <b>AI Guide:</b> {chat['text']}</div>", unsafe_allow_html=True)
            if 'df' in chat and chat['df'] is not None:
                for idx, (_, row) in enumerate(chat['df'].iterrows()):
                    explanation = recommender.explain_recommendation(
                        row, chat['mood'], chat['duration'], chat['energy']
                    )
                    render_movie_card(row, explanation, key_suffix=f"chat_{idx}", include_feedback=False)

    # Input Form
    with st.form(key='chat_form', clear_on_submit=True):
        user_query = st.text_input("Message the AI Guide...", placeholder="What kind of movie are you looking for?")
        submit_chat = st.form_submit_button("Send ✉️")
        
        if submit_chat and user_query:
            # Save user query
            st.session_state.chat_history.append({"role": "user", "text": user_query})
            
            # Process query
            with st.spinner("Thinking..."):
                response_text, recommendations, mood, detected_duration, detected_energy = chatbot.get_response(recommender, user_query)
                
                # Save bot response
                st.session_state.chat_history.append({
                    "role": "bot", 
                    "text": response_text,
                    "df": recommendations,
                    "mood": mood,
                    "duration": detected_duration,
                    "energy": detected_energy
                })
            
            # Rerun to update chat ui
            st.rerun()
