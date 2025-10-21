'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { 
  BarChart3, 
  AlertTriangle, 
  Clock, 
  Shield, 
  FileText, 
  CheckCircle,
  Edit3,
  TrendingUp,
  ArrowRight,
  Activity,
  Target
} from 'lucide-react'

const monitoringSchema = z.object({
  loggingScope: z.array(z.string()).optional(),
  logRetentionPeriod: z.string().optional(),
  retentionMonths: z.number().optional(),
  driftAlertThreshold: z.number().min(0).max(100).optional(),
  driftThreshold: z.string().optional(),
  fairnessMetricsMonitored: z.array(z.string()).optional(),
  fairnessMetrics: z.string().optional(),
  incidentRegisterTool: z.string().optional(),
  incidentTool: z.string().optional(),
  correctiveActionTracking: z.string().optional(),
  hasNonConformities: z.boolean().optional(),
  nonConformitiesDescription: z.string().optional(),
  internalAuditFrequency: z.string().optional(),
  auditFrequency: z.string().optional(),
  managementReviewFrequency: z.string().optional(),
  improvementPlan: z.string().optional(),
  euDbRequired: z.boolean().optional(),
  euDbStatus: z.string().optional()
})

type MonitoringFormData = z.infer<typeof monitoringSchema>

interface MonitoringImprovementProps {
  data?: any
  onUpdate: (data: any) => void
}

const loggingScopes = [
  'Model Performance',
  'Data Quality',
  'Bias Detection',
  'User Interactions',
  'System Errors',
  'Security Events',
  'Compliance Events',
  'Model Drift'
]

const logRetentionPeriods = [
  '30 days',
  '90 days',
  '6 months',
  '1 year',
  '2 years',
  '5 years',
  'Indefinite'
]

const fairnessMetrics = [
  'Demographic Parity',
  'Equalized Odds',
  'Equal Opportunity',
  'Calibration',
  'Individual Fairness',
  'Group Fairness',
  'Counterfactual Fairness'
]

const incidentRegisterTools = [
  'Internal Ticketing System',
  'JIRA',
  'ServiceNow',
  'Custom Dashboard',
  'Spreadsheet',
  'Other'
]

const auditFrequencies = [
  'Monthly',
  'Quarterly',
  'Semi-annually',
  'Annually',
  'As needed'
]

export default function MonitoringImprovement({ data, onUpdate }: MonitoringImprovementProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showTemplatePreview, setShowTemplatePreview] = useState(false)
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<MonitoringFormData>({
    resolver: zodResolver(monitoringSchema),
    defaultValues: {
      loggingScope: data?.loggingScope || [],
      logRetentionPeriod: data?.logRetentionPeriod || '',
      driftAlertThreshold: data?.driftAlertThreshold || 10,
      fairnessMetricsMonitored: data?.fairnessMetricsMonitored || [],
      incidentRegisterTool: data?.incidentRegisterTool || '',
      correctiveActionTracking: data?.correctiveActionTracking || '',
      hasNonConformities: data?.hasNonConformities || false,
      nonConformitiesDescription: data?.nonConformitiesDescription || '',
      internalAuditFrequency: data?.internalAuditFrequency || '',
      managementReviewFrequency: data?.managementReviewFrequency || '',
      improvementPlan: data?.improvementPlan || ''
    }
  })

  const loggingScope = watch('loggingScope')
  const fairnessMetricsMonitored = watch('fairnessMetricsMonitored')
  const hasNonConformities = watch('hasNonConformities')
  const driftAlertThreshold = watch('driftAlertThreshold')

  const onSubmit = async (formData: MonitoringFormData) => {
    setIsSubmitting(true)
    try {
      onUpdate({ monitoring: formData })
    } finally {
      setIsSubmitting(false)
    }
  }

  const toggleLoggingScope = (scope: string) => {
    const current = loggingScope || []
    if (current.includes(scope)) {
      setValue('loggingScope', current.filter(s => s !== scope))
    } else {
      setValue('loggingScope', [...current, scope])
    }
  }

  const toggleFairnessMetric = (metric: string) => {
    const current = fairnessMetricsMonitored || []
    if (current.includes(metric)) {
      setValue('fairnessMetricsMonitored', current.filter(m => m !== metric))
    } else {
      setValue('fairnessMetricsMonitored', [...current, metric])
    }
  }

  const generateLoggingPlan = () => {
    const formData = watch()
    return `# Logging Plan

## Logging Scope
${formData.loggingScope?.map(scope => `- ${scope}`).join('\n') || 'No scope defined'}

## Log Retention Period
${formData.logRetentionPeriod || 'Not specified'}

## Drift Alert Threshold
${formData.driftAlertThreshold || 10}% deviation from baseline

## Fairness Metrics Monitored
${formData.fairnessMetricsMonitored?.map(metric => `- ${metric}`).join('\n') || 'No metrics defined'}

## Incident Register Tool
${formData.incidentRegisterTool || 'Not specified'}

## Corrective Action Tracking
${formData.correctiveActionTracking || 'Not defined'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
  }

  const generatePMMReport = () => {
    const formData = watch()
    return `# Post-Market Monitoring Report

## Monitoring Activities
- **Logging Scope**: ${formData.loggingScope?.join(', ') || 'Not defined'}
- **Retention Period**: ${formData.logRetentionPeriod || 'Not specified'}
- **Drift Threshold**: ${formData.driftAlertThreshold || 10}%

## Fairness Monitoring
${formData.fairnessMetricsMonitored?.map(metric => `- ${metric}`).join('\n') || 'No fairness metrics monitored'}

## Incident Management
- **Tool**: ${formData.incidentRegisterTool || 'Not specified'}
- **Tracking**: ${formData.correctiveActionTracking || 'Not defined'}

## Non-conformities
${formData.hasNonConformities ? 'Yes - Non-conformities identified' : 'No - No non-conformities identified'}
${formData.nonConformitiesDescription ? `\nDescription: ${formData.nonConformitiesDescription}` : ''}

## Audit Schedule
- **Internal Audits**: ${formData.internalAuditFrequency || 'Not specified'}
- **Management Reviews**: ${formData.managementReviewFrequency || 'Not specified'}

## Improvement Plan
${formData.improvementPlan || 'Not defined'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
  }

  const generateAuditLog = () => {
    const formData = watch()
    return `# Audit Log Template

## Audit Information
- **Frequency**: ${formData.internalAuditFrequency || 'Not specified'}
- **Management Review**: ${formData.managementReviewFrequency || 'Not specified'}

## Monitoring Scope
${formData.loggingScope?.map(scope => `- ${scope}`).join('\n') || 'No scope defined'}

## Non-conformities
${formData.hasNonConformities ? 'Yes' : 'No'}
${formData.nonConformitiesDescription ? `\nDetails: ${formData.nonConformitiesDescription}` : ''}

## Improvement Actions
${formData.improvementPlan || 'Not defined'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
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
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white mb-4"
        >
          <BarChart3 className="w-8 h-8" />
        </motion.div>
        <h2 className="text-3xl font-bold gradient-text">Monitoring & Improvement</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Set up monitoring, logging, and continuous improvement processes for your AI systems
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Logging Configuration */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Activity className="w-6 h-6 text-blue-500" />
                Logging Configuration
              </CardTitle>
              <CardDescription className="text-base">
                Define what will be logged and for how long
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <Label className="text-sm font-semibold">Logging Scope *</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {loggingScopes.map((scope, index) => (
                    <motion.div
                      key={scope}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.4 + index * 0.05 }}
                      className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 border border-border/50 hover:bg-muted/50 transition-all duration-300"
                    >
                      <Switch
                        id={`scope-${scope}`}
                        checked={loggingScope?.includes(scope) || false}
                        onCheckedChange={() => toggleLoggingScope(scope)}
                      />
                      <Label htmlFor={`scope-${scope}`} className="text-sm font-medium cursor-pointer">
                        {scope}
                      </Label>
                    </motion.div>
                  ))}
                </div>
                {errors.loggingScope && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.loggingScope.message}
                  </p>
                )}
              </div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Log Retention Period *</Label>
                <Select onValueChange={(value) => setValue('logRetentionPeriod', value)}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select retention period" />
                  </SelectTrigger>
                  <SelectContent>
                    {logRetentionPeriods.map(period => (
                      <SelectItem key={period} value={period}>{period}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.logRetentionPeriod && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.logRetentionPeriod.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="space-y-3"
              >
                <Label className="flex items-center gap-2 text-sm font-semibold">
                  <TrendingUp className="w-4 h-4 text-primary" />
                  Drift Alert Threshold: {driftAlertThreshold}%
                </Label>
                <div className="p-4 rounded-xl bg-muted/30 border border-border/50">
                  <Slider
                    value={[driftAlertThreshold || 10]}
                    onValueChange={(value) => setValue('driftAlertThreshold', value[0])}
                    max={100}
                    step={1}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Alert when model performance deviates by this percentage from baseline
                  </p>
                </div>
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Fairness Monitoring */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Shield className="w-6 h-6 text-green-500" />
                Fairness Monitoring
              </CardTitle>
              <CardDescription className="text-base">
                Define fairness metrics to monitor
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <Label className="text-sm font-semibold">Fairness Metrics Monitored *</Label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {fairnessMetrics.map((metric, index) => (
                    <motion.div
                      key={metric}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.8 + index * 0.05 }}
                      className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 border border-border/50 hover:bg-muted/50 transition-all duration-300"
                    >
                      <Switch
                        id={`metric-${metric}`}
                        checked={fairnessMetricsMonitored?.includes(metric) || false}
                        onCheckedChange={() => toggleFairnessMetric(metric)}
                      />
                      <Label htmlFor={`metric-${metric}`} className="text-sm font-medium cursor-pointer">
                        {metric}
                      </Label>
                    </motion.div>
                  ))}
                </div>
                {errors.fairnessMetricsMonitored && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.fairnessMetricsMonitored.message}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Incident Management */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <AlertTriangle className="w-6 h-6 text-orange-500" />
                Incident Management
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.0 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Incident Register Tool *</Label>
                <Select onValueChange={(value) => setValue('incidentRegisterTool', value)}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select incident register tool" />
                  </SelectTrigger>
                  <SelectContent>
                    {incidentRegisterTools.map(tool => (
                      <SelectItem key={tool} value={tool}>{tool}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.incidentRegisterTool && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.incidentRegisterTool.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.1 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Corrective Action Tracking *</Label>
                <Textarea
                  {...register('correctiveActionTracking')}
                  placeholder="Describe how corrective actions will be tracked and managed"
                  rows={4}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.correctiveActionTracking && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.correctiveActionTracking.message}
                  </p>
                )}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Non-conformities */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <CheckCircle className="w-6 h-6 text-purple-500" />
                Non-conformities
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 1.3 }}
                className="flex items-center space-x-3 p-4 rounded-xl bg-muted/30 border border-border/50"
              >
                <Switch
                  id="hasNonConformities"
                  checked={hasNonConformities}
                  onCheckedChange={(checked) => setValue('hasNonConformities', checked)}
                />
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-primary" />
                  <Label htmlFor="hasNonConformities" className="text-sm font-medium">
                    Non-conformities identified
                  </Label>
                </div>
              </motion.div>

              <AnimatePresence>
                {hasNonConformities && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    className="space-y-3"
                  >
                    <Label className="text-sm font-semibold">Non-conformities Description</Label>
                    <Textarea
                      {...register('nonConformitiesDescription')}
                      placeholder="Describe the identified non-conformities"
                      rows={4}
                      className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>

        {/* Audit Schedule */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.4 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Clock className="w-6 h-6 text-indigo-500" />
                Audit Schedule
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.5 }}
                  className="space-y-3"
                >
                  <Label className="text-sm font-semibold">Internal Audit Frequency *</Label>
                  <Select onValueChange={(value) => setValue('internalAuditFrequency', value)}>
                    <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      {auditFrequencies.map(frequency => (
                        <SelectItem key={frequency} value={frequency}>{frequency}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.internalAuditFrequency && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-destructive"></span>
                      {errors.internalAuditFrequency.message}
                    </p>
                  )}
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 1.6 }}
                  className="space-y-3"
                >
                  <Label className="text-sm font-semibold">Management Review Frequency *</Label>
                  <Select onValueChange={(value) => setValue('managementReviewFrequency', value)}>
                    <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                      <SelectValue placeholder="Select frequency" />
                    </SelectTrigger>
                    <SelectContent>
                      {auditFrequencies.map(frequency => (
                        <SelectItem key={frequency} value={frequency}>{frequency}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.managementReviewFrequency && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-destructive"></span>
                      {errors.managementReviewFrequency.message}
                    </p>
                  )}
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Improvement Plan */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.7 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <TrendingUp className="w-6 h-6 text-emerald-500" />
                Improvement Plan
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.8 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Improvement Plan *</Label>
                <Textarea
                  {...register('improvementPlan')}
                  placeholder="Describe the plan for continuous improvement of AI governance"
                  rows={5}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.improvementPlan && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.improvementPlan.message}
                  </p>
                )}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Template Preview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.9 }}
        >
          <Card  className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg text-primary flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Template Preview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowTemplatePreview(!showTemplatePreview)}
                  className="flex items-center gap-2"
                >
                  <Edit3 className="w-4 h-4" />
                  {showTemplatePreview ? 'Hide' : 'Show'} Templates
                </Button>
                
                <AnimatePresence>
                  {showTemplatePreview && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-4"
                    >
                      <div>
                        <h4 className="font-medium text-sm mb-2">Logging Plan Template:</h4>
                        <pre className="text-xs bg-background/70 p-4 rounded-lg border border-border/50 overflow-auto max-h-40">
                          {generateLoggingPlan()}
                        </pre>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm mb-2">PMM Report Template:</h4>
                        <pre className="text-xs bg-background/70 p-4 rounded-lg border border-border/50 overflow-auto max-h-40">
                          {generatePMMReport()}
                        </pre>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm mb-2">Audit Log Template:</h4>
                        <pre className="text-xs bg-background/70 p-4 rounded-lg border border-border/50 overflow-auto max-h-40">
                          {generateAuditLog()}
                        </pre>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* ISO Coverage Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0 }}
        >
          <Card  className="border-green-200/50 bg-green-50/50 dark:bg-green-950/20">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg text-green-800 dark:text-green-200">
                📋 ISO/IEC 42001 Coverage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-green-700 dark:text-green-300">
                <p className="mb-3 font-medium">This step covers the following ISO/IEC 42001 clauses:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">8.1</Badge>
                    <span>Operational planning and control</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">8.2</Badge>
                    <span>Performance evaluation</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">9.1</Badge>
                    <span>Monitoring, measurement, analysis and evaluation</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">9.2</Badge>
                    <span>Internal audit</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">9.3</Badge>
                    <span>Management review</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">10.1</Badge>
                    <span>Nonconformity and corrective action</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">10.2</Badge>
                    <span>Continual improvement</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Submit Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.1 }}
          className="flex justify-end"
        >
          <Button
            type="submit"
            disabled={!isValid || isSubmitting}
            variant="default"
            size="lg"
            className="min-w-[200px]"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Saving...
              </>
            ) : (
              <>
                Save & Continue
                <ArrowRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </motion.div>
      </form>
    </motion.div>
  )
}
