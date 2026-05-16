import streamlit as st
import pandas as pd
from recommender import MovieRecommender
from chatbot import MovieChatbot
import time

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YourNextBinge",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }

    /* ── Hero ── */
    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 3rem; font-weight: 800;
        text-align: center; margin-bottom: 0.2rem; letter-spacing: -1px;
    }
    .hero-title-text {
        background: linear-gradient(135deg, #a78bfa 0%, #38bdf8 60%, #34d399 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        text-align: center; color: #64748b; font-size: 1rem; margin-bottom: 2rem;
    }

    /* ── Filter labels (no wrapping div — just labels above widgets) ── */
    .filter-label {
        font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 1.2px; color: #a78bfa; margin-bottom: 4px;
    }

    /* ── Movie Cards ── */
    .movie-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(167, 139, 250, 0.12);
        border-radius: 16px; padding: 22px 24px; margin-bottom: 4px;
        transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
    }
    .movie-card:hover {
        border-color: rgba(56, 189, 248, 0.45);
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(56, 189, 248, 0.08);
    }
    .movie-card-liked   { border-color: rgba(52, 211, 153, 0.5) !important; background: rgba(52, 211, 153, 0.04) !important; }
    .movie-card-disliked{ border-color: rgba(248, 113, 113, 0.4) !important; background: rgba(248, 113, 113, 0.03) !important; opacity: 0.75; }

    .movie-title {
        font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700;
        color: #f1f5f9; margin-bottom: 8px; letter-spacing: -0.3px;
    }
    .movie-badges { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
    .badge {
        background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px; padding: 3px 11px; font-size: 0.77rem; color: #94a3b8;
    }
    .badge-energy-high   { border-color: rgba(52, 211, 153, 0.45); color: #34d399; }
    .badge-energy-medium { border-color: rgba(56, 189, 248, 0.45); color: #38bdf8; }
    .badge-energy-low    { border-color: rgba(167, 139, 250, 0.45); color: #a78bfa; }

    .movie-desc { font-size: 0.93rem; color: #94a3b8; line-height: 1.7; margin-bottom: 14px; }
    .explanation-box {
        background: rgba(56, 189, 248, 0.06); border-left: 3px solid #38bdf8;
        padding: 10px 14px; border-radius: 0 10px 10px 0;
        font-size: 0.875rem; color: #7dd3fc; font-style: italic; margin-bottom: 14px;
    }

    /* ── Feedback pills ── */
    .feedback-liked {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(52, 211, 153, 0.12); border: 1px solid rgba(52, 211, 153, 0.35);
        color: #34d399; border-radius: 20px; padding: 3px 12px; font-size: 0.8rem; font-weight: 600;
    }
    .feedback-disliked {
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.35);
        color: #f87171; border-radius: 20px; padding: 3px 12px; font-size: 0.8rem; font-weight: 600;
    }

    /* ── Mood pill ── */
    .mood-pill {
        display: inline-block;
        background: rgba(52, 211, 153, 0.1); border: 1px solid rgba(52, 211, 153, 0.3);
        color: #34d399; border-radius: 20px; padding: 4px 14px; font-size: 0.85rem; margin-bottom: 16px;
    }

    /* ── Section header ── */
    .section-header {
        font-family: 'Syne', sans-serif; font-size: 1.4rem; font-weight: 700;
        color: #f1f5f9; margin-bottom: 16px; padding-bottom: 10px;
        border-bottom: 1px solid rgba(167, 139, 250, 0.15); letter-spacing: -0.3px;
    }

    /* ── Chat ── */
    .chat-bubble-user {
        background: rgba(167, 139, 250, 0.1); border: 1px solid rgba(167, 139, 250, 0.2);
        border-radius: 16px 16px 4px 16px; padding: 12px 16px; margin: 8px 0 8px 20%;
        color: #e9d5ff; font-size: 0.95rem; text-align: right;
    }
    .chat-bubble-bot {
        background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px 16px 16px 4px; padding: 12px 16px; margin: 8px 20% 8px 0;
        color: #e2e8f0; font-size: 0.95rem;
    }
    .chat-label {
        font-size: 0.68rem; text-transform: uppercase;
        letter-spacing: 1.2px; color: #475569; margin-bottom: 4px;
    }
    .divider { border-top: 1px solid rgba(167, 139, 250, 0.1); margin: 20px 0; }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: 10px; font-weight: 600;
        font-family: 'Inter', sans-serif; transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #a78bfa, #38bdf8); border: none; color: white;
    }
    .stButton > button:hover { opacity: 0.85; transform: translateY(-1px); }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; border-bottom: 1px solid rgba(167, 139, 250, 0.15); margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0; padding: 10px 22px; font-weight: 600; color: #475569;
    }
    .stTabs [aria-selected="true"] {
        color: #a78bfa !important; border-bottom: 2px solid #a78bfa !important;
    }

    /* ── Empty state ── */
    .empty-state { text-align: center; padding: 60px 20px; }
    .empty-state-icon { font-size: 3rem; margin-bottom: 12px; }
    .empty-state-text { font-size: 1rem; color: #475569; }

    /* ── Suppress Streamlit's stale input ghost elements ── */
    div[data-testid="stTextInput"] > div > div > input { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def mins_to_hours(mins):
    try:
        m = int(float(mins))
        h, rem = divmod(m, 60)
        if h and rem: return f"{h}h {rem}m"
        if h:         return f"{h}h"
        return f"{rem}m"
    except Exception:
        return str(mins)


def energy_badge_class(energy):
    return {'High': 'badge-energy-high',
            'Medium': 'badge-energy-medium',
            'Low': 'badge-energy-low'}.get(str(energy), '')


# ── Session State ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        # tab1
        'mood_text': '',
        'max_duration': 120,
        'target_energy': 'Any',
        'last_recs': None,
        'last_mood': None,
        'show_results': False,
        'skipped_ids': set(),
        'feedback_map': {},
        'refresh_count': 0,
        'seen_movie_ids': set(),   # accumulates across refreshes to avoid repeats
        # tab2 — completely separate
        'chat_history': [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Resources ─────────────────────────────────────────────────────────────────

@st.cache_resource
def get_recommender():
    return MovieRecommender()

@st.cache_resource
def get_chatbot():
    return MovieChatbot()

recommender = get_recommender()
chatbot     = get_chatbot()


# ── Movie Card ────────────────────────────────────────────────────────────────

def render_movie_card(row, explanation, key_suffix, include_feedback=True):
    movie_id     = row['movie_id']
    feedback     = st.session_state.feedback_map.get(movie_id)
    duration_str = mins_to_hours(row['duration'])
    energy_cls   = energy_badge_class(row['energy_level'])
    genres_str   = str(row['genres'])

    card_cls = (" movie-card-liked"    if feedback == 'liked'
                else " movie-card-disliked" if feedback == 'disliked'
                else "")

    st.markdown(f"""
    <div class="movie-card{card_cls}">
        <div class="movie-title">{row['title']}</div>
        <div class="movie-badges">
            <span class="badge">🕐 {duration_str}</span>
            <span class="badge {energy_cls}">⚡ {row['energy_level']}</span>
            <span class="badge">🎭 {genres_str}</span>
        </div>
        <div class="movie-desc">{row['overview']}</div>
        <div class="explanation-box">🧠 <b>Why this?</b> {explanation.replace(chr(10), ' ')}</div>
    </div>
    """, unsafe_allow_html=True)

    if include_feedback:
        c1, c2, c3, c_status = st.columns([1, 1, 1.3, 4.5])
        with c1:
            lbl = "👍 ✓" if feedback == 'liked' else "👍"
            if st.button(lbl, key=f"like_{movie_id}_{key_suffix}", help="Like"):
                recommender.update_feedback(movie_id, 'Like')
                st.session_state.feedback_map[movie_id] = 'liked'
                st.rerun()
        with c2:
            lbl = "👎 ✓" if feedback == 'disliked' else "👎"
            if st.button(lbl, key=f"dislike_{movie_id}_{key_suffix}", help="Dislike"):
                recommender.update_feedback(movie_id, 'Dislike')
                st.session_state.feedback_map[movie_id] = 'disliked'
                st.rerun()
        with c3:
            if st.button("⏭ Skip", key=f"skip_{movie_id}_{key_suffix}", help="Remove from list"):
                recommender.update_feedback(movie_id, 'Not Interested')
                st.session_state.skipped_ids.add(movie_id)
                st.rerun()
        with c_status:
            if feedback == 'liked':
                st.markdown("<span class='feedback-liked'>✓ Liked</span>", unsafe_allow_html=True)
            elif feedback == 'disliked':
                st.markdown("<span class='feedback-disliked'>✗ Disliked</span>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    "<div class='hero-title'>🍿 <span class='hero-title-text'>YourNextBinge</span></div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='hero-subtitle'>Find your perfect watch — matched to your mood, time, and vibe.</div>",
    unsafe_allow_html=True
)

tab1, tab2 = st.tabs(["🎬 Find My Movie", "💬 Chat & Discover"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — FIND MY MOVIE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Filter row — NO wrapping div, just columns ──────────────────────────
    col_mood, col_dur, col_energy, col_btns = st.columns([3, 1.5, 1.5, 1.2])

    with col_mood:
        st.markdown("<div class='filter-label'>Your Mood</div>", unsafe_allow_html=True)
        user_mood_text = st.text_input(
            label="mood_input",
            value=st.session_state.mood_text,
            placeholder="e.g. 'I had a fantastic day!' or 'Feeling tired...'",
            label_visibility="collapsed",
            key="mood_input_widget"
        )

    with col_dur:
        st.markdown("<div class='filter-label'>Max Duration</div>", unsafe_allow_html=True)
        max_duration = st.slider(
            "Max Duration", min_value=60, max_value=240,
            value=st.session_state.max_duration, step=10,
            label_visibility="collapsed", key="dur_slider"
        )
        st.caption(f"Up to {mins_to_hours(max_duration)}")

    with col_energy:
        st.markdown("<div class='filter-label'>Energy Level</div>", unsafe_allow_html=True)
        target_energy = st.selectbox(
            "Energy", options=["Any", "Low", "Medium", "High"],
            index=["Any", "Low", "Medium", "High"].index(st.session_state.target_energy),
            label_visibility="collapsed", key="energy_select"
        )

    with col_btns:
        st.markdown("<div class='filter-label'>&nbsp;</div>", unsafe_allow_html=True)
        find_btn  = st.button("🚀 Find",  use_container_width=True, type="primary", key="find_btn")
        clear_btn = st.button("🗑 Clear", use_container_width=True, key="clear_btn")

    st.markdown("---", unsafe_allow_html=False)   # simple HR — no rectangle

    # ── Clear ────────────────────────────────────────────────────────────────
    if clear_btn:
        st.session_state.mood_text     = ''
        st.session_state.max_duration  = 120
        st.session_state.target_energy = 'Any'
        st.session_state.last_recs     = None
        st.session_state.last_mood     = None
        st.session_state.show_results  = False
        st.session_state.skipped_ids   = set()
        st.session_state.feedback_map  = {}
        st.session_state.refresh_count = 0
        st.session_state.seen_movie_ids = set()
        st.rerun()

    # ── Search ───────────────────────────────────────────────────────────────
    if find_btn:
        st.session_state.mood_text      = user_mood_text
        st.session_state.max_duration   = max_duration
        st.session_state.target_energy  = target_energy
        st.session_state.skipped_ids    = set()
        st.session_state.feedback_map   = {}
        st.session_state.refresh_count  = 0
        st.session_state.seen_movie_ids = set()

        with st.spinner("Finding your perfect binge... 🍿"):
            time.sleep(0.6)
            recs, detected_mood = recommender.recommend_movies(
                user_text=user_mood_text,
                max_duration=max_duration,
                target_energy=target_energy
            )
            if len(recs) == 0:
                recs, detected_mood = recommender.recommend_movies(top_n=5)

        # track which ids have been shown
        st.session_state.seen_movie_ids = set(recs['movie_id'].tolist())
        st.session_state.last_recs      = recs
        st.session_state.last_mood      = detected_mood
        st.session_state.show_results   = True

    # ── Results ──────────────────────────────────────────────────────────────
    if st.session_state.show_results and st.session_state.last_recs is not None:
        recs         = st.session_state.last_recs
        detected_mood = st.session_state.last_mood
        visible_recs = recs[~recs['movie_id'].isin(st.session_state.skipped_ids)]

        if st.session_state.mood_text:
            st.markdown(
                f"<div class='mood-pill'>🎭 Detected Mood: <b>{detected_mood}</b></div>",
                unsafe_allow_html=True
            )

        st.markdown("<div class='section-header'>✨ Your Top Picks</div>", unsafe_allow_html=True)

        if len(visible_recs) == 0:
            st.info("You've skipped everything! Click **Show Me Different Movies** below.")
        else:
            for idx, (_, row) in enumerate(visible_recs.iterrows()):
                explanation = recommender.explain_recommendation(
                    row, detected_mood,
                    st.session_state.max_duration,
                    st.session_state.target_energy
                )
                render_movie_card(
                    row, explanation,
                    key_suffix=f"t1_r{st.session_state.refresh_count}_{idx}"
                )

        # ── Refresh button — key includes refresh_count so it's always fresh ─
        st.markdown(" ")
        st.caption("Not feeling any of these?")
        # Dynamic key = button is re-registered on every refresh so it keeps working
        if st.button(
            "🔄 Show Me Different Movies",
            key=f"refresh_btn_{st.session_state.refresh_count}",
            type="primary"
        ):
            with st.spinner("Fetching a fresh batch..."):
                new_recs, new_mood = recommender.recommend_movies(
                    user_text=st.session_state.mood_text,
                    max_duration=st.session_state.max_duration,
                    target_energy=st.session_state.target_energy,
                    top_n=5
                )
                # If recommender keeps returning same movies, fall back to top_n without filters
                if (new_recs is not None and len(new_recs) > 0 and
                        set(new_recs['movie_id'].tolist()).issubset(st.session_state.seen_movie_ids)):
                    new_recs, new_mood = recommender.recommend_movies(top_n=5)

            if new_recs is not None and len(new_recs) > 0:
                st.session_state.seen_movie_ids.update(new_recs['movie_id'].tolist())

            st.session_state.last_recs    = new_recs
            st.session_state.last_mood    = new_mood
            st.session_state.skipped_ids  = set()
            st.session_state.feedback_map = {}
            st.session_state.refresh_count += 1   # changes key → button always clickable
            st.rerun()

    elif not st.session_state.show_results:
        st.markdown("""
        <div class='empty-state'>
            <div class='empty-state-icon'>🎬</div>
            <div class='empty-state-text'>Describe your mood above and hit <b>Find</b> to get personalized picks.</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CHAT & DISCOVER  (100% independent of tab1)
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("<div class='section-header'>💬 Chat with YourNextBinge</div>", unsafe_allow_html=True)
    st.caption("Try: *'I want something exciting and high energy under 2 hours, feeling great!'*")

    _, col_clearchat = st.columns([5, 1])
    with col_clearchat:
        if st.button("🗑 Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.rerun()

    # ── Chat history ─────────────────────────────────────────────────────────
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
                <div class='chat-label'>🤖 YourNextBinge</div>
                <div class='chat-bubble-bot'>{chat['text']}</div>
                """, unsafe_allow_html=True)
                if 'df' in chat and chat['df'] is not None:
                    for idx, (_, row) in enumerate(chat['df'].iterrows()):
                        explanation = recommender.explain_recommendation(
                            row,
                            chat.get('mood', 'Neutral'),
                            chat.get('duration', 120),
                            chat.get('energy', 'Any')
                        )
                        render_movie_card(
                            row, explanation,
                            key_suffix=f"chat_{i}_{idx}",
                            include_feedback=True
                        )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ── Input — isolated from tab1 entirely ──────────────────────────────────
    col_input, col_send = st.columns([5, 1])
    with col_input:
        chat_query = st.text_input(
            "Type your message",
            placeholder="What kind of movie are you looking for?",
            label_visibility="collapsed",
            key="chat_text_input"
        )
    with col_send:
        send_btn = st.button("Send ✉️", use_container_width=True, type="primary", key="send_btn")

    if send_btn and chat_query:
        # Save what the user typed right now
        current_query = chat_query
        st.session_state.chat_history.append({"role": "user", "text": current_query})

        with st.spinner("Thinking..."):
            # Pass current_query directly — no session state from tab1 involved
            response_text, recommendations, mood, detected_duration, detected_energy = \
                chatbot.get_response(recommender, current_query)

        st.session_state.chat_history.append({
            "role": "bot",
            "text": response_text,
            "df": recommendations,
            "mood": mood,
            "duration": detected_duration,
            "energy": detected_energy
        })

        st.rerun()
