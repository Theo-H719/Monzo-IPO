import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from PyPDF2 import PdfReader
import time
import random

# ==========================================
# CONFIGURATION
# ==========================================
# User-Agent is crucial to identify your bot legitimately
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    
}

# List of target URLs (Public Investor Relations & News)
TARGET_URLS =

# ==========================================
# SCRAPER FUNCTIONS
# ==========================================

def scrape_html(url):
    """Extracts text content from standard web pages."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles to clean text
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract title and body text
            title = soup.title.string if soup.title else "No Title"
            text = " ".join(soup.get_text(separator=' ').split())
            return {"source": url, "title": title, "content": text[:5000]} # Limit text for preview
        else:
            print(f"Failed to retrieve HTML: {url} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"Error scraping HTML {url}: {e}")
        return None

def scrape_pdf(url):
    """Downloads and extracts text from PDF reports."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = ""
                # Extract text from first 10 pages (Executive Summaries usually here)
                for page in reader.pages[:10]: 
                    text += page.extract_text() + " "
            
            return {"source": url, "title": "PDF Document", "content": text[:5000]}
        else:
            print(f"Failed to retrieve PDF: {url} (Status: {response.status_code})")
            return None
    except Exception as e:
        print(f"Error scraping PDF {url}: {e}")
        return None

# ==========================================
# EXECUTION LOOP
# ==========================================

results =

print(f"Starting research on {len(TARGET_URLS)} sources...")

for url in TARGET_URLS:
    # Rate Limiting: Sleep between 2-5 seconds to respect server load
    time.sleep(random.uniform(2, 5))
    
    if url.lower().endswith('.pdf'):
        print(f"Processing PDF: {url}")
        data = scrape_pdf(url)
    else:
        print(f"Processing HTML: {url}")
        data = scrape_html(url)
    
    if data:
        results.append(data)

# ==========================================
# OUTPUT
# ==========================================

# Convert to DataFrame for analysis
df = pd.DataFrame(results)

# Save to CSV for your website's backend
df.to_csv('monzo_research_data.csv', index=False)
print("Research complete. Data saved to 'monzo_research_data.csv'")

# Display preview
print(df[['source', 'title']].head())
