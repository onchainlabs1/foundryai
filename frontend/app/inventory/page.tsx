'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton, TableSkeleton } from '@/components/ui/loading-skeleton'
import { api } from '@/lib/api'
import { 
  Database, 
  Search, 
  Plus, 
  Upload, 
  Eye, 
  Filter, 
  Download,
  Bot,
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowRight,
  Sparkles
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function InventoryPage() {
  const [systems, setSystems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [selectedFilter, setSelectedFilter] = useState('all')

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

  const getFilteredSystems = () => {
    let filtered = systems.filter(s => 
      s.name.toLowerCase().includes(filter.toLowerCase()) ||
      s.domain?.toLowerCase().includes(filter.toLowerCase())
    )

    if (selectedFilter !== 'all') {
      filtered = filtered.filter(s => s.ai_act_class === selectedFilter)
    }

    return filtered
  }

  const getRiskStats = () => {
    const high = systems.filter(s => s.ai_act_class === 'high').length
    const limited = systems.filter(s => s.ai_act_class === 'limited').length
    const minimal = systems.filter(s => s.ai_act_class === 'minimal').length
    const unclassified = systems.filter(s => !s.ai_act_class).length

    return { high, limited, minimal, unclassified }
  }

  const stats = getRiskStats()
  const filteredSystems = getFilteredSystems()

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="text-center space-y-4">
          <Skeleton className="h-12 w-80 mx-auto bg-card/50" />
          <Skeleton className="h-6 w-96 mx-auto bg-card/30" />
        </div>
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} className="h-32 rounded-2xl bg-card/50" />
          ))}
        </div>
        <Card className="">
          <CardHeader>
            <Skeleton className="h-6 w-48 bg-card/30" />
            <Skeleton className="h-4 w-32 bg-card/20" />
          </CardHeader>
          <CardContent>
            <TableSkeleton rows={5} />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.section
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3">
          <Database className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold gradient-text">AI Systems Inventory</h1>
          <Sparkles className="h-6 w-6 text-primary" />
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Manage, classify, and monitor your AI systems with comprehensive compliance tracking
        </p>
      </motion.section>

      {/* Stats Cards */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid gap-6 md:grid-cols-4"
      >
        <Card className="group cursor-pointer hover:scale-105 transition-transform">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-blue-500/20">
                <Database className="h-6 w-6 text-blue-600" />
              </div>
              <Badge variant="secondary">Total</Badge>
            </div>
            <CardTitle className="text-lg">All Systems</CardTitle>
            <CardDescription>Registered systems</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-blue-600">{systems.length}</div>
          </CardContent>
        </Card>

        <Card className="group cursor-pointer hover:scale-105 transition-transform">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-red-500/20">
                <Shield className="h-6 w-6 text-red-600" />
              </div>
              <Badge variant="destructive">High Risk</Badge>
            </div>
            <CardTitle className="text-lg">High Risk</CardTitle>
            <CardDescription>EU AI Act classification</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-red-600">{stats.high}</div>
          </CardContent>
        </Card>

        <Card className="group cursor-pointer hover:scale-105 transition-transform">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-yellow-500/20">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
              </div>
              <Badge variant="secondary">Limited</Badge>
            </div>
            <CardTitle className="text-lg">Limited Risk</CardTitle>
            <CardDescription>Moderate compliance needs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-yellow-600">{stats.limited}</div>
          </CardContent>
        </Card>

        <Card className="group cursor-pointer hover:scale-105 transition-transform">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-3 rounded-xl bg-green-500/20">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <Badge variant="default">Minimal</Badge>
            </div>
            <CardTitle className="text-lg">Minimal Risk</CardTitle>
            <CardDescription>Low compliance requirements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-black text-green-600">{stats.minimal}</div>
          </CardContent>
        </Card>
      </motion.section>

      {/* Main Content */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="grid gap-6 lg:grid-cols-4"
      >
        {/* Filters Sidebar */}
        <Card className="lg:col-span-1 h-fit">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Risk Classification</label>
              <div className="space-y-2">
                {[
                  { value: 'all', label: 'All Systems', count: systems.length },
                  { value: 'high', label: 'High Risk', count: stats.high },
                  { value: 'limited', label: 'Limited Risk', count: stats.limited },
                  { value: 'minimal', label: 'Minimal Risk', count: stats.minimal },
                  { value: 'unclassified', label: 'Unclassified', count: stats.unclassified },
                ].map((filter) => (
                  <button
                    key={filter.value}
                    onClick={() => setSelectedFilter(filter.value)}
                    className={`w-full flex items-center justify-between p-2 rounded-lg text-sm transition-all ${
                      selectedFilter === filter.value
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <span>{filter.label}</span>
                    <Badge variant="secondary" className="text-xs">
                      {filter.count}
                    </Badge>
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Systems Table */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI Systems
                </CardTitle>
                <CardDescription>
                  {filteredSystems.length} of {systems.length} systems
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="default" size="sm" onClick={handleCreateSystem}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create System
                </Button>
                <label className="cursor-pointer">
                  <Button variant="outline" size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Import
                  </Button>
                  <input
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={handleImport}
                  />
                </label>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Search Bar */}
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search systems by name or domain..."
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Systems Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">System</th>
                    <th className="text-left p-4 font-semibold">Domain</th>
                    <th className="text-left p-4 font-semibold">Risk Level</th>
                    <th className="text-left p-4 font-semibold">Owner</th>
                    <th className="text-left p-4 font-semibold">Status</th>
                    <th className="text-left p-4 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <AnimatePresence>
                    {filteredSystems.map((system, index) => (
                      <motion.tr
                        key={system.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3, delay: index * 0.05 }}
                        className="border-b hover:bg-muted/50 transition-colors group"
                      >
                        <td className="p-4">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-primary/10">
                              <Bot className="h-4 w-4 text-primary" />
                            </div>
                            <div>
                              <div className="font-medium">{system.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {system.purpose || 'No description'}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="p-4">
                          <Badge variant="outline">{system.domain || 'N/A'}</Badge>
                        </td>
                        <td className="p-4">
                          <Badge 
                            variant={
                              system.ai_act_class === 'high' ? 'destructive' :
                              system.ai_act_class === 'limited' ? 'secondary' :
                              system.ai_act_class === 'minimal' ? 'default' :
                              'secondary'
                            }
                          >
                            {system.ai_act_class || 'Unclassified'}
                          </Badge>
                        </td>
                        <td className="p-4">
                          <div className="text-sm">
                            {system.owner_email || 'N/A'}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm text-muted-foreground">Active</span>
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <Link href={`/systems/${system.id}`}>
                              <Button variant="ghost" size="sm">
                                <Eye className="h-4 w-4 mr-2" />
                                View
                              </Button>
                            </Link>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                </tbody>
              </table>
              
              {filteredSystems.length === 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12"
                >
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                    <Database className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">No systems found</h3>
                  <p className="text-muted-foreground mb-4">
                    {filter || selectedFilter !== 'all' 
                      ? 'Try adjusting your filters or search terms'
                      : 'Get started by creating your first AI system'
                    }
                  </p>
                  {!filter && selectedFilter === 'all' && (
                    <Button variant="default" onClick={handleCreateSystem}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create First System
                    </Button>
                  )}
                </motion.div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.section>
    </div>
  )
}