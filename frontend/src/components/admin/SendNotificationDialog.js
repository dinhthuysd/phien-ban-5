import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { useToast } from '../../hooks/use-toast';
import notificationService from '../../services/notificationService';
import { Bell, Send, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';

const SendNotificationDialog = ({ isOpen, onClose, userId, userEmail }) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [sendTelegram, setSendTelegram] = useState(true);
  
  const [formData, setFormData] = useState({
    type: 'info',
    title: '',
    message: ''
  });

  useEffect(() => {
    if (isOpen) {
      fetchTemplates();
    }
  }, [isOpen]);

  const fetchTemplates = async () => {
    try {
      const data = await notificationService.getTemplates();
      setTemplates(data.templates || []);
    } catch (error) {
      console.error('Failed to fetch templates:', error);
    }
  };

  const handleTemplateSelect = (templateId) => {
    setSelectedTemplate(templateId);
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setFormData({
        type: template.type,
        title: template.title,
        message: template.message
      });
    }
  };

  const handleSubmit = async () => {
    if (!formData.title || !formData.message) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    try {
      setLoading(true);
      await notificationService.sendNotificationToUser(
        userId,
        formData,
        sendTelegram
      );
      
      toast({
        title: 'Success',
        description: 'Notification sent successfully',
        icon: <CheckCircle className="w-5 h-5" />
      });
      
      onClose();
      
      // Reset form
      setFormData({ type: 'info', title: '', message: '' });
      setSelectedTemplate('');
    } catch (error) {
      console.error('Notification error:', error);
      let errorMessage = 'Failed to send notification';
      
      // Handle validation errors properly
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // If detail is an array of errors, extract messages
        if (Array.isArray(detail)) {
          errorMessage = detail.map(err => err.msg || JSON.stringify(err)).join('; ');
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail);
        }
      }
      
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Send className="w-5 h-5" />
            Send Notification
          </DialogTitle>
          <DialogDescription>
            Send a notification to {userEmail}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Template Selection */}
          <div className="space-y-2">
            <Label>Select Template (Optional)</Label>
            <Select value={selectedTemplate} onValueChange={handleTemplateSelect}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a template..." />
              </SelectTrigger>
              <SelectContent>
                {templates.map((template) => (
                  <SelectItem key={template.id} value={template.id}>
                    <div className="flex items-center gap-2">
                      {getTypeIcon(template.type)}
                      {template.name}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Notification Type */}
          <div className="space-y-2">
            <Label>Notification Type *</Label>
            <Select 
              value={formData.type} 
              onValueChange={(value) => setFormData({ ...formData, type: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="info">
                  <div className="flex items-center gap-2">
                    <Info className="w-4 h-4 text-blue-500" />
                    Information
                  </div>
                </SelectItem>
                <SelectItem value="success">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500" />
                    Success
                  </div>
                </SelectItem>
                <SelectItem value="warning">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                    Warning
                  </div>
                </SelectItem>
                <SelectItem value="error">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-500" />
                    Error
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Title */}
          <div className="space-y-2">
            <Label>Title *</Label>
            <Input
              placeholder="Notification title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            />
          </div>

          {/* Message */}
          <div className="space-y-2">
            <Label>Message *</Label>
            <Textarea
              placeholder="Notification message"
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              rows={5}
            />
          </div>

          {/* Send to Telegram */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <Bell className="w-4 h-4 text-blue-500" />
              <div>
                <Label className="text-sm font-medium">Send to Telegram</Label>
                <p className="text-xs text-gray-500">Also notify admin via Telegram bot</p>
              </div>
            </div>
            <Switch
              checked={sendTelegram}
              onCheckedChange={setSendTelegram}
            />
          </div>

          {/* Preview */}
          <div className="p-4 border rounded-lg bg-gray-50">
            <Label className="text-xs text-gray-500 uppercase mb-2 block">Preview</Label>
            <div className={`p-3 rounded border ${
              formData.type === 'success' ? 'bg-green-50 border-green-200' :
              formData.type === 'warning' ? 'bg-yellow-50 border-yellow-200' :
              formData.type === 'error' ? 'bg-red-50 border-red-200' :
              'bg-blue-50 border-blue-200'
            }`}>
              <div className="flex gap-2">
                {getTypeIcon(formData.type)}
                <div>
                  <h4 className="font-semibold text-sm">
                    {formData.title || 'Notification Title'}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {formData.message || 'Notification message will appear here...'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Sending...' : 'Send Notification'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default SendNotificationDialog;
