# Interactive Book AI

An AI-powered application that allows users to interact with and query PDF/TXT documents using natural language processing and Google's Gemini API.

## Features
- PDF and TXT file support
- Natural language querying
- AI-enhanced responses using Google Gemini
- Interactive chat interface
- Document statistics

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/interactive-book-ai.git
cd interactive-book-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your API key
```

5. Run the application:
```bash
streamlit run src/app.py
```

## Environment Variables

Create a `.env` file with the following variables:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.