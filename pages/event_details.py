import streamlit as st
import datetime
import pandas as pd
from utils.data_manager import DataManager
from utils.session import navigate_to
from utils.ai_helper import chat_with_assistant
from utils.fund_allocator import FundAllocator

def show_event_details_page():
    """Display event details, wishlist, and chat"""
    event_id = st.session_state.selected_event
    user_id = st.session_state.user_id
    
    event = DataManager.get_event(event_id)
    if not event:
        st.error("Event not found")
        navigate_to("dashboard")
        st.rerun()
    
    creator = DataManager.get_user(event["creator"])
    is_creator = event["creator"] == user_id
    
    # Event header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(event["title"])
        st.markdown(f"**Date:** {event['date']} | **Type:** {event['type'].capitalize()}")
        
        if creator:
            st.markdown(f"Created by: {creator['name']}")
    
    with col2:
        st.button("Back to Dashboard", on_click=navigate_to, kwargs={"page": "dashboard"})
    
    # Tabs for different event sections
    tab1, tab2, tab3, tab4 = st.tabs(["Wishlist", "Chat", "Participants", "Fund Allocation"])
    
    with tab1:
        show_wishlist(event_id, user_id, is_creator)
        
    with tab2:
        show_chat(event_id, user_id)
        
    with tab3:
        show_participants(event, user_id)
        
    with tab4:
        show_fund_allocation(event_id, user_id, is_creator)

def show_wishlist(event_id, user_id, is_creator):
    """Show the event's wishlist"""
    wishlist = DataManager.get_wishlist(event_id)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Wishlist Items")
    
    if is_creator:
        with col2:
            st.button("Add Item", key="add_item_btn",
                     on_click=navigate_to, 
                     kwargs={"page": "add_wishlist_item", "selected_event": event_id})
    
    if not wishlist:
        st.write("No items in the wishlist yet.")
        return
    
    # Group items by category
    categories = {"small": [], "medium": [], "large": []}
    for item in wishlist:
        category = item.get("category", "medium")
        if category in categories:
            categories[category].append(item)
    
    # Display items by category
    for category_name, category_title in [
        ("large", "Large Gifts ($200+)"), 
        ("medium", "Medium Gifts ($50-$200)"), 
        ("small", "Small Gifts (Under $50)")
    ]:
        items = categories[category_name]
        if items:
            st.markdown(f"#### {category_title}")
            
            for item in items:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    title_text = item["title"]
                    if item["status"] == "reserved":
                        title_text += " (Reserved)"
                    elif item["status"] == "purchased":
                        title_text += " (Purchased)"
                    
                    st.markdown(f"**{title_text}**")
                    if item.get("description"):
                        st.markdown(item["description"])
                    
                    # Show contributors if any
                    if item.get("contributors"):
                        contributor_names = []
                        for c_id in item["contributors"]:
                            user = DataManager.get_user(c_id)
                            if user:
                                contributor_names.append(user["name"])
                        
                        st.markdown(f"*Contributors: {', '.join(contributor_names)}*")
                    
                    # Show pooled amount if any
                    if item.get("pooled_amount"):
                        progress = min(item["pooled_amount"] / item["price"], 1.0)
                        st.progress(progress)
                        st.markdown(f"${item['pooled_amount']:.2f} of ${item['price']:.2f} raised")
                
                with col2:
                    st.markdown(f"**${item['price']:.2f}**")
                    
                    # Show priority if this is the creator's wishlist
                    if is_creator and item.get("priority"):
                        priority_colors = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }
                        priority = item.get("priority", "medium")
                        st.markdown(f"{priority_colors.get(priority, '⚪')} {priority.capitalize()} priority")
                
                with col3:
                    if item["status"] == "available":
                        st.button("Contribute", key=f"contribute_{item['id']}",
                                 on_click=navigate_to,
                                 kwargs={"page": "contribute", "selected_event": event_id, "selected_item": item["id"]})
                    elif item["status"] == "reserved" and item["id"] in [c.get("item_id") for c in DataManager.get_user_contributions(user_id) if c.get("event_id") == event_id]:
                        st.button("View", key=f"view_{item['id']}",
                                 on_click=navigate_to,
                                 kwargs={"page": "view_item", "selected_event": event_id, "selected_item": item["id"]})

def show_chat(event_id, user_id):
    """Show the event chat"""
    st.subheader("Group Chat")
    
    # Chat container with fixed height and scrolling
    chat_container = st.container()
    
    # Input for new message
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            message = st.text_area("New message:", height=100, placeholder="Type your message or @assistant to ask the gift assistant for help")
        
        with col2:
            st.markdown("**Need help?**")
            st.markdown("Start your message with `@assistant` to ask our AI assistant for gift ideas, contribution suggestions, etc.")
            submitted = st.form_submit_button("Send")
        
        if submitted and message:
            # Check if this is a question for the assistant
            if message.lower().startswith("@assistant"):
                query = message[10:].strip()  # Remove the "@assistant" prefix
                
                with st.spinner("Assistant is thinking..."):
                    response = chat_with_assistant(query, event_type=DataManager.get_event(event_id)["type"])
                
                # Add user's question
                DataManager.add_chat_message(event_id, user_id, message)
                
                # Add assistant's response
                DataManager.add_chat_message(event_id, "assistant", response)
            else:
                # Normal message
                DataManager.add_chat_message(event_id, user_id, message)
            
            st.rerun()
    
    # Display existing messages
    with chat_container:
        messages = DataManager.get_chat_messages(event_id)
        
        if not messages:
            st.info("No messages yet. Start the conversation!")
        
        for msg in messages:
            col1, col2 = st.columns([1, 5])
            
            # Get sender info
            if msg["user"] == "assistant":
                sender_name = "Gift Assistant 🤖"
                sender_image = "https://api.dicebear.com/7.x/bottts/svg?seed=assistant"
            else:
                sender = DataManager.get_user(msg["user"])
                sender_name = sender["name"] if sender else "Unknown User"
                sender_image = sender.get("profile_photo", "https://api.dicebear.com/7.x/avataaars/svg?seed=" + msg["user"])
            
            with col1:
                st.image(sender_image, width=50)
            
            with col2:
                st.markdown(f"**{sender_name}** • {msg['timestamp']}")
                
                # Render message with special formatting for @mentions and links
                message_text = msg["message"]
                
                # Format assistant messages differently
                if msg["user"] == "assistant":
                    st.markdown(f"""
                    <div style="background-color: #f0f7ff; padding: 10px; border-radius: 5px; border-left: 5px solid #1f77b4;">
                    {message_text}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(message_text)
                
            st.divider()

def show_participants(event, user_id):
    """Show event participants and their RSVP status"""
    st.subheader("Participants")
    
    # Show creator
    creator = DataManager.get_user(event["creator"])
    if creator:
        st.markdown(f"**Creator:** {creator['name']} ({creator['email']})")
    
    # Show participants
    st.markdown("### RSVPs")
    
    # Create status columns
    yes_col, maybe_col, no_col, pending_col = st.columns(4)
    
    # Group participants by status
    statuses = {"yes": [], "maybe": [], "no": [], "not responded": []}
    
    for participant_id in event["participants"]:
        status = event["rsvp"].get(participant_id, "not responded")
        if status in statuses:
            statuses[status].append(participant_id)
    
    # Display participants by status
    with yes_col:
        st.markdown("#### ✅ Attending")
        for p_id in statuses["yes"]:
            participant = DataManager.get_user(p_id)
            if participant:
                st.markdown(f"- {participant['name']}")
    
    with maybe_col:
        st.markdown("#### ❓ Maybe")
        for p_id in statuses["maybe"]:
            participant = DataManager.get_user(p_id)
            if participant:
                st.markdown(f"- {participant['name']}")
    
    with no_col:
        st.markdown("#### ❌ Declined")
        for p_id in statuses["no"]:
            participant = DataManager.get_user(p_id)
            if participant:
                st.markdown(f"- {participant['name']}")
    
    with pending_col:
        st.markdown("#### ⏳ Pending")
        for p_id in statuses["not responded"]:
            participant = DataManager.get_user(p_id)
            if participant:
                st.markdown(f"- {participant['name']}")
    
    # RSVP controls if the user is a participant but not the creator
    if user_id in event["participants"] and user_id != event["creator"]:
        st.markdown("### Update Your RSVP")
        
        current_status = event["rsvp"].get(user_id, "not responded")
        new_status = st.radio("Your RSVP:", ["yes", "maybe", "no"], 
                            index=["yes", "maybe", "no"].index(current_status) if current_status in ["yes", "maybe", "no"] else 0)
        
        if st.button("Update RSVP"):
            # In a real application, this would update the database
            # For this prototype, we'll update the mock data directly
            event["rsvp"][user_id] = new_status
            st.success("RSVP updated successfully!")
            st.rerun()

def show_fund_allocation(event_id, user_id, is_creator):
    """Show fund allocation and splitting analysis with the new sophisticated logic"""
    st.subheader("Fund Allocation Analysis")
    
    wishlist = DataManager.get_wishlist(event_id)
    event = DataManager.get_event(event_id)
    
    if not wishlist:
        st.info("No items in the wishlist yet.")
        return
    
    # Initialize the fund allocator
    fund_allocator = FundAllocator()
    
    # Analyze wishlist status
    total_wishlist_value = sum(item["price"] for item in wishlist)
    funded_amount = sum(item.get("pooled_amount", 0) for item in wishlist)
    remaining_amount = total_wishlist_value - funded_amount
    
    # Calculate required amounts including fees
    fee_breakdown = fund_allocator.calculate_total_required(total_wishlist_value)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Wishlist Value", f"${total_wishlist_value:.2f}")
    
    with col2:
        st.metric("Funded So Far", f"${funded_amount:.2f}")
    
    with col3:
        st.metric("Remaining", f"${remaining_amount:.2f}")
    
    # Show fee breakdown
    with st.expander("Fee & Buffer Details"):
        st.markdown(f"""
        ### Total Required: ${fee_breakdown['total_required']:.2f}
        
        - **Gift Price:** ${fee_breakdown['gift_price']:.2f}
        - **Platform Fee (5%):** ${fee_breakdown['platform_fee']:.2f}
        - **Payment Processing (3%):** ${fee_breakdown['payment_processing_fee']:.2f}
        - **Currency Buffer (5%):** ${fee_breakdown['exchange_buffer']:.2f}
        
        These fees are estimates. Actual fees may vary slightly at time of purchase.
        """)
    
    # Progress bar for overall funding
    if total_wishlist_value > 0:
        progress = min(funded_amount / total_wishlist_value, 1.0)
        st.progress(progress)
        st.markdown(f"Overall funding progress: **{progress * 100:.1f}%**")
    
    # Pool splitting analysis
    st.markdown("### Proportional Contribution Analysis")
    
    # Get available participants based on RSVPs
    confirmed_participants = [p_id for p_id, status in event["rsvp"].items() if status in ["yes", "maybe"]]
    
    # Get contributors who already contributed
    all_contributions = [c for c in DataManager.get_user_contributions(None) if c["event_id"] == event_id]
    contributor_ids = list(set([c["user_id"] for c in all_contributions]))
    
    # Format contributions for the allocator
    contributions_for_allocator = []
    for c_id in contributor_ids:
        user_contributions = [c for c in all_contributions if c["user_id"] == c_id]
        total_amount = sum(c["amount"] for c in user_contributions)
        contributions_for_allocator.append({
            "user_id": c_id,
            "amount": total_amount
        })
    
    # Calculate proportional contributions
    if contributions_for_allocator:
        proportional_contributions = fund_allocator.allocate_individual_contributions(
            contributions_for_allocator, 
            total_wishlist_value
        )
        
        # Show current contributions table
        st.write("#### Current Contributions")
        
        contribution_data = []
        for contrib in proportional_contributions:
            user = DataManager.get_user(contrib["user_id"])
            username = user["name"] if user else "Unknown"
            contribution_data.append({
                "Contributor": username,
                "Amount": f"${contrib['amount']:.2f}",
                "Percentage": f"{contrib['percentage']:.1f}%",
                "Effective Share": f"${contrib['individual_share']:.2f}"
            })
        
        # Display as a DataFrame for better formatting
        st.dataframe(pd.DataFrame(contribution_data))
    
    # Analyze funding status
    if funded_amount >= total_wishlist_value:
        # Overfunding scenario
        st.markdown("### Overfunding Analysis")
        
        surplus = funded_amount - total_wishlist_value
        st.success(f"The wishlist is fully funded with a surplus of ${surplus:.2f}!")
        
        options = st.radio(
            "How would you like to handle the surplus?",
            ["Proportional Refund", "Keep as Extra", "Add Bonus Gift"],
            index=0
        )
        
        option_mapping = {
            "Proportional Refund": "proportional_refund",
            "Keep as Extra": "keep",
            "Add Bonus Gift": "bonus_tier"
        }
        
        if st.button("Calculate Allocation"):
            allocation = fund_allocator.handle_overfunding(
                funded_amount,
                total_wishlist_value,
                contributions_for_allocator,
                option_mapping[options]
            )
            
            st.write("#### Allocation Plan")
            if options == "Proportional Refund":
                refund_data = []
                for contrib in allocation["contributors"]:
                    user = DataManager.get_user(contrib["user_id"])
                    username = user["name"] if user else "Unknown"
                    refund_data.append({
                        "Contributor": username,
                        "Total Contributed": f"${contrib['amount']:.2f}",
                        "Refund Amount": f"${contrib['refund']:.2f}",
                        "Final Amount": f"${contrib['final_contribution']:.2f}"
                    })
                
                st.dataframe(pd.DataFrame(refund_data))
                
            elif options == "Keep as Extra":
                st.write(f"All contributors keep their full contribution amounts, and the recipient receives an extra ${surplus:.2f}")
                
            elif options == "Add Bonus Gift":
                st.write(f"The surplus of ${surplus:.2f} will be used to purchase an additional bonus gift")
                st.info("AI would suggest complementary items here based on the wishlist")
    
    elif funded_amount < total_wishlist_value:
        # Underfunding scenario
        st.markdown("### Funding Gap Analysis")
        
        shortfall = total_wishlist_value - funded_amount
        st.warning(f"The wishlist is currently underfunded by ${shortfall:.2f}")
        
        # Calculate average contribution per person
        avg_contribution = 25.0  # Default value
        if contributions_for_allocator:
            avg_contribution = funded_amount / len(contributions_for_allocator)
        
        # Show analysis for remaining participants
        remaining_participants = [p for p in confirmed_participants if p not in contributor_ids]
        potential_funding = len(remaining_participants) * avg_contribution
        
        st.markdown(f"""
        - Currently confirmed participants: **{len(confirmed_participants)}**
        - Contributors so far: **{len(contributor_ids)}**
        - Average contribution: **${avg_contribution:.2f}**
        - Potential additional funding: **${potential_funding:.2f}** (if all confirmed participants contribute)
        """)
        
        # Prioritize items
        priority_values = {"high": 3, "medium": 2, "low": 1}
        for item in wishlist:
            item["priority_value"] = priority_values.get(item.get("priority", "medium"), 2)
        
        # Calculate optimal purchase plan
        prioritized_items = fund_allocator.prioritize_multi_item_purchase(
            wishlist,
            funded_amount,
            event["date"]
        )
        
        st.write("#### Recommended Purchase Plan")
        
        purchase_plan_data = []
        for item in prioritized_items:
            pooled = item.get("pooled_amount", 0)
            decision = item.get("purchase_decision", "unknown")
            
            status = ""
            if decision == "buy":
                status = "✅ Ready to Purchase"
            elif decision == "suggest_topup":
                status = f"⚠️ Need ${item.get('additional_needed', 0):.2f} more"
            elif decision == "suggest_alternative":
                status = "❌ Consider alternatives"
            
            purchase_plan_data.append({
                "Item": item["title"],
                "Price": f"${item['price']:.2f}",
                "Funded": f"${pooled:.2f}",
                "Priority": item.get("priority", "medium").capitalize(),
                "Status": status
            })
        
        st.dataframe(pd.DataFrame(purchase_plan_data))
        
        # Option to handle underfunding
        options = st.radio(
            "How would you like to handle underfunding?",
            ["Buy what's possible", "Extend funding deadline", "Refund all contributions"],
            index=0
        )
        
        option_mapping = {
            "Buy what's possible": "partial_fulfillment",
            "Extend funding deadline": "extension",
            "Refund all contributions": "refund"
        }
        
        if st.button("Apply Strategy"):
            allocation = fund_allocator.handle_underfunding(
                funded_amount,
                total_wishlist_value,
                contributions_for_allocator,
                {"items": wishlist},
                option_mapping[options]
            )
            
            st.write("#### Strategy Application")
            
            if options == "Buy what's possible":
                affordable_items = [item for item in prioritized_items if item.get("can_purchase", False)]
                if affordable_items:
                    st.success(f"Can purchase {len(affordable_items)} items with the current funding")
                    for item in affordable_items:
                        st.markdown(f"- {item['title']} (${item['price']:.2f})")
                else:
                    st.error("Cannot afford any complete items with the current funding")
                    st.info("Consider using the funds for gift cards or partial contributions")
                    
            elif options == "Extend funding deadline":
                st.write(f"Funding deadline will be extended to collect the missing ${shortfall:.2f}")
                st.info("Participants who haven't contributed yet will be reminded")
                
            elif options == "Refund all contributions":
                st.write("All contributions will be refunded to their original contributors")
                refund_data = []
                for contrib in allocation["contributors"]:
                    user = DataManager.get_user(contrib["user_id"])
                    username = user["name"] if user else "Unknown"
                    refund_data.append({
                        "Contributor": username,
                        "Refund Amount": f"${contrib['amount']:.2f}"
                    })
                
                st.dataframe(pd.DataFrame(refund_data))
    
    # Suggest splitting contributions for individual items
    st.markdown("### Suggested Item Contributions")
    
    for item in wishlist:
        if item["status"] != "purchased":
            pooled_amount = item.get("pooled_amount", 0)
            remaining = item["price"] - pooled_amount
            
            if remaining > 0:
                with st.expander(f"{item['title']} - ${remaining:.2f} needed"):
                    # Show item details
                    st.markdown(f"**Price:** ${item['price']:.2f}")
                    if pooled_amount > 0:
                        st.markdown(f"**Funded so far:** ${pooled_amount:.2f}")
                        progress = min(pooled_amount / item["price"], 1.0)
                        st.progress(progress)
                    
                    # Estimate number of contributors needed
                    participants_needed = max(1, round(remaining / avg_contribution))
                    contribution_per_person = remaining / participants_needed
                    
                    st.markdown(f"""
                    **Smart Contribution Plan:**
                    
                    - Split between **{participants_needed}** people
                    - **${contribution_per_person:.2f}** per person
                    
                    This plan is calculated based on the average contribution amount and group size.
                    """)
                    
                    # Get current contributors to this item
                    item_contributors = item.get("contributors", [])
                    if user_id not in item_contributors:
                        if st.button("Contribute Smart Amount", key=f"smart_contribute_{item['id']}"):
                            st.session_state.selected_item = item["id"]
                            st.session_state.suggested_amount = contribution_per_person
                            navigate_to("contribute", selected_event=event_id, selected_item=item["id"]) 