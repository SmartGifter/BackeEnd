import streamlit as st
import datetime
import uuid
import random
from utils.data_manager import DataManager
from utils.session import navigate_to

def show_create_event_page():
    """Display the create event page"""
    st.title("Create New Event")
    
    # Back to dashboard button
    st.button("Back to Dashboard", on_click=navigate_to, kwargs={"page": "dashboard"})
    
    # Form for creating a new event
    with st.form(key="create_event_form"):
        event_title = st.text_input("Event Title")
        
        # Event type selection
        event_type = st.selectbox(
            "Event Type",
            ["birthday", "wedding", "baby_shower", "holiday", "graduation", "anniversary", "other"]
        )
        
        # Event date selection
        today = datetime.datetime.now()
        next_month = today + datetime.timedelta(days=30)
        event_date = st.date_input(
            "Event Date",
            value=next_month,
            min_value=today
        )
        
        # Description
        event_description = st.text_area("Description (optional)")
        
        # Privacy setting
        privacy = st.radio(
            "Privacy Setting",
            ["public", "private"],
            horizontal=True
        )
        
        # Participant selection from existing users (in a real app, this would be a search)
        all_users = DataManager.get_all_users()
        current_user = DataManager.get_user(st.session_state.user_id)
        other_users = [user for user in all_users if user["id"] != st.session_state.user_id]
        
        # Use multiselect for participants
        selected_participants = st.multiselect(
            "Invite Participants",
            options=[user["id"] for user in other_users],
            format_func=lambda user_id: next((user["name"] for user in other_users if user["id"] == user_id), "Unknown")
        )
        
        # Submit button
        submitted = st.form_submit_button("Create Event")
        
        if submitted:
            if not event_title:
                st.error("Please enter an event title.")
                return
                
            # Create new event
            new_event_id = str(uuid.uuid4())
            new_event = {
                "id": new_event_id,
                "title": event_title,
                "type": event_type,
                "date": event_date.strftime("%Y-%m-%d"),
                "description": event_description,
                "creator": st.session_state.user_id,
                "participants": selected_participants,
                "privacy": privacy,
                "rsvp": {participant_id: "not responded" for participant_id in selected_participants},
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to the mock data
            DataManager.add_event(new_event)
            
            st.success(f"Event '{event_title}' created successfully!")
            
            # Store in session state for navigation
            st.session_state.selected_event = new_event_id
            
            # Create initial chat message
            welcome_message = f"Welcome to the event chat for {event_title}! Use this space to coordinate gift ideas and planning."
            DataManager.add_chat_message(new_event_id, "system", welcome_message)
            
            # Success message and view button
            st.info("Your event has been created! You can now add items to your wishlist.")
    
    # View event button outside the form
    if "selected_event" in st.session_state and st.session_state.selected_event:
        if st.button("View Event", key="view_created_event"):
            navigate_to("event_details", selected_event=st.session_state.selected_event) 