# UK Finance Graduate Tracker with AI Cover Letter Generator

A full-stack web application that tracks UK finance graduate roles and generates personalized cover letters using AI.

## Features

- 🔄 **Automatic Updates**: Scrapes tracker data every hour
- 📊 **Smart Filtering**: Shows currently open roles based on application dates
- ✨ **AI Cover Letters**: Generates personalized cover letters using GPT-4o-mini
- 🔗 **Link Integration**: Scrapes company and role pages for better context
- 🎨 **Modern UI**: Clean, responsive interface with real-time search

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 4. Run the Application

```bash
python app.py
```

The app will:
- Start a web server on `http://localhost:5000`
- Run the scraper initially to get data
- Schedule hourly scraper runs automatically

## Usage

1. **View Roles**: Browse all graduate roles in the tracker
2. **Filter Open Roles**: Click "Show Open Roles Only" to see currently accepting applications
3. **Search**: Use the search bar to filter by company, role, or category
4. **Generate Cover Letters**: 
   - Click "Generate Cover Letter" on any role
   - Optionally add your information for personalization
   - Get an AI-generated, professional cover letter
   - Copy to clipboard with one click

## API Endpoints

- `GET /api/roles?open=true` - Get all roles (filter by open status)
- `POST /api/generate-cover-letter` - Generate cover letter for a role
- `POST /api/scrape-now` - Manually trigger scraper
- `GET /api/status` - Get application statistics

## Project Structure

```
tracker/
├── app.py                 # Flask backend
├── scraper.py             # Web scraper
├── templates/
│   └── index.html        # Frontend
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── .env.example          # Example env file
└── README.md             # This file
```

## Requirements

- Python 3.8+
- Chrome browser (for Selenium)
- OpenAI API key
