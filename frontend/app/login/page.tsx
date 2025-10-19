'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { setApiKey } from '@/lib/api'

export default function LoginPage() {
  const [apiKey, setApiKeyInput] = useState('')
  const router = useRouter()

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    if (apiKey) {
      setApiKey(apiKey)
      router.push('/')
    }
  }

  const handleDemoMode = () => {
    // Demo mode removed for security - users must provide their own API key
    alert('Demo mode is not available. Please contact your administrator for an API key.')
  }

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Enter your API key to access AIMS Readiness
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">API Key</label>
              <Input
                type="password"
                placeholder="Enter your API key"
                value={apiKey}
                onChange={(e) => setApiKeyInput(e.target.value)}
                required
              />
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 text-sm text-yellow-800">
              <strong>⚠️ Development Only:</strong> API keys are stored in localStorage. 
              This is not secure for production use. OAuth will be added in future versions.
            </div>
            <Button type="submit" className="w-full">
              Login
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t">
            <div className="text-center mb-3">
              <p className="text-sm text-muted-foreground">Need an API key?</p>
            </div>
            <Button 
              type="button" 
              variant="outline" 
              className="w-full"
              onClick={handleDemoMode}
            >
              📞 Contact Administrator
            </Button>
            <p className="text-xs text-muted-foreground text-center mt-2">
              Contact your system administrator to obtain an API key for access
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

