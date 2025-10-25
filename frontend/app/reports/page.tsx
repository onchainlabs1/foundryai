'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { api, downloadFile } from '@/lib/api'
import { IncidentsTable } from '@/components/incidents-modal'
import ComplianceSuite from '@/components/compliance-suite'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, 
  Download, 
  BarChart3, 
  TrendingUp, 
  Shield, 
  Bot, 
  Target, 
  FileSpreadsheet,
  Archive,
  Eye,
  Sparkles,
  ArrowRight,
  CheckCircle,
  AlertTriangle,
  Info
} from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null)
  const [score, setScore] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getReportSummary(),
      api.getReportScore()
    ])
      .then(([summaryData, scoreData]) => {
        setSummary(summaryData)
        setScore(scoreData)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-5xl font-bold gradient-text">
            Reports & Analytics
          </h1>
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Generate comprehensive compliance reports, export data, and track your AI governance progress.
        </p>
      </motion.div>

      {/* Key Metrics Cards */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          whileHover={{ y: -8, scale: 1.02 }}
        >
          <Card  className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-xl bg-blue-500/20">
                  <BarChart3 className="h-6 w-6 text-blue-600" />
                </div>
                <Badge variant="secondary">Total</Badge>
              </div>
              <CardTitle className="text-lg">AI Systems</CardTitle>
              <CardDescription>Registered in inventory</CardDescription>
            </CardHeader>
            <CardContent>
              <motion.div 
                className="text-4xl font-black text-blue-600"
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                {loading ? <Skeleton className="h-10 w-16" /> : (summary?.systems || 0)}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          whileHover={{ y: -8, scale: 1.02 }}
        >
          <Card  className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-xl bg-red-500/20">
                  <Shield className="h-6 w-6 text-red-600" />
                </div>
                <Badge variant="destructive">High Risk</Badge>
              </div>
              <CardTitle className="text-lg">High-Risk Systems</CardTitle>
              <CardDescription>EU AI Act classification</CardDescription>
            </CardHeader>
            <CardContent>
              <motion.div 
                className="text-4xl font-black text-red-600"
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                {loading ? <Skeleton className="h-10 w-16" /> : (summary?.high_risk || 0)}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          whileHover={{ y: -8, scale: 1.02 }}
        >
          <Card  className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-xl bg-purple-500/20">
                  <Bot className="h-6 w-6 text-purple-600" />
                </div>
                <Badge variant="secondary">GPAI</Badge>
              </div>
              <CardTitle className="text-lg">GPAI Systems</CardTitle>
              <CardDescription>General Purpose AI</CardDescription>
            </CardHeader>
            <CardContent>
              <motion.div 
                className="text-4xl font-black text-purple-600"
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                {loading ? <Skeleton className="h-10 w-16" /> : (summary?.gpai_count || 0)}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          whileHover={{ y: -8, scale: 1.02 }}
        >
          <Card  className="h-full">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="p-3 rounded-xl bg-green-500/20">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
                <Badge variant="default">Overall</Badge>
              </div>
              <CardTitle className="text-lg">Compliance Score</CardTitle>
              <CardDescription>Overall readiness</CardDescription>
            </CardHeader>
            <CardContent>
              <motion.div 
                className="text-4xl font-black text-green-600"
                initial={{ scale: 0.5 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
              >
                {loading ? <Skeleton className="h-10 w-20" /> : 
                  (score?.org_score ? `${Math.round(score.org_score * 100)}%` : 'N/A')}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>

      {/* Export & Templates Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="grid gap-6 md:grid-cols-2"
      >
        {/* CSV Templates Card */}
        <Card  className="overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-emerald-500/20">
                <FileSpreadsheet className="h-6 w-6 text-emerald-600" />
              </div>
              <div>
                <CardTitle className="text-xl">CSV Templates</CardTitle>
                <CardDescription>Download templates for data import</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <motion.a 
              href="/assets/templates/aims_inventory_template.csv" 
              download
              whileHover={{ x: 4 }}
              className="block"
            >
              <Button variant="outline" className="w-full justify-start gap-3" size="lg">
                <FileSpreadsheet className="h-4 w-4" />
                AI Systems Inventory
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.a>
            <motion.a 
              href="/assets/templates/aims_control_plan_raci_template.csv" 
              download
              whileHover={{ x: 4 }}
              className="block"
            >
              <Button variant="outline" className="w-full justify-start gap-3" size="lg">
                <FileSpreadsheet className="h-4 w-4" />
                RACI Control Plan
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.a>
            <motion.a 
              href="/assets/templates/aims_evidence_manifest_template.csv" 
              download
              whileHover={{ x: 4 }}
              className="block"
            >
              <Button variant="outline" className="w-full justify-start gap-3" size="lg">
                <FileSpreadsheet className="h-4 w-4" />
                Evidence Manifest
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.a>
          </CardContent>
        </Card>

        {/* Export Reports Card */}
        <Card  className="overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-indigo-500/20">
                <Download className="h-6 w-6 text-indigo-600" />
              </div>
              <div>
                <CardTitle className="text-xl">Export Reports</CardTitle>
                <CardDescription>Generate compliance documentation</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <motion.div whileHover={{ x: 4 }}>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-3" 
                size="lg"
                onClick={async () => {
                  try {
                    await downloadFile('/reports/deck.pptx', 'executive-deck.pptx');
                  } catch (error) {
                    console.error('Download failed:', error);
                    alert('Download failed. Please check your API key.');
                  }
                }}
              >
                <BarChart3 className="h-4 w-4" />
                Executive Deck (.pptx)
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.div>
            <motion.div whileHover={{ x: 4 }}>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-3" 
                size="lg"
                onClick={async () => {
                  try {
                    // Get the first available system ID for Annex IV export
                    const systems = await api.getSystems();
                    if (systems.length === 0) {
                      alert('No systems available for Annex IV export. Please create a system first.');
                      return;
                    }
                    const systemId = systems[0].id;
                    await downloadFile(`/reports/annex-iv/${systemId}`, 'annex-iv.zip');
                  } catch (error) {
                    console.error('Download failed:', error);
                    alert('Download failed. Please check your API key and ensure you have systems configured.');
                  }
                }}
              >
                <Archive className="h-4 w-4" />
                Annex IV Package (.zip)
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.div>
            <motion.a 
              href="/assets/mock/aims_readiness_mock.html" 
              target="_blank"
              whileHover={{ x: 4 }}
              className="block"
            >
              <Button variant="outline" className="w-full justify-start gap-3" size="lg">
                <Eye className="h-4 w-4" />
                View Sample Report
                <ArrowRight className="h-4 w-4 ml-auto" />
              </Button>
            </motion.a>
          </CardContent>
        </Card>
      </motion.div>

      {/* Compliance Suite */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.0 }}
      >
        <ComplianceSuite />
      </motion.div>

      {/* Incidents Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 1.2 }}
      >
        <IncidentsTable />
      </motion.div>
    </div>
  )
}

