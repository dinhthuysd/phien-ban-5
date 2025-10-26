from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from database import get_db
from models import (
    Notification,
    NotificationCreate,
    NotificationTemplate,
    NotificationTemplateCreate,
    BroadcastNotification,
    MessageResponse
)
from middleware import get_current_user, get_current_admin_user
from utils.telegram_service import telegram_service
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["notifications"])

# ============ USER NOTIFICATION ENDPOINTS ============

@router.get("/users/notifications/me")
async def get_my_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get current user's notifications"""
    
    query = {"user_id": current_user["id"]}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.notifications.count_documents(query)
    unread_count = await db.notifications.count_documents({
        "user_id": current_user["id"],
        "is_read": False
    })
    
    return {
        "notifications": notifications,
        "total": total,
        "unread_count": unread_count
    }

@router.patch("/users/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark a notification as read"""
    
    notification = await db.notifications.find_one({
        "id": notification_id,
        "user_id": current_user["id"]
    })
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.notifications.update_one(
        {"id": notification_id},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return MessageResponse(message="Notification marked as read")

@router.post("/users/notifications/mark-all-read")
async def mark_all_notifications_read(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark all user notifications as read"""
    
    result = await db.notifications.update_many(
        {"user_id": current_user["id"], "is_read": False},
        {
            "$set": {
                "is_read": True,
                "read_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    
    return MessageResponse(
        message=f"{result.modified_count} notifications marked as read"
    )

@router.delete("/users/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a notification"""
    
    result = await db.notifications.delete_one({
        "id": notification_id,
        "user_id": current_user["id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return MessageResponse(message="Notification deleted")

# ============ ADMIN NOTIFICATION ENDPOINTS ============

@router.post("/admin/users/{user_id}/notify")
async def send_notification_to_user(
    user_id: str,
    notification: NotificationCreate,
    send_telegram: bool = True,
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Send notification to a specific user"""
    
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create notification
    notification_data = Notification(
        user_id=user_id,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        metadata=notification.metadata or {}
    )
    
    await db.notifications.insert_one(notification_data.model_dump())
    
    # Send to Telegram if enabled
    if send_telegram:
        try:
            telegram_message = f"""
📬 <b>{notification.title}</b>

{notification.message}

👤 To: {user.get('email', 'N/A')}
"""
            asyncio.create_task(
                telegram_service.send_message(
                    telegram_service.admin_chat_id,
                    telegram_message
                )
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    return {
        "success": True,
        "notification": notification_data.model_dump(),
        "message": "Notification sent successfully"
    }

@router.post("/admin/notifications/broadcast")
async def broadcast_notification(
    broadcast: BroadcastNotification,
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Send notification to multiple users"""
    
    notifications = []
    
    for user_id in broadcast.user_ids:
        # Check if user exists
        user = await db.users.find_one({"id": user_id})
        if not user:
            continue
        
        # Create notification
        notification_data = Notification(
            user_id=user_id,
            type=broadcast.type,
            title=broadcast.title,
            message=broadcast.message
        )
        
        notifications.append(notification_data.model_dump())
    
    # Bulk insert
    if notifications:
        await db.notifications.insert_many(notifications)
    
    # Send to Telegram if enabled
    if broadcast.send_telegram:
        try:
            telegram_message = f"""
📢 <b>Broadcast: {broadcast.title}</b>

{broadcast.message}

👥 Sent to: {len(notifications)} users
"""
            asyncio.create_task(
                telegram_service.send_to_admin(telegram_message)
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram broadcast: {e}")
    
    return {
        "success": True,
        "sent_count": len(notifications),
        "message": f"Notification sent to {len(notifications)} users"
    }

@router.get("/admin/users/{user_id}/notifications")
async def get_user_notifications(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get notifications for a specific user (admin view)"""
    
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    notifications = await db.notifications.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.notifications.count_documents({"user_id": user_id})
    
    return {
        "notifications": notifications,
        "total": total,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user.get("username", "N/A")
        }
    }

# ============ NOTIFICATION TEMPLATE ENDPOINTS ============

@router.get("/admin/notification-templates")
async def get_notification_templates(
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Get all notification templates"""
    
    templates = await db.notification_templates.find({"is_active": True}).sort("created_at", -1).to_list(100)
    
    return {"templates": templates}

@router.post("/admin/notification-templates")
async def create_notification_template(
    template: NotificationTemplateCreate,
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Create a new notification template"""
    
    template_data = NotificationTemplate(
        name=template.name,
        type=template.type,
        title=template.title,
        message=template.message,
        created_by=admin["id"]
    )
    
    await db.notification_templates.insert_one(template_data.model_dump())
    
    return {
        "success": True,
        "template": template_data.model_dump(),
        "message": "Template created successfully"
    }

@router.delete("/admin/notification-templates/{template_id}")
async def delete_notification_template(
    template_id: str,
    admin: dict = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """Delete a notification template"""
    
    result = await db.notification_templates.delete_one({"id": template_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return MessageResponse(message="Template deleted successfully")

# ============ SYSTEM NOTIFICATION UTILITIES ============

async def create_system_notification(
    user_id: str,
    notification_type: str,
    title: str,
    message: str,
    send_telegram: bool = True,
    db = None
):
    """Helper function to create system notifications"""
    if not db:
        from database import db as database
        db = database
    
    notification_data = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message
    )
    
    db.notifications.insert_one(notification_data.model_dump())
    
    # Send to Telegram if enabled
    if send_telegram:
        try:
            user = db.users.find_one({"id": user_id})
            telegram_message = f"""
🔔 <b>{title}</b>

{message}

👤 User: {user.get('email', 'N/A') if user else 'N/A'}
"""
            await telegram_service.send_to_admin(telegram_message)
        except Exception as e:
            logger.error(f"Failed to send system notification to Telegram: {e}")
