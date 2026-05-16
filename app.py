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
    initial_sidebar_state="collapsed"
)

# --- Custom Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@700&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }

    /* Hero Title */
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #F8B400 0%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        text-align: center;
        color: #718096;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Filter Bar (top horizontal layout) */
    .filter-bar {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .filter-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #F8B400;
        margin-bottom: 6px;
    }

    /* Movie Cards */
    .movie-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .movie-card:hover {
        border-color: rgba(248, 180, 0, 0.4);
        transform: translateY(-2px);
    }
    .movie-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 6px;
    }
    .movie-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    .badge {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 3px 10px;
        font-size: 0.78rem;
        color: #CBD5E0;
    }
    .badge-energy-high { border-color: rgba(252, 129, 74, 0.5); color: #FC814A; }
    .badge-energy-medium { border-color: rgba(248, 180, 0, 0.5); color: #F8B400; }
    .badge-energy-low { border-color: rgba(99, 179, 237, 0.5); color: #63B3ED; }

    .movie-desc {
        font-size: 0.95rem;
        color: #A0AEC0;
        line-height: 1.65;
        margin-bottom: 14px;
    }
    .explanation-box {
        background: rgba(248, 180, 0, 0.07);
        border-left: 3px solid #F8B400;
        padding: 10px 14px;
        border-radius: 0 10px 10px 0;
        font-size: 0.875rem;
        color: #ECC94B;
        font-style: italic;
        margin-bottom: 14px;
    }

    /* Mood detected pill */
    .mood-pill {
        display: inline-block;
        background: rgba(99, 179, 237, 0.12);
        border: 1px solid rgba(99, 179, 237, 0.3);
        color: #90CDF4;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        margin-bottom: 16px;
    }

    /* Section header */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #FFFFFF;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    /* Chat messages */
    .chat-bubble-user {
        background: rgba(248, 180, 0, 0.12);
        border: 1px solid rgba(248, 180, 0, 0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        margin: 8px 0 8px 20%;
        color: #FEF3C7;
        font-size: 0.95rem;
        text-align: right;
    }
    .chat-bubble-bot {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px 16px 16px 4px;
        padding: 12px 16px;
        margin: 8px 20% 8px 0;
        color: #E2E8F0;
        font-size: 0.95rem;
    }
    .chat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #718096;
        margin-bottom: 4px;
    }

    /* Divider */
    .divider { border-top: 1px solid rgba(255,255,255,0.07); margin: 20px 0; }

    /* Streamlit button overrides */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        font-family: 'DM Sans', sans-serif;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #F8B400, #ff6b6b);
        border: none;
        color: white;
    }
    .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 22px;
        font-weight: 600;
        color: #718096;
    }
    .stTabs [aria-selected="true"] {
        color: #F8B400 !important;
        border-bottom: 2px solid #F8B400 !important;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #4A5568;
    }
    .empty-state-icon { font-size: 3rem; margin-bottom: 12px; }
    .empty-state-text { font-size: 1rem; }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
def init_state():
    defaults = {
        'chat_history': [],
        'mood_text': '',
        'max_duration': 120,
        'target_energy': 'Any',
        'last_recs': None,
        'last_mood': None,
        'show_results': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# --- App State & Initialization ---
@st.cache_resource
def get_recommender():
    return MovieRecommender()

@st.cache_resource
def get_chatbot():
    return MovieChatbot()

recommender = get_recommender()
chatbot = get_chatbot()


# --- Helper: Energy badge class ---
def energy_badge_class(energy):
    mapping = {'High': 'badge-energy-high', 'Medium': 'badge-energy-medium', 'Low': 'badge-energy-low'}
    return mapping.get(energy, '')


# --- Helper: Render a movie card ---
def render_movie_card(row, explanation, key_suffix, include_feedback=True):
    energy_cls = energy_badge_class(str(row['energy_level']))
    genres_str = str(row['genres'])

    st.markdown(f"""
    <div class="movie-card">
        <div class="movie-title">{row['title']}</div>
        <div class="movie-badges">
            <span class="badge">⏱ {row['duration']} mins</span>
            <span class="badge {energy_cls}">⚡ {row['energy_level']}</span>
            <span class="badge">🎭 {genres_str}</span>
        </div>
        <div class="movie-desc">{row['overview']}</div>
        <div class="explanation-box">🧠 <b>Why this?</b> {explanation.replace(chr(10), ' ')}</div>
    </div>
    """, unsafe_allow_html=True)

    if include_feedback:
        c1, c2, c3, _ = st.columns([1, 1, 1.5, 3])
        with c1:
            if st.button("👍", key=f"like_{row['movie_id']}_{key_suffix}", help="Like"):
                recommender.update_feedback(row['movie_id'], 'Like')
                st.toast(f"Liked {row['title']}!", icon="✅")
        with c2:
            if st.button("👎", key=f"dislike_{row['movie_id']}_{key_suffix}", help="Dislike"):
                recommender.update_feedback(row['movie_id'], 'Dislike')
                st.toast(f"Disliked {row['title']}.", icon="❌")
        with c3:
            if st.button("⏭ Skip", key=f"skip_{row['movie_id']}_{key_suffix}", help="Not Interested"):
                recommender.update_feedback(row['movie_id'], 'Not Interested')
                st.toast(f"Skipped {row['title']}.", icon="⏭️")


# ========== MAIN UI ==========

st.markdown("<div class='hero-title'>🎦 AI Movie Compass</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Discover movies tailored exactly to your mood, time, and vibe.</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎯 Precision Discovery", "💬 Chat Recommendations"])


# ===== TAB 1: PRECISION DISCOVERY =====
with tab1:

    # ---- Filter Bar (horizontal, top layout) ----
    st.markdown("<div class='filter-bar'>", unsafe_allow_html=True)

    col_mood, col_dur, col_energy, col_btns = st.columns([3, 1.5, 1.5, 1.2])

    with col_mood:
        st.markdown("<div class='filter-label'>Your Mood</div>", unsafe_allow_html=True)
        user_mood_text = st.text_input(
            label="mood_input",
            value=st.session_state.mood_text,
            placeholder="e.g. 'I had a fantastic day!' or 'Feeling tired and sad...'",
            label_visibility="collapsed",
            key="mood_input_widget"
        )

    with col_dur:
        st.markdown("<div class='filter-label'>Max Duration</div>", unsafe_allow_html=True)
        max_duration = st.slider(
            "Max Duration (mins)",
            min_value=60, max_value=240,
            value=st.session_state.max_duration,
            step=10,
            label_visibility="collapsed",
            key="dur_slider"
        )
        st.caption(f"{max_duration} mins")

    with col_energy:
        st.markdown("<div class='filter-label'>Energy Level</div>", unsafe_allow_html=True)
        target_energy = st.selectbox(
            "Energy",
            options=["Any", "Low", "Medium", "High"],
            index=["Any", "Low", "Medium", "High"].index(st.session_state.target_energy),
            label_visibility="collapsed",
            key="energy_select"
        )

    with col_btns:
        st.markdown("<div class='filter-label'>&nbsp;</div>", unsafe_allow_html=True)
        find_btn = st.button("🚀 Find", use_container_width=True, type="primary", key="find_btn")
        clear_btn = st.button("🗑 Clear", use_container_width=True, key="clear_btn")

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- Handle Clear ----
    if clear_btn:
        st.session_state.mood_text = ''
        st.session_state.max_duration = 120
        st.session_state.target_energy = 'Any'
        st.session_state.last_recs = None
        st.session_state.last_mood = None
        st.session_state.show_results = False
        st.rerun()

    # ---- Handle Search ----
    if find_btn:
        st.session_state.mood_text = user_mood_text
        st.session_state.max_duration = max_duration
        st.session_state.target_energy = target_energy

        with st.spinner("Analyzing your preferences... 🧠"):
            time.sleep(0.8)
            recs, detected_mood = recommender.recommend_movies(
                user_text=user_mood_text,
                max_duration=max_duration,
                target_energy=target_energy
            )
            if len(recs) == 0:
                recs, detected_mood = recommender.recommend_movies(top_n=3)

        st.session_state.last_recs = recs
        st.session_state.last_mood = detected_mood
        st.session_state.show_results = True

    # ---- Results ----
    if st.session_state.show_results and st.session_state.last_recs is not None:
        recs = st.session_state.last_recs
        detected_mood = st.session_state.last_mood

        if st.session_state.mood_text:
            st.markdown(f"<div class='mood-pill'>🎭 Detected Mood: <b>{detected_mood}</b></div>", unsafe_allow_html=True)

        st.markdown("<div class='section-header'>✨ Your Top Recommendations</div>", unsafe_allow_html=True)

        for idx, (_, row) in enumerate(recs.iterrows()):
            explanation = recommender.explain_recommendation(
                row, detected_mood,
                st.session_state.max_duration,
                st.session_state.target_energy
            )
            render_movie_card(row, explanation, key_suffix=f"tab1_{idx}")

    elif not st.session_state.show_results:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-state-icon'>🎬</div>
            <div class='empty-state-text'>Describe your mood above and hit <b>Find</b> to get personalized recommendations.</div>
        </div>
        """, unsafe_allow_html=True)


# ===== TAB 2: CHAT =====
with tab2:
    st.markdown("<div class='section-header'>💬 Chat with the AI Movie Guide</div>", unsafe_allow_html=True)
    st.caption("Try: *'I want something exciting and high energy under 2 hours, feeling great!'*")

    # Clear chat button (top right)
    col_spacer, col_clearchat = st.columns([5, 1])
    with col_clearchat:
        if st.button("🗑 Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.rerun()

    # ---- Chat history ----
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class='empty-state'>
                <div class='empty-state-icon'>💬</div>
                <div class='empty-state-text'>Start a conversation to get movie recommendations!</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for i, chat in enumerate(st.session_state.chat_history):
                if chat['role'] == 'user':
                    st.markdown(f"""
                    <div class='chat-label' style='text-align:right;'>You</div>
                    <div class='chat-bubble-user'>{chat['text']}</div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='chat-label'>🤖 AI Guide</div>
                    <div class='chat-bubble-bot'>{chat['text']}</div>
                    """, unsafe_allow_html=True)
                    if 'df' in chat and chat['df'] is not None:
                        for idx, (_, row) in enumerate(chat['df'].iterrows()):
                            explanation = recommender.explain_recommendation(
                                row, chat.get('mood', 'Neutral'),
                                chat.get('duration', 120),
                                chat.get('energy', 'Any')
                            )
                            render_movie_card(row, explanation, key_suffix=f"chat_{i}_{idx}", include_feedback=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ---- Input (outside form so no nesting issues) ----
    col_input, col_send = st.columns([5, 1])
    with col_input:
        user_query = st.text_input(
            "chat_input",
            placeholder="What kind of movie are you looking for?",
            label_visibility="collapsed",
            key="chat_text_input"
        )
    with col_send:
        send_btn = st.button("Send ✉️", use_container_width=True, type="primary", key="send_btn")

    if send_btn and user_query:
        st.session_state.chat_history.append({"role": "user", "text": user_query})

        with st.spinner("Thinking..."):
            response_text, recommendations, mood, detected_duration, detected_energy = chatbot.get_response(
                recommender, user_query
            )
            st.session_state.chat_history.append({
                "role": "bot",
                "text": response_text,
                "df": recommendations,
                "mood": mood,
                "duration": detected_duration,
                "energy": detected_energy
            })

        st.rerun()
