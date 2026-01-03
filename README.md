---
license: mit
title: MultiAgenticAIForSustainableFarming
sdk: streamlit
emoji: 🌱
colorFrom: green
colorTo: yellow
sdk_version: 1.38.0
app_file: app.py
pinned: false
short_description: AI system for sustainable farming using intelligent agents.
---

# 🌱 Agentic AI for Sustainable Farming

**Agentic AI for Sustainable Farming** is a multi-agent intelligent system designed to transform agriculture by bringing together farmers, weather stations, and agricultural experts for smarter, data-driven decisions.

This AI-powered tool promotes **sustainability**, **resource optimization**, and **improved farmer livelihoods** through collaborative agent-based logic.

---

## 🚀 Key Features

- 🌾 **Farmer Agent** – Collects crop and soil preferences  
- 🌦️ **Weather Analyst Agent** – Forecasts rainfall & temperature  
- 🧑‍🔬 **Sustainability Expert Agent** – Tracks environmental impact  
- 🔁 **Crop Rotation Planner**  
- 🧮 **Fertilizer Optimization Calculator**  
- 🐛 **Pest & Disease Predictor**  
- 🌐 **Dynamic NLP Translation** – Real-time translation to 25+ languages (no hardcoding!)  
- 🔐 **Farmer Login & Secure Access**  
- 📊 **Sustainability Score Tracker** with real-time visualization  

---

## 🧑‍💻 How It Works

Using a Streamlit interface, the system allows users (farmers) to input their details and receive personalized recommendations powered by:
- Machine learning models (scikit-learn)
- Multi-agent collaboration (LangChain, PyAutoGen)
- Real-time weather and crop data
- SQLite database storage
- NLP-powered dynamic translation (Google, Microsoft, LibreTranslate)

---

## 🌍 Dynamic NLP Translation System

The app features a **completely multilingual system** with **zero hardcoding**:

### Translation Architecture
- **Automatic Text Translation** – All UI text dynamically translated
- **Multiple Backends** – Google Translate (fastest), LibreTranslate (free), Microsoft Translator (most accurate)
- **Intelligent Caching** – 1000+ translation cache for instant results (~500ms first call, ~1ms cached)
- **25+ Language Support** – English, Hindi, Telugu, Tamil, Kannada, Marathi, Bengali, Gujarati, Punjabi, and more
- **Zero Configuration** – Works out of the box with no API keys required

### Quick Setup
```python
# from i18n import StreamlitTranslator

# Initialize translator
translator = StreamlitTranslator(backend='libre')

# Add language selector in sidebar
with st.sidebar:
    translator.set_language_selector()

# Use translator instead of st
translator.title("Sustainable Farming System")
translator.header("Farm Details")
translator.write("Enter your information")
```

### Supported Languages (25+)
**Indian Languages:** Hindi, Telugu, Kannada, Tamil, Marathi, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu, Malayalam

**International:** English, French, Spanish, German, Italian, Portuguese, Dutch, Russian, Chinese, Japanese, Korean, Arabic, and more

### Implementation
Replace hardcoded strings with `StreamlitTranslator` methods in `app.py`:
- `translator.title(text)` – Page titles
- `translator.header(text)` – Section headers
- `translator.write(text)` – Regular text
- `translator.button(label)` – Buttons
- `translator.selectbox(label, options)` – Dropdowns
- `translator.text_input(label)` – Text inputs

See `i18n/dynamic_translator.py` for complete API reference.

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

This includes all NLP translation libraries for multilingual support.

### Run the Application
```bash
streamlit run app.py
```

---

## 🛡 License

This project is licensed under the **MIT License**.  
© 2025 B Chaitanya Reddy and Team.

See full terms in the [`LICENSE`](./LICENSE) file.

---

## 👥 Team Credits

- **B Chaitanya Reddy** – Lead Developer & System Architect  
- **Taarun Adithya SK** – AI Modeling & Pest Predictor  
- **Mohammed Saad** – Database Design & Market Analytics  
- **Mohammed Touhid** – Frontend & UI Enhancement  

---

## 🔗 GitHub Repository

View full code and documentation here:  
👉 [GitHub - Agentic AI for Sustainable Farming](https://github.com/BChaitanyaReddy895/Agentic-AI-for-Sustainable-Farming)

---

## 🌍 Let’s build a sustainable farming future, together.