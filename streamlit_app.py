import streamlit as st
import sqlite3
import os
import base64
import streamlit.components.v1 as components
from contextlib import closing

# --- Database Functions ---
@st.cache_resource
def init_db():
    conn = sqlite3.connect("wishes.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    with closing(conn.cursor()) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wishes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    return conn

def add_wish(conn, name, message):
    with closing(conn.cursor()) as cursor:
        cursor.execute("INSERT INTO wishes (name, message) VALUES (?, ?)", (name, message))
        conn.commit()

def get_wishes(conn):
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT id, name, message FROM wishes ORDER BY created_at DESC")
        return cursor.fetchall()

def delete_wish(conn, wish_id):
    with closing(conn.cursor()) as cursor:
        cursor.execute("DELETE FROM wishes WHERE id = ?", (wish_id,))
        conn.commit()

# --- Init ---
db_conn = init_db()
st.set_page_config(layout="wide")

# --- Background Music with Play/Pause ---
audio_file = "assets/birthday_song.mp3"

audio_file = "assets/birthday_song.mp3"

if not os.path.exists(audio_file):
    st.warning("Background audio not found at: " + audio_file)
else:
    # Convert to base64
    audio_bytes = open(audio_file, "rb").read()
    b64 = base64.b64encode(audio_bytes).decode()

    # Full HTML wrapper
    player_html = f"""
    <div style="
        background: linear-gradient(135deg, #fff0f5, #ffe4e1);
        border: 2px solid #ed82d6;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        max-width: 400px;
        margin: 20px auto;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    ">
      <p style="font-size:16px; font-weight:bold; color:#654321; margin-bottom:10px;">
        🎶 Birthday Song Player 🎶
      </p>
      <audio id="bg-music" src="data:audio/mp3;base64,{b64}" loop></audio>
      <button onclick="document.getElementById('bg-music').play()" 
              style="background:#ed82d6; color:white; border:none; padding:10px 18px; 
                     border-radius:8px; cursor:pointer; font-size:14px; margin-right:8px;">
          ▶️ Play
      </button>
      <button onclick="document.getElementById('bg-music').pause()" 
              style="background:#654321; color:white; border:none; padding:10px 18px; 
                     border-radius:8px; cursor:pointer; font-size:14px;">
          ⏸️ Pause
      </button>
      <br><br>
      <label for="vol" style="color:#333; font-size:13px; font-weight:bold;">Volume: </label>
      <input id="vol" type="range" min="0" max="1" step="0.01" value="1"
             style="width:60%; vertical-align: middle;"
             onchange="document.getElementById('bg-music').volume = this.value;">
    </div>
    """

    components.html(player_html, height=180)

# --- Styles ---
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(to right top, #fbc2eb, #f8b2e5, #f5a2e0, #f192db, #ed82d6);
        background-size: cover;
    }
    h1, h3, p, label, [data-testid="stMarkdownContainer"] {
        color: #654321 !important;
    }
    [data-testid="stImage"] img {
        border: 10px solid #fff;
        border-radius: 10px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
        max-height: 75vh;
        width: auto;
        object-fit: contain;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Persist state ---
if "show_memories" not in st.session_state:
    st.session_state.show_memories = False

# --- Styles for popup ---
st.markdown("""
<style>
.memories-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    padding: 10px;
}
.memories-grid img {
    width: 100%;
    border-radius: 12px;
    border: 4px solid #fbc2eb;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.15);
    object-fit: cover;
    background-color: #fff;
}
</style>
""", unsafe_allow_html=True)


# Persist show/hide state for wishes
if "show_wishes" not in st.session_state:
    st.session_state["show_wishes"] = False

# Title & image
st.title("🎉 Happy Birthday! 🎉")
st.balloons()

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image("assets/birthday_person.jpg", use_container_width=True)
    st.markdown(
        """
        <p style="text-align: center; color: #654321; margin-top: 10px;">
            Wishing you the best day!
        </p>
        """,
        unsafe_allow_html=True
    )

st.markdown("### Hope you have a wonderful day filled with joy and laughter! 🎈")

# Wish form
with st.expander("💌 Send a Birthday Wish!"):
    with st.form("wish_form", clear_on_submit=True):
        sender_name = st.text_input("Your Name")
        wish_message = st.text_area("Your Wish")
        submitted = st.form_submit_button("Send Wish")
        if submitted:
            if sender_name and wish_message:
                add_wish(db_conn, sender_name, wish_message)
                st.success("Your wish has been sent!")
                st.session_state["show_wishes"] = True
                st.rerun()
            else:
                st.warning("Please fill in both your name and your wish.")

# Toggle visibility
st.session_state.show_wishes = st.checkbox(
    "📜 See All Wishes",
    value=st.session_state.show_wishes,
    key="show_wishes_checkbox"
)

if st.session_state.show_wishes:
    wishes = get_wishes(db_conn)
    if wishes:
        st.subheader("All the lovely wishes just for you!")
        for wish in wishes:
            wish_col, delete_col = st.columns([10, 1])
            with wish_col:
                st.markdown(f"**From:** {wish['name']}")
                st.info(f"**Message:** {wish['message']}")
            with delete_col:
                if st.button("🗑️", key=f"delete_{wish['id']}"):
                    delete_wish(db_conn, wish['id'])
                    st.success("Wish deleted successfully!")
                    st.rerun()
    else:
        st.info("No wishes have been sent yet. Be the first!")

if st.button("📸 Go to Photo Memories"):
    st.session_state.show_memories = True
    st.rerun()

# --- Popup memories sheet ---
if st.session_state.show_memories:
    folder = "assets/memories"
    os.makedirs(folder, exist_ok=True)

    st.markdown('<div class="memories-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="memories-box">', unsafe_allow_html=True)

    st.markdown("### 📸 Photo Memories")

    # Upload Memories button
    if "show_uploader" not in st.session_state:
        st.session_state.show_uploader = False

    if st.button("➕ Upload Memories"):
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()

    if st.session_state.show_uploader:
        uploaded_files = st.file_uploader(
            "Choose photos to upload",
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=True
        )
        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_path = os.path.join(folder, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            st.success("Memories uploaded successfully!")
            st.session_state.show_uploader = False
            st.rerun()

    # Display memories in grid with delete button
    images = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if images:
        cols = st.columns(3)  # 3 images per row
        for i, img in enumerate(images):
            with cols[i % 3]:
                img_path = os.path.join(folder, img)
                st.image(img_path, use_container_width=True)
                if st.button(f"🗑️ Delete", key=f"delete_{img}"):
                    os.remove(img_path)
                    st.success(f"Deleted {img}")
                    st.rerun()
    else:
        st.info("No memories uploaded yet.")

    # Close popup
    if st.button("❌ Close Memories"):
        st.session_state.show_memories = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
