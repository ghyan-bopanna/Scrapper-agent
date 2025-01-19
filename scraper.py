from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from transformers import pipeline
import asyncio
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class ReviewScraper:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="nlptown/bert-base-multilingual-uncased-sentiment",
            token=os.getenv("HUGGINGFACE_TOKEN")
        )
        
    async def identify_review_selectors(self, html_content: str) -> Dict[str, str]:
        """Use HuggingFace model to identify review-related CSS selectors"""
        soup = BeautifulSoup(html_content, 'html.parser')
        selectors = {}
        
        # Common review container class patterns
        review_patterns = ['review', 'rating', 'comment', 'testimonial']
        
        # Find potential review containers
        for element in soup.find_all(['div', 'section', 'article']):
            # Check element classes
            classes = element.get('class', [])
            text_content = element.get_text().lower()
            
            # Check if any review pattern matches
            if any(pattern in ' '.join(classes).lower() for pattern in review_patterns) or \
               any(pattern in text_content for pattern in review_patterns):
                if classes:
                    selectors['container'] = f".{'.'.join(classes)}"
                    break
                
                # If no class found, try getting ID
                element_id = element.get('id')
                if element_id:
                    selectors['container'] = f"#{element_id}"
                    break
        
        return selectors

    async def extract_reviews(self, url: str) -> Dict:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate with timeout and wait until network is idle
                await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for potential lazy-loaded content
                await page.wait_for_timeout(2000)
                
                # Get initial HTML content
                content = await page.content()
                selectors = await self.identify_review_selectors(content)
                
                reviews = []
                total_reviews = 0
                
                if not selectors:
                    logging.warning(f"No review selectors found for {url}")
                    return {"reviews_count": 0, "reviews": []}
                
                # Extract reviews using the identified selectors
                if 'container' in selectors:
                    elements = await page.query_selector_all(selectors['container'])
                    
                    for element in elements:
                        try:
                            review_text = await element.inner_text()
                            if len(review_text.strip()) < 10:  # Skip very short texts
                                continue
                                
                            # Use HuggingFace sentiment analysis to determine rating
                            sentiment = self.classifier(review_text)[0]
                            rating = int(float(sentiment['label'].split()[0]))
                            
                            # Try to find reviewer name
                            reviewer_element = await element.query_selector('.author, .reviewer, .user-name')
                            reviewer_name = "Anonymous"
                            if reviewer_element:
                                reviewer_name = await reviewer_element.inner_text()
                            
                            reviews.append({
                                "title": "Product Review",
                                "body": review_text,
                                "rating": rating,
                                "reviewer": reviewer_name
                            })
                            total_reviews += 1
                            
                        except Exception as e:
                            logging.error(f"Error processing review element: {str(e)}")
                            continue
                
                await browser.close()
                
                if total_reviews == 0:
                    logging.warning(f"No reviews found for {url}")
                
                return {
                    "reviews_count": total_reviews,
                    "reviews": reviews
                }
                
        except Exception as e:
            logging.error(f"Error scraping reviews: {str(e)}")
            raise Exception(f"Failed to extract reviews: {str(e)}")
