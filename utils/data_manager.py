import datetime
from data.mock_data import USERS, EVENTS, WISHLISTS, CHAT_MESSAGES, CONTRIBUTIONS

class DataManager:
    """Class to manage mock data operations"""
    
    @staticmethod
    def get_user(user_id):
        """Get user by ID"""
        return USERS.get(user_id)
    
    @staticmethod
    def get_all_users():
        """Get all users"""
        return USERS
        
    @staticmethod
    def get_user_friends(user_id):
        """Get a user's friends"""
        user = USERS.get(user_id)
        if not user:
            return []
        
        friend_ids = user.get("friends", [])
        return [USERS.get(friend_id) for friend_id in friend_ids]
    
    @staticmethod
    def get_event(event_id):
        """Get event by ID"""
        return EVENTS.get(event_id)
    
    @staticmethod
    def get_user_events(user_id):
        """Get events where the user is creator or participant"""
        user_events = []
        for event_id, event in EVENTS.items():
            if event["creator"] == user_id or user_id in event["participants"]:
                user_events.append(event)
        return user_events
    
    @staticmethod
    def get_wishlist(event_id):
        """Get wishlist for an event"""
        return WISHLISTS.get(event_id, [])
    
    @staticmethod
    def get_wishlist_item(event_id, item_id):
        """Get a specific wishlist item"""
        wishlist = WISHLISTS.get(event_id, [])
        for item in wishlist:
            if item["id"] == item_id:
                return item
        return None
    
    @staticmethod
    def update_wishlist_item(event_id, item_id, updates):
        """Update a wishlist item"""
        wishlist = WISHLISTS.get(event_id, [])
        for i, item in enumerate(wishlist):
            if item["id"] == item_id:
                wishlist[i].update(updates)
                return True
        return False
    
    @staticmethod
    def add_wishlist_item(event_id, item_data):
        """Add a new item to a wishlist"""
        if event_id not in WISHLISTS:
            WISHLISTS[event_id] = []
            
        # Generate a new item ID
        item_id = f"item{len(WISHLISTS[event_id]) + 1}"
        
        # Set defaults
        new_item = {
            "id": item_id,
            "title": "",
            "description": "",
            "price": 0.0,
            "category": "medium",
            "url": "",
            "status": "available",
            "priority": "medium",
            "contributors": []
        }
        
        # Update with provided data
        new_item.update(item_data)
        
        WISHLISTS[event_id].append(new_item)
        return item_id
    
    @staticmethod
    def get_chat_messages(event_id):
        """Get chat messages for an event"""
        return CHAT_MESSAGES.get(event_id, [])
    
    @staticmethod
    def add_chat_message(event_id, user_id, message):
        """Add a chat message to an event"""
        if event_id not in CHAT_MESSAGES:
            CHAT_MESSAGES[event_id] = []
            
        new_message = {
            "user": user_id,
            "message": message,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        CHAT_MESSAGES[event_id].append(new_message)
        return True
    
    @staticmethod
    def get_user_contributions(user_id):
        """Get contributions made by a user"""
        return [c for c in CONTRIBUTIONS if c["user_id"] == user_id]
    
    @staticmethod
    def get_item_contributions(event_id, item_id):
        """Get all contributions for a specific item"""
        return [c for c in CONTRIBUTIONS if c["event_id"] == event_id and c["item_id"] == item_id]
    
    @staticmethod
    def add_contribution(event_id, item_id, user_id, amount):
        """Add a new contribution"""
        # Update user wallet balance
        user = USERS.get(user_id)
        if not user or user["wallet_balance"] < amount:
            return False
            
        user["wallet_balance"] -= amount
        
        # Add to contributions list
        new_contribution = {
            "event_id": event_id,
            "item_id": item_id,
            "user_id": user_id,
            "amount": amount,
            "date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
        
        CONTRIBUTIONS.append(new_contribution)
        
        # Update item contributors
        item = DataManager.get_wishlist_item(event_id, item_id)
        if item:
            if user_id not in item["contributors"]:
                item["contributors"].append(user_id)
                
            # Add/update pooled amount
            pooled_amount = item.get("pooled_amount", 0)
            item["pooled_amount"] = pooled_amount + amount
            
            # Check if fully funded
            if item["pooled_amount"] >= item["price"]:
                item["status"] = "purchased"
                
            DataManager.update_wishlist_item(event_id, item_id, item)
            
        return True 