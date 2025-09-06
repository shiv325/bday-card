import streamlit as st
import sqlite3
import os
import base64
import streamlit.components.v1 as components
from contextlib import closing

# --- Database Functions ---
@st.cache_resource
# --- Wishes DB Init ---
def init_db():
    with sqlite3.connect("wishes.db", check_same_thread=False) as conn:
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

# --- Wishes Operations ---
def add_wish(name, message):
    with sqlite3.connect("wishes.db", check_same_thread=False) as conn:
        conn.execute("INSERT INTO wishes (name, message) VALUES (?, ?)", (name, message))
        conn.commit()

def get_wishes():
    with sqlite3.connect("wishes.db", check_same_thread=False) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute("SELECT id, name, message FROM wishes ORDER BY created_at DESC").fetchall()

def delete_wish(wish_id):
    with sqlite3.connect("wishes.db", check_same_thread=False) as conn:
        conn.execute("DELETE FROM wishes WHERE id = ?", (wish_id,))
        conn.commit()

# --- Memories Notes Database ---
def init_memories_db():
    conn = sqlite3.connect("memories.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    with closing(conn.cursor()) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL UNIQUE,
                note TEXT
            )
        """)
        conn.commit()
    return conn

mem_conn = init_memories_db()

def get_note_for_image(conn, filename):
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT note FROM memory_notes WHERE filename=?", (filename,))
        row = cursor.fetchone()
        return row["note"] if row else ""

def save_note_for_image(conn, filename, note):
    with closing(conn.cursor()) as cursor:
        cursor.execute("""
            INSERT INTO memory_notes (filename, note)
            VALUES (?, ?)
            ON CONFLICT(filename) DO UPDATE SET note=excluded.note
        """, (filename, note))
        conn.commit()

st.set_page_config(layout="wide")

# --- Background Music with Play/Pause ---
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

cake_html = """
<div style="display: flex; flex-direction: column; align-items: center; margin-top: 80px; margin-bottom: -40px;">
  <div id="cake" style="margin-top: 40px; margin-bottom: 20px; position: relative;">
    <!-- Cake body -->
    <div style="width:200px;height:100px;background:#8B4513;border-radius:10px;position:relative;z-index:2;">
      
      <!-- Middle Cream Layer -->
      <div style="position:absolute;top:35px;left:0;width:200px;height:10px;background:#fff;border-radius:5px;"></div>
      
      <!-- Top Cream Layer -->
      <div style="position:absolute;top:-10px;left:0;width:200px;height:15px;background:#ff69b4;border-radius:10px 10px 0 0;"></div>
      
      <!-- Candles -->
      <div class="candle" style="position:absolute;top:-40px;left:31px;width:10px;height:40px;background:#fff;">
        <div class="flame"></div>
      </div>
      <div class="candle" style="position:absolute;top:-40px;left:91px;width:10px;height:40px;background:#fff;">
        <div class="flame"></div>
      </div>
      <div class="candle" style="position:absolute;top:-40px;left:151px;width:10px;height:40px;background:#fff;">
        <div class="flame"></div>
      </div>
    </div>

    <!-- Plate -->
    <div style="width:240px;height:30px;background:#fff;border-radius:50%;position:absolute;bottom:-15px;left:-20px;z-index:1;box-shadow:0 4px 8px rgba(0,0,0,0.2);"></div>
  </div>

  <div style="margin-top:15px;">
    <button onclick="blowCandles()" style="padding:10px 20px;font-size:18px;cursor:pointer;">
      💨 Blow Candles
    </button>
    <button onclick="lightCandles()" style="padding:10px 20px;font-size:18px;cursor:pointer;margin-left:10px;">
      🕯️ Light Candles
    </button>
  </div>

  <!-- Hidden birthday text -->
  <h1 id="birthdayText" style="display:none; font-size:48px; color:#d63384; margin-top:20px; text-align:center; animation: pop 1s ease;">
    🎉 Happy Birthday 🎂
  </h1>
</div>

<canvas id="confettiCanvas" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; display:none;"></canvas>

<style>
  .flame {
    width: 12px;
    height: 20px;
    background: radial-gradient(circle, yellow 40%, orange 70%, transparent 100%);
    border-radius: 50%;
    margin: -20px auto 0 auto;
    animation: flicker 0.3s infinite alternate;
  }
  @keyframes flicker {
    from { transform: scale(1); opacity: 1; }
    to { transform: scale(1.2); opacity: 0.8; }
  }
  @keyframes blowOut {
    0%   { transform: scale(1) rotate(0deg); opacity: 1; }
    50%  { transform: scale(1.3,0.7) translateX(10px); opacity: 0.7; }
    100% { transform: scale(0) translateY(-20px); opacity: 0; }
  }
  @keyframes pop {
    0% { transform: scale(0.5); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
  }
</style>

<script>
let confettiRunning = false;
let confettiAnimation;

function blowCandles() {
  const flames = document.querySelectorAll('.flame');
  flames.forEach((flame, index) => {
    setTimeout(() => {
      flame.style.animation = "blowOut 1s forwards";
    }, index * 400);
  });

  setTimeout(() => {
    document.getElementById("birthdayText").style.display = "block";
    startConfetti();
  }, flames.length * 400 + 1000);
}

function lightCandles() {
  // Reset flames
  const candles = document.querySelectorAll('.candle');
  candles.forEach(candle => {
    let flame = candle.querySelector('.flame');
    if (!flame) {
      flame = document.createElement('div');
      flame.className = 'flame';
      candle.appendChild(flame);
    }
    flame.style.animation = "flicker 0.3s infinite alternate";
    flame.style.opacity = "1";
  });

  // Hide birthday text
  document.getElementById("birthdayText").style.display = "none";

  // Stop confetti
  stopConfetti();
}

function startConfetti() {
  if (confettiRunning) return;
  confettiRunning = true;

  const canvas = document.getElementById("confettiCanvas");
  const ctx = canvas.getContext("2d");
  canvas.style.display = "block";
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const confetti = Array.from({length: 150}).map(() => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height - canvas.height,
    r: Math.random() * 6 + 4,
    d: Math.random() * 10 + 5,
    color: `hsl(${Math.random() * 360},100%,50%)`,
    tilt: Math.random() * 10 - 10
  }));

  function drawConfetti() {
    ctx.clearRect(0,0,canvas.width,canvas.height);
    confetti.forEach(p => {
      ctx.beginPath();
      ctx.lineWidth = p.r;
      ctx.strokeStyle = p.color;
      ctx.moveTo(p.x + p.tilt + p.r/2, p.y);
      ctx.lineTo(p.x + p.tilt, p.y + p.r);
      ctx.stroke();
    });
    updateConfetti();
    confettiAnimation = requestAnimationFrame(drawConfetti);
  }

  function updateConfetti() {
    confetti.forEach(p => {
      p.y += (Math.cos(p.d) + 3 + p.r/2)/2;
      p.x += Math.sin(0.01 * p.d);
      if(p.y > canvas.height) {
        p.y = -10;
        p.x = Math.random() * canvas.width;
      }
    });
  }

  drawConfetti();
}

function stopConfetti() {
  confettiRunning = false;
  cancelAnimationFrame(confettiAnimation);
  document.getElementById("confettiCanvas").style.display = "none";
}
</script>
"""

components.html(cake_html, height=550, scrolling=False)

st.markdown("### Hope you have a wonderful day filled with joy and laughter! 🎈")

# Wish form
with st.expander("💌 Send a Birthday Wish!"):
    with st.form("wish_form", clear_on_submit=True):
        sender_name = st.text_input("Your Name")
        wish_message = st.text_area("Your Wish")
        submitted = st.form_submit_button("Send Wish")
        if submitted:
            if sender_name and wish_message:
                add_wish(sender_name, wish_message)
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
    wishes = get_wishes()
    if wishes:
        st.subheader("All the lovely wishes just for you!")
        for wish in wishes:
            wish_col, delete_col = st.columns([10, 1])
            with wish_col:
                st.markdown(f"**From:** {wish['name']}")
                st.info(f"**Message:** {wish['message']}")
            with delete_col:
                if st.button("🗑️", key=f"delete_{wish['id']}"):
                    delete_wish(wish['id'])
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

    # Display memories in grid with delete + notes
    images = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if images:
        cols = st.columns(3)  # 3 images per row
        for i, img in enumerate(images):
            with cols[i % 3]:
                img_path = os.path.join(folder, img)
                st.image(img_path, use_container_width=True)

                # Load any saved note
                current_note = get_note_for_image(mem_conn, img)

                # Show note box
                new_note = st.text_area("", value=current_note, key=f"note_{img}")

                if st.button("💾 Save Note", key=f"save_{img}"):
                    save_note_for_image(mem_conn, img, new_note)
                    st.success("Note saved!")
                    st.rerun()

                if st.button(f"🗑️ Delete", key=f"delete_{img}"):
                    os.remove(img_path)
                    save_note_for_image(mem_conn, img, "")  # clear note when deleting
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

st.header("🎶 Songs Dedicated for You")

# --- Songs folder ---
folder = "assets/songs"
os.makedirs(folder, exist_ok=True)

# --- Upload Songs ---
uploaded_songs = st.file_uploader(
    "Upload songs (mp3 only)", 
    type=["mp3"], 
    accept_multiple_files=True
)

if uploaded_songs:
    for song in uploaded_songs:
        song_path = os.path.join(folder, song.name)
        with open(song_path, "wb") as f:
            f.write(song.getbuffer())
    st.success("✅ Songs uploaded successfully!")

# --- Display and Play Songs ---
songs = [f for f in os.listdir(folder) if f.lower().endswith(".mp3")]
if songs:
    st.subheader("📀 Your Dedicated Songs")
    for song in songs:
        st.write(f"▶️ {song}")
        st.audio(os.path.join(folder, song), format="audio/mp3")
else:
    st.info("No songs uploaded yet. Use the uploader above to add songs 🎶")
