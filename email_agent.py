import os
import json
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
import google.generativeai as genai
from mailjet_rest import Client

# Load environment variables
load_dotenv()

# Initialize clients
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Initialize Mailjet with v3.1
mailjet = Client(auth=(os.getenv('MJ_APIKEY_PUBLIC'), os.getenv('MJ_APIKEY_PRIVATE')), version='v3.1')

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
        print(f"Full error details: {str(e)}")
        return None

def generate_email_content(data):
    """
    Generate email content using Gemini
    """
    try:
        prompt = """You are a direct and data-driven financial analyst. Create a concise but well-structured market update.

        Analyze the provided BTC price data and market news to create a brief narrative that covers:
        1. Price Movement
           - Current price and significant changes
           - Key technical levels if relevant
        
        2. Market Context
           - Most impactful recent events
           - Notable institutional activity
        
        3. Forward Look
           - Key levels to watch
           - Potential catalysts ahead
        
        Rules:
        - Write in clear, flowing paragraphs
        - No generic commentary or filler phrases
        - Only include significant information
        - Skip any section if nothing noteworthy
        - Maximum 3 short paragraphs
        - No greetings or sign-offs
        
        Format:
        - Subject line: One clear insight about current state
        - 2-3 concise paragraphs
        - Optional bullet points for key levels
        
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
    Send email using Mailjet API v3.1
    """
    try:
        html_body = body.replace('\n', '<br>')
        
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": "khldalrs@gmail.com",
                        "Name": "Finance Bot"
                    },
                    "To": [
                        {
                            "Email": recipient,
                            "Name": "Khalid"
                        }
                    ],
                    "Subject": subject,
                    "TextPart": body,
                    "HTMLPart": f"<h3>Financial Market Update</h3><br>{html_body}"
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        
        if result.status_code == 200:
            print("Email sent successfully!")
            print(f"Response: {result.json()}")
            return True
        else:
            print(f"Failed to send email. Status code: {result.status_code}")
            print(f"Response: {result.json()}")
            return False
        
    except Exception as e:
        print(f"Error sending email: {e}")
        print(f"Attempted to send with data: {json.dumps(data, indent=2)}")
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
