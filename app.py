import streamlit as st
import fitz  # PyMuPDF
import requests
import hashlib
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from db import init_db, register_user, login_user, save_upload, get_user_history

# Load Hugging Face token
try:
    hf_token = st.secrets["HF_TOKEN"]
except Exception:
    hf_token = ""

# --- INIT DB ---
init_db()

# --- CONFIG ---
st.set_page_config(page_title="LegalLite", layout="wide", page_icon="⚖️")

# --- HEADER BRANDING ---
st.markdown("<h1 style='text-align: center; color: #3A6EA5;'>LegalLite ⚖️</h1>", unsafe_allow_html=True)


# --- SESSION STATE ---
for key in ["logged_in", "user_email", "mode", "api_key", "mode_chosen"]:
    if key not in st.session_state:
        st.session_state[key] = False if key == "logged_in" else ""

# --- UTILITY ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_pdf(summary_text, filename):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    margin = 40
    y = height - margin

    c.drawString(margin, y, f"LegalLite Summary - {filename}")
    y -= 20
    c.drawString(margin, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    lines = summary_text.split('\n')
    for line in lines:
        for subline in [line[i:i+90] for i in range(0, len(line), 90)]:
            if y < margin:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - margin
            c.drawString(margin, y, subline)
            y -= 20

    c.save()
    buffer.seek(0)
    return buffer

# --- HUGGING FACE API WRAPPER ---
@st.cache_data
def query_huggingface_api(prompt):
    API_URL = "https://api-inference.huggingface.co/models/csebuetnlp/mT5_multilingual_XLSum"
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
        if isinstance(output, dict) and "summary_text" in output:
            return output["summary_text"]
        else:
            return f"⚠️ Unexpected output: {output}"

    except Exception as e:
        return f"❌ Exception: {str(e)}"

# --- MAIN APP ---
def login_section():
    with st.container():
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

def choose_mode():
    st.markdown("### 🎛️ Choose how you'd like to use LegalLite:")
    st.markdown("Pick a mode based on your preference:")

    col1, col2, col3 = st.columns(3)

    # initialize a session variable to hold temporary API input
    if "api_input" not in st.session_state:
        st.session_state.api_input = ""

    with col1:
        if st.button("🧪 Demo Mode"):
            st.session_state.mode = "Demo Mode"
            st.session_state.mode_chosen = True

    with col2:
        if st.button("🔐 Use Your API Key"):
            st.session_state.mode = "Use Your Own OpenAI API Key"
            st.session_state.mode_chosen = False  # wait for key entry

    with col3:
        if st.button("🌐 Hugging Face"):
            st.session_state.mode = "Use Open-Source AI via Hugging Face"
            st.session_state.mode_chosen = True

    if st.session_state.mode == "Use Your Own OpenAI API Key" and not st.session_state.mode_chosen:
        st.session_state.api_input = st.text_input("Paste your OpenAI API Key", type="password")
        if st.button("➡️ Continue"):
            if st.session_state.api_input.strip() == "":
                st.warning("Please enter your API key.")
            else:
                st.session_state.api_key = st.session_state.api_input
                st.session_state.mode_chosen = True

def signup_section():
    with st.container():
        st.subheader("📝 Create an Account")
        email = st.text_input("New Email")
        password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if register_user(email, hash_password(password)):
                st.success("Account created! You can now login.")
            else:
                st.error("User already exists.")  
  
        if st.button("Continue"):
           if mode == "Use Your Own OpenAI API Key" and not api_key:
               st.warning("Please enter your API key to continue.")
           else:
                 st.session_state.mode = mode
                 st.session_state.api_key = api_key
                 st.session_state.mode_chosen = True

def app_main():
    if st.button("🔙 Back to Mode Selection"):
        st.session_state.mode_chosen = False
        st.session_state.mode = ""
        st.session_state.api_key = ""
        return

    st.sidebar.title("📓 Navigation")
    choice = st.sidebar.radio("Go to", ["👤 Profile", "📄 Upload & Simplify", "📂 My History", "❓ Help & Feedback"])

    if choice == "👤 Profile":
        st.subheader("👤 Your Profile")
        st.write(f"**Logged in as:** `{st.session_state.user_email}`")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.success("Logged out. Refresh to login again.")

    if choice == "📄 Upload & Simplify":
        st.subheader("📄 Upload Your Legal Document (PDF)")
        uploaded_file = st.file_uploader("Select a legal PDF", type=["pdf"])

        if uploaded_file:
            doc_name = uploaded_file.name.lower()
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
                simplified = None
                if st.session_state.mode == "Use Your Own OpenAI API Key":
                     if not st.session_state.api_key:
                         st.error("❌ API key not found. Please go back and enter your key.")
                         return
                         
                     try:
                         st.warning("✅ Entered OpenAI summarization block")
                         from openai import OpenAI
                         client=OpenAI(api_key = st.session_state.api_key)
                         response = client.chat.completions.create(
                             model = "gpt-3.5-turbo",
                             messages=[
                                 {"role":"system","content": "You are a legal assistant. Simplify legal documents in plain English."},
                                 {"role": "user", "content": full_text}
                             ]
                         )
                         simplified = response.choices[0].message.content
                         
                     except Exception as e:
                         st.error(f"❌ OpenAI Error: {str(e)}")
                         return
                        
                elif st.session_state.mode == "Use Open-Source AI via Hugging Face":
                    prompt = f"""Summarize the following document in bullet points:\n\n{full_text}"""
                    with st.spinner("Simplifying using Hugging Face..."):
                        simplified = query_huggingface_api(prompt)

                else:
                    doc_name = uploaded_file.name.lower()
                    if "rental" in doc_name:
                        simplified = """
This is a rental agreement made between Mr. Rakesh Kumar (the property owner) and Mr. Anil Reddy (the person renting).

- The house is in Jubilee Hills, Hyderabad.
- Rent is ₹18,000/month, paid by the 5th.
- Anil pays a ₹36,000 security deposit.
- The rental period is 11 months: from August 1, 2025, to June 30, 2026.
- Either side can cancel the agreement with 1 month’s written notice.
- Anil can't sub-rent the house to anyone else unless Rakesh agrees.

In short: this document explains the rules of staying in the rented house, money terms, and how both sides can exit the deal.
                    """
                    if "nda" in doc_name:
                        simplified =  """
This Non-Disclosure Agreement (NDA) is between TechNova Pvt. Ltd. and Mr. Kiran Rao.

- Kiran will receive sensitive business information from TechNova.
- He agrees to keep this confidential and not use it for anything other than their business discussions.
- This includes technical data, strategies, client info, designs, etc.
- He cannot share it, even after the project ends, for 3 years.
- Exceptions: if info is public, received legally from others, or required by law.
- If he breaks the agreement, TechNova can take legal action, including asking the court to stop him immediately.

In short: Kiran must not reveal or misuse any business secrets he gets from TechNova during their potential partnership.
                    """
                    if "employment" in doc_name:
                        simplified =  """
This is an official job contract between GlobalTech Ltd. and Ms. Priya Sharma.

- Priya will join as a Senior Software Engineer from August 1, 2025.
- She will earn Rs. 12,00,000/year, including bonuses and allowances.
- She must work 40+ hours/week, either from office or remotely.
- First 6 months = probation, 15-day notice for quitting or firing.
- After that, it becomes 60-day notice.
- She must not share company secrets or join rival companies for 1 year after leaving.
- Any inventions or code she builds belong to the company.
- She gets 20 paid leaves + public holidays.

In short: This contract outlines Priya’s job, salary, rules during and after employment, and what happens if she quits or is fired.
                    """
                    else:
                        simplified = "📜 Demo Summary: Unable to identify document type. This is a general contract."

                if simplified:
                        st.subheader("✅ Simplified Summary")
                        st.success(simplified)
                        save_upload(st.session_state.user_email, uploaded_file.name, simplified)
                        # PDF download
                        pdf_file = generate_pdf(simplified, uploaded_file.name)
                        st.download_button(
                            label="📅 Download Summary as PDF",
                            data=pdf_file,
                            file_name=f"simplified_{uploaded_file.name.replace('.pdf','')}.pdf",
                            mime="application/pdf"
                        )

    if choice == "📂 My History":
        st.subheader("📂 Your Uploaded History")
        history = get_user_history(st.session_state.user_email)
        if not history:
            st.info("No uploads yet.")
        else:
            for file_name, summary, timestamp in history:
                with st.expander(f"📄 {file_name} | 🕒 {timestamp}"):
                    st.text(summary)
    if choice == "❓ Help & Feedback":
      st.subheader("❓ Help & Feedback")
      st.markdown("""
      - **About LegalEase**: This tool simplifies legal documents in plain English using AI.
      - **Modes**:
          - *Demo Mode*: Uses sample summaries.
          - *OpenAI API*: Your key, high-quality output.
          - *Hugging Face*: Free, open-source summarization.
      - **Suggestions or bugs?** Drop a message at `support@legalease.com`.

      ### 🖼️ How It Works
      Below is a visual guide to how LegalLite works:
      """)

      st.image("flowchart.png.png", caption="LegalLite App Flow", width=500)
  
      st.markdown("### 📂 Download Predefined Demo Files")

      col1, col2, col3 = st.columns(3)

      with col1:
          with open("Sample_Rental_Agreement.pdf", "rb") as file:
              st.download_button(
                  label="🏠 Rental", 
                  data=file, 
                  file_name="Sample_Rental_Agreement.pdf", 
                  mime="application/pdf"
              )

      with col2:
          with open("Sample_NDA_Agreement.pdf", "rb") as file:
              st.download_button(
                  label="🔒 NDA", 
                  data=file, 
                  file_name="Sample_NDA_Agreement.pdf", 
                  mime="application/pdf"
              )

      with col3:
          with open("Sample_Employment_Contract.pdf", "rb") as file:
              st.download_button(
                  label="🧑‍💼 Employment", 
                  data=file, 
                  file_name="Sample_Employment_Contract.pdf", 
                  mime="application/pdf"
              )

  
# --- ROUTING ---
if not st.session_state.logged_in:
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        login_section()
    with signup_tab:
        signup_section()

else:
    if not st.session_state.mode_chosen:
        choose_mode()
    else:
        app_main()

# --- FOOTER ---
st.markdown("<hr><p style='text-align: center; color: gray;'>© 2025 LegalLite. Built with ❤️ in Streamlit.</p>", unsafe_allow_html=True)
