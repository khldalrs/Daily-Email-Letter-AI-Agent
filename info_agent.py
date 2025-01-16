import os
import json
import requests
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv
from typing import List, Dict
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Initialize clients
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def search_news(query: str) -> List[Dict]:
    """
    Search for news using Brave Search API
    """
    try:
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": os.getenv('BRAVE_API_KEY')
        }
        
        params = {
            "q": query,
            "count": 10,
            "search_lang": "en",
            "text_decorations": False
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/news/search",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json().get('results', [])
        
    except Exception as e:
        print(f"Error searching news: {e}")
        return []

def store_news(finance_info: str) -> bool:
    """
    Store news in Supabase database
    """
    try:
        data = {
            "finance_info": finance_info,
             "timestamp": datetime.utcnow().isoformat()
        }
        supabase.table('eco_news').insert(data).execute()
        return True
    except Exception as e:
        print(f"Error storing news: {e}")
        return False

def process_with_gemini(news_items: List[Dict], category: str) -> List[str]:
    """
    Process news items using Gemini Pro
    
    Args:
        news_items: List of news articles
        category: Either 'crypto' or 'macro' to determine prompt focus
    """
    try:
        # Different prompts based on category
        if category == 'crypto':
            system_prompt = """You are a cryptocurrency market analyst.
            Analyze these news items and provide a comprehensive summary of the current Bitcoin and crypto landscape.
            Focus on:
            1. Bitcoin price movements and trends
            2. Major cryptocurrency developments
            3. Industry news and adoption
            4. Regulatory updates
            
            Provide ONE complete analysis that captures the current state of the crypto market."""
        else:
            system_prompt = """You are a macro-economic analyst.
            Analyze these news items and provide a comprehensive summary of the current global financial landscape.
            Focus on:
            1. Major market movements
            2. Economic indicators
            3. Central bank policies
            4. Global market trends that could impact Bitcoin
            
            Provide ONE complete analysis that captures the current state of global markets."""
        
        user_content = f"Analyze these financial news items and provide a comprehensive market summary:\n{json.dumps(news_items, indent=2)}"
        
        # Combine prompts
        full_prompt = f"{system_prompt}\n\n{user_content}"
        
        # Generate response
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=800,
            )
        )

        return [response.text.strip()]

    except Exception as e:
        print(f"Error processing with Gemini: {e}")
        return []

def main():
    # Define search queries for each category
    search_queries = {
        'crypto': "bitcoin cryptocurrency market price trends adoption news",
        'macro': "global financial markets economic trends central banks interest rates"
    }
    
    print("Starting news collection and analysis...")
    
    for category, query in search_queries.items():
        print(f"\nProcessing category: {category}")
        
        # Search for news
        news_items = search_news(query)
        if not news_items:
            print(f"No news found for: {category}")
            continue
            
        # Process news items with Gemini
        analyzed_entry = process_with_gemini(news_items, category)
        
        # Store the comprehensive analysis
        if analyzed_entry and analyzed_entry[0]:
            if store_news(analyzed_entry[0]):
                print(f"Successfully stored analysis for category: {category}")
            else:
                print(f"Failed to store analysis for category: {category}")

if __name__ == "__main__":
    main()
