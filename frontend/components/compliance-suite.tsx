'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

interface ComplianceDocument {
  type: string
  coverage: number
  sections: Array<{
    key: string
    coverage: number
    paragraphs: Array<{
      text: string
      citations: Array<{
        evidence_id: number
        page: number
        checksum: string
      }>
    }>
  }>
  missing: string[]
}

interface ComplianceDraftResponse {
  docs: ComplianceDocument[]
}

const DOCUMENT_TYPES = [
  { key: 'annex_iv', name: 'Annex IV', description: 'Technical Documentation' },
  { key: 'fria', name: 'FRIA', description: 'Fundamental Rights Impact Assessment' },
  { key: 'pmm', name: 'PMM', description: 'Post-Market Monitoring Report' },
  { key: 'soa', name: 'SoA', description: 'Statement of Applicability' },
  { key: 'risk_register', name: 'Risk Register', description: 'AI Risk Register & CAPA' }
]

export default function ComplianceSuite() {
  const [drafts, setDrafts] = useState<ComplianceDocument[]>([])
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState<string | null>(null)
  const [exporting, setExporting] = useState<string | null>(null)

  const generateDraft = async (docType: string) => {
    setGenerating(docType)
    try {
      const response = await api.generateComplianceDraft(undefined, [docType])
      setDrafts(prev => {
        const filtered = prev.filter(d => d.type !== docType)
        return [...filtered, ...response.docs]
      })
    } catch (error) {
      console.error(`Failed to generate ${docType} draft:`, error)
    } finally {
      setGenerating(null)
    }
  }

  const exportDocument = async (docType: string, format: 'md' | 'docx' | 'pdf') => {
    setExporting(`${docType}-${format}`)
    try {
      const response = await api.exportDocument(docType, format)
      
      // Create download link
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${docType}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error(`Failed to export ${docType} as ${format}:`, error)
    } finally {
      setExporting(null)
    }
  }

  const getDocumentDraft = (docType: string): ComplianceDocument | undefined => {
    return drafts.find(d => d.type === docType)
  }

  const makeCitationClickable = (text: string, citations: any[]) => {
    if (!citations || citations.length === 0) return text

    let result = text
    citations.forEach((citation, index) => {
      const citationText = `[${citation.evidence_id}:${citation.page}]`
      const citationUrl = `/viewer?evidence_id=${citation.evidence_id}&page=${citation.page}`
      const replacement = `<a href="${citationUrl}" target="_blank" class="text-blue-600 hover:underline font-medium">${citationText}</a>`
      result = result.replace(citationText, replacement)
    })
    return result
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Compliance Suite</h2>
        <p className="text-muted-foreground">
          Generate and export compliance documentation with evidence citations
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {DOCUMENT_TYPES.map((doc) => {
          const draft = getDocumentDraft(doc.key)
          const coverage = draft ? draft.coverage : 0
          const missingCount = draft ? draft.missing.length : 0

          return (
            <Card key={doc.key} className="relative">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">{doc.name}</CardTitle>
                    <CardDescription>{doc.description}</CardDescription>
                  </div>
                  {draft && (
                    <Badge 
                      variant={coverage > 0.8 ? "default" : coverage > 0.5 ? "secondary" : "destructive"}
                    >
                      {Math.round(coverage * 100)}% covered
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Coverage Bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Coverage</span>
                    <span>{Math.round(coverage * 100)}%</span>
                  </div>
                  <Progress value={coverage * 100} className="h-2" />
                </div>

                {/* Missing Items */}
                {missingCount > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-red-600">
                      Missing: {missingCount} items
                    </p>
                    {draft && draft.missing.length > 0 && (
                      <div className="text-xs text-muted-foreground max-h-20 overflow-y-auto">
                        {draft.missing.slice(0, 3).map((item, idx) => (
                          <div key={idx}>• {item}</div>
                        ))}
                        {draft.missing.length > 3 && (
                          <div>... and {draft.missing.length - 3} more</div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="space-y-2">
                  <Button
                    onClick={() => generateDraft(doc.key)}
                    disabled={generating === doc.key}
                    className="w-full"
                    size="sm"
                  >
                    {generating === doc.key ? 'Generating...' : 'Generate Draft'}
                  </Button>

                  {draft && (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportDocument(doc.key, 'md')}
                        disabled={exporting === `${doc.key}-md`}
                        className="flex-1"
                      >
                        {exporting === `${doc.key}-md` ? '...' : 'MD'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportDocument(doc.key, 'docx')}
                        disabled={exporting === `${doc.key}-docx`}
                        className="flex-1"
                      >
                        {exporting === `${doc.key}-docx` ? '...' : 'DOCX'}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportDocument(doc.key, 'pdf')}
                        disabled={exporting === `${doc.key}-pdf`}
                        className="flex-1"
                      >
                        {exporting === `${doc.key}-pdf` ? '...' : 'PDF'}
                      </Button>
                    </div>
                  )}

                  {/* FRIA Special CTA */}
                  {doc.key === 'fria' && missingCount > 0 && (
                    <Button
                      variant="secondary"
                      size="sm"
                      className="w-full"
                      onClick={() => {
                        // Navigate to evidence tab with filter
                        window.location.href = '/systems/1?tab=evidence&filter=fria'
                      }}
                    >
                      Add Missing Evidence →
                    </Button>
                  )}
                </div>

                {/* Draft Preview */}
                {draft && draft.sections.length > 0 && (
                  <div className="mt-4 p-3 bg-gray-50 rounded text-xs max-h-32 overflow-y-auto">
                    <p className="font-medium mb-2">Preview:</p>
                    {draft.sections.slice(0, 2).map((section, idx) => (
                      <div key={idx} className="mb-2">
                        <p className="font-medium">{section.key}</p>
                        {section.paragraphs.slice(0, 1).map((para, pIdx) => (
                          <p 
                            key={pIdx}
                            dangerouslySetInnerHTML={{ 
                              __html: makeCitationClickable(para.text, para.citations) 
                            }}
                          />
                        ))}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Feature Flag Notice */}
      {process.env.NEXT_PUBLIC_FEATURE_LLM_REFINE === 'true' && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>LLM Refinement:</strong> Document refinement features are enabled. 
            Use the &quot;Refine wording&quot; option in document previews to improve content.
          </p>
        </div>
      )}
    </div>
  )
}