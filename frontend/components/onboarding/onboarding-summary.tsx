'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
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
  RotateCcw,
  AlertTriangle,
  Sparkles,
  Zap,
  Target
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
      const systemsWithoutIds = []
      
      // Generate compliance documents for each system
      if (data.systems && data.systems.length > 0) {
        for (const system of data.systems) {
          // Ensure we have a valid system ID
          if (!system.id) {
            console.warn(`System ${system.name} has no ID`)
            systemsWithoutIds.push(system.name)
            continue
          }
          
          // Generate all compliance documents with real onboarding data
          try {
            const onboardingData = {
              company: data.company,
              risks: data.risks,
              oversight: data.oversight,
              monitoring: data.monitoring
            }
            
            const response = await api.generateSystemDocuments(system.id, onboardingData)
            if (response.status === 'success' && response.generated_documents > 0) {
              reports.push(`${response.generated_documents} documents for ${system.name}`)
            } else {
              reports.push(`No documents generated for ${system.name}`)
            }
          } catch (error) {
            console.error(`Error generating documents for system ${system.id}:`, error)
            reports.push(`Error generating documents for ${system.name}: ${error instanceof Error ? error.message : 'Unknown error'}`)
          }
        }
      }
      
      setGeneratedReports(reports)
      
      // Handle systems without IDs (should be rare with deterministic mapping)
      if (systemsWithoutIds.length > 0) {
        const systemList = systemsWithoutIds.join(', ')
        console.warn(`Systems without IDs detected: ${systemList}`)
        alert(`Some systems (${systemList}) don't have valid IDs. This may indicate a synchronization issue. Please try refreshing the page or going back to Step 2.`)
        return
      }
      
      // Only redirect if at least one system had documents generated successfully
      const successCount = reports.filter(r => r.includes('documents for') && !r.includes('Error')).length
      if (successCount > 0) {
        setTimeout(() => {
          router.push('/documents')
        }, 2000)
      } else {
        alert('Failed to generate documents for any system. Please check the console for details.')
      }
      
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
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8"
    >
      {/* Header */}
      <div className="text-center space-y-4">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 text-white mb-4"
        >
          <CheckCircle className="w-10 h-10" />
        </motion.div>
        <h1 className="text-4xl font-bold gradient-text">
          Onboarding Complete!
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Your AI governance framework has been set up successfully. You're now ready to generate compliance documents.
        </p>
      </div>

      {/* Completion Progress */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card  className="p-6">
          <CardHeader className="pb-4">
            <CardTitle className="flex items-center gap-3 text-xl">
              <Target className="w-6 h-6 text-green-500" />
              Setup Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold">Overall Completion</span>
                <span className="text-2xl font-bold text-primary">{getCompletionPercentage()}%</span>
              </div>
              <Progress value={getCompletionPercentage()} className="w-full h-3" />
              <p className="text-sm text-muted-foreground text-center">
                All major components of your AI governance framework have been configured
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Company Setup */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-600 text-white">
                  <Building2 className="w-5 h-5" />
                </div>
                Company Setup
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data.company ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-semibold text-lg">{data.company.companyName}</p>
                    <p className="text-muted-foreground">{data.company.sector}</p>
                    <p className="text-muted-foreground">{data.company.country}</p>
                  </div>
                  <Badge variant="default" className="w-fit">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Complete
                  </Badge>
                </div>
              ) : (
                <p className="text-muted-foreground">Not completed</p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* AI Systems */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-600 text-white">
                  <Bot className="w-5 h-5" />
                </div>
                AI Systems
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data.systems && data.systems.length > 0 ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-semibold text-lg">{data.systems.length} system(s) defined</p>
                    <div className="space-y-2 mt-3">
                      {data.systems.map((system: any, index: number) => {
                        const riskLevel = getRiskLevel(system)
                        const hasValidId = system.id && system.id > 0
                        return (
                          <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted/30">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium">{system.name}</span>
                              {hasValidId ? (
                                <CheckCircle className="w-3 h-3 text-green-500" />
                              ) : (
                                <AlertTriangle className="w-3 h-3 text-orange-500" />
                              )}
                            </div>
                            <Badge variant={riskLevel.level === 'Critical' ? 'destructive' : riskLevel.level === 'High' ? 'secondary' : 'secondary'}>
                              {riskLevel.level}
                            </Badge>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="w-fit">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Complete
                    </Badge>
                    {data.systems.some((s: any) => !s.id) && (
                      <Badge variant="secondary" className="w-fit">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        Missing IDs
                      </Badge>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-muted-foreground">No systems defined</p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Risk & Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-600 text-white">
                  <Shield className="w-5 h-5" />
                </div>
                Risk & Controls
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data.risks ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-semibold text-lg">{data.risks.topRisks?.length || 0} risks identified</p>
                    <p className="text-muted-foreground">
                      {data.risks.controlsSelected?.length || 0} controls selected
                    </p>
                  </div>
                  <Badge variant="default" className="w-fit">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Complete
                  </Badge>
                </div>
              ) : (
                <p className="text-muted-foreground">Not completed</p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Human Oversight */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-teal-600 text-white">
                  <Users className="w-5 h-5" />
                </div>
                Human Oversight
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data.oversight ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-semibold text-lg">{data.oversight.oversightMethod}</p>
                    <p className="text-muted-foreground">
                      {data.oversight.changeApprovalRoles?.length || 0} approval roles
                    </p>
                  </div>
                  <Badge variant="default" className="w-fit">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Complete
                  </Badge>
                </div>
              ) : (
                <p className="text-muted-foreground">Not completed</p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Monitoring */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
                  <BarChart3 className="w-5 h-5" />
                </div>
                Monitoring
              </CardTitle>
            </CardHeader>
            <CardContent>
              {data.monitoring ? (
                <div className="space-y-3">
                  <div>
                    <p className="font-semibold text-lg">{data.monitoring.loggingScope?.length || 0} logging scopes</p>
                    <p className="text-muted-foreground">
                      {data.monitoring.fairnessMetricsMonitored?.length || 0} fairness metrics
                    </p>
                  </div>
                  <Badge variant="default" className="w-fit">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Complete
                  </Badge>
                </div>
              ) : (
                <p className="text-muted-foreground">Not completed</p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Evidence Generated */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <Card  className="p-6 hover:shadow-lg transition-all duration-300">
            <CardHeader className="pb-4">
              <CardTitle className="text-xl flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-emerald-500 to-green-600 text-white">
                  <FileText className="w-5 h-5" />
                </div>
                Evidence Generated
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <p className="font-semibold text-lg">11+ compliance documents</p>
                  <p className="text-muted-foreground text-sm">
                    Risk Assessment, Impact Assessment, Model Card, Data Sheet, Logging Plan, Monitoring Report, Human Oversight SOP, Appeals Flow, SoA, Policy Register, Audit Log
                  </p>
                </div>
                <Badge variant="secondary" className="w-fit">
                  <FileText className="w-3 h-3 mr-1" />
                  Ready
                </Badge>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Generated Reports */}
      <AnimatePresence>
        {generatedReports.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
          >
            <Card  className="border-green-200/50 bg-green-50/50 dark:bg-green-950/20">
              <CardHeader className="pb-4">
                <CardTitle className="text-green-800 dark:text-green-200 flex items-center gap-3 text-xl">
                  <CheckCircle className="w-6 h-6" />
                  Reports Generated Successfully
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2 mb-4">
                  {generatedReports.map((report, index) => (
                    <Badge key={index} variant="default">
                      {report}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-green-700 dark:text-green-300 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Redirecting to documents page...
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Action Buttons */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="flex flex-col sm:flex-row gap-4 justify-center"
      >
        <Button
          onClick={handleGenerateDrafts}
          disabled={isGenerating}
          variant="default"
          size="lg"
          className="min-w-[250px] flex items-center gap-3"
        >
          {isGenerating ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5" />
              Generate Documents
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </Button>

        <Button
          onClick={onRestart}
          variant="outline"
          size="lg"
          className="min-w-[200px] flex items-center gap-3"
        >
          <RotateCcw className="w-4 h-4" />
          Start Over
        </Button>
      </motion.div>

      {/* Next Steps */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.1 }}
      >
        <Card  className="border-primary/20 bg-primary/5">
          <CardHeader className="pb-4">
            <CardTitle className="text-primary text-2xl flex items-center gap-3">
              <Sparkles className="w-6 h-6" />
              Next Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-muted-foreground space-y-4">
              <p className="text-lg font-medium">Your AI governance framework is now set up! Here's what you can do next:</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Generate 11+ compliance documents (Risk Assessment, Model Card, SoA, etc.)</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Review and customize the generated templates</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Download documents in Markdown and PDF formats</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Upload additional evidence as needed</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Set up regular monitoring and review cycles</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 flex-shrink-0"></span>
                    <span>Train your team on the governance framework</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
