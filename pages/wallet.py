import streamlit as st
import random
import time
from utils.data_manager import DataManager
from utils.session import navigate_to

def show_wallet_page():
    """Display the wallet page with funding options"""
    user_id = st.session_state.user_id
    user = DataManager.get_user(user_id)
    
    if not user:
        st.error("User not found")
        navigate_to("dashboard")
        st.rerun()
    
    # Header
    st.title("My Wallet")
    
    # Back button
    st.button("Back to Dashboard", on_click=navigate_to, kwargs={"page": "dashboard"})
    
    # Current balance
    st.markdown(f"## Current Balance: ${user['wallet_balance']:.2f}")
    
    # Transaction history (if any)
    if 'transactions' in user:
        st.markdown("### Recent Transactions")
        for tx in user.get('transactions', [])[-5:]:  # Show last 5 transactions
            st.markdown(f"- {tx['date']}: {tx['description']} ${tx['amount']:.2f}")
    
    # Add funds section
    st.markdown("## Add Funds")
    
    # Preset amounts
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        add_25 = st.button("Add $25")
    with col2:
        add_50 = st.button("Add $50")
    with col3:
        add_100 = st.button("Add $100")
    with col4:
        add_200 = st.button("Add $200")
    
    # Custom amount
    with st.form("add_funds_form"):
        st.subheader("Add Custom Amount")
        
        amount = st.number_input("Amount to add ($):", min_value=5.0, max_value=1000.0, step=5.0)
        
        payment_method = st.selectbox(
            "Payment Method:",
            options=["Credit Card", "PayPal", "Apple Pay", "Google Pay"]
        )
        
        if payment_method == "Credit Card":
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Card Number:", placeholder="•••• •••• •••• ••••")
            with col2:
                st.text_input("CVV:", placeholder="•••", type="password")
                
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Expiration Date:", placeholder="MM/YY")
            with col2:
                st.text_input("Cardholder Name:", placeholder="Your Name")
        
        submitted = st.form_submit_button("Add Funds")
        
        if submitted:
            add_funds(user_id, amount, payment_method)
    
    # Handle preset amount buttons
    if add_25:
        add_funds(user_id, 25, "Quick Add")
    elif add_50:
        add_funds(user_id, 50, "Quick Add")
    elif add_100:
        add_funds(user_id, 100, "Quick Add")
    elif add_200:
        add_funds(user_id, 200, "Quick Add")

def add_funds(user_id, amount, payment_method):
    """Add funds to user wallet with simulated payment processing"""
    user = DataManager.get_user(user_id)
    if not user:
        st.error("User not found")
        return
    
    # Show payment processing animation
    with st.spinner("Processing payment..."):
        progress_bar = st.progress(0)
        for i in range(100):
            # Simulate payment processing
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        # 95% chance of success, 5% chance of failure
        success = random.random() < 0.95
    
    if success:
        # Update user wallet balance
        user['wallet_balance'] += amount
        
        # Add transaction record
        if 'transactions' not in user:
            user['transactions'] = []
            
        transaction = {
            'date': time.strftime("%Y-%m-%d"),
            'description': f"Added funds via {payment_method}",
            'amount': amount,
            'type': 'credit'
        }
        
        user['transactions'].append(transaction)
        
        # Show success message
        st.success(f"Successfully added ${amount:.2f} to your wallet!")
        st.balloons()
        
        # Show updated balance
        st.markdown(f"**New Balance:** ${user['wallet_balance']:.2f}")
    else:
        # Show error message for failed payment
        st.error("Payment processing failed. Please try again or use a different payment method.")
    
    # Button to return to dashboard
    st.button("Return to Dashboard", key="return_after_funding", 
             on_click=navigate_to, kwargs={"page": "dashboard"}) 