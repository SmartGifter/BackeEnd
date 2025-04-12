import streamlit as st
import random
import time
from datetime import datetime, timedelta
from utils.data_manager import DataManager
from utils.session import navigate_to

# Sample community posts
SAMPLE_POSTS = [
    {
        "user_id": "user3",
        "type": "gift_received",
        "content": "Just received this amazing coffee machine from my birthday wishlist! Thanks to everyone who contributed!",
        "image_url": "https://images.unsplash.com/photo-1606937478082-9bfacb70a67e",
        "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
        "likes": 7,
        "comments": [
            {"user_id": "user1", "text": "Looks awesome! Enjoy your coffee!"},
            {"user_id": "user4", "text": "Happy to contribute! ☕"}
        ]
    },
    {
        "user_id": "user2",
        "type": "store_recommendation",
        "content": "Found this great website for personalized gifts. They have amazing quality and quick delivery!",
        "store_name": "PersonalizeIt",
        "store_url": "https://example.com/personalize",
        "date": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "likes": 12,
        "comments": [
            {"user_id": "user5", "text": "I've used them before, they're great!"},
            {"user_id": "user3", "text": "Thanks for sharing, will check them out for my next gift."}
        ]
    },
    {
        "user_id": "user4",
        "type": "gift_recommendation",
        "content": "Looking for a housewarming gift? These smart light bulbs were a hit at my friend's party!",
        "product_name": "SmartBright Color Bulbs",
        "product_url": "https://example.com/smartbulbs",
        "date": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d"),
        "likes": 5,
        "comments": []
    }
]

def show_community_page():
    """Display the community feed page"""
    user_id = st.session_state.user_id
    user = DataManager.get_user(user_id)
    
    if not user:
        st.error("User not found")
        navigate_to("dashboard")
        st.rerun()
    
    # Header
    st.title("Community")
    
    # Back button
    st.button("Back to Dashboard", on_click=navigate_to, kwargs={"page": "dashboard"})
    
    # Add reward points if not already present
    if 'reward_points' not in user:
        user['reward_points'] = random.randint(50, 200)  # Give initial points
    
    # Show user's reward points
    st.markdown(f"## Your Rewards")
    st.metric("Reward Points", f"{user['reward_points']} pts")
    
    # Show level based on points
    levels = [
        {"name": "Gift Novice", "min_points": 0, "color": "gray"},
        {"name": "Gift Giver", "min_points": 100, "color": "blue"},
        {"name": "Gift Expert", "min_points": 300, "color": "green"},
        {"name": "Gift Master", "min_points": 700, "color": "purple"},
        {"name": "Gift Legend", "min_points": 1500, "color": "gold"}
    ]
    
    current_level = levels[0]
    for level in levels:
        if user['reward_points'] >= level['min_points']:
            current_level = level
    
    st.markdown(f"**Level:** <span style='color:{current_level['color']}'>{current_level['name']}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different community sections
    tab1, tab2, tab3 = st.tabs(["Community Feed", "Share Something", "Redeem Rewards"])
    
    with tab1:
        show_community_feed(user_id)
    
    with tab2:
        show_post_form(user_id)
    
    with tab3:
        show_rewards_redemption(user_id, user)

def show_community_feed(user_id):
    """Show the community feed with posts"""
    st.subheader("Latest from the Community")
    
    # In a real app, we would load posts from a database
    # For this prototype, we'll use sample posts
    
    # Get community posts
    posts = []
    if 'community_posts' in st.session_state:
        posts = st.session_state.community_posts + SAMPLE_POSTS
    else:
        posts = SAMPLE_POSTS
        st.session_state.community_posts = []
    
    # Sort posts by date (newest first)
    posts = sorted(posts, key=lambda p: p.get('date', ''), reverse=True)
    
    # Display each post
    for post in posts:
        post_user = DataManager.get_user(post['user_id'])
        
        with st.container():
            # Post header with user info
            col1, col2 = st.columns([1, 5])
            with col1:
                if post_user and 'profile_photo' in post_user:
                    st.image(post_user['profile_photo'], width=50)
            
            with col2:
                user_name = post_user['name'] if post_user else "Unknown User"
                st.markdown(f"**{user_name}** • {post['date']}")
            
            # Post content
            st.markdown(post['content'])
            
            # Post image if available
            if 'image_url' in post:
                st.image(post['image_url'], use_column_width=True)
            
            # Store or product info if available
            if post['type'] == 'store_recommendation' and 'store_name' in post:
                st.markdown(f"🏪 **Store:** [{post['store_name']}]({post.get('store_url', '#')})")
            
            if post['type'] == 'gift_recommendation' and 'product_name' in post:
                st.markdown(f"🎁 **Product:** [{post['product_name']}]({post.get('product_url', '#')})")
            
            # Like button and comment count
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button(f"❤️ {post.get('likes', 0)}", key=f"like_{posts.index(post)}"):
                    # Increment likes
                    post['likes'] = post.get('likes', 0) + 1
                    
                    # Award points for engagement (first time only)
                    user = DataManager.get_user(user_id)
                    if user and post['user_id'] != user_id:
                        user['reward_points'] = user.get('reward_points', 0) + 2
                        st.success("+2 reward points for engagement!")
            
            with col2:
                comment_count = len(post.get('comments', []))
                st.markdown(f"💬 {comment_count} comments")
            
            # Show existing comments
            with st.expander(f"View comments ({comment_count})"):
                for comment in post.get('comments', []):
                    comment_user = DataManager.get_user(comment['user_id'])
                    comment_user_name = comment_user['name'] if comment_user else "Unknown User"
                    st.markdown(f"**{comment_user_name}:** {comment['text']}")
                
                # Add comment form
                new_comment = st.text_input("Add a comment:", key=f"comment_{posts.index(post)}")
                if st.button("Post Comment", key=f"post_comment_{posts.index(post)}"):
                    if new_comment:
                        if 'comments' not in post:
                            post['comments'] = []
                        
                        post['comments'].append({
                            'user_id': user_id,
                            'text': new_comment
                        })
                        
                        # Award points for commenting (first time only)
                        user = DataManager.get_user(user_id)
                        if user and post['user_id'] != user_id:
                            user['reward_points'] = user.get('reward_points', 0) + 5
                            st.success("+5 reward points for commenting!")
                        
                        st.rerun()
            
            st.markdown("---")

def show_post_form(user_id):
    """Show form for creating a new community post"""
    st.subheader("Share with the Community")
    
    with st.form("new_post_form"):
        post_type = st.selectbox(
            "Post Type:", 
            options=["Gift Received", "Store Recommendation", "Gift Recommendation", "General Update"]
        )
        
        content = st.text_area("Your Post:", 
                              placeholder="Share your thoughts, recommendations, or experiences...")
        
        # Additional fields based on post type
        if post_type == "Gift Received":
            image_url = st.text_input("Image URL (optional):", 
                                     placeholder="https://example.com/your-image.jpg")
            
        elif post_type == "Store Recommendation":
            store_name = st.text_input("Store Name:", placeholder="Store Name")
            store_url = st.text_input("Store URL (optional):", placeholder="https://example.com/store")
            
        elif post_type == "Gift Recommendation":
            product_name = st.text_input("Product Name:", placeholder="Product Name")
            product_url = st.text_input("Product URL (optional):", placeholder="https://example.com/product")
        
        submitted = st.form_submit_button("Share Post")
        
        if submitted:
            if not content:
                st.error("Please enter some content for your post")
            else:
                # Create new post
                new_post = {
                    "user_id": user_id,
                    "type": post_type.lower().replace(" ", "_"),
                    "content": content,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "likes": 0,
                    "comments": []
                }
                
                # Add type-specific fields
                if post_type == "Gift Received" and 'image_url' in locals() and image_url:
                    new_post["image_url"] = image_url
                    
                elif post_type == "Store Recommendation" and 'store_name' in locals() and store_name:
                    new_post["store_name"] = store_name
                    if 'store_url' in locals() and store_url:
                        new_post["store_url"] = store_url
                    
                elif post_type == "Gift Recommendation" and 'product_name' in locals() and product_name:
                    new_post["product_name"] = product_name
                    if 'product_url' in locals() and product_url:
                        new_post["product_url"] = product_url
                
                # Add post to session state
                if 'community_posts' not in st.session_state:
                    st.session_state.community_posts = []
                    
                st.session_state.community_posts.append(new_post)
                
                # Award points for posting
                user = DataManager.get_user(user_id)
                if user:
                    user['reward_points'] = user.get('reward_points', 0) + 10
                
                st.success("Post shared successfully! (+10 reward points)")
                st.rerun()

def show_rewards_redemption(user_id, user):
    """Show options for redeeming reward points"""
    st.subheader("Redeem Your Reward Points")
    
    st.markdown(f"You have **{user.get('reward_points', 0)} points** to redeem")
    
    # List of available rewards
    rewards = [
        {"name": "5% Discount on Next Contribution", "cost": 100, "code": "DISC5PCT"},
        {"name": "Free Gift Wrapping", "cost": 50, "code": "FREEWRAP"},
        {"name": "Exclusive Gift Theme", "cost": 200, "code": "EXCTHEME"},
        {"name": "Premium Profile Badge", "cost": 300, "code": "PREMBADGE"},
        {"name": "Donation to Charity on Your Behalf", "cost": 400, "code": "DONATE"}
    ]
    
    # Display available rewards
    for reward in rewards:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"**{reward['name']}**")
        
        with col2:
            st.markdown(f"{reward['cost']} points")
        
        with col3:
            # Disable button if user doesn't have enough points
            disabled = user.get('reward_points', 0) < reward['cost']
            if st.button("Redeem", key=f"redeem_{rewards.index(reward)}", disabled=disabled):
                # Process redemption
                with st.spinner("Processing your redemption..."):
                    time.sleep(1)  # Simulate processing
                    
                    # Deduct points
                    user['reward_points'] -= reward['cost']
                    
                    # Add redemption record
                    if 'redemptions' not in user:
                        user['redemptions'] = []
                        
                    user['redemptions'].append({
                        'date': datetime.now().strftime("%Y-%m-%d"),
                        'reward': reward['name'],
                        'code': reward['code'],
                        'cost': reward['cost']
                    })
                    
                    st.success(f"Redeemed: {reward['name']}")
                    st.code(reward['code'])
                    st.markdown("*Use this code during checkout*")
                    
                    # Show updated points
                    st.markdown(f"**Remaining points:** {user['reward_points']}") 