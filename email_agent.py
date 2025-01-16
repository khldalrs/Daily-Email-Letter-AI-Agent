import os
import requests
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
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

def fetch_latest_data():
    """
    Fetch the latest data from both tables
    """
    try:
        # Get latest BTC price data
        btc_query = supabase.table('btc_prices') \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(10) \
            .execute()
        
        # Get latest market analysis (using 'timestamp' instead of 'created_at')
        news_query = supabase.table('eco_news') \
            .select('*') \
            .order('timestamp', desc=True) \
            .limit(2) \
            .execute()
        
        return {
            'btc_data': btc_query.data,
            'news_data': news_query.data
        }
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        print(f"Full error details: {str(e)}")  # Added for better debugging
        return None

def generate_email_content(data):
    """
    Generate email content using Gemini
    """
    try:
        prompt = """You are a professional financial analyst writing a brief email update.
        Based on the provided BTC price data and market analysis, create a very concise but insightful email.
        
        Focus on:
        1. Key price movements and their significance
        2. Important market correlations
        3. Notable trends or patterns
        
        Keep the analysis professional but brief (max 4-5 sentences).
        Format it as a proper email with a subject line.
        
        Context:
        {data}
        """
        
        response = model.generate_content(
            prompt.format(data=data),
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=500,
            )
        )
        
        # Split response into subject and body
        content = response.text.strip()
        subject = content.split('\n')[0].replace('Subject:', '').strip()
        body = '\n'.join(content.split('\n')[1:]).strip()
        
        return subject, body
    
    except Exception as e:
        print(f"Error generating content: {e}")
        return None, None

def send_email(subject, body, recipient="khldalrs@gmail.com"):
    """
    Send email using Mailgun API
    """
    try:
        response = requests.post(
            "https://api.mailgun.net/v3/sandbox0645c47f3ba7bda99c274ad1780fbbb1.mailgun.org/messages",
            auth=("api", os.getenv("MAILGUN_API_KEY")),
            data={
                "from": "Finance Bot <mailgun@sandbox0645c47f3ba7bda99c274ad1780fbbb1.mailgun.org>",
                "to": recipient,
                "subject": subject,
                "text": body
            }
        )
        
        response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    print("Starting financial email update process...")
    
    # Fetch latest data
    data = fetch_latest_data()
    if not data:
        print("Failed to fetch data from database")
        return
    
    # Generate email content
    subject, body = generate_email_content(data)
    if not subject or not body:
        print("Failed to generate email content")
        return
    
    # Send email
    if send_email(subject, body):
        print("Successfully sent financial update email")
    else:
        print("Failed to send email")

if __name__ == "__main__":
    main()
