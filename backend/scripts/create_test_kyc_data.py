"""
Script to create test KYC submissions for existing users
"""
import asyncio
import sys
sys.path.append('/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid
import os
from pathlib import Path

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "trading_db")

async def create_test_kyc_data():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🔍 Checking for existing users...")
    
    # Get all users that don't have KYC submissions yet
    users = await db.users.find({"is_admin": {"$ne": True}}).to_list(100)
    
    if not users:
        print("⚠️  No regular users found. Please create some users first.")
        return
    
    print(f"✅ Found {len(users)} users")
    
    # Check existing KYC submissions
    existing_kyc_count = await db.kyc_submissions.count_documents({})
    print(f"📊 Existing KYC submissions: {existing_kyc_count}")
    
    # Create sample KYC submissions for the first 3-5 users
    id_types = ["passport", "driver_license", "national_id"]
    sample_count = min(5, len(users))
    
    created_count = 0
    
    for i in range(sample_count):
        user = users[i]
        
        # Check if user already has KYC
        existing = await db.kyc_submissions.find_one({"user_id": user["id"]})
        if existing:
            print(f"⏭️  Skipping {user['email']} - already has KYC submission")
            continue
        
        # Create KYC submission
        kyc_id = str(uuid.uuid4())
        id_type = id_types[i % len(id_types)]
        
        # Create dummy file IDs
        file_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        
        kyc_submission = {
            "id": kyc_id,
            "user_id": user["id"],
            "id_type": id_type,
            "file_ids": file_ids,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "analysis": {
                "validation_score": 75 + (i * 5),  # Vary scores
                "quality_analysis": {
                    "quality_score": 80 + i,
                    "quality_level": "good"
                },
                "auto_approved": False,
                "analyzed_at": datetime.now(timezone.utc).isoformat()
            }
        }
        
        await db.kyc_submissions.insert_one(kyc_submission)
        
        # Update user KYC status
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"kyc_status": "pending"}}
        )
        
        created_count += 1
        print(f"✅ Created KYC submission for {user['email']} ({id_type})")
    
    print(f"\n🎉 Successfully created {created_count} test KYC submissions")
    
    # Show statistics
    total_kyc = await db.kyc_submissions.count_documents({})
    pending = await db.kyc_submissions.count_documents({"status": "pending"})
    approved = await db.kyc_submissions.count_documents({"status": "approved"})
    rejected = await db.kyc_submissions.count_documents({"status": "rejected"})
    
    print(f"\n📊 KYC Statistics:")
    print(f"   Total: {total_kyc}")
    print(f"   Pending: {pending}")
    print(f"   Approved: {approved}")
    print(f"   Rejected: {rejected}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_kyc_data())
