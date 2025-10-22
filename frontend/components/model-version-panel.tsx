'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Package, CheckCircle } from 'lucide-react'
import { api } from '@/lib/api'

interface ModelVersion {
  id: number
  version: string
  released_at: string
  approver_email: string
  notes?: string
  artifact_hash?: string
}

interface ModelVersionPanelProps {
  systemId: number
}

export function ModelVersionPanel({ systemId }: ModelVersionPanelProps) {
  const [versions, setVersions] = useState<ModelVersion[]>([])
  const [latestVersion, setLatestVersion] = useState<ModelVersion | null>(null)
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [showForm, setShowForm] = useState(false)
  
  // Form fields
  const [version, setVersion] = useState('')
  const [approverEmail, setApproverEmail] = useState('')
  const [notes, setNotes] = useState('')
  const [artifactHash, setArtifactHash] = useState('')

  useEffect(() => {
    loadVersions()
  }, [systemId])

  const loadVersions = async () => {
    try {
      const [versionsList, latest] = await Promise.all([
        api.listModelVersions(systemId),
        api.getLatestModelVersion(systemId)
      ])
      setVersions(versionsList)
      setLatestVersion(latest)
    } catch (error) {
      console.error('Failed to load versions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!version || !approverEmail) {
      alert('Version and approver email are required')
      return
    }

    // Basic version format validation
    if (!/^\d+\.\d+(\.\d+)?$/.test(version)) {
      alert('Version must be in format: 1.0 or 1.0.0')
      return
    }

    // Email validation
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(approverEmail)) {
      alert('Please enter a valid email address')
      return
    }

    setCreating(true)
    try {
      await api.createModelVersion(
        systemId,
        version,
        approverEmail,
        notes || undefined,
        artifactHash || undefined
      )
      
      // Reset form
      setVersion('')
      setApproverEmail('')
      setNotes('')
      setArtifactHash('')
      setShowForm(false)
      
      // Reload versions
      await loadVersions()
      
      alert(`✅ Model version ${version} created successfully!`)
    } catch (error: any) {
      alert('Failed to create version: ' + (error.message || error))
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return <div className="text-sm text-gray-500">Loading model versions...</div>
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Model Versions
            </CardTitle>
            <CardDescription>Track model releases and approvals</CardDescription>
          </div>
          <Button
            onClick={() => setShowForm(!showForm)}
            variant={showForm ? "outline" : "default"}
          >
            {showForm ? 'Cancel' : '+ Create Version'}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Latest Version Display */}
        {latestVersion && latestVersion.version && (
          <div className="p-4 border rounded bg-blue-50 border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="h-5 w-5 text-blue-600" />
              <span className="font-medium text-blue-900">Current Version</span>
            </div>
            <div className="text-sm text-blue-800 space-y-1">
              <p><strong>Version:</strong> {latestVersion.version}</p>
              <p><strong>Approved by:</strong> {latestVersion.approver_email}</p>
              <p><strong>Released:</strong> {new Date(latestVersion.released_at).toLocaleDateString()}</p>
              {latestVersion.artifact_hash && (
                <p><strong>Artifact Hash:</strong> {latestVersion.artifact_hash.substring(0, 16)}...</p>
              )}
            </div>
          </div>
        )}

        {!latestVersion?.version && (
          <div className="p-4 border rounded bg-gray-50">
            <p className="text-sm text-gray-600">No versions created yet. Create your first model version to start tracking releases.</p>
          </div>
        )}

        {/* Create Form */}
        {showForm && (
          <div className="p-4 border rounded space-y-3 bg-gray-50">
            <h4 className="font-medium">Create New Version</h4>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Version <span className="text-red-500">*</span>
              </label>
              <Input
                type="text"
                placeholder="e.g., 1.0.0 or 2.1.3"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">Format: major.minor or major.minor.patch</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Approver Email <span className="text-red-500">*</span>
              </label>
              <Input
                type="email"
                placeholder="approver@company.com"
                value={approverEmail}
                onChange={(e) => setApproverEmail(e.target.value)}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Notes</label>
              <Textarea
                placeholder="Release notes, changes, improvements..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={3}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Artifact Hash (optional)</label>
              <Input
                type="text"
                placeholder="SHA-256 hash of model artifact"
                value={artifactHash}
                onChange={(e) => setArtifactHash(e.target.value)}
              />
              <p className="text-xs text-gray-500 mt-1">Recommended: SHA-256 hash for artifact integrity</p>
            </div>
            
            <Button 
              onClick={handleCreate} 
              disabled={creating || !version || !approverEmail}
              className="w-full"
            >
              {creating ? 'Creating...' : 'Create Version'}
            </Button>
          </div>
        )}

        {/* Version History */}
        {versions.length > 0 && (
          <div>
            <h4 className="font-medium mb-2">Version History</h4>
            <div className="space-y-2">
              {versions.map((v) => (
                <div key={v.id} className="p-3 border rounded hover:bg-gray-50">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">v{v.version}</span>
                    <span className="text-xs text-gray-500">
                      {new Date(v.released_at).toLocaleDateString()}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    <p>Approved by: {v.approver_email}</p>
                    {v.notes && <p className="text-xs mt-1 text-gray-500">{v.notes}</p>}
                    {v.artifact_hash && (
                      <p className="text-xs mt-1 font-mono text-gray-400">
                        Hash: {v.artifact_hash.substring(0, 16)}...
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
