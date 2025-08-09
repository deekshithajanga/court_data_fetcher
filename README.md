# Court-Data Fetcher & Mini-Dashboard (Delhi High Court)

A FastAPI + Mock Scraper app to fetch Delhi High Court case metadata and latest orders/judgments.

##  Completed Features

- **FastAPI Backend**: RESTful API with proper error handling
- **Database Integration**: SQLite with SQLModel for query logging
- **Real Captcha System**: Fetches actual captcha from Delhi High Court
- **Form Validation**: Proper input validation and error messages
- **Responsive UI**: Bootstrap-based responsive design
- **Session Management**: Secure session handling for captcha validation

##  Tech Stack

- **Backend**: FastAPI, SQLModel (SQLite), Jinja2
- **Scraping**: httpx for HTTP requests, Beautiful Soup for parsing, PIL for captcha handling
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript
- **Database**: SQLite with query logging

##  Quick Start

`bash
git clone https://github.com/deekshithajanga/court_data_fetcher.git
cd court_data_fetcher
python -m venv .venv && .\.venv\Scripts\activate
pip install -r requirements.txt
pip install Pillow
python run.py   # Visit http://127.0.0.1:8000
`

## 📋 Demo Note

This version demonstrates full functionality using realistic mock data. The architecture supports easy integration with real court website scraping by replacing the mock response in `scraper.py`.

##  How to Use

1. **Start the application** using the Quick Start commands above
2. **Open your browser** and go to http://127.0.0.1:8000
3. **Click "Get/Refresh Captcha"** to load a real captcha from Delhi High Court
4. **Fill the form:**
   - Case Type: `W.P.(C)` (or any valid case type)
   - Case Number: `1234` (any number)
   - Filing Year: `2022` (any year)
   - Enter the captcha code shown in the image
5. **Click "Fetch Case Details"** to see the results

##  Project Structure

`
court_data_fetcher/
 app/
    courts/              # Court configuration files
    db/                  # Database models and session
    services/            # Business logic (scraper, parser)
    static/              # CSS, JS files
    templates/           # HTML templates
   ─ main.py             # FastAPI application
├── docs/                   # Documentation
├── tests/                  # Test files
├── .env.example            # Environment variables example
├── requirements.txt        # Python dependencies
 run.py                 # Application runner
`

## 🏆 Key Features Demonstrated

1. **Web Scraping Architecture**: Clean separation between scraping logic and API endpoints
2. **Real-time Captcha**: Fetches and displays actual captcha from Delhi High Court
3. **Database Integration**: Logs all queries and responses for audit trail
4. **Error Handling**: Comprehensive error handling with user-friendly messages
5. **Session Management**: Secure captcha validation using session-based approach
6. **Responsive Design**: Works on desktop and mobile devices

##  Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and modify as needed:

`bash
cp .env.example .env
`

##  Notes for Production

The current implementation uses mock data for demonstration. For production deployment:

- Replace mock response in `scraper.py` with real scraping logic
- Add proper error handling for court website changes
- Implement result caching and rate limiting
- Add comprehensive logging and monitoring
- Handle CAPTCHA solving mechanisms

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ��‍💻 Author

**Deekshitha Janga**
- GitHub: [@deekshithajanga](https://github.com/deekshithajanga)
- Project: [Court Data Fetcher](https://github.com/deekshithajanga/court_data_fetcher)

---

*Built as part of internship project demonstrating full-stack web development, web scraping, and database integration skills.*
