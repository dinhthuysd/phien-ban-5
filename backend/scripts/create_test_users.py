"""
Script to create test users with various statuses
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
from security import hash_password

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "trading_db")

async def create_test_users():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 Creating test users...")
    
    # Sample users data
    test_users = [
        {
            "username": "user1",
            "email": "user1@demo.com",
            "full_name": "John Smith",
            "phone": "+1234567890",
            "is_verified": True,
            "is_premium": False,
            "kyc_status": "pending"
        },
        {
            "username": "user2",
            "email": "user2@demo.com",
            "full_name": "Jane Doe",
            "phone": "+1234567891",
            "is_verified": True,
            "is_premium": True,
            "kyc_status": "pending"
        },
        {
            "username": "user3",
            "email": "user3@demo.com",
            "full_name": "Bob Johnson",
            "phone": "+1234567892",
            "is_verified": False,
            "is_premium": False,
            "kyc_status": "pending"
        },
        {
            "username": "user4",
            "email": "user4@demo.com",
            "full_name": "Alice Williams",
            "phone": "+1234567893",
            "is_verified": True,
            "is_premium": False,
            "kyc_status": "not_submitted"
        },
        {
            "username": "user5",
            "email": "user5@demo.com",
            "full_name": "Charlie Brown",
            "phone": "+1234567894",
            "is_verified": False,
            "is_premium": True,
            "kyc_status": "not_submitted"
        }
    ]
    
    created_count = 0
    
    for user_data in test_users:
        # Check if user already exists
        existing = await db.users.find_one({"email": user_data["email"]})
        if existing:
            print(f"⏭️  Skipping {user_data['email']} - already exists")
            continue
        
        # Create user
        user = {
            "id": str(uuid.uuid4()),
            "username": user_data["username"],
            "email": user_data["email"],
            "hashed_password": hash_password("Demo@123456"),  # Default password
            "full_name": user_data["full_name"],
            "phone": user_data["phone"],
            "is_verified": user_data["is_verified"],
            "is_premium": user_data["is_premium"],
            "is_active": True,
            "is_admin": False,
            "kyc_status": user_data["kyc_status"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "telegram_id": None,
            "telegram_username": None
        }
        
        await db.users.insert_one(user)
        created_count += 1
        print(f"✅ Created user: {user_data['email']} (Password: Demo@123456)")
    
    print(f"\n🎉 Successfully created {created_count} test users")
    
    # Show statistics
    total_users = await db.users.count_documents({"is_admin": {"$ne": True}})
    verified = await db.users.count_documents({"is_verified": True, "is_admin": {"$ne": True}})
    premium = await db.users.count_documents({"is_premium": True, "is_admin": {"$ne": True}})
    
    print(f"\n📊 User Statistics:")
    print(f"   Total Users: {total_users}")
    print(f"   Verified: {verified}")
    print(f"   Premium: {premium}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_users())
