import streamlit as st
import sqlite3
import os
from contextlib import closing

st.set_page_config(page_title="🎂 Birthday Wishes", layout="wide")

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

# --- Styles (NO <script> block) ---
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
    .delete-col {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Persist show/hide state for wishes
if "show_wishes" not in st.session_state:
    st.session_state["show_wishes"] = False

# Title & image
st.title("🎉 Happy Birthday! 🎉")
st.balloons()

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Render image normally with Streamlit
    st.image("assets/birthday_person.jpg", use_container_width=True)

    # Add caption with HTML centered
    st.markdown(
        """
        <p style="text-align: center; color: #654321; margin-top: 10px;">
            Wishing you the best day!
        </p>
        """,
        unsafe_allow_html=True
    )

st.markdown("### Hope you have a wonderful day filled with joy and laughter! 🎈")
st.divider()

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
                # show the list automatically after sending
                st.session_state["show_wishes"] = True
                st.rerun()
            else:
                st.warning("Please fill in both your name and your wish.")

# Toggle visibility (separate widget key)
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
                    st.session_state.show_wishes = True
                    st.rerun()
    else:
        st.info("No wishes have been sent yet. Be the first!")