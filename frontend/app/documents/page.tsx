'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  FileText, 
  Download, 
  Eye, 
  Plus, 
  RefreshCw,
  CheckCircle,
  Clock,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Database,
  Shield,
  Bot,
  Target,
  FileCode,
  BookOpen,
  Settings,
  Zap
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { api } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import { Skeleton } from '@/components/ui/skeleton'

interface Document {
  type: string
  name: string
  markdown_path: string
  pdf_path: string
  markdown_size: number
  pdf_size: number
  created_at: string
  updated_at: string
}

interface System {
  id: number
  name: string
  purpose: string
  domain: string
  ai_act_class: string
}

export default function DocumentsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [systems, setSystems] = useState<System[]>([])
  const [selectedSystem, setSelectedSystem] = useState<number | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSystems()
  }, [])

  useEffect(() => {
    if (selectedSystem) {
      loadDocuments(selectedSystem)
    }
  }, [selectedSystem])

  const loadSystems = async () => {
    try {
      setLoading(true)
      const response = await api.getSystems()
      setSystems(response)
      if (response.length > 0) {
        setSelectedSystem(response[0].id)
      }
    } catch (err) {
      setError('Failed to load systems')
      console.error('Error loading systems:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async (systemId: number) => {
    try {
      setLoading(true)
      const response = await api.getSystemDocuments(systemId)
      setDocuments(response.documents || [])
    } catch (err) {
      setError('Failed to load documents')
      console.error('Error loading documents:', err)
    } finally {
      setLoading(false)
    }
  }

  const generateDocuments = async (systemId: number) => {
    try {
      setGenerating(true)
      setError(null)

      // Backend already handles defaults when onboarding data is missing,
      // so we call generation directly and surface precise backend errors.
      const response = await api.generateSystemDocuments(systemId)

      if (response.status === 'success' || response.status === 'success_with_warnings') {
        setError(null)
        await loadDocuments(systemId)
        const desc = response.status === 'success_with_warnings' && response.warnings?.length
          ? response.warnings.join(' ')
          : 'Your compliance documents are ready.'
        toast({ title: 'Documents generated', description: desc })
      }
    } catch (err: any) {
      const message = err?.message || 'Failed to generate documents'
      setError(message)
      toast({ title: 'Failed to generate documents', description: message, variant: 'destructive' })
      console.error('Error generating documents:', err)
    } finally {
      setGenerating(false)
    }
  }

  const downloadDocument = async (systemId: number, docType: string, format: 'markdown' | 'pdf') => {
    try {
      const blob = await api.downloadDocument(systemId, docType, format)
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${docType}.${format === 'pdf' ? 'pdf' : 'md'}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download document')
      console.error('Error downloading document:', err)
    }
  }

  const previewDocument = (systemId: number, docType: string) => {
    const url = `/documents/preview?systemId=${systemId}&docType=${docType}`
    window.open(url, '_blank')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getDocumentIcon = (docType: string) => {
    const iconMap: { [key: string]: string } = {
      'risk_assessment': '🛡️',
      'impact_assessment': '📊',
      'model_card': '🤖',
      'data_sheet': '📋',
      'logging_plan': '📝',
      'monitoring_report': '📈',
      'human_oversight': '👥',
      'appeals_flow': '⚖️',
      'soa': '📄',
      'policy_register': '📚',
      'audit_log': '🔍'
    }
    return iconMap[docType] || '📄'
  }

  if (loading && systems.length === 0) {
    return (
      <div className="space-y-8">
        {/* Header Skeleton */}
        <div className="text-center space-y-4">
          <Skeleton className="h-16 w-96 mx-auto" />
          <Skeleton className="h-6 w-80 mx-auto" />
        </div>

        {/* Systems Skeleton */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-5xl font-bold gradient-text">
            Compliance Documents
          </h1>
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Generate and manage ISO/IEC 42001 and EU AI Act compliance documents for your AI systems.
        </p>
        <div className="flex items-center justify-center gap-4 mt-6">
          <Button
            onClick={() => router.push('/onboarding')}
            variant="default"
            size="lg"
            className="gap-2"
          >
            <Plus className="h-4 w-4" />
            Create New System
          </Button>
          <Button
            onClick={() => router.push('/templates')}
            variant="outline"
            size="lg"
            className="gap-2"
          >
            <BookOpen className="h-4 w-4" />
            View Templates
          </Button>
        </div>
      </motion.div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="border-destructive/50 bg-destructive/10">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center text-destructive">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span>{error}</span>
                </div>
                {error.includes('No onboarding data') && (
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => window.location.href = '/onboarding'}
                    className="ml-4"
                  >
                    Go to Onboarding
                  </Button>
                )}
                {error.toLowerCase().includes('fria') && selectedSystem && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.location.href = `/systems/${selectedSystem}?tab=risk-fria`}
                    className="ml-2"
                  >
                    Complete FRIA
                  </Button>
                )}
                {error.toLowerCase().includes('api key') && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.location.reload()}
                    className="ml-2"
                  >
                    Refresh Session
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* System Selection */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <Card className="overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-primary/20">
                <Database className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-xl">Select AI System</CardTitle>
                <CardDescription>Choose a system to view and manage its compliance documents</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {systems.map((system) => (
                <motion.div
                  key={system.id}
                  whileHover={{ y: -4, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    className={`cursor-pointer transition-all duration-300 ${
                      selectedSystem === system.id
                        ? 'ring-2 ring-primary/50'
                        : 'hover:shadow-xl hover:shadow-primary/10'
                    }`}
                    onClick={() => setSelectedSystem(system.id)}
                  >
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-xl bg-primary/20">
                            <Bot className="h-5 w-5 text-primary" />
                          </div>
                          <h3 className="font-bold text-lg">{system.name}</h3>
                        </div>
                        <Badge 
                          variant={
                            system.ai_act_class === 'high' ? 'destructive' :
                            system.ai_act_class === 'limited' ? 'secondary' :
                            'default'
                          }
                        >
                          {system.ai_act_class || 'Not classified'}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{system.purpose}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Settings className="h-3 w-3" />
                        <span>Domain: {system.domain}</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Document Management */}
      {selectedSystem && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Card className="overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-emerald-500/20">
                    <FileText className="h-6 w-6 text-emerald-600" />
                  </div>
                  <div>
                    <CardTitle className="text-xl">Generated Documents</CardTitle>
                    <CardDescription>
                      {systems.find(s => s.id === selectedSystem)?.name} • 
                      {documents.length} documents available
                    </CardDescription>
                  </div>
                </div>
                <Button
                  onClick={() => generateDocuments(selectedSystem)}
                  disabled={generating}
                  variant="default"
                  size="lg"
                  className="gap-2"
                >
                  {generating ? (
                    <>
                      <RefreshCw className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4" />
                      Generate Documents
                    </>
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {generating && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mb-6 p-4 rounded-xl bg-primary/10 border border-primary/20"
                >
                  <div className="flex items-center mb-3">
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin text-primary" />
                    <span className="text-sm font-semibold">Generating compliance documents...</span>
                  </div>
                  <Progress value={33} className="w-full" />
                </motion.div>
              )}

              {documents.length === 0 ? (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-center py-12"
                >
                  <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-muted/50 flex items-center justify-center">
                    <FileText className="h-12 w-12 text-muted-foreground" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">No documents generated</h3>
                  <p className="text-muted-foreground mb-6">
                    Generate compliance documents for this system to get started with your AI governance.
                  </p>
                  <Button 
                    onClick={() => generateDocuments(selectedSystem)}
                    variant="default"
                    size="lg"
                    className="gap-2"
                  >
                    <Zap className="h-4 w-4" />
                    Generate Documents
                  </Button>
                </motion.div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {documents.map((doc, index) => (
                    <motion.div
                      key={doc.type}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      whileHover={{ y: -4, scale: 1.02 }}
                    >
                      <Card className="h-full overflow-hidden group">
                        <CardContent className="pt-6">
                          <div className="flex items-center mb-4">
                            <div className="p-3 rounded-xl bg-primary/20 mr-3">
                              <span className="text-2xl">{getDocumentIcon(doc.type)}</span>
                            </div>
                            <div className="flex-1">
                              <h3 className="font-bold text-lg">{doc.name}</h3>
                              <p className="text-xs text-muted-foreground font-medium">{doc.type}</p>
                            </div>
                          </div>
                          
                          <div className="space-y-3 mb-6">
                            <div className="flex justify-between items-center text-sm">
                              <span className="text-muted-foreground">Markdown:</span>
                              <Badge variant="secondary" className="text-xs">
                                {formatFileSize(doc.markdown_size)}
                              </Badge>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                              <span className="text-muted-foreground">PDF:</span>
                              <Badge variant="secondary" className="text-xs">
                                {formatFileSize(doc.pdf_size)}
                              </Badge>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                              <span className="text-muted-foreground">Updated:</span>
                              <span className="text-xs font-medium">{formatDate(doc.updated_at)}</span>
                            </div>
                          </div>

                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => previewDocument(selectedSystem, doc.type)}
                              className="flex-1 gap-2"
                            >
                              <Eye className="h-3 w-3" />
                              Preview
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => downloadDocument(selectedSystem, doc.type, 'markdown')}
                              className="flex-1 gap-2"
                            >
                              <Download className="h-3 w-3" />
                              MD
                            </Button>
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => downloadDocument(selectedSystem, doc.type, 'pdf')}
                              className="flex-1 gap-2"
                            >
                              <Download className="h-3 w-3" />
                              PDF
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
