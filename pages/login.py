import streamlit as st
from utils.session import login
from data.mock_data import USERS

def show_login_page():
    """Display the login page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("HubsHub")
        st.markdown("### Gift coordination made simple")
        
        with st.form("login_form"):
            # In a real app, this would be a proper login form
            # For this prototype, we'll use a simple dropdown
            st.subheader("Login")
            
            users = list(USERS.values())
            options = [f"{user['name']} ({user['email']})" for user in users]
            selected_option = st.selectbox("Select a user:", options)
            
            submit = st.form_submit_button("Login")
            
            if submit:
                selected_index = options.index(selected_option)
                selected_user = users[selected_index]
                login(selected_user["id"])
                st.rerun()

        with st.expander("About HubsHub"):
            st.markdown("""
            HubsHub is a gift coordination platform that helps people:
            - Create events and wishlists
            - Get AI-powered gift suggestions
            - Pool funds for larger gifts
            - Coordinate with friends and family
            
            This is a prototype with simulated functionality.
            """) 