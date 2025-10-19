'use client'

import React, { useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Download, 
  ArrowLeft, 
  RefreshCw,
  AlertCircle
} from 'lucide-react'
import { api } from '@/lib/api'

export default function DocumentPreviewPage() {
  const searchParams = useSearchParams()
  const systemId = searchParams.get('systemId')
  const docType = searchParams.get('docType')
  
  const [content, setContent] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (systemId && docType) {
      loadDocumentPreview()
    }
  }, [systemId, docType])

  const loadDocumentPreview = async () => {
    if (!systemId || !docType) return

    try {
      setLoading(true)
      setError(null)
      
      const response = await api.previewDocument(parseInt(systemId), docType)
      setContent(response)
    } catch (err) {
      setError('Failed to load document preview')
      console.error('Error loading preview:', err)
    } finally {
      setLoading(false)
    }
  }

  const downloadDocument = async (format: 'markdown' | 'pdf') => {
    if (!systemId || !docType) return

    try {
      const blob = await api.downloadDocument(parseInt(systemId), docType, format)
      
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

  const goBack = () => {
    window.close()
  }

  if (!systemId || !docType) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
              <h2 className="text-xl font-semibold mb-2">Invalid Parameters</h2>
              <p className="text-gray-600 mb-4">
                System ID and document type are required to preview documents.
              </p>
              <Button onClick={goBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go Back
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={goBack}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-semibold">
                  {docType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                </h1>
                <p className="text-sm text-gray-600">System ID: {systemId}</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                onClick={() => downloadDocument('markdown')}
                disabled={loading}
              >
                <Download className="h-4 w-4 mr-2" />
                Download MD
              </Button>
              <Button
                variant="outline"
                onClick={() => downloadDocument('pdf')}
                disabled={loading}
              >
                <Download className="h-4 w-4 mr-2" />
                Download PDF
              </Button>
              <Button
                variant="outline"
                onClick={loadDocumentPreview}
                disabled={loading}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto p-6">
        {error && (
          <Card className="border-red-200 bg-red-50 mb-6">
            <CardContent className="pt-6">
              <div className="flex items-center text-red-600">
                <AlertCircle className="h-5 w-5 mr-2" />
                {error}
              </div>
            </CardContent>
          </Card>
        )}

        {loading ? (
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-center h-64">
                <RefreshCw className="h-8 w-8 animate-spin mr-2" />
                <span>Loading document preview...</span>
              </div>
            </CardContent>
          </Card>
        ) : content ? (
          <Card>
            <CardContent className="pt-6">
              <div 
                className="prose prose-lg max-w-none"
                dangerouslySetInnerHTML={{ __html: content }}
              />
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-12">
                <AlertCircle className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">No content available</h3>
                <p className="text-gray-600">
                  The document preview could not be loaded.
                </p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
