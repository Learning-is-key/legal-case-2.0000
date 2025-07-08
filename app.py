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
st.set_page_config(page_title="LegalEase ", layout="centered", page_icon="📜")

# --- SESSION STATE ---
for key in ["logged_in", "user_email", "mode", "api_key", "mode_chosen"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else ""

# --- UTILITY ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- UI HEADER ---
st.markdown("<h1 style='text-align: center;'>📜 LegalEase 2.0</h1>", unsafe_allow_html=True)
st.caption("Your personal AI legal document explainer — with login, history, and dual modes.")

# --- AUTH ---
def login_section():
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

def signup_section():
    st.subheader("📝 Create an Account")
    email = st.text_input("New Email")
    password = st.text_input("New Password", type="password")
    if st.button("Sign Up"):
        if register_user(email, hash_password(password)):
            st.success("Account created! You can now login.")
        else:
            st.error("User already exists.")

# --- MODE SELECTOR ---
def choose_mode():
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
    st.sidebar.title("📚 Navigation")
    choice = st.sidebar.radio("Go to", ["Upload & Simplify", "My History", "Logout"])

    if choice == "Upload & Simplify":
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
                st.text_area("📄 Extracted Text", full_text, height=300)
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

    elif choice == "My History":
        st.subheader("📂 Your Uploaded History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file_name, summary, timestamp in history:
                with st.expander(f"📄 {file_name} | 🕒 {timestamp}"):
                    st.text(summary)

    elif choice == "Logout":
        for key in ["logged_in", "user_email", "mode", "api_key", "mode_chosen"]:
            st.session_state[key] = False if key == "logged_in" else ""
        st.success("✅ Logged out. Refresh the page to log in again.")

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
