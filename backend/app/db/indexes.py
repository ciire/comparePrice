from app.db.mongo_client import db

def setup_indexes():
    users_collection = db["users"]
    pending_users_collection = db["pending_users"]

    # Critical indexes
    users_collection.create_index("email", unique=True)
    users_collection.create_index("trackedItems.itemId")
    pending_users_collection.create_index("email", unique=True) #did this to avoid email enumeration

    # Optional indexes (enable as needed)
    # users_collection.create_index("trackedItems.lastChecked")
    # users_collection.create_index("trackedItems.currentPrice")
    # users_collection.create_index("notificationSettings.preferredTime")
