# Product Reviews Extractor API

This API server extracts reviews from any product page using Hugging Face's transformers for dynamic CSS identification and Playwright for web automation.

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────┐
│   FastAPI       │     │  Review Scraper  │     │  Playwright   │
│   Endpoint      │────▶│  with HuggingFace│────▶│  Browser      │
└─────────────────┘     └──────────────────┘     └───────────────┘
        ▲                        │                       │
        │                        ▼                       ▼
        │                ┌──────────────────┐    ┌──────────────┐
        └────────────────│  Review Parser   │◀───│  Web Page    │
                        └──────────────────┘    └──────────────┘
```

## Features

- Dynamic CSS selector identification using Hugging Face transformers
- Automatic pagination handling
- Universal compatibility with different e-commerce platforms
- Playwright-based web automation
- FastAPI-powered REST API

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```
4. Create a .env file with your Hugging Face token:
   ```
   HUGGINGFACE_TOKEN=your_token_here
   ```
5. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

## API Usage

### Get Reviews
```http
GET /api/reviews?page={url}
```

#### Parameters
- `url`: The product page URL (URL encoded)

#### Response Format
```json
{
  "reviews_count": 100,
  "reviews": [
    {
      "title": "Review Title",
      "body": "Review body text",
      "rating": 5,
      "reviewer": "Reviewer Name"
    }
  ]
}
```

## Example Usage

```python
import requests

url = "http://localhost:8000/api/reviews"
params = {"page": "https://example.com/product"}
response = requests.get(url, params=params)
reviews = response.json()
```

## Technical Details

- Uses Hugging Face's transformers for intelligent CSS selector identification
- Implements Playwright for reliable web scraping and pagination handling
- FastAPI for high-performance API endpoints
- Beautiful Soup 4 for HTML parsing

## Error Handling

The API includes comprehensive error handling for:
- Invalid URLs
- Network issues
- Page loading failures
- Missing review elements

