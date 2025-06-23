# Research Feed

A Twitter-like, infinitely-scrollable feed of arXiv pre-prints with ultra-short LLM summaries.

## Features

- Fetch newest papers from selected arXiv categories every 3 hours
- Generate ≤ 60-word summaries via Gemini Flash 2.0 (or OpenAI GPT models as a fallback)
- Serve a paginated feed ordered most-recent first with optional user keyword filter
- User registration/login (email + OAuth-Google)
- Users can save/unsave papers
- Daily digest email with top 5 papers

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Celery, Redis, PostgreSQL with pgvector
- **Frontend**: Next.js 14, Tailwind CSS
- **Authentication**: Next-Auth
- **LLM**: Google Gemini Flash 2.0 (default) or OpenAI GPT-4o mini (optional fallback)
- **Email**: SendGrid
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key (or OpenAI API key as fallback)

### Quick Start

The easiest way to get started is to use the provided run script:

```bash
./run.sh
```

This script will:
1. Create a .env file if one doesn't exist
2. Prompt you to add your Gemini API key
3. Provide options to test the Gemini API, run examples, or start the application

### Manual Setup

If you prefer to set things up manually:

1. Clone the repository:

```bash
git clone https://github.com/yourusername/research-feed.git
cd research-feed
```

2. Run the setup script to create the .env file:

```bash
./setup-env.sh
```

3. Edit the .env file and add your Gemini API key:

```bash
# Using your favorite editor
nano .env

# Add your Gemini API key to the GOOGLE_API_KEY variable
GOOGLE_API_KEY=your-gemini-api-key
```

4. Test the Gemini API connection:

```bash
python test_gemini.py
```

5. Run examples of different Gemini summarization techniques:

```bash
python gemini_examples.py
```

6. Start the services:

```bash
docker-compose up -d
```

7. The API will be available at http://localhost:8000, and the frontend at http://localhost:3000

## LLM Configuration

By default, the system uses Google's Gemini 2.0 Flash Lite model for generating paper summaries. You can switch to OpenAI's GPT models by changing the LLM_PROVIDER in your .env file:

```
# To use OpenAI instead of Gemini
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
```

## Test and Example Scripts

### Testing Gemini Integration

The `test_gemini.py` script lets you verify your Gemini API integration:

```bash
python test_gemini.py
```

This script:
- Lists available Gemini models
- Tests summary generation with Gemini
- Provides a comparison with OpenAI if configured
- Reports success or failure with detailed error information

### Gemini Examples

The `gemini_examples.py` script demonstrates various summarization techniques:

```bash
# Run with default model
python gemini_examples.py

# List available models
python gemini_examples.py --list-models

# Use a specific model
python gemini_examples.py --model gemini-2.0-flash
```

Examples include:
- Basic summary generation
- Detailed summary with methodology and results
- Key points extraction
- Handling placeholder embeddings

## Development

### Backend

The backend is built with FastAPI and uses Celery for background tasks. The database is PostgreSQL with pgvector extension for vector search.

To run the backend in development mode:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### API Documentation

FastAPI generates automatic documentation for the API. You can access it at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to arXiv for use of its open-access interoperability
- Google Gemini for powering the paper summaries 