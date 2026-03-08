import requests
from bs4 import BeautifulSoup
import trafilatura
import groq
import os
from dotenv import load_dotenv

load_dotenv()
client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

def scrape_url(url):
    """Extract clean text from any URL"""
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        if text:
            return text[:4000]
        # Fallback to BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e:
        return f"Could not scrape: {e}"

def scrape_app_reviews(text_or_url):
    """Accept raw pasted reviews or URL"""
    if text_or_url.startswith("http"):
        return scrape_url(text_or_url)
    return text_or_url[:4000]

def scrape_competitor(url):
    """Scrape competitor website"""
    return scrape_url(url)

def ask_groq(prompt, max_tokens=2000):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content