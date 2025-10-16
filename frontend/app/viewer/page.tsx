'use client'

import { useEffect, useState, useRef } from 'react'
import { useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function PDFViewerPage() {
  const searchParams = useSearchParams()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [pdfDoc, setPdfDoc] = useState<any>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [evidenceInfo, setEvidenceInfo] = useState<any>(null)
  
  const evidenceId = searchParams.get('evidence_id')
  const targetPage = parseInt(searchParams.get('page') || '1')

  useEffect(() => {
    if (!evidenceId) {
      setError('Evidence ID is required')
      setLoading(false)
      return
    }

    // Load evidence info
    fetch(`/api/evidence/${evidenceId}`)
      .then(res => res.json())
      .then(data => setEvidenceInfo(data))
      .catch(err => console.error('Failed to load evidence info:', err))

    // Load PDF.js dynamically (TODO: install pdfjs-dist)
    // For now, use mock data
    try {
      // Mock PDF document
      setPdfDoc({ numPages: 10 })
      setTotalPages(10)
      setCurrentPage(targetPage)
      setLoading(false)
    } catch (err) {
      console.error('Failed to load PDF:', err)
      setError('Failed to load PDF document')
      setLoading(false)
    }
  }, [evidenceId, targetPage])

  const renderPage = async (pageNum: number) => {
    if (!pdfDoc || !canvasRef.current) return

    // Mock page rendering - in real implementation, you would:
    // const page = await pdfDoc.getPage(pageNum)
    // const viewport = page.getViewport({ scale: 1.5 })
    // const canvas = canvasRef.current
    // const context = canvas.getContext('2d')
    // canvas.height = viewport.height
    // canvas.width = viewport.width
    // await page.render({ canvasContext: context, viewport }).promise

    // For demo purposes, draw a mock page
    const canvas = canvasRef.current
    const context = canvas.getContext('2d')
    if (context) {
      context.fillStyle = '#ffffff'
      context.fillRect(0, 0, canvas.width, canvas.height)
      context.fillStyle = '#000000'
      context.font = '16px Arial'
      context.fillText(`Evidence ID: ${evidenceId}`, 50, 50)
      context.fillText(`Page ${pageNum} of ${totalPages}`, 50, 80)
      context.fillText('This is a mock PDF viewer for demonstration.', 50, 120)
      context.fillText('In production, this would display the actual PDF content.', 50, 150)
    }
  }

  useEffect(() => {
    if (pdfDoc && currentPage) {
      renderPage(currentPage)
    }
  }, [pdfDoc, currentPage])

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="flex items-center justify-center h-96">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
              <p>Loading PDF document...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="flex items-center justify-center h-96">
            <div className="text-center text-red-600">
              <p className="text-lg font-semibold mb-2">Error</p>
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                PDF Evidence Viewer
                {evidenceInfo && (
                  <Badge variant="secondary">{evidenceInfo.label}</Badge>
                )}
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Evidence ID: {evidenceId} | Page {currentPage} of {totalPages}
              </p>
            </div>
            <Button 
              variant="outline" 
              onClick={() => window.close()}
            >
              Close
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Page Navigation */}
            <div className="flex items-center justify-center gap-4">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                Previous
              </Button>
              <span className="text-sm">
                Page {currentPage} of {totalPages}
              </span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage >= totalPages}
              >
                Next
              </Button>
            </div>

            {/* PDF Canvas */}
            <div className="border rounded-lg overflow-hidden bg-gray-50">
              <canvas 
                ref={canvasRef}
                className="max-w-full h-auto mx-auto block"
                width={800}
                height={600}
              />
            </div>

            {/* Citation Info */}
            {evidenceInfo && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">Evidence Details</h4>
                <div className="text-sm text-blue-800 space-y-1">
                  <p><strong>Label:</strong> {evidenceInfo.label}</p>
                  <p><strong>ISO 42001 Clause:</strong> {evidenceInfo.iso42001_clause || 'N/A'}</p>
                  <p><strong>Control Name:</strong> {evidenceInfo.control_name || 'N/A'}</p>
                  <p><strong>Uploaded:</strong> {new Date(evidenceInfo.created_at).toLocaleDateString()}</p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}