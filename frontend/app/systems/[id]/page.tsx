'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api, downloadFile } from '@/lib/api'
import { FRIAWizard } from '@/components/fria-wizard'
import { ControlsTable } from '@/components/controls-table'
import { IncidentsTable } from '@/components/incidents-modal'

export default function SystemDetailPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = useState('overview')
  const [assessment, setAssessment] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [system, setSystem] = useState<any>(null)
  const [systemLoading, setSystemLoading] = useState(true)

  useEffect(() => {
    const fetchSystem = async () => {
      try {
        const systemData = await api.getSystem(parseInt(params.id))
        setSystem(systemData)
      } catch (error) {
        console.error('Failed to fetch system:', error)
      } finally {
        setSystemLoading(false)
      }
    }
    fetchSystem()
  }, [params.id])

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
            {systemLoading ? (
              <div className="space-y-4">
                <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
              </div>
            ) : system ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">System Name</h3>
                      <p className="text-lg font-medium">{system.name || 'N/A'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Purpose</h3>
                      <p className="text-sm">{system.purpose || 'N/A'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Domain</h3>
                      <p className="text-sm">{system.domain || 'N/A'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Lifecycle Stage</h3>
                      <p className="text-sm">{system.lifecycle_stage || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">AI Act Classification</h3>
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                        system.ai_act_class === 'high' ? 'bg-red-100 text-red-800' :
                        system.ai_act_class === 'limited' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {system.ai_act_class?.toUpperCase() || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Deployment Context</h3>
                      <p className="text-sm">{system.deployment_context || 'N/A'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">System Owner</h3>
                      <p className="text-sm">{system.owner_email || 'N/A'}</p>
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide">Risk Category</h3>
                      <p className="text-sm">{system.risk_category || 'N/A'}</p>
                    </div>
                  </div>
                </div>
                
                <div className="border-t pt-6">
                  <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide mb-4">System Characteristics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${
                        system.uses_biometrics ? 'bg-red-500' : 'bg-gray-300'
                      }`}></span>
                      <span className="text-sm">Uses Biometrics</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${
                        system.is_general_purpose_ai ? 'bg-purple-500' : 'bg-gray-300'
                      }`}></span>
                      <span className="text-sm">General Purpose AI</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${
                        system.impacts_fundamental_rights ? 'bg-orange-500' : 'bg-gray-300'
                      }`}></span>
                      <span className="text-sm">Impacts Rights</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`w-3 h-3 rounded-full ${
                        system.personal_data_processed ? 'bg-blue-500' : 'bg-gray-300'
                      }`}></span>
                      <span className="text-sm">Personal Data</span>
                    </div>
                  </div>
                </div>

                {system.notes && (
                  <div className="border-t pt-6">
                    <h3 className="font-semibold text-sm text-gray-500 uppercase tracking-wide mb-2">Notes</h3>
                    <p className="text-sm text-gray-700">{system.notes}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">Failed to load system data</p>
              </div>
            )}
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
                  onClick={async () => {
                    try {
                      await downloadFile(`/reports/annex-iv.zip?system_id=${params.id}`, 'annex-iv.zip');
                    } catch (error) {
                      console.error('Download failed:', error);
                      alert('Download failed. Please check your API key.');
                    }
                  }}
                >
                  Export Annex IV (.zip)
                </Button>
                <Button 
                  variant="outline"
                  onClick={async () => {
                    try {
                      await downloadFile('/reports/deck.pptx', 'executive-deck.pptx');
                    } catch (error) {
                      console.error('Download failed:', error);
                      alert('Download failed. Please check your API key.');
                    }
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

