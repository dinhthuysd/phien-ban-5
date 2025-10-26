import os
import asyncio
from typing import Optional, List
from telegram import Bot
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self):
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
        self.bot = None
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
        else:
            logger.warning("Telegram bot token not configured")
    
    async def send_message(
        self, 
        chat_id: str, 
        message: str, 
        parse_mode: str = 'HTML'
    ) -> bool:
        """Send a text message to a Telegram chat"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.info(f"Message sent to chat {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")
            return False
    
    async def send_photo(
        self,
        chat_id: str,
        photo_data: bytes,
        caption: Optional[str] = None,
        filename: str = "image.jpg"
    ) -> bool:
        """Send a photo to a Telegram chat"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_photo(
                chat_id=chat_id,
                photo=photo_data,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info(f"Photo sent to chat {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send photo to {chat_id}: {e}")
            return False
    
    async def send_document(
        self,
        chat_id: str,
        document_data: bytes,
        filename: str,
        caption: Optional[str] = None
    ) -> bool:
        """Send a document to a Telegram chat"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            await self.bot.send_document(
                chat_id=chat_id,
                document=document_data,
                filename=filename,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info(f"Document sent to chat {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Failed to send document to {chat_id}: {e}")
            return False
    
    async def send_to_admin(self, message: str) -> bool:
        """Send a message to the admin chat"""
        if not self.admin_chat_id:
            logger.error("Admin chat ID not configured")
            return False
        
        return await self.send_message(self.admin_chat_id, message)
    
    async def send_kyc_notification(
        self,
        user_email: str,
        user_name: str,
        kyc_id: str,
        status: str = "pending"
    ) -> bool:
        """Send KYC submission notification to admin"""
        message = f"""
🆔 <b>KYC Submission</b>

👤 User: {user_name}
📧 Email: {user_email}
🔖 KYC ID: {kyc_id}
📊 Status: {status.upper()}

⏰ Time: {asyncio.get_event_loop().time()}
"""
        return await self.send_to_admin(message)
    
    async def send_kyc_images(
        self,
        user_email: str,
        user_name: str,
        images: List[bytes],
        id_type: str
    ) -> bool:
        """Send KYC images to admin"""
        try:
            # Send header message
            header = f"""
📸 <b>KYC Documents</b>

👤 User: {user_name}
📧 Email: {user_email}
🆔 ID Type: {id_type}
📄 Total Images: {len(images)}
"""
            await self.send_to_admin(header)
            
            # Send each image
            for idx, image_data in enumerate(images, 1):
                caption = f"Document {idx}/{len(images)} - {user_name}"
                await self.send_photo(
                    self.admin_chat_id,
                    image_data,
                    caption
                )
            
            return True
        except Exception as e:
            logger.error(f"Failed to send KYC images: {e}")
            return False
    
    async def send_deposit_notification(
        self,
        user_email: str,
        amount: float,
        payment_method: str,
        deposit_id: str
    ) -> bool:
        """Send deposit notification to admin"""
        message = f"""
💰 <b>New Deposit Request</b>

👤 User: {user_email}
💵 Amount: ${amount:.2f}
💳 Method: {payment_method}
🔖 Deposit ID: {deposit_id}

⏰ Time: {asyncio.get_event_loop().time()}
"""
        return await self.send_to_admin(message)
    
    async def send_withdrawal_notification(
        self,
        user_email: str,
        amount: float,
        withdrawal_method: str,
        withdrawal_id: str
    ) -> bool:
        """Send withdrawal notification to admin"""
        message = f"""
💸 <b>New Withdrawal Request</b>

👤 User: {user_email}
💵 Amount: ${amount:.2f}
💳 Method: {withdrawal_method}
🔖 Withdrawal ID: {withdrawal_id}

⏰ Time: {asyncio.get_event_loop().time()}
"""
        return await self.send_to_admin(message)
    
    async def send_new_user_notification(
        self,
        user_email: str,
        username: str,
        registration_method: str = "email"
    ) -> bool:
        """Send new user registration notification to admin"""
        message = f"""
👥 <b>New User Registration</b>

👤 Username: {username}
📧 Email: {user_email}
🔐 Method: {registration_method}

⏰ Time: {asyncio.get_event_loop().time()}
"""
        return await self.send_to_admin(message)
    
    async def send_security_alert(
        self,
        alert_type: str,
        details: str,
        severity: str = "warning"
    ) -> bool:
        """Send security alert to admin"""
        emoji = "⚠️" if severity == "warning" else "🚨"
        message = f"""
{emoji} <b>Security Alert</b>

🔔 Type: {alert_type}
📝 Details: {details}
⚡ Severity: {severity.upper()}

⏰ Time: {asyncio.get_event_loop().time()}
"""
        return await self.send_to_admin(message)
    
    def sync_send_message(self, chat_id: str, message: str) -> bool:
        """Synchronous wrapper for send_message"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.send_message(chat_id, message))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync_send_message: {e}")
            return False
    
    def sync_send_photo(self, chat_id: str, photo_data: bytes, caption: str = None) -> bool:
        """Synchronous wrapper for send_photo"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.send_photo(chat_id, photo_data, caption))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"Error in sync_send_photo: {e}")
            return False

# Global instance
telegram_service = TelegramService()
