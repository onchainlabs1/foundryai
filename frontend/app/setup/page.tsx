'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function SetupPage() {
  const router = useRouter()

  useEffect(() => {
    // Definir a API key no localStorage
    localStorage.setItem('apiKey', 'dev-aims-demo-key')
    
    // Aguardar um pouco e redirecionar
    setTimeout(() => {
      router.push('/')
    }, 2000)
  }, [router])

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="max-w-md mx-auto text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-primary-foreground font-bold text-2xl">A</span>
          </div>
          <h1 className="text-2xl font-bold text-foreground mb-2">
            Configurando AIMS Studio
          </h1>
          <p className="text-muted-foreground">
            Definindo a chave da API e preparando o sistema...
          </p>
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center justify-center space-x-2">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
          
          <div className="bg-muted rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              ✅ API Key configurada<br/>
              ✅ Conectando ao backend<br/>
              ✅ Redirecionando para o dashboard...
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
