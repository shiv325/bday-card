import streamlit as st

st.set_page_config(page_title="📸 Photo Memories", layout="wide")

st.title("📸 Beautiful Photo Memories")

st.write("Here are some wonderful moments to cherish:")

# Example photo gallery
col1, col2, col3 = st.columns(3)

with col1:
    st.image("assets/memory1.jpg", caption="Special Moment 1", use_container_width=True)

with col2:
    st.image("assets/memory2.jpg", caption="Special Moment 2", use_container_width=True)

with col3:
    st.image("assets/memory3.jpg", caption="Special Moment 3", use_container_width=True)

st.markdown("---")
st.info("Use the sidebar to go back to the Birthday Wishes page 🎂")
