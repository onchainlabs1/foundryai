'use client'

import { useState } from 'react'
import { X, Bell, AlertCircle, CheckCircle, Clock, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface Notification {
  id: string
  title: string
  description: string
  type: 'warning' | 'info' | 'success' | 'urgent'
  time: string
  action?: string
  actionUrl?: string
}

interface NotificationsModalProps {
  isOpen: boolean
  onClose: () => void
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'FRIA Completion Required',
    description: 'System "Test System" needs FRIA completion to meet compliance requirements',
    type: 'warning',
    time: '2 hours ago',
    action: 'Complete FRIA',
    actionUrl: '/risk-fria'
  },
  {
    id: '2',
    title: 'Evidence Missing',
    description: 'Control A.5.2 requires evidence documentation for audit readiness',
    type: 'info',
    time: '4 hours ago',
    action: 'Add Evidence',
    actionUrl: '/controls'
  },
  {
    id: '3',
    title: 'EU Database Registration',
    description: 'EU Database registration due in 5 days for high-risk systems',
    type: 'urgent',
    time: '1 day ago',
    action: 'Register Now',
    actionUrl: '/eu-register'
  }
]

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'warning':
      return <AlertCircle className="w-5 h-5 text-yellow-500" />
    case 'info':
      return <Bell className="w-5 h-5 text-blue-500" />
    case 'success':
      return <CheckCircle className="w-5 h-5 text-green-500" />
    case 'urgent':
      return <AlertCircle className="w-5 h-5 text-red-500" />
    default:
      return <Bell className="w-5 h-5 text-gray-500" />
  }
}

const getNotificationBadgeColor = (type: Notification['type']) => {
  switch (type) {
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    case 'info':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'success':
      return 'bg-green-100 text-green-800 border-green-200'
    case 'urgent':
      return 'bg-red-100 text-red-800 border-red-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

export function NotificationsModal({ isOpen, onClose }: NotificationsModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Bell className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Notifications
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {mockNotifications.length} unread items
              </p>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
          {mockNotifications.map((notification) => (
            <Card key={notification.id} className="border-l-4 border-l-blue-500 hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-medium text-gray-900 dark:text-white">
                        {notification.title}
                      </h3>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getNotificationBadgeColor(notification.type)}`}
                      >
                        {notification.type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                      {notification.description}
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                        <Clock className="w-3 h-3" />
                        {notification.time}
                      </div>
                      {notification.action && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-xs"
                          onClick={() => {
                            if (notification.actionUrl) {
                              window.location.href = notification.actionUrl
                            }
                          }}
                        >
                          {notification.action}
                          <ExternalLink className="w-3 h-3 ml-1" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <Button variant="ghost" size="sm">
            Mark all as read
          </Button>
          <Button onClick={onClose} size="sm">
            Close
          </Button>
        </div>
      </div>
    </div>
  )
}
