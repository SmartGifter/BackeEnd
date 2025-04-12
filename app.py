import streamlit as st
from utils.session import init_session_state

# Import pages
from pages.login import show_login_page
from pages.dashboard import show_dashboard_page
from pages.event_details import show_event_details_page
from pages.create_event import show_create_event_page
from pages.add_wishlist_item import show_add_wishlist_item_page
from pages.contribute import show_contribute_page
from pages.wallet import show_wallet_page
from pages.community import show_community_page

# Set page config
st.set_page_config(
    page_title="HubsHub",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    h1, h2, h3 {
        color: #1f77b4;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
    }
    /* Improve sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    [data-testid="stSidebar"] h3 {
        padding-top: 1rem;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    /* Improve metrics display */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    /* Style for expanders */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Route to the appropriate page based on session state
def route_to_page():
    """Route to the appropriate page based on session state"""
    page = st.session_state.page
    
    # Redirect to login if no user is logged in (except for the login page)
    if not st.session_state.user_id and page != "login":
        page = "login"
        st.session_state.page = page
    
    # Route to the appropriate page
    if page == "login":
        show_login_page()
    elif page == "dashboard":
        show_dashboard_page()
    elif page == "event_details":
        show_event_details_page()
    elif page == "create_event":
        show_create_event_page()
    elif page == "add_wishlist_item":
        show_add_wishlist_item_page()
    elif page == "contribute":
        show_contribute_page()
    elif page == "wallet":
        show_wallet_page()
    elif page == "community":
        show_community_page()
    else:
        st.error(f"Page '{page}' not found")
        st.session_state.page = "dashboard"
        st.rerun()

# Footer
def show_footer():
    """Show the footer with app information"""
    st.divider()
    st.markdown("""
    **HubsHub** - Gift Coordination Platform (Prototype)
    
    This app uses simulated data for demonstration purposes.
    """)

# Main app
def main():
    """Main app function"""
    # Route to the appropriate page
    route_to_page()
    
    # Show footer
    show_footer()

if __name__ == "__main__":
    main() 