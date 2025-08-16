# ⚖️ LegalLite

**LegalLite** is a user-friendly AI-powered web application that simplifies complex legal documents into plain, understandable English. It supports login, upload history, PDF summaries, and offers multiple AI-powered summarization modes including OpenAI and Hugging Face APIs — along with a Demo Mode.

***
## 🚀 Features

* 📝 **User Registration & Login**  
  Secure signup and login with hashed passwords using SQLite.

* 📤 **Upload Legal PDFs**  
  Upload documents like rental agreements, NDAs, and employment contracts.

* 🤖 **AI-Based Summarization Modes**
  * 🧪 **Demo Mode**: Uses hardcoded summaries for specific file names.
  * 🔐 **OpenAI API**: Plug your OpenAI key to use GPT-3.5 for summarization.
  * 🌐 **Hugging Face**: Free summarization via open-source transformer model.

* ⚠️ **Risky Terms Detector**  
  Automatically detects and highlights risky clauses or legal terms in uploaded documents to help users spot important red flags.

* 📄 **History View**  
  Track all previously uploaded files and their AI-generated summaries.

* 📥 **Download PDF**  
  Download simplified summaries as printable PDF files.

* 🎤 **Download Voice Summary**  
  Create and download an audio summary of your document using text-to-speech.

* 🖼️ **Flowchart Display**  
  Visual representation of how the app works.

* 🔧 **Help & Feedback Section**  
  Basic onboarding, help text, and downloadable demo contracts.

***

## ⚡ Disclaimers

LegalLite does **not** replace professional legal advice. The platform is intended to make legal information more accessible and less intimidating for users. It should not be relied upon for any actual legal or contractual decisions.  
**We are NOT responsible for any information that might be used as actual legal advice.**

***

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

***

## 🛠️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/legallite.git
cd legallite
```

### 2. Create Virtual Environment (Optional)

```bash
python -m venv venv
source venv/bin/activate  
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
streamlit run app.py
```

***

## 🔐 Optional: Add Hugging Face Secret

Create a `.streamlit/secrets.toml` file:

```toml
HF_TOKEN = "your_huggingface_token_here"
```

***

## 📊 Sample Documents

Test with the built-in sample files:

* `Sample_Rental_Agreement.pdf`
* `Sample_NDA_Agreement.pdf`
* `Sample_Employment_Contract.pdf`

***

## 🧠 Tech Stack

| Tech           | Purpose                        |
| -------------- | ------------------------------ |
| Streamlit      | Web App Frontend               |
| SQLite         | User/Auth/History DB           |
| PyMuPDF (fitz) | PDF Text Extraction            |
| HuggingFace    | Free Summarization (mT5 Model) |
| OpenAI API     | GPT-3.5 Summarization          |
| ReportLab      | Generate downloadable PDFs     |
| gTTS           | Voice summary from text        |

***

## 📎 Known Limitations

* File size limited to **3MB**.
* Demo summaries are only triggered for specific file names.
* Hugging Face output may be brief or generic compared to OpenAI.

***

## 🧪 Demo Mode Support

Demo mode triggers when filenames contain:  
`rental`, `nda`, `employment`  

For unidentified documents: a general fallback summary is shown.

***

## 📝 License

This project is for educational/demo purposes. Please do not use in production without appropriate validation.

---

Citations:
[1] app.py https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/fc6ce82d-f8f5-40c2-aa44-3eef8778451b/app.py
[2] db.py https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/9716b2da-d366-47cc-8b2d-01c8546a35d1/db.py
[3] flowchart.jpeg.jpeg https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/88673023/7317e8b3-4731-438c-933e-5ecb513d8bb9/flowchart.jpeg.jpeg
[4] requirements.txt https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/587368ad-be1c-42c3-823a-84864d07d85a/requirements.txt
[5] Sample_Employment_Contract.pdf https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/4ec36f72-0c11-4e97-b3c4-39049f6a50b0/Sample_Employment_Contract.pdf
[6] Sample_NDA_Agreement.pdf https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/0118de3a-d43d-484c-b0be-2bcd33478099/Sample_NDA_Agreement.pdf
[7] Sample_Rental_Agreement.pdf https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/e4debda7-0c77-4e76-9af3-03eb9ecf0716/Sample_Rental_Agreement.pdf
[8] README.md https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/88673023/570c0ab2-29e2-4867-8627-607e3420c4dc/README.md
