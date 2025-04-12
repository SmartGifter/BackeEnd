import streamlit as st
from utils.data_manager import DataManager
from utils.session import navigate_to

def show_contribute_page():
    """Display the contribution page"""
    event_id = st.session_state.selected_event
    item_id = st.session_state.selected_item
    user_id = st.session_state.user_id
    
    event = DataManager.get_event(event_id)
    item = DataManager.get_wishlist_item(event_id, item_id)
    user = DataManager.get_user(user_id)
    
    if not event or not item or not user:
        st.error("Could not find the event, item, or user")
        navigate_to("dashboard")
        st.rerun()
    
    # Header
    st.title("Contribute to Gift")
    
    # Back button
    st.button("Back to Event", on_click=navigate_to, 
             kwargs={"page": "event_details", "selected_event": event_id})
    
    # Item details
    st.subheader(item["title"])
    st.markdown(f"**Price:** ${item['price']:.2f}")
    
    if item.get("description"):
        st.markdown(item["description"])
    
    if item.get("url"):
        st.markdown(f"[View Item Online]({item['url']})")
    
    # Current funding status
    pooled_amount = item.get("pooled_amount", 0)
    remaining_amount = max(0, item["price"] - pooled_amount)
    
    st.markdown("### Current Funding Status")
    progress = min(pooled_amount / item["price"], 1.0)
    st.progress(progress)
    st.markdown(f"${pooled_amount:.2f} of ${item['price']:.2f} raised")
    st.markdown(f"**Remaining:** ${remaining_amount:.2f}")
    
    # Contributors
    if item.get("contributors"):
        st.markdown("### Current Contributors")
        
        for contributor_id in item["contributors"]:
            contributor = DataManager.get_user(contributor_id)
            if contributor:
                contributions = [c for c in DataManager.get_item_contributions(event_id, item_id) 
                                if c["user_id"] == contributor_id]
                total = sum(c["amount"] for c in contributions)
                st.markdown(f"- {contributor['name']}: ${total:.2f}")
    
    # Contribution form
    st.markdown("### Make Your Contribution")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"Your wallet balance: **${user['wallet_balance']:.2f}**")
        
        # Show reward points if available
        if 'reward_points' in user:
            st.markdown(f"Current reward points: **{user['reward_points']} pts**")
            st.markdown("*You'll earn points for contributing!*")
    
    # Variables to store form results
    contribution_success = False
    is_fully_funded = False
    contribution_amount = 0
    
    # Check if item is already fully funded
    if remaining_amount <= 0:
        st.info("This item is already fully funded!")
        st.button("Back to Event", key="back_funded", on_click=navigate_to, 
                 kwargs={"page": "event_details", "selected_event": event_id})
        return
    
    with st.form("contribute_form"):
        # Check if we have a suggested amount from the fund allocation page
        suggested_amount = st.session_state.get("suggested_amount", None)
        
        if suggested_amount:
            st.info(f"Recommended contribution amount: **${suggested_amount:.2f}**")
            
            # Radio buttons for using suggested amount or custom
            amount_option = st.radio(
                "Contribution options:",
                ["Use recommended amount", "Choose different amount"]
            )
            
            if amount_option == "Use recommended amount":
                contribution_amount = suggested_amount
                st.markdown(f"You will contribute: **${contribution_amount:.2f}**")
            else:
                # Custom amount flow
                contribution_amount = select_contribution_amount(user, remaining_amount)
        else:
            # No suggested amount - use standard flow
            contribution_amount = select_contribution_amount(user, remaining_amount)
        
        # Message to recipient (optional)
        add_message = st.checkbox("Add a message for the recipient")
        
        if add_message:
            message = st.text_area("Your message:")
        else:
            message = ""
        
        # Submit button
        submit = st.form_submit_button("Confirm Contribution")
        
        if submit:
            # Process the contribution
            success = DataManager.add_contribution(event_id, item_id, user_id, contribution_amount)
            
            if success:
                contribution_success = True
                
                # Award points for contribution
                if 'reward_points' not in user:
                    user['reward_points'] = 0
                    
                # Award 10 points per $10 contributed (rounded up)
                points_earned = max(10, int((contribution_amount / 10) * 10))
                user['reward_points'] += points_earned
                
                # Check if item is now fully funded
                updated_item = DataManager.get_wishlist_item(event_id, item_id)
                if updated_item and updated_item.get("status") == "purchased":
                    is_fully_funded = True
    
    # Show success message and button OUTSIDE the form
    if contribution_success:
        st.success(f"Successfully contributed ${contribution_amount:.2f} to {item['title']}!")
        st.success(f"You earned {points_earned} reward points for your contribution!")
        
        if is_fully_funded:
            st.balloons()
            st.success(f"🎉 Congratulations! The gift is now fully funded!")
        
        st.button("Back to Event", key="back_after_contribution", on_click=navigate_to, 
                 kwargs={"page": "event_details", "selected_event": event_id})

def select_contribution_amount(user, remaining_amount):
    """Helper function to handle contribution amount selection"""
    # Suggest contribution amounts
    suggested_amounts = []
    
    # Full amount
    if user["wallet_balance"] >= remaining_amount:
        suggested_amounts.append(("Full amount", remaining_amount))
    
    # Half
    half_amount = remaining_amount / 2
    if user["wallet_balance"] >= half_amount:
        suggested_amounts.append(("Half", half_amount))
    
    # Custom smaller amounts
    for percent, label in [(0.25, "25%"), (0.1, "10%")]:
        partial_amount = remaining_amount * percent
        if user["wallet_balance"] >= partial_amount:
            suggested_amounts.append((label, partial_amount))
    
    # Add custom option
    suggested_amounts.append(("Custom amount", 0))
    
    # Create radio buttons for suggested amounts
    selected_option = st.radio(
        "Suggested contribution amounts:",
        options=[label for label, _ in suggested_amounts],
        index=0
    )
    
    # Find the selected amount
    selected_amount = 0
    for label, amount in suggested_amounts:
        if label == selected_option:
            selected_amount = amount
            break
    
    # If custom amount selected, show input field
    if selected_option == "Custom amount":
        max_allowed = min(user["wallet_balance"], remaining_amount)
        contribution_amount = st.number_input(
            "Enter contribution amount:",
            min_value=1.0,
            max_value=float(max_allowed),
            step=5.0,
            value=min(20.0, max_allowed)
        )
    else:
        contribution_amount = selected_amount
        st.markdown(f"You will contribute: **${contribution_amount:.2f}**")
    
    return contribution_amount 