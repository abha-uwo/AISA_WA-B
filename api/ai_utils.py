import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ai_response(prompt, context=""):
    """
    Generates a response using OpenAI based on the provided prompt and context.
    """
    try:
        system_prompt = f"You are an AI assistant for a business. Context: {context}. Be helpful, professional, and concise."
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Using a fast and cost-effective model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {str(e)}")
        return "I'm sorry, I'm having trouble thinking right now. Please try again later."

def get_platform_assistance(user_query):
    """
    Specific assistant for explaining the Kon Hai Best platform.
    """
    platform_context = """
    Aisaconnect (Kon Hai Best) is a WhatsApp Automation SaaS. 
    Features:
    1. Automated Keyword Replies: Set specific responses for keywords.
    2. Global Greeting Message: Auto-welcome new customers.
    3. Visual Workflow Builder: Create complex multi-step automations.
    4. Team Inbox: Real-time chat dashboard for multiple agents.
    5. Broadcast Manager: Send bulk marketing messages.
    6. CRM Integration: Manage client leads and data.
    Clients use it to automate their business communication on WhatsApp.
    """
    return get_ai_response(user_query, platform_context)
