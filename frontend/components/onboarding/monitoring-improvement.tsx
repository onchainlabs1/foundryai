'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
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
  TrendingUp
} from 'lucide-react'

const monitoringSchema = z.object({
  loggingScope: z.array(z.string()).min(1, 'At least one logging scope is required'),
  logRetentionPeriod: z.string().min(1, 'Log retention period is required'),
  driftAlertThreshold: z.number().min(0).max(100),
  fairnessMetricsMonitored: z.array(z.string()).min(1, 'At least one fairness metric is required'),
  incidentRegisterTool: z.string().min(1, 'Incident register tool is required'),
  correctiveActionTracking: z.string().min(1, 'Corrective action tracking is required'),
  hasNonConformities: z.boolean(),
  nonConformitiesDescription: z.string().optional(),
  internalAuditFrequency: z.string().min(1, 'Internal audit frequency is required'),
  managementReviewFrequency: z.string().min(1, 'Management review frequency is required'),
  improvementPlan: z.string().min(1, 'Improvement plan is required')
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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Logging Configuration */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-blue-500" />
            Logging Configuration
          </CardTitle>
          <CardDescription>
            Define what will be logged and for how long
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <Label>Logging Scope *</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {loggingScopes.map(scope => (
                <div key={scope} className="flex items-center space-x-2">
                  <Switch
                    id={`scope-${scope}`}
                    checked={loggingScope?.includes(scope) || false}
                    onCheckedChange={() => toggleLoggingScope(scope)}
                  />
                  <Label htmlFor={`scope-${scope}`} className="text-sm">
                    {scope}
                  </Label>
                </div>
              ))}
            </div>
            {errors.loggingScope && (
              <p className="text-sm text-red-500">{errors.loggingScope.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Log Retention Period *</Label>
            <Select onValueChange={(value) => setValue('logRetentionPeriod', value)}>
              <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                <SelectValue placeholder="Select retention period" />
              </SelectTrigger>
              <SelectContent>
                {logRetentionPeriods.map(period => (
                  <SelectItem key={period} value={period}>{period}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.logRetentionPeriod && (
              <p className="text-sm text-red-500">{errors.logRetentionPeriod.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Drift Alert Threshold: {driftAlertThreshold}%
            </Label>
            <Slider
              value={[driftAlertThreshold]}
              onValueChange={(value) => setValue('driftAlertThreshold', value[0])}
              max={100}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-500">
              Alert when model performance deviates by this percentage from baseline
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Fairness Monitoring */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-green-500" />
            Fairness Monitoring
          </CardTitle>
          <CardDescription>
            Define fairness metrics to monitor
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <Label>Fairness Metrics Monitored *</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {fairnessMetrics.map(metric => (
                <div key={metric} className="flex items-center space-x-2">
                  <Switch
                    id={`metric-${metric}`}
                    checked={fairnessMetricsMonitored?.includes(metric) || false}
                    onCheckedChange={() => toggleFairnessMetric(metric)}
                  />
                  <Label htmlFor={`metric-${metric}`} className="text-sm">
                    {metric}
                  </Label>
                </div>
              ))}
            </div>
            {errors.fairnessMetricsMonitored && (
              <p className="text-sm text-red-500">{errors.fairnessMetricsMonitored.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Incident Management */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            Incident Management
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Incident Register Tool *</Label>
            <Select onValueChange={(value) => setValue('incidentRegisterTool', value)}>
              <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                <SelectValue placeholder="Select incident register tool" />
              </SelectTrigger>
              <SelectContent>
                {incidentRegisterTools.map(tool => (
                  <SelectItem key={tool} value={tool}>{tool}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.incidentRegisterTool && (
              <p className="text-sm text-red-500">{errors.incidentRegisterTool.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Corrective Action Tracking *</Label>
            <Textarea
              {...register('correctiveActionTracking')}
              placeholder="Describe how corrective actions will be tracked and managed"
              rows={3}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.correctiveActionTracking && (
              <p className="text-sm text-red-500">{errors.correctiveActionTracking.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Non-conformities */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-purple-500" />
            Non-conformities
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="hasNonConformities"
              checked={hasNonConformities}
              onCheckedChange={(checked) => setValue('hasNonConformities', checked)}
            />
            <Label htmlFor="hasNonConformities" className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Non-conformities identified
            </Label>
          </div>

          {hasNonConformities && (
            <div className="space-y-2">
              <Label>Non-conformities Description</Label>
              <Textarea
                {...register('nonConformitiesDescription')}
                placeholder="Describe the identified non-conformities"
                rows={3}
                className="bg-white/70 dark:bg-gray-700/70"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Audit Schedule */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5 text-indigo-500" />
            Audit Schedule
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Internal Audit Frequency *</Label>
              <Select onValueChange={(value) => setValue('internalAuditFrequency', value)}>
                <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  {auditFrequencies.map(frequency => (
                    <SelectItem key={frequency} value={frequency}>{frequency}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.internalAuditFrequency && (
                <p className="text-sm text-red-500">{errors.internalAuditFrequency.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Management Review Frequency *</Label>
              <Select onValueChange={(value) => setValue('managementReviewFrequency', value)}>
                <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                  <SelectValue placeholder="Select frequency" />
                </SelectTrigger>
                <SelectContent>
                  {auditFrequencies.map(frequency => (
                    <SelectItem key={frequency} value={frequency}>{frequency}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.managementReviewFrequency && (
                <p className="text-sm text-red-500">{errors.managementReviewFrequency.message}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Improvement Plan */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-500" />
            Improvement Plan
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Improvement Plan *</Label>
            <Textarea
              {...register('improvementPlan')}
              placeholder="Describe the plan for continuous improvement of AI governance"
              rows={4}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.improvementPlan && (
              <p className="text-sm text-red-500">{errors.improvementPlan.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Template Preview */}
      <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="text-sm text-blue-800 dark:text-blue-200 flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Template Preview
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            <div className="flex gap-2">
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
            </div>
            
            {showTemplatePreview && (
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-sm mb-2">Logging Plan Template:</h4>
                  <pre className="text-xs bg-white/70 dark:bg-gray-800/70 p-3 rounded border overflow-auto max-h-40">
                    {generateLoggingPlan()}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">PMM Report Template:</h4>
                  <pre className="text-xs bg-white/70 dark:bg-gray-800/70 p-3 rounded border overflow-auto max-h-40">
                    {generatePMMReport()}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Audit Log Template:</h4>
                  <pre className="text-xs bg-white/70 dark:bg-gray-800/70 p-3 rounded border overflow-auto max-h-40">
                    {generateAuditLog()}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* ISO Coverage Info */}
      <Card className="bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-green-800 dark:text-green-200">
            📋 ISO/IEC 42001 Coverage
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="text-sm text-green-700 dark:text-green-300">
            <p className="mb-2">This step covers:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Clause 8.1: Operational planning and control</li>
              <li>Clause 8.2: Performance evaluation</li>
              <li>Clause 9.1: Monitoring, measurement, analysis and evaluation</li>
              <li>Clause 9.2: Internal audit</li>
              <li>Clause 9.3: Management review</li>
              <li>Clause 10.1: Nonconformity and corrective action</li>
              <li>Clause 10.2: Continual improvement</li>
            </ul>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {isSubmitting ? 'Saving...' : 'Save & Continue'}
        </Button>
      </div>
    </form>
  )
}
