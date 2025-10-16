'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

interface IncidentsModalProps {
  systemId: number
  onClose?: () => void
  onSuccess?: () => void
}

export function IncidentsModal({ systemId, onClose, onSuccess }: IncidentsModalProps) {
  const [formData, setFormData] = useState({
    severity: 'low',
    description: '',
    detected_at: new Date().toISOString().slice(0, 16),
    corrective_action: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      await api.createIncident({
        system_id: systemId,
        ...formData,
        detected_at: new Date(formData.detected_at).toISOString(),
      })
      alert('Incident created successfully')
      onSuccess?.()
      onClose?.()
    } catch (error) {
      alert('Failed to create incident: ' + error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>Report Incident</CardTitle>
          <CardDescription>Post-Market Monitoring (Article 72)</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Severity</label>
              <select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                className="w-full border rounded-md px-3 py-2"
                required
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full border rounded-md px-3 py-2 min-h-[100px]"
                placeholder="Describe the incident..."
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Detected At</label>
              <Input
                type="datetime-local"
                value={formData.detected_at}
                onChange={(e) => setFormData({ ...formData, detected_at: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Corrective Action</label>
              <textarea
                value={formData.corrective_action}
                onChange={(e) => setFormData({ ...formData, corrective_action: e.target.value })}
                className="w-full border rounded-md px-3 py-2 min-h-[100px]"
                placeholder="Describe corrective actions taken..."
              />
            </div>

            <div className="flex gap-2 justify-end pt-4">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Incident'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

interface IncidentsTableProps {
  systemId?: number
}

export function IncidentsTable({ systemId }: IncidentsTableProps) {
  const [incidents, setIncidents] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [filter, setFilter] = useState<'all' | 'open' | 'resolved'>('all')

  const loadIncidents = async () => {
    setLoading(true)
    try {
      const data = await api.getIncidents(systemId)
      setIncidents(data)
    } catch (error) {
      console.error('Failed to load incidents:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleResolve = async (incidentId: number) => {
    try {
      await api.updateIncident(incidentId, {
        resolved_at: new Date().toISOString(),
      })
      await loadIncidents()
    } catch (error) {
      alert('Failed to resolve incident: ' + error)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-600 text-white'
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredIncidents = incidents.filter(inc => {
    if (filter === 'all') return true
    if (filter === 'open') return !inc.resolved_at
    if (filter === 'resolved') return !!inc.resolved_at
    return true
  })

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Incidents Register (PMM)</CardTitle>
          <CardDescription>Post-Market Monitoring incident tracking</CardDescription>
          <div className="flex gap-2 mt-4">
            <Button onClick={() => { setShowModal(true); loadIncidents(); }}>
              Add Incident
            </Button>
            <div className="flex gap-1 ml-auto">
              <Button 
                size="sm" 
                variant={filter === 'all' ? 'default' : 'outline'}
                onClick={() => setFilter('all')}
              >
                All
              </Button>
              <Button 
                size="sm" 
                variant={filter === 'open' ? 'default' : 'outline'}
                onClick={() => setFilter('open')}
              >
                Open
              </Button>
              <Button 
                size="sm" 
                variant={filter === 'resolved' ? 'default' : 'outline'}
                onClick={() => setFilter('resolved')}
              >
                Resolved
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading incidents...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-gray-50">
                    <th className="text-left p-2 font-medium">Severity</th>
                    <th className="text-left p-2 font-medium">Description</th>
                    <th className="text-left p-2 font-medium">Detected</th>
                    <th className="text-left p-2 font-medium">Resolved</th>
                    <th className="text-left p-2 font-medium">Corrective Action</th>
                    <th className="text-left p-2 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredIncidents.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="text-center py-8 text-muted-foreground">
                        No incidents found
                      </td>
                    </tr>
                  ) : (
                    filteredIncidents.map((incident) => (
                      <tr key={incident.id} className="border-b hover:bg-gray-50">
                        <td className="p-2">
                          <span className={`px-2 py-1 rounded text-xs ${getSeverityColor(incident.severity)}`}>
                            {incident.severity}
                          </span>
                        </td>
                        <td className="p-2 max-w-xs">
                          <span className="text-xs">{incident.description}</span>
                        </td>
                        <td className="p-2">
                          <span className="text-xs">
                            {new Date(incident.detected_at).toLocaleDateString()}
                          </span>
                        </td>
                        <td className="p-2">
                          {incident.resolved_at ? (
                            <span className="text-xs text-green-600">
                              {new Date(incident.resolved_at).toLocaleDateString()}
                            </span>
                          ) : (
                            <span className="text-xs text-red-600">Open</span>
                          )}
                        </td>
                        <td className="p-2 max-w-xs">
                          <span className="text-xs truncate">{incident.corrective_action || '-'}</span>
                        </td>
                        <td className="p-2">
                          {!incident.resolved_at && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleResolve(incident.id)}
                            >
                              Resolve
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {showModal && systemId && (
        <IncidentsModal
          systemId={systemId}
          onClose={() => setShowModal(false)}
          onSuccess={loadIncidents}
        />
      )}
    </>
  )
}

