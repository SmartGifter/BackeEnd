import requests
import json
import re
from data.mock_data import AI_SUGGESTIONS
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Initialize Ollama model with direct API access as fallback
ollama_model = None

try:
    # Try to initialize Ollama through LangChain
    ollama_model = OllamaLLM(model="qwen2.5:latest")
    print("Successfully initialized Ollama through LangChain")
except Exception as e:
    print(f"Failed to initialize Ollama model through LangChain: {e}")
    # We'll implement a direct API call method as fallback

# Fallback direct API call to Ollama
def call_ollama_api(prompt, model="qwen2.5:latest"):
    """Direct API call to Ollama as fallback"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(f"Ollama API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error calling Ollama API: {e}")
        return None

def get_gift_suggestions(event_type, budget=None, interests=None, participant_count=None):
    """
    Get gift suggestions based on event type, budget, and interests.
    Uses Ollama if available, otherwise falls back to predefined suggestions.
    """
    # If we have Ollama available, use it for more personalized suggestions
    if ollama_model or True:  # Always attempt to use Ollama, with fallback
        try:
            # Calculate expected budget based on participant count
            budget_info = ""
            if budget:
                budget_info = f"with a budget of ${budget}"
            elif participant_count:
                estimated_budget = participant_count * 25  # $25 per person average
                budget_info = f"with an estimated total gift budget of ${estimated_budget}"
            
            # Create prompt for Ollama with properly escaped JSON brackets
            template = """
            You are a gift suggestion expert. Suggest 4 appropriate gift ideas for a {event_type} event {budget_info}.
            
            For each gift, provide:
            - Name of the gift
            - Approximate price
            - Brief description
            - Size category (small if < $50, medium if $50-$200, large if > $200)
            
            Return the results as a JSON array in this format:
            [
                {{"title": "Gift Name", "price": price_as_number, "description": "Description", "category": "size_category"}}
            ]
            
            Return only the JSON array with no other text.
            """
            
            result = None
            if ollama_model:
                # Try using LangChain
                prompt = ChatPromptTemplate.from_template(template)
                chain = prompt | ollama_model
                result = chain.invoke({"event_type": event_type, "budget_info": budget_info})
            else:
                # Fallback to direct API
                prompt_text = template.format(event_type=event_type, budget_info=budget_info)
                result = call_ollama_api(prompt_text)
            
            if result:
                # Try to parse the JSON response
                try:
                    # Find the JSON array in the response (it might be surrounded by markdown code blocks or other text)
                    json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
                    if json_match:
                        suggestions = json.loads(json_match.group(0))
                        return suggestions
                except Exception as e:
                    print(f"Error parsing gift suggestions: {e}")
                    # Fall back to predefined suggestions
        except Exception as e:
            print(f"Error getting gift suggestions: {e}")
            # Fall back to predefined suggestions
            
    # Fallback to predefined suggestions
    suggestions = AI_SUGGESTIONS.get(event_type, AI_SUGGESTIONS["birthday"])
    
    # Filter by budget if provided
    if budget:
        suggestions = [item for item in suggestions if item["price"] <= budget]
    
    return suggestions

def refine_wishlist_item(item_description):
    """
    Refine a vague wishlist item with more specific questions and suggestions.
    Uses Ollama if available, otherwise falls back to predefined refinements.
    """
    if len(item_description) > 3:  # Only use for non-trivial descriptions
        try:
            # Create prompt for Ollama with properly escaped JSON brackets
            template = """
            A user wants to add "{item_description}" to their gift wishlist, but this might be too vague.
            
            First, identify if the description is specific enough. If it's specific, return 3 similar alternatives with price and features.
            
            If it's vague, provide 2-3 clarifying questions, then suggest 3 specific products that match the description, with prices and features.
            
            Format your response as JSON:
            {{
                "is_vague": true/false,
                "clarifying_questions": ["question1", "question2"],  // Include only if is_vague is true
                "suggestions": [
                    {{"name": "Product Name", "price": price_as_number, "features": "Key features"}}
                ]
            }}
            
            Return only the JSON object with no other text.
            """
            
            result = None
            if ollama_model:
                # Try using LangChain
                prompt = ChatPromptTemplate.from_template(template)
                chain = prompt | ollama_model
                result = chain.invoke({"item_description": item_description})
            else:
                # Fallback to direct API
                prompt_text = template.format(item_description=item_description)
                result = call_ollama_api(prompt_text)
            
            if result:
                # Try to parse the JSON response
                try:
                    # Find the JSON object in the response
                    json_match = re.search(r'\{\s*"is_vague".*\}', result, re.DOTALL)
                    if json_match:
                        refinement = json.loads(json_match.group(0))
                        return refinement
                except Exception as e:
                    print(f"Error parsing refinement JSON: {e}")
                    # Continue to fallback
        except Exception as e:
            print(f"Error refining wishlist item: {e}")
            # Continue to fallback
    
    # Fallback to predefined refinements
    refinements = {
        "smart speaker": [
            {"name": "Amazon Echo Dot (5th Gen)", "price": 49.99, "features": "Compact size, good sound quality"},
            {"name": "Google Nest Audio", "price": 99.99, "features": "Better sound, Google Assistant"},
            {"name": "Apple HomePod Mini", "price": 99.00, "features": "Apple ecosystem integration"}
        ],
        "headphones": [
            {"name": "Sony WH-1000XM5", "price": 349.99, "features": "Best noise cancellation"},
            {"name": "Apple AirPods Pro", "price": 249.99, "features": "Great for iPhone users"},
            {"name": "Bose QuietComfort", "price": 299.99, "features": "Comfortable for long wear"}
        ],
        "fitness tracker": [
            {"name": "Fitbit Charge 6", "price": 149.99, "features": "Good battery life, heart rate monitoring"},
            {"name": "Garmin Vivosmart 5", "price": 149.99, "features": "Accurate fitness tracking"},
            {"name": "Samsung Galaxy Fit3", "price": 99.99, "features": "Affordable, water resistant"}
        ]
    }
    
    # Find the closest match (in a real app, this would use semantic search)
    for key in refinements:
        if key in item_description.lower():
            # Format the response similar to the Ollama response for consistency
            return {
                "is_vague": False,
                "suggestions": refinements[key]
            }
    
    # Default response if no match found
    return {
        "is_vague": True,
        "clarifying_questions": [
            "What specific features are you looking for?",
            "Do you have a preferred brand?",
            "What's your approximate budget?"
        ],
        "suggestions": [{"name": "Custom item", "price": 0.00, "features": "Please provide more details about this item"}]
    }

def categorize_gift_by_price(price):
    """Categorize a gift based on its price"""
    if price < 50:
        return "small"
    elif price < 200:
        return "medium"
    else:
        return "large"

def calculate_gift_distribution(participant_count, avg_contribution=25):
    """
    Calculate recommended gift distribution based on expected participants.
    Returns suggested number of items in each price category.
    """
    total_budget = participant_count * avg_contribution
    
    # Allocate budget to different categories
    # 50% to large gifts, 30% to medium, 20% to small
    large_budget = total_budget * 0.5
    medium_budget = total_budget * 0.3
    small_budget = total_budget * 0.2
    
    # Estimate number of items in each category
    # Assuming average prices: large=$300, medium=$100, small=$30
    large_items = max(1, round(large_budget / 300))
    medium_items = max(1, round(medium_budget / 100))
    small_items = max(2, round(small_budget / 30))
    
    return {
        "large": large_items,
        "medium": medium_items,
        "small": small_items,
        "total_budget": total_budget
    }

# Simulate Ollama chat for the gift assistant
def chat_with_assistant(message, event_type=None, context=None):
    """
    Chat with the gift assistant.
    Uses Ollama if available, otherwise falls back to predefined responses.
    """
    try:
        # Create prompt for Ollama
        event_context = f"for a {event_type} event" if event_type else ""
        
        template = """
        You are a helpful gift coordination assistant for HubsHub, a platform where people can create wishlists for events and friends can contribute towards gifts.
        
        User query: {message}
        
        Event type: {event_context}
        
        Provide a helpful, concise response focused on gift coordination and collaboration.
        Keep your response under 100 words.
        """
        
        result = None
        if ollama_model:
            # Try using LangChain
            prompt = ChatPromptTemplate.from_template(template)
            chain = prompt | ollama_model
            result = chain.invoke({"message": message, "event_context": event_context})
        else:
            # Fallback to direct API
            prompt_text = template.format(message=message, event_context=event_context)
            result = call_ollama_api(prompt_text)
        
        if result:
            return result
    except Exception as e:
        print(f"Error in chat assistant: {e}")
        # Fall back to predefined responses
    
    # Fallback to predefined responses
    responses = {
        "gift ideas": "Based on the event type, I'd recommend looking at tech gadgets, personalized items, or experience gifts.",
        "budget": "It's common for friends to spend $20-50 on birthday gifts. For closer friends, $50-100 is typical.",
        "group gift": "Group gifts are a great idea! You can use the Pool Funds feature to collect money from multiple people.",
        "help": "I can help with gift suggestions, budget planning, coordination with other gift-givers, and more!"
    }
    
    # Simple keyword matching (in a real app, this would use NLP)
    for key in responses:
        if key in message.lower():
            return responses[key]
    
    # Default response
    return "I'm here to help with gift coordination! Ask me about gift ideas, budgeting, or how to use the app's features." 