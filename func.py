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
    
# 🎤 --- VOICE SUMMARY ---
def generate_voice(summary_text):
    try:
        tts = gTTS(summary_text, lang='en')
        audio_path = "summary_audio.mp3"
        tts.save(audio_path)
        return audio_path
    except Exception as e:
        st.error(f"❌ Voice generation failed: {e}")
        return None
        
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

# --- LOGIN SECTION ---
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
                
# --- MODE SELECTION ---
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

# ---SIGNUP SECTION ---

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

# --- RISKY TERMS FINDER ---
def find_risky_terms(text):
    risky_keywords = [
        "penalty", "termination", "breach", "fine",
        "automatic renewal", "binding arbitration",
        "liquidated damages", "non-compete", "non-disclosure",
        "late fee", "without notice", "waiver of rights",
        "exclusive jurisdiction", "governing law", "intellectual property"
    ]
    found_terms = []
    for keyword in risky_keywords:
        if keyword.lower() in text.lower():
            found_terms.append(keyword)
    return list(set(found_terms))

# --- AI RISK TERMS ---
def ai_risk_analysis(text, api_key):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a legal risk analysis assistant. Identify clauses in contracts that could pose legal or financial risks to the signer, explain why, and suggest ways to mitigate them."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Analysis failed: {e}"

