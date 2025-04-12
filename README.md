# HubsHub - Gift Coordination Platform

HubsHub is a comprehensive gift coordination platform that allows users to create events, build wishlists, and coordinate group gifts using advanced fund allocation algorithms and AI-powered suggestions.

## Features

- **User Authentication**: Simple account creation and login
- **Event Creation**: Birthday, wedding, holiday, and other event types
- **Smart Wishlists**: AI-powered gift suggestions and item refinement
- **Fund Allocation**: Sophisticated algorithms for group gift purchasing
- **Real-time Chat**: In-app messaging with AI assistant integration
- **Wallet System**: Simulated payment system with transaction history
- **Social Feed**: Community interactions and gift recommendations

## Backend Architecture

The HubsHub backend is built with a minimalist yet powerful tech stack:

- **Streamlit**: For rapid UI development and deployment
- **Ollama**: Local LLM integration for AI features
- **ScrapegraphAI**: Web scraping for product information extraction
- **Mock Data Layer**: Simulated database for development

### Directory Structure

```
/hubshub
├── app.py                 # Main application entry point
├── requirements.txt       # Dependencies
├── README.md              # This file
├── data/                  # Data storage and mock database
│   └── mock_data.py       # Simulated database records
├── pages/                 # Page components
│   ├── add_wishlist_item.py
│   ├── community.py
│   ├── contribute.py
│   ├── create_event.py
│   ├── dashboard.py
│   ├── event_details.py
│   ├── login.py
│   ├── profile.py
│   └── wallet.py
└── utils/                 # Utility modules
    ├── ai_helper.py       # Ollama integration for AI features
    ├── data_manager.py    # Data access layer
    ├── fund_allocator.py  # Gift fund allocation logic
    ├── scraper.py         # Product information extraction
    └── session.py         # Session state management
```

## Installation

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/download) (for AI features)
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hubshub.git
   cd hubshub
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up Ollama (optional, for AI features):
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull the qwen2.5 model
   ollama pull qwen2.5:latest
   ```

4. Install Playwright (for web scraping):
   ```bash
   playwright install
   ```

## Running the Application

Start the Streamlit app:

```bash
streamlit run app.py
```

The application will be available at http://localhost:8501 by default.

## Core Components

### Data Manager

The `DataManager` class provides an interface for all data operations, simulating a database using in-memory dictionaries. In a production environment, this would be replaced with a proper database.

### AI Helper

The `ai_helper.py` module integrates with Ollama to provide:
- Gift suggestions based on event type and budget
- Wishlist item refinement
- Chat assistance for users

### Fund Allocator

The `fund_allocator.py` module implements sophisticated algorithms for:
- Calculating total required funding including fees
- Allocating individual contributions proportionally
- Handling overfunding scenarios
- Managing underfunding scenarios
- Prioritizing multi-item purchases
- Fraud prevention

### Web Scraper

The `scraper.py` module provides product information extraction from URLs using ScrapegraphAI, with fallback to simulated extraction when unavailable.

## Configuration

The application uses Streamlit's configuration system. You can create a `.streamlit/config.toml` file to customize:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

[server]
port = 8501
enableCORS = false
```

## Dependencies

Main dependencies include:
- streamlit
- langchain-ollama
- scrapegraphai
- pandas
- playwright

See `requirements.txt` for the complete list.

## Development

### Adding New Features

1. Create appropriate modules in the `utils/` directory
2. Implement page components in the `pages/` directory
3. Update the navigation in `app.py`

### Mock Data

During development, the application uses mock data defined in `data/mock_data.py`. In a production environment, this would be replaced with a database.

## Future Improvements

- Database integration (PostgreSQL, MongoDB)
- User authentication with OAuth
- Real payment processing integration
- Enhanced AI recommendations with personalization
- Mobile app version
- Email notifications for events and contributions

## License

[MIT License](LICENSE) 