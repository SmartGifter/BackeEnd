import datetime

# Mock user data
USERS = {
    "user1": {
        "id": "user1",
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "profile_photo": "https://randomuser.me/api/portraits/men/1.jpg",
        "birthday": "1990-05-15",
        "friends": ["user2", "user3", "user4", "user5"],
        "wallet_balance": 500.00
    },
    "user2": {
        "id": "user2",
        "name": "Jamie Smith",
        "email": "jamie@example.com",
        "profile_photo": "https://randomuser.me/api/portraits/women/2.jpg",
        "birthday": "1992-08-22",
        "friends": ["user1", "user3", "user5"],
        "wallet_balance": 350.00
    },
    "user3": {
        "id": "user3",
        "name": "Taylor Wilson",
        "email": "taylor@example.com",
        "profile_photo": "https://randomuser.me/api/portraits/men/3.jpg",
        "birthday": "1988-11-30",
        "friends": ["user1", "user2", "user4"],
        "wallet_balance": 725.50
    },
    "user4": {
        "id": "user4",
        "name": "Morgan Lee",
        "email": "morgan@example.com",
        "profile_photo": "https://randomuser.me/api/portraits/women/4.jpg",
        "birthday": "1995-02-14",
        "friends": ["user1", "user3", "user5"],
        "wallet_balance": 180.25
    },
    "user5": {
        "id": "user5",
        "name": "Casey Brown",
        "email": "casey@example.com",
        "profile_photo": "https://randomuser.me/api/portraits/men/5.jpg",
        "birthday": "1991-07-08",
        "friends": ["user1", "user2", "user4"],
        "wallet_balance": 420.75
    }
}

# Mock events data
EVENTS = {
    "event1": {
        "id": "event1",
        "title": "Alex's Birthday",
        "date": "2024-05-15",
        "type": "birthday",
        "creator": "user1",
        "privacy": "public",
        "participants": ["user2", "user3", "user4", "user5"],
        "rsvp": {
            "user2": "yes",
            "user3": "yes",
            "user4": "maybe",
            "user5": "no"
        }
    },
    "event2": {
        "id": "event2",
        "title": "Jamie's Wedding",
        "date": "2024-09-10",
        "type": "wedding",
        "creator": "user2",
        "privacy": "private",
        "participants": ["user1", "user3", "user5"],
        "rsvp": {
            "user1": "yes",
            "user3": "yes",
            "user5": "yes"
        }
    },
    "event3": {
        "id": "event3",
        "title": "Taylor's Housewarming",
        "date": "2024-06-20",
        "type": "housewarming",
        "creator": "user3",
        "privacy": "public",
        "participants": ["user1", "user2", "user4"],
        "rsvp": {
            "user1": "maybe",
            "user2": "yes",
            "user4": "no"
        }
    }
}

# Mock wishlist data
WISHLISTS = {
    "event1": [
        {
            "id": "item1",
            "title": "Sony WH-1000XM5 Headphones",
            "description": "Noise-cancelling headphones",
            "price": 349.99,
            "category": "large",
            "url": "https://example.com/sony-headphones",
            "status": "available",
            "priority": "high",
            "contributors": []
        },
        {
            "id": "item2",
            "title": "Nintendo Switch Game",
            "description": "Zelda: Tears of the Kingdom",
            "price": 59.99,
            "category": "medium",
            "url": "https://example.com/zelda-game",
            "status": "reserved",
            "priority": "medium",
            "contributors": ["user3"]
        },
        {
            "id": "item3",
            "title": "Book - Dune",
            "description": "Hardcover edition",
            "price": 24.99,
            "category": "small",
            "url": "https://example.com/dune-book",
            "status": "purchased",
            "priority": "low",
            "contributors": ["user4"]
        }
    ],
    "event2": [
        {
            "id": "item4",
            "title": "KitchenAid Stand Mixer",
            "description": "Professional 5 Plus Series",
            "price": 399.99,
            "category": "large",
            "url": "https://example.com/kitchenaid",
            "status": "available",
            "priority": "high",
            "contributors": []
        },
        {
            "id": "item5",
            "title": "Dyson Vacuum",
            "description": "V15 Detect",
            "price": 749.99,
            "category": "large",
            "url": "https://example.com/dyson",
            "status": "available",
            "priority": "medium",
            "contributors": ["user1", "user5"],
            "pooled_amount": 250.00
        }
    ],
    "event3": [
        {
            "id": "item6",
            "title": "Indoor Plants Set",
            "description": "Set of 3 low-maintenance plants",
            "price": 89.99,
            "category": "medium",
            "url": "https://example.com/plants",
            "status": "available",
            "priority": "high",
            "contributors": []
        },
        {
            "id": "item7",
            "title": "Smart Speaker",
            "description": "Amazon Echo Dot",
            "price": 49.99,
            "category": "small",
            "url": "https://example.com/echo-dot",
            "status": "available",
            "priority": "medium",
            "contributors": []
        }
    ]
}

# AI Suggestions based on event type
AI_SUGGESTIONS = {
    "birthday": [
        {"title": "Wireless Earbuds", "price": 129.99, "category": "medium"},
        {"title": "Fitness Tracker", "price": 99.99, "category": "medium"},
        {"title": "Subscription Box", "price": 59.99, "category": "small"},
        {"title": "Personalized Birthday Book", "price": 39.99, "category": "small"}
    ],
    "wedding": [
        {"title": "Robot Vacuum", "price": 299.99, "category": "large"},
        {"title": "High-Quality Bedding Set", "price": 199.99, "category": "medium"},
        {"title": "Smart Home Starter Kit", "price": 249.99, "category": "large"},
        {"title": "Cookware Set", "price": 349.99, "category": "large"}
    ],
    "housewarming": [
        {"title": "Air Purifier", "price": 149.99, "category": "medium"},
        {"title": "Smart Light Bulbs Kit", "price": 79.99, "category": "small"},
        {"title": "Espresso Machine", "price": 199.99, "category": "medium"},
        {"title": "Quality Throw Blanket", "price": 69.99, "category": "small"}
    ]
}

# Chat messages data
CHAT_MESSAGES = {
    "event1": [
        {"user": "user2", "message": "What about pooling for those headphones?", "timestamp": "2024-04-10 14:32:00"},
        {"user": "user3", "message": "Great idea! I can contribute $100", "timestamp": "2024-04-10 14:35:00"},
        {"user": "user4", "message": "I'll chip in $75", "timestamp": "2024-04-10 15:01:00"}
    ],
    "event2": [
        {"user": "user1", "message": "I'm already contributing to the Dyson, can someone else get the mixer?", "timestamp": "2024-08-05 09:17:00"},
        {"user": "user3", "message": "I can cover half if someone matches", "timestamp": "2024-08-05 09:25:00"}
    ],
    "event3": [
        {"user": "user4", "message": "Has anyone reserved the plants yet?", "timestamp": "2024-06-05 18:45:00"},
        {"user": "user1", "message": "Not yet, did you want to get them?", "timestamp": "2024-06-05 18:52:00"}
    ]
}

# Contribution history for tracking who gave what
CONTRIBUTIONS = [
    {"event_id": "event1", "item_id": "item2", "user_id": "user3", "amount": 59.99, "date": "2024-04-12"},
    {"event_id": "event1", "item_id": "item3", "user_id": "user4", "amount": 24.99, "date": "2024-04-15"},
    {"event_id": "event2", "item_id": "item5", "user_id": "user1", "amount": 150.00, "date": "2024-08-15"},
    {"event_id": "event2", "item_id": "item5", "user_id": "user5", "amount": 100.00, "date": "2024-08-16"}
] 