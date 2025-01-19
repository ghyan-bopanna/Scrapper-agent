from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from scraper import ReviewScraper
import uvicorn
import os

class Review(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    rating: Optional[int] = None
    reviewer: Optional[str] = None

class ReviewsData(BaseModel):
    reviews_count: int
    reviews: List[Review]

app = FastAPI(title="Product Reviews Extractor API")
scraper = ReviewScraper()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse('static/index.html')

@app.get("/api/reviews", response_model=ReviewsData)
async def get_reviews(page: str):
    try:
        result = await scraper.extract_reviews(page)
        return ReviewsData(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
