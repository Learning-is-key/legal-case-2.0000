
---

# ⚖️ LegalLite

**LegalLite** is a user-friendly AI-powered web application that simplifies complex legal documents into plain, understandable English. It supports login, upload history, PDF summaries, and offers multiple AI-powered summarization modes including OpenAI and Hugging Face APIs — along with a Demo Mode.

---
## 🚀 Features

* 📝 **User Registration & Login**
  Secure signup and login with hashed passwords using SQLite.

* 📤 **Upload Legal PDFs**
  Upload documents like rental agreements, NDAs, and employment contracts.

* 🤖 **AI-Based Summarization Modes**

  * 🧪 **Demo Mode**: Uses hardcoded summaries for specific file names.
  * 🔐 **OpenAI API**: Plug your OpenAI key to use GPT-3.5 for summarization.
  * 🌐 **Hugging Face**: Free summarization via open-source transformer model.

* 📄 **History View**
  Track all previously uploaded files and their AI-generated summaries.

* 📥 **Download PDF**
  Download simplified summaries as printable PDF files.

* 🖼️ **Flowchart Display**
  Visual representation of how the app works.

* 🔧 **Help & Feedback Section**
  Basic onboarding, help text, and downloadable demo contracts.

---

## 📂 Project Structure

```bash
.
├── app.py                        # Streamlit main app logic
├── db.py                         # SQLite database utility functions
├── Sample_Rental_Agreement.pdf   # Demo input
├── Sample_NDA_Agreement.pdf      # Demo input
├── Sample_Employment_Contract.pdf# Demo input
├── flowchart.png.png             # How-it-works visual
├── requirements.txt              # Python package requirements
└── users.db                      # Generated after first run
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/legallite.git
cd legallite
```

### 2. Create Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

---

## 🔐 Optional: Add Hugging Face Secret

Create a `.streamlit/secrets.toml` file:

```toml
HF_TOKEN = "your_huggingface_token_here"
```

---

## 📊 Sample Documents

Test with the built-in sample files:

* `Sample_Rental_Agreement.pdf`
* `Sample_NDA_Agreement.pdf`
* `Sample_Employment_Contract.pdf`

---

## 🧠 Tech Stack

| Tech           | Purpose                        |
| -------------- | ------------------------------ |
| Streamlit      | Web App Frontend               |
| SQLite         | User/Auth/History DB           |
| PyMuPDF (fitz) | PDF Text Extraction            |
| HuggingFace    | Free Summarization (mT5 Model) |
| OpenAI API     | GPT-3.5 Summarization          |
| ReportLab      | Generate downloadable PDFs     |

---

## 📎 Known Limitations

* File size limited to **3MB**.
* Demo summaries are only triggered for specific file names.
* Hugging Face output may be brief or generic compared to OpenAI.

---

## 🧪 Demo Mode Support

Demo mode triggers when filenames contain:
`rental`, `nda`, `employment`

For unidentified documents: a general fallback summary is shown.

---

## 📝 License

This project is for educational/demo purposes. Please do not use in production without appropriate validation.

---
