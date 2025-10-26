import api from './api';

const notificationService = {
  // ===== USER NOTIFICATIONS =====
  
  /**
   * Get current user's notifications
   */
  getMyNotifications: async (params = {}) => {
    const { skip = 0, limit = 50, unread_only = false } = params;
    const response = await api.get('/api/users/notifications/me', {
      params: { skip, limit, unread_only }
    });
    return response.data;
  },
  
  /**
   * Mark a notification as read
   */
  markAsRead: async (notificationId) => {
    const response = await api.patch(`/api/users/notifications/${notificationId}/read`);
    return response.data;
  },
  
  /**
   * Mark all notifications as read
   */
  markAllAsRead: async () => {
    const response = await api.post('/api/users/notifications/mark-all-read');
    return response.data;
  },
  
  /**
   * Delete a notification
   */
  deleteNotification: async (notificationId) => {
    const response = await api.delete(`/api/users/notifications/${notificationId}`);
    return response.data;
  },
  
  // ===== ADMIN NOTIFICATIONS =====
  
  /**
   * Send notification to a specific user (Admin only)
   */
  sendNotificationToUser: async (userId, notificationData, sendTelegram = true) => {
    const response = await api.post(
      `/api/admin/users/${userId}/notify`,
      notificationData,
      { params: { send_telegram: sendTelegram } }
    );
    return response.data;
  },
  
  /**
   * Broadcast notification to multiple users (Admin only)
   */
  broadcastNotification: async (broadcastData) => {
    const response = await api.post('/api/admin/notifications/broadcast', broadcastData);
    return response.data;
  },
  
  /**
   * Get notifications for a specific user (Admin view)
   */
  getUserNotifications: async (userId, params = {}) => {
    const { skip = 0, limit = 50 } = params;
    const response = await api.get(`/api/admin/users/${userId}/notifications`, {
      params: { skip, limit }
    });
    return response.data;
  },
  
  // ===== NOTIFICATION TEMPLATES =====
  
  /**
   * Get all notification templates (Admin only)
   */
  getTemplates: async () => {
    const response = await api.get('/api/admin/notification-templates');
    return response.data;
  },
  
  /**
   * Create a new notification template (Admin only)
   */
  createTemplate: async (templateData) => {
    const response = await api.post('/api/admin/notification-templates', templateData);
    return response.data;
  },
  
  /**
   * Delete a notification template (Admin only)
   */
  deleteTemplate: async (templateId) => {
    const response = await api.delete(`/api/admin/notification-templates/${templateId}`);
    return response.data;
  }
};

export default notificationService;
