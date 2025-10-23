'use client'

import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { api, downloadFile } from '@/lib/api'

interface Control {
  id?: number
  system_id: number
  iso_clause: string
  name: string
  priority: string
  status: string
  owner_email?: string
  due_date?: string
  rationale?: string
  evidence_ids?: number[]  // New field for evidence linking
}

interface Evidence {
  id: number
  label: string
  version: string
  checksum: string
  control_id?: number
  iso_clause?: string
  upload_date?: string
}

interface ControlsTableProps {
  systemId: number
}

export function ControlsTable({ systemId }: ControlsTableProps) {
  const [controls, setControls] = useState<Control[]>([])
  const [evidence, setEvidence] = useState<Evidence[]>([])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [editMode, setEditMode] = useState<Record<number, boolean>>({})
  const [evidenceModalOpen, setEvidenceModalOpen] = useState<number | null>(null)
  const [selectedEvidence, setSelectedEvidence] = useState<number[]>([])

  const loadControls = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getSystemControls(systemId)
      setControls(data)
    } catch (error) {
      console.error('Failed to load controls:', error)
    } finally {
      setLoading(false)
    }
  }, [systemId])

  const loadEvidence = useCallback(async () => {
    try {
      const data = await api.getSystemEvidence(systemId)
      setEvidence(data)
    } catch (error) {
      console.error('Failed to load evidence:', error)
    }
  }, [systemId])

  useEffect(() => {
    loadControls()
    loadEvidence()
  }, [loadControls, loadEvidence])

  const handleSaveAll = async () => {
    setSaving(true)
    try {
      await api.bulkUpsertControls(controls)
      alert('Controls saved successfully')
      setEditMode({})
      await loadControls()
    } catch (error) {
      alert('Failed to save controls: ' + error)
    } finally {
      setSaving(false)
    }
  }

  const handleAddRow = () => {
    const newControl: Control = {
      system_id: systemId,
      iso_clause: '',
      name: '',
      priority: 'medium',
      status: 'missing',
      owner_email: '',
      due_date: '',
      rationale: '',
    }
    setControls([...controls, newControl])
    setEditMode({ ...editMode, [controls.length]: true })
  }

  const handleFieldChange = (index: number, field: keyof Control, value: string) => {
    const updated = [...controls]
    updated[index] = { ...updated[index], [field]: value }
    setControls(updated)
  }

  const handleOpenEvidenceModal = (controlIndex: number) => {
    setEvidenceModalOpen(controlIndex)
    setSelectedEvidence(controls[controlIndex].evidence_ids || [])
  }

  const handleCloseEvidenceModal = () => {
    setEvidenceModalOpen(null)
    setSelectedEvidence([])
  }

  const handleEvidenceSelection = (evidenceId: number, checked: boolean) => {
    if (checked) {
      setSelectedEvidence([...selectedEvidence, evidenceId])
    } else {
      setSelectedEvidence(selectedEvidence.filter(id => id !== evidenceId))
    }
  }

  const handleSaveEvidenceLinks = () => {
    if (evidenceModalOpen !== null) {
      const updated = [...controls]
      updated[evidenceModalOpen] = { 
        ...updated[evidenceModalOpen], 
        evidence_ids: selectedEvidence 
      }
      setControls(updated)
      handleCloseEvidenceModal()
    }
  }

  const getEvidenceForControl = (controlIndex: number) => {
    const control = controls[controlIndex]
    if (!control.evidence_ids) return []
    return evidence.filter(ev => control.evidence_ids?.includes(ev.id))
  }

  const handleExportSoA = async () => {
    try {
      await downloadFile(`/systems/${systemId}/soa.csv`, 'statement-of-applicability.csv');
    } catch (error) {
      console.error('SoA export failed:', error);
      alert('Export failed. Please check your API key.');
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'implemented': return 'bg-green-100 text-green-800'
      case 'partial': return 'bg-yellow-100 text-yellow-800'
      case 'missing': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return <div className="text-center py-8">Loading controls...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Controls Management (RACI)</CardTitle>
        <CardDescription>Manage ISO 42001 controls with responsibility assignment</CardDescription>
        <div className="flex gap-2 mt-4">
          <Button onClick={handleAddRow} variant="outline">Add Control</Button>
          <Button onClick={handleSaveAll} disabled={saving}>
            {saving ? 'Saving...' : 'Save All Changes'}
          </Button>
          <Button onClick={handleExportSoA} variant="outline">Export SoA CSV</Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="text-left p-2 font-medium">ISO Clause</th>
                <th className="text-left p-2 font-medium">Name</th>
                <th className="text-left p-2 font-medium">Priority</th>
                <th className="text-left p-2 font-medium">Status</th>
                <th className="text-left p-2 font-medium">Owner</th>
                <th className="text-left p-2 font-medium">Due Date</th>
                <th className="text-left p-2 font-medium">Evidence</th>
                <th className="text-left p-2 font-medium">Rationale</th>
                <th className="text-left p-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {controls.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-muted-foreground">
                    No controls found. Add controls or run assessment to generate them.
                  </td>
                </tr>
              ) : (
                controls.map((control, index) => {
                  const isEditing = editMode[index]
                  return (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2">
                        {isEditing ? (
                          <Input
                            value={control.iso_clause}
                            onChange={(e) => handleFieldChange(index, 'iso_clause', e.target.value)}
                            className="w-32"
                          />
                        ) : (
                          <span className="font-mono text-xs">{control.iso_clause}</span>
                        )}
                      </td>
                      <td className="p-2">
                        {isEditing ? (
                          <Input
                            value={control.name}
                            onChange={(e) => handleFieldChange(index, 'name', e.target.value)}
                            className="w-48"
                          />
                        ) : (
                          <span>{control.name}</span>
                        )}
                      </td>
                      <td className="p-2">
                        {isEditing ? (
                          <select
                            value={control.priority}
                            onChange={(e) => handleFieldChange(index, 'priority', e.target.value)}
                            className="border rounded px-2 py-1"
                          >
                            <option value="high">High</option>
                            <option value="medium">Medium</option>
                            <option value="low">Low</option>
                          </select>
                        ) : (
                          <span className={`px-2 py-1 rounded text-xs ${getPriorityColor(control.priority)}`}>
                            {control.priority}
                          </span>
                        )}
                      </td>
                      <td className="p-2">
                        {isEditing ? (
                          <select
                            value={control.status}
                            onChange={(e) => handleFieldChange(index, 'status', e.target.value)}
                            className="border rounded px-2 py-1"
                          >
                            <option value="missing">Missing</option>
                            <option value="partial">Partial</option>
                            <option value="implemented">Implemented</option>
                          </select>
                        ) : (
                          <span className={`px-2 py-1 rounded text-xs ${getStatusColor(control.status)}`}>
                            {control.status}
                          </span>
                        )}
                      </td>
                      <td className="p-2">
                        {isEditing ? (
                          <Input
                            type="email"
                            value={control.owner_email || ''}
                            onChange={(e) => handleFieldChange(index, 'owner_email', e.target.value)}
                            className="w-40"
                            placeholder="owner@company.com"
                          />
                        ) : (
                          <span className="text-xs">{control.owner_email || '-'}</span>
                        )}
                      </td>
                      <td className="p-2">
                        {isEditing ? (
                          <Input
                            type="date"
                            value={control.due_date || ''}
                            onChange={(e) => handleFieldChange(index, 'due_date', e.target.value)}
                            className="w-36"
                          />
                        ) : (
                          <span className="text-xs">{control.due_date || '-'}</span>
                        )}
                      </td>
                      <td className="p-2">
                        <div className="flex flex-col gap-1">
                          {getEvidenceForControl(index).map(ev => (
                            <span key={ev.id} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {ev.label} (v{ev.version})
                            </span>
                          ))}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleOpenEvidenceModal(index)}
                            className="text-xs"
                          >
                            {getEvidenceForControl(index).length > 0 ? 'Edit' : 'Add'} Evidence
                          </Button>
                        </div>
                      </td>
                      <td className="p-2 max-w-xs">
                        {isEditing ? (
                          <Input
                            value={control.rationale || ''}
                            onChange={(e) => handleFieldChange(index, 'rationale', e.target.value)}
                            className="w-48"
                            placeholder="Rationale..."
                          />
                        ) : (
                          <span className="text-xs truncate">{control.rationale || '-'}</span>
                        )}
                      </td>
                      <td className="p-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setEditMode({ ...editMode, [index]: !isEditing })}
                        >
                          {isEditing ? 'Done' : 'Edit'}
                        </Button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
      
      {/* Evidence Linking Modal */}
      {evidenceModalOpen !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">Link Evidence to Control</h3>
            <p className="text-sm text-gray-600 mb-4">
              Select evidence to link to: <strong>{controls[evidenceModalOpen]?.name}</strong>
            </p>
            
            <div className="space-y-2 mb-4">
              {evidence.map(ev => (
                <label key={ev.id} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedEvidence.includes(ev.id)}
                    onChange={(e) => handleEvidenceSelection(ev.id, e.target.checked)}
                    className="rounded"
                  />
                  <div className="flex-1">
                    <span className="font-medium">{ev.label}</span>
                    <span className="text-sm text-gray-500 ml-2">v{ev.version}</span>
                    {ev.checksum && (
                      <span className="text-xs text-gray-400 ml-2">sha256:{ev.checksum.substring(0, 8)}...</span>
                    )}
                  </div>
                </label>
              ))}
            </div>
            
            {evidence.length === 0 && (
              <p className="text-gray-500 text-center py-4">
                No evidence available. Upload evidence first in the Evidence tab.
              </p>
            )}
            
            <div className="flex justify-end space-x-2">
              <Button variant="outline" onClick={handleCloseEvidenceModal}>
                Cancel
              </Button>
              <Button onClick={handleSaveEvidenceLinks}>
                Save Links
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  )
}

