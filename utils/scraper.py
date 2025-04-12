import streamlit as st
import json
import time
from typing import Dict, Any, Optional

# Try importing scrapegraphai, but provide fallback if not available
try:
    from scrapegraphai.graphs import SmartScraperGraph
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False

def extract_product_details(url: str) -> Dict[str, Any]:
    """
    Extract product details from a URL using scrapegraphai.
    Falls back to simulated extraction if scrapegraphai is not available.
    
    Args:
        url: URL of the product to scrape
        
    Returns:
        Dictionary with product details (title, price, description, etc.)
    """
    if SCRAPER_AVAILABLE:
        try:
            return smart_scrape_product(url)
        except Exception as e:
            st.warning(f"Error scraping with AI: {str(e)}. Falling back to simulated extraction.")
            return simulated_extract_product(url)
    else:
        st.info("Smart scraping not available. Using simulated product extraction.")
        return simulated_extract_product(url)

def smart_scrape_product(url: str) -> Dict[str, Any]:
    """
    Extract product details using scrapegraphai's SmartScraperGraph.
    
    Args:
        url: URL of the product to scrape
        
    Returns:
        Dictionary with product details
    """
    # Define the configuration for the scraping pipeline
    graph_config = {
        "llm": {
            "model": "ollama/qwen2.5",
            "model_tokens": 8192
        },
        "verbose": False,
        "headless": True,  # Run browser in headless mode for server environments
    }
    
    # Create and run the scraper
    smart_scraper_graph = SmartScraperGraph(
        prompt="""
        1) Navigate to the product page at source url
        2) Locate and extract the following product details:
           - Product title/name
           - Price (extract just the number)
           - Description or key features
           - Brand/manufacturer
           - Any available ratings (e.g., 4.5/5)
           - Category or product type
        3) Add them into a proper JSON with the following structure:
           {
             "title": "Product Name",
             "price": 99.99,
             "description": "Product description text",
             "brand": "Brand name",
             "rating": 4.5,
             "category": "Electronics"
           }
        4) Return only the JSON result
        """,
        source=url,
        config=graph_config
    )
    
    # Run the pipeline
    with st.spinner("AI is scraping product details..."):
        result = smart_scraper_graph.run()
    
    # Process the result
    if isinstance(result, dict):
        # Ensure price is a float
        if "price" in result and not isinstance(result["price"], float):
            try:
                # Remove currency symbols and convert to float
                price_str = str(result["price"]).replace("$", "").replace("£", "").replace("€", "").strip()
                result["price"] = float(price_str)
            except (ValueError, TypeError):
                result["price"] = 0.0
                
        return result
    else:
        # If result is not a dict, create a basic dict with an error message
        return {
            "title": f"Product from {url}",
            "price": 0.0,
            "description": "Could not extract detailed information",
            "error": "Invalid scraping result format"
        }

def simulated_extract_product(url: str) -> Dict[str, Any]:
    """
    Simulate product information extraction based on URL keywords.
    Used as a fallback when scrapegraphai is not available.
    
    Args:
        url: Product URL to simulate extraction from
        
    Returns:
        Dictionary with simulated product details
    """
    # Simulate network delay
    time.sleep(1)
    
    # Default extraction result
    extracted_data = {
        "title": f"Product from {url.split('//')[1].split('/')[0]}",
        "price": 59.99,
        "description": "This information was generated from the product URL.",
        "brand": "Unknown",
        "category": "general",
        "rating": None
    }
    
    # Simple keyword matching for demo purposes
    url_lower = url.lower()
    
    if "amazon" in url_lower:
        if "echo" in url_lower or "alexa" in url_lower:
            extracted_data = {
                "title": "Amazon Echo Dot (5th Gen) Smart Speaker",
                "price": 49.99,
                "description": "Our best sounding Echo Dot yet - Enjoy an improved audio experience with clearer vocals, deeper bass and vibrant sound in any room.",
                "brand": "Amazon",
                "category": "smart_home",
                "rating": 4.7
            }
        elif "headphone" in url_lower or "airpod" in url_lower:
            extracted_data = {
                "title": "Apple AirPods Pro (2nd Generation)",
                "price": 249.00,
                "description": "Wireless earbuds with noise cancellation, Transparency mode, Spatial Audio with dynamic head tracking.",
                "brand": "Apple",
                "category": "audio",
                "rating": 4.8
            }
        elif "kindle" in url_lower:
            extracted_data = {
                "title": "Kindle Paperwhite (16 GB)",
                "price": 149.99,
                "description": "The thinnest, lightest Kindle Paperwhite yet—with a flush-front design and 300 ppi glare-free display.",
                "brand": "Amazon",
                "category": "electronics",
                "rating": 4.6
            }
    elif "apple" in url_lower:
        if "watch" in url_lower:
            extracted_data = {
                "title": "Apple Watch Series 9",
                "price": 399.99,
                "description": "GPS 41mm Midnight Aluminum Case with Midnight Sport Band",
                "brand": "Apple",
                "category": "wearables",
                "rating": 4.9
            }
        elif "ipad" in url_lower:
            extracted_data = {
                "title": "iPad Air",
                "price": 599.00,
                "description": "10.9-inch Liquid Retina display with True Tone, P3 wide color, and ultra-low reflectivity",
                "brand": "Apple",
                "category": "tablets",
                "rating": 4.8
            }
    elif "samsung" in url_lower:
        if "tv" in url_lower:
            extracted_data = {
                "title": "Samsung 65-Inch OLED 4K S95C Series",
                "price": 2599.99,
                "description": "Quantum HDR OLED+, Neural Quantum Processor with 4K Upscaling",
                "brand": "Samsung",
                "category": "televisions",
                "rating": 4.7
            }
        elif "phone" in url_lower or "galaxy" in url_lower:
            extracted_data = {
                "title": "Samsung Galaxy S23 Ultra",
                "price": 1199.99,
                "description": "200MP Camera, S Pen, Nightography, and Premium Design",
                "brand": "Samsung",
                "category": "smartphones",
                "rating": 4.6
            }
    
    return extracted_data 