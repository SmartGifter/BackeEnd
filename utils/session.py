import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None  # Currently logged in user
        
    if 'page' not in st.session_state:
        st.session_state.page = 'login'  # Current page
        
    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = None  # Currently selected event
        
    if 'selected_item' not in st.session_state:
        st.session_state.selected_item = None  # Currently selected wishlist item

def login(user_id):
    """Log a user in"""
    st.session_state.user_id = user_id
    st.session_state.page = 'dashboard'

def logout():
    """Log the current user out"""
    st.session_state.user_id = None
    st.session_state.page = 'login'
    st.session_state.selected_event = None
    st.session_state.selected_item = None

def navigate_to(page, **kwargs):
    """Navigate to a different page"""
    st.session_state.page = page
    
    # Update other session variables if provided
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value 