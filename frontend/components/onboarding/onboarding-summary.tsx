'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle, 
  Building2, 
  Bot, 
  Shield, 
  Users, 
  BarChart3,
  FileText,
  Download,
  ArrowRight,
  RotateCcw
} from 'lucide-react'
import { api } from '@/lib/api'

interface OnboardingSummaryProps {
  data: any
  onRestart: () => void
}

export default function OnboardingSummary({ data, onRestart }: OnboardingSummaryProps) {
  const router = useRouter()
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedReports, setGeneratedReports] = useState<string[]>([])

  const handleGenerateDrafts = async () => {
    setIsGenerating(true)
    try {
      const reports = []
      
      // Generate Annex IV
      if (data.systems && data.systems.length > 0) {
        const systemId = data.systems[0].id || 1
        reports.push('Annex IV')
        await api.generateComplianceDraft(systemId, ['annex_iv'])
      }
      
      // Generate FRIA
      if (data.systems && data.systems.length > 0) {
        const systemId = data.systems[0].id || 1
        reports.push('FRIA')
        await api.generateComplianceDraft(systemId, ['fria'])
      }
      
      // Generate SoA
      if (data.systems && data.systems.length > 0) {
        const systemId = data.systems[0].id || 1
        reports.push('Statement of Applicability')
        await api.generateComplianceDraft(systemId, ['soa'])
      }
      
      // Generate PMM Report
      if (data.systems && data.systems.length > 0) {
        const systemId = data.systems[0].id || 1
        reports.push('PMM Report')
        await api.generateComplianceDraft(systemId, ['pmm'])
      }
      
      setGeneratedReports(reports)
      
      // Redirect to reports page
      setTimeout(() => {
        router.push('/reports')
      }, 2000)
      
    } catch (error) {
      console.error('Failed to generate drafts:', error)
      alert('Failed to generate drafts. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  const getCompletionPercentage = () => {
    let completed = 0
    let total = 0
    
    // Company setup
    total += 1
    if (data.company) completed += 1
    
    // Systems
    total += 1
    if (data.systems && data.systems.length > 0) completed += 1
    
    // Risk & Controls
    total += 1
    if (data.risks) completed += 1
    
    // Oversight
    total += 1
    if (data.oversight) completed += 1
    
    // Monitoring
    total += 1
    if (data.monitoring) completed += 1
    
    return Math.round((completed / total) * 100)
  }

  const getRiskLevel = (system: any) => {
    if (system.riskCategory?.includes('Unacceptable')) return { level: 'Critical', color: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' }
    if (system.riskCategory?.includes('High Risk')) return { level: 'High', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300' }
    if (system.riskCategory?.includes('Limited')) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' }
    return { level: 'Low', color: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4">
            Onboarding Complete!
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Your AI governance framework has been set up successfully. You're now ready to generate compliance documents.
          </p>
        </motion.div>

        {/* Completion Progress */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card className="bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Setup Progress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Overall Completion</span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">{getCompletionPercentage()}%</span>
                </div>
                <Progress value={getCompletionPercentage()} className="w-full" />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Company Setup */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Building2 className="w-5 h-5 text-blue-500" />
                  Company Setup
                </CardTitle>
              </CardHeader>
              <CardContent>
                {data.company ? (
                  <div className="space-y-2">
                    <p className="font-medium">{data.company.companyName}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{data.company.sector}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{data.company.country}</p>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Not completed</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* AI Systems */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bot className="w-5 h-5 text-purple-500" />
                  AI Systems
                </CardTitle>
              </CardHeader>
              <CardContent>
                {data.systems && data.systems.length > 0 ? (
                  <div className="space-y-2">
                    <p className="font-medium">{data.systems.length} system(s) defined</p>
                    {data.systems.map((system: any, index: number) => {
                      const riskLevel = getRiskLevel(system)
                      return (
                        <div key={index} className="flex items-center justify-between">
                          <span className="text-sm">{system.name}</span>
                          <Badge className={riskLevel.color}>
                            {riskLevel.level}
                          </Badge>
                        </div>
                      )
                    })}
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No systems defined</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Risk & Controls */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Shield className="w-5 h-5 text-orange-500" />
                  Risk & Controls
                </CardTitle>
              </CardHeader>
              <CardContent>
                {data.risks ? (
                  <div className="space-y-2">
                    <p className="font-medium">{data.risks.topRisks?.length || 0} risks identified</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {data.risks.controlsSelected?.length || 0} controls selected
                    </p>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Not completed</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Human Oversight */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Users className="w-5 h-5 text-green-500" />
                  Human Oversight
                </CardTitle>
              </CardHeader>
              <CardContent>
                {data.oversight ? (
                  <div className="space-y-2">
                    <p className="font-medium">{data.oversight.oversightMethod}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {data.oversight.changeApprovalRoles?.length || 0} approval roles
                    </p>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Not completed</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Monitoring */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-indigo-500" />
                  Monitoring
                </CardTitle>
              </CardHeader>
              <CardContent>
                {data.monitoring ? (
                  <div className="space-y-2">
                    <p className="font-medium">{data.monitoring.loggingScope?.length || 0} logging scopes</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {data.monitoring.fairnessMetricsMonitored?.length || 0} fairness metrics
                    </p>
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Not completed</p>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Evidence Generated */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <FileText className="w-5 h-5 text-emerald-500" />
                  Evidence Generated
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="font-medium">Templates ready</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Risk Assessment, Model Card, Oversight SOP, Logging Plan, PMM Report
                  </p>
                  <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300">
                    <FileText className="w-3 h-3 mr-1" />
                    Ready
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Generated Reports */}
        {generatedReports.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <Card className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
              <CardHeader>
                <CardTitle className="text-green-800 dark:text-green-200 flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  Reports Generated Successfully
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {generatedReports.map((report, index) => (
                    <Badge key={index} className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300">
                      {report}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-green-700 dark:text-green-300 mt-2">
                  Redirecting to reports page...
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Action Buttons */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <Button
            onClick={handleGenerateDrafts}
            disabled={isGenerating}
            className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
            size="lg"
          >
            {isGenerating ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                Generate Drafts
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>

          <Button
            onClick={onRestart}
            variant="outline"
            className="flex items-center gap-2"
            size="lg"
          >
            <RotateCcw className="w-4 h-4" />
            Start Over
          </Button>
        </motion.div>

        {/* Next Steps */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
          className="mt-8"
        >
          <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="text-blue-800 dark:text-blue-200">
                🎉 Next Steps
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-blue-700 dark:text-blue-300 space-y-2">
                <p>Your AI governance framework is now set up! Here's what you can do next:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Generate compliance documents (Annex IV, FRIA, SoA, PMM)</li>
                  <li>Review and customize the generated templates</li>
                  <li>Upload additional evidence as needed</li>
                  <li>Set up regular monitoring and review cycles</li>
                  <li>Train your team on the governance framework</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
