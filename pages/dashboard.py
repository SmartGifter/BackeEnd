import streamlit as st
import datetime
from utils.data_manager import DataManager
from utils.session import navigate_to, logout

def show_dashboard_page():
    """Display the user dashboard"""
    user_id = st.session_state.user_id
    user = DataManager.get_user(user_id)
    
    if not user:
        st.error("User not found")
        logout()
        st.rerun()
    
    # Add sidebar navigation
    show_sidebar_navigation(user)
    
    # Header with user info and logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"Welcome, {user['name']}")
    with col2:
        st.button("Logout", on_click=logout)
    
    # User stats
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"Wallet Balance: ${user['wallet_balance']:.2f}")
        st.button("Add Funds", on_click=navigate_to, kwargs={"page": "wallet"})
    
    with col2:
        # Show reward points if available
        if 'reward_points' in user:
            st.success(f"Reward Points: {user['reward_points']} pts")
            st.button("Community Hub", on_click=navigate_to, kwargs={"page": "community"})
    
    # Tabs for different dashboard sections
    tab1, tab2, tab3 = st.tabs(["My Events", "Events I'm Invited To", "My Contributions"])
    
    with tab1:
        show_my_events(user_id)
        
    with tab2:
        show_invited_events(user_id)
        
    with tab3:
        show_contributions(user_id)

def show_sidebar_navigation(user):
    """Show sidebar with navigation links"""
    with st.sidebar:
        st.title("HubsHub")
        st.markdown("### Navigation")
        
        # Profile section
        st.image(user.get('profile_photo', 'https://via.placeholder.com/150'), width=100)
        st.markdown(f"**{user['name']}**")
        
        # Navigation links
        st.markdown("---")
        
        if st.button("🏠 Dashboard", use_container_width=True):
            navigate_to("dashboard")
            
        if st.button("💰 My Wallet", use_container_width=True):
            navigate_to("wallet")
            
        if st.button("🎁 Create Event", use_container_width=True):
            navigate_to("create_event")
            
        if st.button("👥 Community", use_container_width=True):
            navigate_to("community")
            
        # Event quick links if any
        events = DataManager.get_user_events(user['id'])
        if events:
            st.markdown("---")
            st.markdown("### My Events")
            for event in events[:3]:  # Show only the first 3 events
                if st.button(f"📅 {event['title']}", key=f"sidebar_{event['id']}", use_container_width=True):
                    navigate_to("event_details", selected_event=event['id'])
            
            if len(events) > 3:
                st.write("*...and more*")
        
        # App info
        st.markdown("---")
        st.markdown("*HubsHub Gift Coordination Platform*")
        st.markdown("*v1.0 Prototype*")

def show_my_events(user_id):
    """Show events created by the user"""
    events = [e for e in DataManager.get_user_events(user_id) if e["creator"] == user_id]
    
    if not events:
        st.write("You haven't created any events yet.")
        
    st.button("Create New Event", key="create_event_btn", 
              on_click=navigate_to, kwargs={"page": "create_event"})
    
    # Display each event
    for event in events:
        with st.expander(f"{event['title']} ({event['date']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Type:** {event['type'].capitalize()}")
                st.write(f"**Privacy:** {event['privacy'].capitalize()}")
                
                # Count RSVPs
                rsvp_counts = {"yes": 0, "maybe": 0, "no": 0, "not responded": 0}
                for status in event["rsvp"].values():
                    if status in rsvp_counts:
                        rsvp_counts[status] += 1
                
                st.write(f"**RSVPs:** {rsvp_counts['yes']} Yes, {rsvp_counts['maybe']} Maybe, {rsvp_counts['no']} No, {rsvp_counts['not responded']} Pending")
            
            with col2:
                st.button("View Event", key=f"view_{event['id']}", 
                         on_click=navigate_to, 
                         kwargs={"page": "event_details", "selected_event": event["id"]})

def show_invited_events(user_id):
    """Show events the user is invited to"""
    events = [e for e in DataManager.get_user_events(user_id) 
              if e["creator"] != user_id and user_id in e["participants"]]
    
    if not events:
        st.write("You don't have any event invitations.")
        return
    
    # Display each invited event
    for event in events:
        creator = DataManager.get_user(event["creator"])
        creator_name = creator["name"] if creator else "Unknown"
        
        with st.expander(f"{event['title']} by {creator_name} ({event['date']})"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Type:** {event['type'].capitalize()}")
                
                # Show user's RSVP status
                user_status = event["rsvp"].get(user_id, "not responded")
                status_display = {
                    "yes": "✅ You're attending",
                    "maybe": "❓ You might attend",
                    "no": "❌ You declined",
                    "not responded": "⏳ You haven't responded"
                }
                st.write(f"**Status:** {status_display.get(user_status, user_status)}")
                
                # RSVP options if not already responded with "no"
                if user_status != "no":
                    rsvp_col1, rsvp_col2, rsvp_col3 = st.columns(3)
                    with rsvp_col1:
                        if st.button("Yes", key=f"yes_{event['id']}"):
                            event["rsvp"][user_id] = "yes"
                            st.success("RSVP updated to Yes!")
                            st.rerun()
                    with rsvp_col2:
                        if st.button("Maybe", key=f"maybe_{event['id']}"):
                            event["rsvp"][user_id] = "maybe"
                            st.success("RSVP updated to Maybe!")
                            st.rerun()
                    with rsvp_col3:
                        if st.button("No", key=f"no_{event['id']}"):
                            event["rsvp"][user_id] = "no"
                            st.success("RSVP updated to No!")
                            st.rerun()
            
            with col2:
                st.button("View Event", key=f"view_invited_{event['id']}",
                         on_click=navigate_to, 
                         kwargs={"page": "event_details", "selected_event": event["id"]})
            
            with col3:
                # Only show contribute button if user has RSVP'd yes or maybe
                if user_status in ["yes", "maybe"]:
                    st.button("Contribute", key=f"contribute_{event['id']}",
                             on_click=navigate_to, 
                             kwargs={"page": "event_details", "selected_event": event["id"]})

def show_contributions(user_id):
    """Show the user's contributions to events"""
    contributions = DataManager.get_user_contributions(user_id)
    
    if not contributions:
        st.write("You haven't made any contributions yet.")
        return
    
    total_contributed = sum(c["amount"] for c in contributions)
    st.metric("Total Contributed", f"${total_contributed:.2f}")
    
    # Group by event
    contributions_by_event = {}
    for contrib in contributions:
        event_id = contrib["event_id"]
        if event_id not in contributions_by_event:
            contributions_by_event[event_id] = []
        contributions_by_event[event_id].append(contrib)
    
    # Display contributions grouped by event
    for event_id, event_contribs in contributions_by_event.items():
        event = DataManager.get_event(event_id)
        if not event:
            continue
            
        with st.expander(f"{event['title']} - ${sum(c['amount'] for c in event_contribs):.2f}"):
            for contrib in event_contribs:
                item = DataManager.get_wishlist_item(event_id, contrib["item_id"])
                if item:
                    st.write(f"- ${contrib['amount']:.2f} for {item['title']} on {contrib['date']}")
                else:
                    st.write(f"- ${contrib['amount']:.2f} on {contrib['date']}")
            
            st.button("View Event", key=f"contrib_{event_id}",
                     on_click=navigate_to, 
                     kwargs={"page": "event_details", "selected_event": event_id}) 