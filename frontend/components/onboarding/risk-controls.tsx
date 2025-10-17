'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { 
  Shield, 
  AlertTriangle, 
  Plus, 
  Trash2, 
  FileText, 
  CheckCircle,
  Upload,
  Edit3
} from 'lucide-react'

const riskSchema = z.object({
  topRisks: z.array(z.string()).min(1, 'At least one risk is required'),
  likelihood: z.string().min(1, 'Likelihood assessment is required'),
  impact: z.string().min(1, 'Impact assessment is required'),
  mitigationActions: z.string().min(1, 'Mitigation actions are required'),
  residualRisk: z.string().min(1, 'Residual risk assessment is required'),
  riskAcceptanceCriteria: z.string().min(1, 'Risk acceptance criteria are required'),
  riskOwner: z.string().min(1, 'Risk owner is required'),
  controlsSelected: z.array(z.string()).min(1, 'At least one control is required'),
  relatedPolicies: z.array(z.string()).optional(),
  modelValidationMethod: z.string().min(1, 'Model validation method is required'),
  continuousMonitoringPlan: z.string().min(1, 'Continuous monitoring plan is required'),
  existingEvidence: z.string().optional()
})

type RiskFormData = z.infer<typeof riskSchema>

interface RiskControlsProps {
  data?: any
  onUpdate: (data: any) => void
}

const likelihoodOptions = [
  { value: 'Low', label: 'Low (1-3)' },
  { value: 'Medium', label: 'Medium (4-6)' },
  { value: 'High', label: 'High (7-9)' }
]

const impactOptions = [
  { value: 'Low', label: 'Low (1-3)' },
  { value: 'Medium', label: 'Medium (4-6)' },
  { value: 'High', label: 'High (7-9)' }
]

const riskOwners = [
  'CTO',
  'AI Ethics Officer',
  'Risk Manager',
  'Legal Counsel',
  'Product Manager',
  'Data Protection Officer',
  'Other'
]

const availableControls = [
  'Data Quality Controls',
  'Model Validation',
  'Bias Detection',
  'Human Oversight',
  'Audit Logging',
  'Access Controls',
  'Data Minimization',
  'Transparency Measures',
  'Explainability Requirements',
  'Performance Monitoring',
  'Incident Response',
  'Regular Reviews'
]

const relatedPolicies = [
  'AI Ethics Policy',
  'Data Protection Policy',
  'Risk Management Policy',
  'Model Governance Policy',
  'Incident Response Policy',
  'Audit Policy',
  'Training Policy'
]

export default function RiskControls({ data, onUpdate }: RiskControlsProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showTemplatePreview, setShowTemplatePreview] = useState(false)
  
  const form = useForm<RiskFormData>({
    resolver: zodResolver(riskSchema),
    defaultValues: {
      topRisks: data?.topRisks || [''],
      likelihood: data?.likelihood || '',
      impact: data?.impact || '',
      mitigationActions: data?.mitigationActions || '',
      residualRisk: data?.residualRisk || '',
      riskAcceptanceCriteria: data?.riskAcceptanceCriteria || '',
      riskOwner: data?.riskOwner || '',
      controlsSelected: data?.controlsSelected || [],
      relatedPolicies: data?.relatedPolicies || [],
      modelValidationMethod: data?.modelValidationMethod || '',
      continuousMonitoringPlan: data?.continuousMonitoringPlan || '',
      existingEvidence: data?.existingEvidence || ''
    }
  })

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isValid }
  } = form

  const topRisks = watch('topRisks')
  const controlsSelected = watch('controlsSelected')
  const relatedPolicies = watch('relatedPolicies')

  const onSubmit = async (formData: RiskFormData) => {
    setIsSubmitting(true)
    try {
      onUpdate({ risks: formData })
    } finally {
      setIsSubmitting(false)
    }
  }

  const addRiskItem = () => {
    setValue('topRisks', [...(topRisks || []), ''])
  }

  const removeRiskItem = (index: number) => {
    const newRisks = [...(topRisks || [])]
    newRisks.splice(index, 1)
    setValue('topRisks', newRisks)
  }

  const toggleControl = (control: string) => {
    const current = controlsSelected || []
    if (current.includes(control)) {
      setValue('controlsSelected', current.filter(c => c !== control))
    } else {
      setValue('controlsSelected', [...current, control])
    }
  }

  const togglePolicy = (policy: string) => {
    const current = relatedPolicies || []
    if (current.includes(policy)) {
      setValue('relatedPolicies', current.filter(p => p !== policy))
    } else {
      setValue('relatedPolicies', [...current, policy])
    }
  }

  const generateRiskAssessment = () => {
    const formData = watch()
    return `# Risk Assessment

## Identified Risks
${formData.topRisks?.filter(risk => risk.trim()).map(risk => `- ${risk}`).join('\n') || 'No risks identified'}

## Risk Analysis
- **Likelihood**: ${formData.likelihood || 'Not assessed'}
- **Impact**: ${formData.impact || 'Not assessed'}

## Mitigation Actions
${formData.mitigationActions || 'No mitigation actions defined'}

## Residual Risk
${formData.residualRisk || 'Not assessed'}

## Risk Acceptance Criteria
${formData.riskAcceptanceCriteria || 'Not defined'}

## Risk Owner
${formData.riskOwner || 'Not assigned'}

## Selected Controls
${formData.controlsSelected?.map(control => `- ${control}`).join('\n') || 'No controls selected'}

## Model Validation Method
${formData.modelValidationMethod || 'Not specified'}

## Continuous Monitoring Plan
${formData.continuousMonitoringPlan || 'Not defined'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
  }

  const generateModelCard = () => {
    return `# Model Card

## Model Information
- **Validation Method**: ${watch('modelValidationMethod') || 'Not specified'}
- **Monitoring Plan**: ${watch('continuousMonitoringPlan') || 'Not defined'}

## Risk Assessment
- **Likelihood**: ${watch('likelihood') || 'Not assessed'}
- **Impact**: ${watch('impact') || 'Not assessed'}

## Controls Implemented
${watch('controlsSelected')?.map(control => `- ${control}`).join('\n') || 'No controls selected'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Risk Identification */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-500" />
            Risk Identification
          </CardTitle>
          <CardDescription>
            Identify and assess the top risks associated with your AI systems
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-3">
            <Label>Top Risks *</Label>
            {topRisks?.map((risk, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  {...register(`topRisks.${index}`)}
                  placeholder={`Risk ${index + 1}: Describe the risk`}
                  className="bg-white/70 dark:bg-gray-700/70"
                />
                {topRisks.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeRiskItem(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              onClick={addRiskItem}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Risk
            </Button>
            {errors.topRisks && (
              <p className="text-sm text-red-500">{errors.topRisks.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Risk Assessment */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-500" />
            Risk Assessment
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Likelihood *</Label>
              <Select onValueChange={(value) => setValue('likelihood', value)}>
                <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                  <SelectValue placeholder="Select likelihood" />
                </SelectTrigger>
                <SelectContent>
                  {likelihoodOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.likelihood && (
                <p className="text-sm text-red-500">{errors.likelihood.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Impact *</Label>
              <Select onValueChange={(value) => setValue('impact', value)}>
                <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                  <SelectValue placeholder="Select impact" />
                </SelectTrigger>
                <SelectContent>
                  {impactOptions.map(option => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.impact && (
                <p className="text-sm text-red-500">{errors.impact.message}</p>
              )}
            </div>
          </div>

          <div className="space-y-2">
            <Label>Mitigation Actions *</Label>
            <Textarea
              {...register('mitigationActions')}
              placeholder="Describe the actions taken to mitigate identified risks"
              rows={3}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.mitigationActions && (
              <p className="text-sm text-red-500">{errors.mitigationActions.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Residual Risk *</Label>
            <Textarea
              {...register('residualRisk')}
              placeholder="Describe the remaining risk after mitigation measures"
              rows={2}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.residualRisk && (
              <p className="text-sm text-red-500">{errors.residualRisk.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Risk Acceptance Criteria *</Label>
            <Textarea
              {...register('riskAcceptanceCriteria')}
              placeholder="Define the criteria for accepting residual risks"
              rows={2}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.riskAcceptanceCriteria && (
              <p className="text-sm text-red-500">{errors.riskAcceptanceCriteria.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Risk Owner *</Label>
            <Select onValueChange={(value) => setValue('riskOwner', value)}>
              <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                <SelectValue placeholder="Select risk owner" />
              </SelectTrigger>
              <SelectContent>
                {riskOwners.map(owner => (
                  <SelectItem key={owner} value={owner}>{owner}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.riskOwner && (
              <p className="text-sm text-red-500">{errors.riskOwner.message}</p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Controls Selection */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            Controls Selection
          </CardTitle>
          <CardDescription>
            Select the controls that will be implemented to manage risks
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {availableControls.map(control => (
              <div key={control} className="flex items-center space-x-2">
                <Switch
                  id={`control-${control}`}
                  checked={controlsSelected?.includes(control) || false}
                  onCheckedChange={() => toggleControl(control)}
                />
                <Label htmlFor={`control-${control}`} className="text-sm">
                  {control}
                </Label>
              </div>
            ))}
          </div>
          {errors.controlsSelected && (
            <p className="text-sm text-red-500">{errors.controlsSelected.message}</p>
          )}
        </CardContent>
      </Card>

      {/* Related Policies */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-500" />
            Related Policies
          </CardTitle>
          <CardDescription>
            Select policies that are related to AI governance
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {relatedPolicies?.map(policy => (
              <div key={policy} className="flex items-center space-x-2">
                <Switch
                  id={`policy-${policy}`}
                  checked={relatedPolicies?.includes(policy) || false}
                  onCheckedChange={() => togglePolicy(policy)}
                />
                <Label htmlFor={`policy-${policy}`} className="text-sm">
                  {policy}
                </Label>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Model Validation & Monitoring */}
      <Card className="bg-white/50 dark:bg-gray-800/50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-500" />
            Model Validation & Monitoring
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Model Validation Method *</Label>
            <Textarea
              {...register('modelValidationMethod')}
              placeholder="Describe how the model will be validated (testing, benchmarking, etc.)"
              rows={3}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.modelValidationMethod && (
              <p className="text-sm text-red-500">{errors.modelValidationMethod.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Continuous Monitoring Plan *</Label>
            <Textarea
              {...register('continuousMonitoringPlan')}
              placeholder="Describe the plan for continuous monitoring of the AI system"
              rows={3}
              className="bg-white/70 dark:bg-gray-700/70"
            />
            {errors.continuousMonitoringPlan && (
              <p className="text-sm text-red-500">{errors.continuousMonitoringPlan.message}</p>
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
                  <h4 className="font-medium text-sm mb-2">Risk Assessment Template:</h4>
                  <pre className="text-xs bg-white/70 dark:bg-gray-800/70 p-3 rounded border overflow-auto max-h-40">
                    {generateRiskAssessment()}
                  </pre>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Model Card Template:</h4>
                  <pre className="text-xs bg-white/70 dark:bg-gray-800/70 p-3 rounded border overflow-auto max-h-40">
                    {generateModelCard()}
                  </pre>
                </div>
              </div>
            )}
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
