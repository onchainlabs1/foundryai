'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { FRIAWizard } from '@/components/fria-wizard'
import { ControlsTable } from '@/components/controls-table'
import { IncidentsTable } from '@/components/incidents-modal'

export default function SystemDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [assessment, setAssessment] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleAssess = async () => {
    setLoading(true)
    try {
      const result = await api.assessSystem(parseInt(params.id))
      setAssessment(result)
    } catch (error) {
      alert('Assessment failed: ' + error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      try {
        await api.uploadEvidence(
          parseInt(params.id),
          file.name,
          file,
          { uploaded_by: 'Current User' }
        )
        alert('Evidence uploaded successfully')
      } catch (error) {
        alert('Upload failed: ' + error)
      }
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'aiact', label: 'AI Act Class' },
    { id: 'fria', label: 'FRIA' },
    { id: 'controls', label: 'Controls' },
    { id: 'evidence', label: 'Evidence' },
    { id: 'reports', label: 'Reports' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI System Details</h1>
        <p className="text-muted-foreground">System ID: {params.id}</p>
      </div>

      <div className="border-b">
        <div className="flex gap-4">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-primary text-primary font-medium'
                  : 'border-transparent hover:border-muted-foreground'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'overview' && (
        <Card>
          <CardHeader>
            <CardTitle>System Overview</CardTitle>
            <CardDescription>Basic information about the AI system</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Detailed system information will be displayed here
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'aiact' && (
        <Card>
          <CardHeader>
            <CardTitle>AI Act Classification</CardTitle>
            <CardDescription>EU AI Act risk assessment</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button onClick={handleAssess} disabled={loading}>
              {loading ? 'Assessing...' : 'Run Assessment'}
            </Button>

            {assessment && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Classification Result</h3>
                  <div className="flex gap-2 items-center">
                    <span className={`px-3 py-1 rounded ${
                      assessment.ai_act_class === 'high' ? 'bg-red-100 text-red-800' :
                      assessment.ai_act_class === 'limited' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {assessment.ai_act_class.toUpperCase()}
                    </span>
                    {assessment.is_gpai && (
                      <span className="px-3 py-1 rounded bg-purple-100 text-purple-800">
                        GPAI
                      </span>
                    )}
                    <span className="px-3 py-1 rounded bg-blue-100 text-blue-800">
                      {assessment.role || 'Provider'}
                    </span>
                  </div>
                </div>

                {assessment.rationale && (
                  <div>
                    <h3 className="font-semibold mb-2">Rationale</h3>
                    <p className="text-sm text-muted-foreground">{assessment.rationale}</p>
                  </div>
                )}

                <div>
                  <h3 className="font-semibold mb-2">ISO 42001 Gaps</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {assessment.gap.map((g: string, i: number) => (
                      <li key={i} className="text-sm">{g}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'fria' && (
        <FRIAWizard systemId={parseInt(params.id)} />
      )}

      {activeTab === 'controls' && (
        <ControlsTable systemId={parseInt(params.id)} />
      )}

      {activeTab === 'evidence' && (
        <Card>
          <CardHeader>
            <CardTitle>Evidence Upload</CardTitle>
            <CardDescription>Upload compliance documentation</CardDescription>
          </CardHeader>
          <CardContent>
            <label className="cursor-pointer">
              <Button>Upload Evidence</Button>
              <input
                type="file"
                className="hidden"
                onChange={handleFileUpload}
              />
            </label>
            <p className="text-sm text-muted-foreground mt-4">
              Files are hashed with SHA256 and stored securely
            </p>
          </CardContent>
        </Card>
      )}

      {activeTab === 'reports' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>System Reports & Exports</CardTitle>
              <CardDescription>Export system documentation</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                <Button 
                  variant="outline"
                  onClick={() => {
                    const apiKey = localStorage.getItem('apiKey')
                    window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002'}/reports/annex-iv.zip?system_id=${params.id}`, '_blank')
                  }}
                >
                  Export Annex IV (.zip)
                </Button>
                <Button 
                  variant="outline"
                  onClick={() => {
                    const apiKey = localStorage.getItem('apiKey')
                    window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002'}/reports/deck.pptx`, '_blank')
                  }}
                >
                  Generate Executive Deck (.pptx)
                </Button>
              </div>
            </CardContent>
          </Card>

          <IncidentsTable systemId={parseInt(params.id)} />
        </div>
      )}
    </div>
  )
}

