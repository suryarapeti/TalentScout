# 🎯 TalentScout Hiring Assistant Chatbot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-red.svg)](https://streamlit.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT%20API-green.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> An intelligent AI-powered chatbot designed to streamline the initial screening process for technology recruitment agencies. TalentScout automates candidate information collection and generates personalized technical assessments based on declared skill sets.

## ✨ Features

- 🤖 **Intelligent Conversation Flow** - Context-aware conversations with natural language processing
- 📝 **Automated Candidate Screening** - Collects essential candidate information systematically
- 💻 **Dynamic Tech Assessment** - Generates personalized technical questions based on candidate's tech stack
- 📊 **Progress Tracking** - Visual progress indicators and real-time status updates
- 🎨 **Modern UI/UX** - Clean, responsive interface built with Streamlit
- 🔒 **Data Privacy** - Secure handling of candidate information with appropriate disclaimers
- 📱 **Responsive Design** - Works seamlessly across desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip package manager

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd TalentScout-Hiring-Assistant-Chatbot
   ```
2. **Create virtual environment**

   ```bash
   python -m venv venv

   # Activate on macOS/Linux
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**

   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```
5. **Run the application**

   ```bash
   streamlit run app.py
   ```
6. **Access the app**
   Open your browser and navigate to `http://localhost:8501`

## 🏗️ Project Structure

```
TalentScout-Hiring-Assistant-Chatbot/
├── app.py                      # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── config/
│   └── config.py              # Configuration settings
├── modules/
│   ├── conversation.py         # Conversation flow management
│   ├── candidate_info.py      # Candidate information collection
│   └── tech_questions.py      # Technical question generation
├── utils/
│   ├── llm_utils.py           # Language model utilities
│   └── data_handler.py        # Data processing functions
├── static/
│   └── style.css              # Custom styling
└── data/                      # Data storage directory
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Key Dependencies

- **Streamlit** - Web application framework
- **OpenAI** - GPT model API integration
- **Python-dotenv** - Environment variable management
- **Pandas** - Data manipulation and analysis

## 📱 Usage Guide

1. **Initial Greeting** - Receive welcome message and process overview
2. **Information Collection** - Provide personal and professional details
3. **Tech Stack Declaration** - Specify technical skills and experience levels
4. **Technical Assessment** - Answer personalized technical questions
5. **Completion** - Receive confirmation and next steps information

## 🧠 How It Works

### 1. Conversation Management

The system maintains conversation context using a state machine approach, ensuring smooth transitions between different screening stages.

### 2. Information Collection

- **Personal Details**: Name, email, phone, location
- **Professional Info**: Experience level, desired positions
- **Technical Skills**: Tech stack declaration and proficiency levels

### 3. Dynamic Question Generation

Based on the candidate's declared tech stack, the system generates relevant technical questions using AI-powered content generation.

### 4. Progress Tracking

Real-time progress indicators show candidates their completion status and guide them through the screening process.

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app.py
```

### 🔮 Future Enhancements

- [ ] **Multi-language Support** - Internationalization for global recruitment
- [ ] **Advanced Analytics** - Candidate performance metrics and insights
- [ ] **Integration APIs** - Connect with popular ATS and HR systems
- [ ] **Video Interview Support** - AI-powered video screening capabilities
- [ ] **Sentiment Analysis** - Emotional intelligence in candidate interactions
- [ ] **Custom Question Banks** - Industry-specific technical assessments

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Made with ❤️ for the recruitment industry**

_TalentScout - Where AI meets human potential_
