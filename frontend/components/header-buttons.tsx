'use client'

import { useState } from 'react'
import { Plus, Bell, Globe, User } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import { NotificationsModal } from '@/components/notifications-modal'
import { LanguageModal } from '@/components/language-modal'
import { ProfileModal } from '@/components/profile-modal'

export function HeaderButtons() {
  const [showNotifications, setShowNotifications] = useState(false)
  const [showLanguage, setShowLanguage] = useState(false)
  const [showProfile, setShowProfile] = useState(false)

  const handleNewSystem = () => {
    window.location.href = '/onboarding'
  }

  const handleNotifications = () => {
    setShowNotifications(true)
  }

  const handleLanguage = () => {
    setShowLanguage(true)
  }

  const handleProfile = () => {
    setShowProfile(true)
  }

  const handleUpdate = () => {
    console.log('🔄 Updating dashboard data...')
    window.location.reload()
  }

  return (
    <div className="flex items-center gap-4">
      <button 
        className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90"
        onClick={handleNewSystem}
      >
        <Plus className="w-4 h-4" />
        New System
      </button>
      <button 
        className="relative p-2 text-muted-foreground hover:text-foreground"
        onClick={handleNotifications}
      >
        <Bell className="w-5 h-5" />
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full text-xs text-destructive-foreground flex items-center justify-center">3</span>
      </button>
      <button 
        className="p-2 text-muted-foreground hover:text-foreground"
        onClick={handleLanguage}
      >
        <Globe className="w-5 h-5" />
      </button>
      <button 
        className="p-2 text-muted-foreground hover:text-foreground"
        onClick={handleProfile}
      >
        <User className="w-5 h-5" />
      </button>
      <button 
        className="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600"
        onClick={handleUpdate}
      >
        Update
      </button>
      <ThemeToggle />
      
      {/* Modals */}
      <NotificationsModal 
        isOpen={showNotifications}
        onClose={() => setShowNotifications(false)}
      />
      <LanguageModal 
        isOpen={showLanguage}
        onClose={() => setShowLanguage(false)}
      />
      <ProfileModal 
        isOpen={showProfile}
        onClose={() => setShowProfile(false)}
      />
    </div>
  )
}
