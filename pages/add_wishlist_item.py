import streamlit as st
import datetime
import uuid
from utils.data_manager import DataManager
from utils.session import navigate_to
from utils.ai_helper import get_gift_suggestions, refine_wishlist_item, categorize_gift_by_price, calculate_gift_distribution
from utils.scraper import extract_product_details

def show_add_wishlist_item_page():
    """Display the add wishlist item page"""
    event_id = st.session_state.selected_event
    user_id = st.session_state.user_id
    
    event = DataManager.get_event(event_id)
    if not event or event["creator"] != user_id:
        st.error("You don't have permission to add items to this wishlist")
        navigate_to("dashboard")
        st.rerun()
    
    # Header
    st.title("Add Wishlist Item")
    
    # Back button
    st.button("Back to Event", on_click=navigate_to, 
             kwargs={"page": "event_details", "selected_event": event_id})
    
    # Calculate recommended distribution of items based on participants
    participant_count = len(event["participants"])
    distribution = calculate_gift_distribution(participant_count)
    
    # Show recommended distribution
    st.info(f"""
    **Recommended Wishlist Distribution** (based on {participant_count} invited friends)
    
    - Large gifts (${200}+): {distribution['large']} items
    - Medium gifts ($50-$200): {distribution['medium']} items
    - Small gifts (under $50): {distribution['small']} items
    - Estimated total budget: ${distribution['total_budget']:.2f}
    
    *This helps your friends know what to expect and coordinate their giving.*
    """)
    
    # Tabs for different ways to add items
    tab1, tab2, tab3, tab4 = st.tabs(["Manual Entry", "AI Suggestions", "Refine Item", "Product URL"])
    
    with tab1:
        show_manual_entry(event_id)
        
    with tab2:
        show_ai_suggestions(event_id, event["type"], participant_count)
        
    with tab3:
        show_refine_item(event_id)
        
    with tab4:
        show_product_url_entry(event_id)

def show_manual_entry(event_id):
    """Show manual entry form for adding a wishlist item"""
    st.subheader("Add Item Manually")
    
    # Variables to store form results
    item_added = False
    item_title = ""
    
    with st.form("add_item_form"):
        title = st.text_input("Item title:", placeholder="e.g., Sony WH-1000XM5 Headphones")
        
        col1, col2 = st.columns(2)
        with col1:
            price = st.number_input("Price ($):", min_value=0.01, step=5.0, value=49.99)
        with col2:
            category = categorize_gift_by_price(price)
            category_display = {
                "small": "Small (Under $50)",
                "medium": "Medium ($50-$200)",
                "large": "Large ($200+)"
            }
            st.text_input("Category:", value=category_display.get(category, category), disabled=True)
        
        description = st.text_area("Description:", placeholder="Optional description")
        url = st.text_input("URL:", placeholder="Optional link to product")
        
        priority_options = {
            "high": "High - I really want this!",
            "medium": "Medium - Would be nice to have",
            "low": "Low - Just an idea"
        }
        priority = st.select_slider(
            "Priority:",
            options=list(priority_options.keys()),
            format_func=lambda x: priority_options[x],
            value="medium"
        )
        
        submitted = st.form_submit_button("Add to Wishlist")
        
        if submitted:
            if not title:
                st.error("Please enter a title for the item")
            else:
                # Create the item
                item_data = {
                    "title": title,
                    "price": price,
                    "category": category,
                    "description": description,
                    "url": url,
                    "priority": priority,
                    "status": "available",
                    "contributors": []
                }
                
                item_id = DataManager.add_wishlist_item(event_id, item_data)
                
                if item_id:
                    item_added = True
                    item_title = title
                else:
                    st.error("Failed to add item. Please try again.")
    
    # Show success message and view wishlist button OUTSIDE the form
    if item_added:
        st.success(f"Added '{item_title}' to your wishlist!")
        st.button("View Wishlist", on_click=navigate_to, 
                 kwargs={"page": "event_details", "selected_event": event_id})

def show_ai_suggestions(event_id, event_type, participant_count):
    """Show AI-powered gift suggestions"""
    st.subheader("AI Gift Suggestions")
    
    # Get budget-aware suggestions based on event type and participant count
    suggestions = get_gift_suggestions(event_type, participant_count=participant_count)
    
    if not suggestions:
        st.write("No suggestions available for this event type.")
        return
    
    st.write(f"Based on the event type ({event_type}) and expected participants, here are some gift ideas:")
    
    # Display suggestions in a grid
    cols = st.columns(2)
    
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            with st.expander(f"{suggestion['title']} - ${suggestion['price']:.2f}"):
                st.write(f"**Category:** {suggestion['category'].capitalize()}")
                
                if 'description' in suggestion:
                    st.write(f"**Description:** {suggestion['description']}")
                
                # Add button outside expander to avoid nested button issues
                add_button_key = f"add_suggestion_{i}"
                add_clicked = st.button("Add to Wishlist", key=add_button_key)
                
                if add_clicked:
                    # Add the suggestion to the wishlist
                    item_data = {
                        "title": suggestion["title"],
                        "price": suggestion["price"],
                        "category": suggestion["category"],
                        "description": suggestion.get("description", f"AI-suggested gift for {event_type} event"),
                        "url": "",
                        "priority": "medium",
                        "status": "available",
                        "contributors": []
                    }
                    
                    item_id = DataManager.add_wishlist_item(event_id, item_data)
                    
                    if item_id:
                        st.success(f"Added '{suggestion['title']}' to your wishlist!")
                        view_button_key = f"view_wishlist_{i}"
                        st.button("View Wishlist", key=view_button_key, 
                                 on_click=navigate_to, 
                                 kwargs={"page": "event_details", "selected_event": event_id})
                    else:
                        st.error("Failed to add item. Please try again.")

def show_refine_item(event_id):
    """Show the interface to refine a vague wishlist item"""
    st.subheader("Refine Your Wishlist Item")
    st.markdown("""
    Enter a description of what you'd like, and our AI will help make it more specific.
    For example, type "smart speaker" and we'll suggest specific models.
    """)
    
    refinements = {}
    submitted_description = ""
    clarifying_answers = {}
    
    with st.form("refine_form"):
        description = st.text_input("What item would you like?", 
                                   placeholder="e.g., smart speaker, headphones, fitness tracker")
        
        submitted = st.form_submit_button("Get Suggestions")
        
        if submitted and description:
            submitted_description = description
    
    # Show refinements OUTSIDE the form
    if submitted_description:
        with st.spinner("Getting suggestions..."):
            refinements = refine_wishlist_item(submitted_description)
        
        if refinements:
            if refinements.get("is_vague", False) and "clarifying_questions" in refinements:
                st.markdown("### Let's get more specific")
                st.write("Your request could be more specific. Please answer these questions:")
                
                # Display clarifying questions
                for i, question in enumerate(refinements["clarifying_questions"]):
                    answer = st.text_input(f"**{question}**", key=f"question_{i}")
                    if answer:
                        clarifying_answers[question] = answer
                
                # Check if all questions are answered
                if len(clarifying_answers) == len(refinements["clarifying_questions"]):
                    # Combine original description with answers
                    refined_query = submitted_description + ". " + " ".join([f"{q}: {a}" for q, a in clarifying_answers.items()])
                    
                    # Get new refinements with the added context
                    with st.spinner("Updating suggestions..."):
                        refinements = refine_wishlist_item(refined_query)
            
            # Display suggestion results
            if "suggestions" in refinements:
                st.markdown("### Suggested Options")
                
                for i, item in enumerate(refinements["suggestions"]):
                    with st.expander(f"{item['name']} - ${item['price']:.2f}"):
                        st.write(f"**Features:** {item['features']}")
                        
                    # Add to wishlist button OUTSIDE the expander
                    if st.button("Add to Wishlist", key=f"add_refined_{i}"):
                        category = categorize_gift_by_price(item['price'])
                        
                        # Create the item
                        item_data = {
                            "title": item["name"],
                            "price": item["price"],
                            "category": category,
                            "description": item["features"],
                            "url": "",
                            "priority": "medium",
                            "status": "available",
                            "contributors": []
                        }
                        
                        item_id = DataManager.add_wishlist_item(event_id, item_data)
                        
                        if item_id:
                            st.success(f"Added '{item['name']}' to your wishlist!")
                            st.button("View Wishlist", key=f"view_wishlist_refined_{i}", 
                                    on_click=navigate_to, 
                                    kwargs={"page": "event_details", "selected_event": event_id})
                        else:
                            st.error("Failed to add item. Please try again.")

def show_product_url_entry(event_id):
    """Show interface to extract product information from URL"""
    st.subheader("Add from Product URL")
    st.write("Paste a link to a product, and we'll extract the details automatically using AI.")
    
    # Initialize extraction status variables
    if "url_extraction_success" not in st.session_state:
        st.session_state.url_extraction_success = False
    if "extracted_product_data" not in st.session_state:
        st.session_state.extracted_product_data = None
    
    # Form for URL input and extraction
    with st.form("product_url_form"):
        product_url = st.text_input("Product URL", placeholder="https://www.amazon.com/product")
        submit_url = st.form_submit_button("Extract Product Info")
    
    # Handle URL extraction outside the form
    if submit_url and product_url:
        with st.spinner("Extracting product information..."):
            # Use our new scraper utility
            extracted_data = extract_product_details(product_url)
            
            # Process the extracted data
            if extracted_data:
                # Determine category based on price
                if "category" not in extracted_data:
                    if extracted_data["price"] < 50:
                        extracted_data["category"] = "small"
                    elif extracted_data["price"] < 200:
                        extracted_data["category"] = "medium"
                    else:
                        extracted_data["category"] = "large"
                
                # Store the extraction result
                st.session_state.url_extraction_success = True
                st.session_state.extracted_product_data = extracted_data
                st.rerun()
    
    # Display extraction results and add form
    if st.session_state.url_extraction_success and st.session_state.extracted_product_data:
        data = st.session_state.extracted_product_data
        
        st.success("Product information extracted successfully!")
        
        # Display product info
        st.write(f"### {data['title']}")
        st.write(f"**Price:** ${data['price']:.2f}")
        if data.get('rating'):
            st.write(f"**Rating:** {'⭐' * int(data['rating'])} ({data['rating']})")
        if data.get('brand'):
            st.write(f"**Brand:** {data['brand']}")
        st.write(f"**Description:** {data['description']}")
        
        # Form to add this product
        with st.form("add_product_form"):
            title = st.text_input("Title", value=data["title"])
            price = st.number_input("Price ($)", value=float(data["price"]), min_value=1.0, step=5.0)
            description = st.text_area("Description", value=data["description"])
            
            # Priority selection (only for event creator)
            if st.session_state.user_id == DataManager.get_event(event_id)["creator"]:
                priority = st.select_slider("Priority", options=["low", "medium", "high"], value="medium")
            else:
                priority = "medium"
            
            # Determine category based on price
            if price < 50:
                category = "small"
            elif price < 200:
                category = "medium"
            else:
                category = "large"
            
            submitted = st.form_submit_button("Add to Wishlist")
            
            if submitted:
                # Create new item
                new_item = {
                    "id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "title": title,
                    "price": price,
                    "description": description,
                    "url": product_url,
                    "status": "available",
                    "creator": st.session_state.user_id,
                    "priority": priority,
                    "category": category,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Add to the mock data
                DataManager.add_wishlist_item(new_item)
                
                st.success(f"Added '{title}' to the wishlist!")
                
                # Reset the extraction state
                st.session_state.url_extraction_success = False
                st.session_state.extracted_product_data = None
                
                # Button to view wishlist (outside the form)
        
        # View wishlist button outside the form
        if st.button("View Wishlist", key="view_wishlist_from_url"):
            navigate_to("event_details", selected_event=event_id) 