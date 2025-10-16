'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { api } from '@/lib/api'

export default function InventoryPage() {
  const [systems, setSystems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    loadSystems()
  }, [])

  const loadSystems = () => {
    api.getSystems()
      .then(setSystems)
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      try {
        const result = await api.importSystems(file)
        loadSystems()
        alert(`Systems imported successfully! ${result.imported || 0} systems added.`)
      } catch (error: any) {
        alert(`Import failed: ${error.message}`)
        console.error('Import error:', error)
      }
    }
  }

  const handleCreateSystem = async () => {
    const systemData = {
      name: "Customer Support Chatbot",
      purpose: "Automated customer support responses",
      domain: "Customer Service",
      owner_email: "support@example.com",
      uses_biometrics: false,
      is_general_purpose_ai: false,
      impacts_fundamental_rights: false,
      personal_data_processed: true,
      training_data_sensitivity: "low",
      output_type: "text",
      deployment_context: "internal",
      criticality: "medium",
      notes: "Handles Tier 1 support queries"
    }

    try {
      await api.createSystem(systemData)
      loadSystems()
      alert('System created successfully!')
    } catch (error: any) {
      alert(`Failed to create system: ${error.message}`)
      console.error('Create system error:', error)
    }
  }

  const filteredSystems = systems.filter(s => 
    s.name.toLowerCase().includes(filter.toLowerCase()) ||
    s.domain?.toLowerCase().includes(filter.toLowerCase())
  )

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">AI Systems Inventory</h1>
        <p className="text-muted-foreground">
          Manage and classify your AI systems
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Systems</CardTitle>
          <CardDescription>
            Total: {systems.length} systems
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-4">
            <Input
              placeholder="Filter by name or domain..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="max-w-sm"
            />
            <Button onClick={handleCreateSystem} variant="default">
              Create Sample System
            </Button>
            <label className="cursor-pointer">
              <Button variant="outline">Import CSV</Button>
              <input
                type="file"
                accept=".csv"
                className="hidden"
                onChange={handleImport}
              />
            </label>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Name</th>
                  <th className="text-left p-2">Domain</th>
                  <th className="text-left p-2">AI Act Class</th>
                  <th className="text-left p-2">Owner</th>
                  <th className="text-left p-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredSystems.map((system) => (
                  <tr key={system.id} className="border-b hover:bg-muted/50">
                    <td className="p-2 font-medium">{system.name}</td>
                    <td className="p-2">{system.domain || 'N/A'}</td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs ${
                        system.ai_act_class === 'high' ? 'bg-red-100 text-red-800' :
                        system.ai_act_class === 'limited' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {system.ai_act_class || 'Not classified'}
                      </span>
                    </td>
                    <td className="p-2">{system.owner_email || 'N/A'}</td>
                    <td className="p-2">
                      <a href={`/systems/${system.id}`}>
                        <Button variant="ghost" size="sm">View</Button>
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredSystems.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No systems found
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

