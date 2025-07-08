import streamlit as st
import fitz  # PyMuPDF
import requests
import hashlib
from db import init_db, register_user, login_user, save_upload, get_user_history

# Load Hugging Face token
try:
    hf_token = st.secrets["HF_TOKEN"]
except Exception:
    hf_token = ""

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalEase 2.0", layout="wide", page_icon="📜")

# --- SESSION STATE ---
for key in ["logged_in", "user_email", "mode", "api_key", "mode_chosen"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else ""

# --- UTILITY ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- STYLED HEADER ---
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        font-size: 2.8em;
        font-weight: 700;
        margin-bottom: 0.2em;
    }
    .tagline {
        text-align: center;
        color: #6c757d;
        margin-bottom: 2em;
    }
    .section {
        background-color: #f8f9fa;
        padding: 2em;
        border-radius: 10px;
        margin-bottom: 2em;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .sidebar-title {
        font-weight: bold;
        font-size: 1.1em;
        margin-top: 2em;
        margin-bottom: 0.5em;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>📜 LegalEase 2.0</div>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>AI-Powered Legal Assistant, Simplified for You</div>", unsafe_allow_html=True)

# --- AUTH ---
def login_section():
    with st.container():
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("🔐 Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(email, hash_password(password))
            if user:
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.success(f"Welcome back, {email}!")
            else:
                st.error("Invalid email or password.")
        st.markdown("</div>", unsafe_allow_html=True)

def signup_section():
    with st.container():
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("📝 Create an Account")
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if register_user(email, hash_password(password)):
                st.success("Account created! You can now login.")
            else:
                st.error("User already exists.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- MODE SELECTOR ---
def choose_mode():
    with st.container():
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.subheader("Choose how you'd like to use LegalEase:")
        mode = st.radio("Select Mode", ["Demo Mode (no real AI)", "Use Your Own OpenAI API Key", "Use Open-Source AI via Hugging Face"])

        api_key = ""
        if mode == "Use Your Own OpenAI API Key":
            api_key = st.text_input("Paste your OpenAI API Key", type="password")

        if st.button("Continue"):
            if mode == "Use Your Own OpenAI API Key" and not api_key:
                st.warning("Please enter your API key to continue.")
            else:
                st.session_state.mode = mode
                st.session_state.api_key = api_key
                st.session_state.mode_chosen = True
        st.markdown("</div>", unsafe_allow_html=True)

# --- HUGGING FACE API WRAPPER ---
@st.cache_data
def query_huggingface_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {hf_token}"}

    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": prompt,
            "parameters": {"max_length": 200, "do_sample": False},
            "options": {"wait_for_model": True}
        })
        if response.status_code != 200:
            return f"❌ API Error {response.status_code}: {response.text}"

        output = response.json()
        if isinstance(output, list) and len(output) > 0:
            return output[0].get("summary_text", str(output[0]))
        elif isinstance(output, dict) and "summary_text" in output:
            return output["summary_text"]
        else:
            return f"⚠️ Unexpected output: {output}"

    except Exception as e:
        return f"❌ Exception: {str(e)}"

# --- MAIN APP ---
def app_main():
    st.sidebar.markdown("<div class='sidebar-title'>🔧 Account</div>", unsafe_allow_html=True)
    nav_choices = ["📇 My Profile", "📤 Upload & Simplify", "📂 My History"]
    st.sidebar.markdown("<div class='sidebar-title'>🛠 Features</div>", unsafe_allow_html=True)
    nav_choices.append("❓ Help & Feedback")

    choice = st.sidebar.radio("", nav_choices)

    if choice == "📇 My Profile":
        with st.container():
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("👤 My Profile")
            st.write(f"**Logged in as:** {st.session_state.user_email}")
            if st.button("🚪 Log Out"):
                for key in ["logged_in", "user_email", "mode", "api_key", "mode_chosen"]:
                    st.session_state[key] = False if key == "logged_in" else ""
                st.success("✅ Logged out. Refresh the page to log in again.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📤 Upload & Simplify":
        with st.container():
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("📄 Upload Your Legal Document (PDF)")
            uploaded_file = st.file_uploader("Select a legal PDF", type=["pdf"])

            if uploaded_file:
                if uploaded_file.size > 3 * 1024 * 1024:
                    st.error("⚠️ File too large. Please upload PDFs under 3MB.")
                    return
                try:
                    with st.spinner("Reading and extracting text..."):
                        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                        full_text = "".join([page.get_text() for page in doc])
                    st.success("✅ Text extracted from PDF.")
                    with st.expander("📄 View Extracted Text"):
                        st.text_area("", full_text, height=300)
                except Exception as e:
                    st.error(f"❌ Error reading PDF: {str(e)}")
                    return

                if st.button("🧐 Simplify Document"):
                    doc_name = uploaded_file.name.lower()
                    if st.session_state.mode == "Use Your Own OpenAI API Key":
                        try:
                            from openai import OpenAI
                            client = OpenAI(api_key=st.session_state.api_key)
                            with st.spinner("Simplifying with OpenAI..."):
                                response = client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "You are a legal assistant. Simplify legal documents in plain English."},
                                        {"role": "user", "content": full_text}
                                    ]
                                )
                                simplified = response.choices[0].message.content
                        except Exception as e:
                            st.error(f"❌ OpenAI error: {str(e)}")
                            return
                    elif st.session_state.mode == "Use Open-Source AI via Hugging Face":
                        prompt = f"""Simplify the following legal document in plain English, avoiding legal jargon:\n\n{full_text}"""
                        with st.spinner("Simplifying using Hugging Face..."):
                            simplified = query_huggingface_api(prompt)
                    else:
                        if "rental" in doc_name:
                            simplified = "📜 Demo Summary: This is a rental agreement between a landlord and tenant."
                        elif "nda" in doc_name:
                            simplified = "📜 Demo Summary: This is a non-disclosure agreement that protects shared confidential information."
                        elif "employment" in doc_name:
                            simplified = "📜 Demo Summary: This outlines terms of employment between a company and an employee."
                        else:
                            simplified = "📜 Demo Summary: Unable to identify document type. This is a general contract."

                    st.subheader("✅ Simplified Summary")
                    st.success(simplified)
                    save_upload(st.session_state.user_email, uploaded_file.name, simplified)
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📂 My History":
        with st.container():
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("📂 Your Uploaded History")
            history = get_user_history(st.session_state.user_email)
            if not history:
                st.info("No uploads yet.")
            else:
                for file_name, summary, timestamp in history:
                    with st.expander(f"📄 {file_name} | 🕒 {timestamp}"):
                        st.text(summary)
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "❓ Help & Feedback":
        with st.container():
            st.markdown("<div class='section'>", unsafe_allow_html=True)
            st.subheader("❓ Help & Feedback")
            st.markdown("""
                - **How to Use**: Upload a legal PDF and click 'Simplify Document'.
                - **Privacy**: Your uploads are stored securely under your account.
                - **Feedback**: Email us at support@legalease.app or use the contact form.
            """)
            st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTING ---
if not st.session_state.logged_in:
    tab = st.tabs(["Login", "Sign Up"])
    with tab[0]:
        login_section()
    with tab[1]:
        signup_section()
else:
    if not st.session_state.mode_chosen:
        choose_mode()
    else:
        app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalEase. Built with ❤️ in Streamlit.</p>", unsafe_allow_html=True)
