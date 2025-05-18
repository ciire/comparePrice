from app.db.mongo_client import db

def setup_indexes():
    users_collection = db["users"]

    # Critical indexes
    users_collection.create_index("email", unique=True)
    users_collection.create_index("trackedItems.itemId")

    # Optional indexes (enable as needed)
    # users_collection.create_index("trackedItems.lastChecked")
    # users_collection.create_index("trackedItems.currentPrice")
    # users_collection.create_index("notificationSettings.preferredTime")
