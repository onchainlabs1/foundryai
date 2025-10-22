'use client'

import { useState } from 'react'
import { X, Globe, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface Language {
  code: string
  name: string
  nativeName: string
  flag: string
}

interface LanguageModalProps {
  isOpen: boolean
  onClose: () => void
}

const languages: Language[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português', flag: '🇵🇹' },
  { code: 'es', name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'fr', name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' }
]

export function LanguageModal({ isOpen, onClose }: LanguageModalProps) {
  const [selectedLanguage, setSelectedLanguage] = useState('en')

  if (!isOpen) return null

  const handleLanguageSelect = (code: string) => {
    setSelectedLanguage(code)
    // Here you would typically update the app's language
    console.log(`Language changed to: ${code}`)
  }

  const handleApply = () => {
    // Apply language change
    console.log(`Applying language: ${selectedLanguage}`)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Globe className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Language Settings
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Choose your preferred language
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
        <div className="p-6">
          <div className="space-y-3">
            {languages.map((language) => (
              <Card 
                key={language.code}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedLanguage === language.code 
                    ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                    : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
                onClick={() => handleLanguageSelect(language.code)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{language.flag}</span>
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white">
                          {language.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {language.nativeName}
                        </p>
                      </div>
                    </div>
                    {selectedLanguage === language.code && (
                      <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                        <Check className="w-5 h-5" />
                        <span className="text-sm font-medium">Selected</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleApply} className="gap-2">
            <Globe className="w-4 h-4" />
            Apply Language
          </Button>
        </div>
      </div>
    </div>
  )
}
