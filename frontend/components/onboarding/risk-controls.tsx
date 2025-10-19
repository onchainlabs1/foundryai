'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
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
  Edit3,
  ArrowRight,
  Target,
  Zap
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
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-red-600 text-white mb-4"
        >
          <Shield className="w-8 h-8" />
        </motion.div>
        <h2 className="text-3xl font-bold gradient-text">Risk & Controls</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Identify risks and implement controls to manage AI system governance
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Risk Identification */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <AlertTriangle className="w-6 h-6 text-orange-500" />
                Risk Identification
              </CardTitle>
              <CardDescription className="text-base">
                Identify and assess the top risks associated with your AI systems
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <Label className="text-sm font-semibold">Top Risks *</Label>
                <AnimatePresence>
                  {topRisks?.map((risk, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.2 }}
                      className="flex gap-3"
                    >
                      <div className="flex-1">
                        <Input
                          {...register(`topRisks.${index}`)}
                          placeholder={`Risk ${index + 1}: Describe the risk`}
                          className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                        />
                      </div>
                      {topRisks.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removeRiskItem(index)}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10 h-12 w-12"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </motion.div>
                  ))}
                </AnimatePresence>
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
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.topRisks.message}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Risk Assessment */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Target className="w-6 h-6 text-blue-500" />
                Risk Assessment
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 }}
                  className="space-y-3"
                >
                  <Label className="text-sm font-semibold">Likelihood *</Label>
                  <Select onValueChange={(value) => setValue('likelihood', value)}>
                    <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
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
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-destructive"></span>
                      {errors.likelihood.message}
                    </p>
                  )}
                </motion.div>

                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 }}
                  className="space-y-3"
                >
                  <Label className="text-sm font-semibold">Impact *</Label>
                  <Select onValueChange={(value) => setValue('impact', value)}>
                    <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
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
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <span className="w-1 h-1 rounded-full bg-destructive"></span>
                      {errors.impact.message}
                    </p>
                  )}
                </motion.div>
              </div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Mitigation Actions *</Label>
                <Textarea
                  {...register('mitigationActions')}
                  placeholder="Describe the actions taken to mitigate identified risks"
                  rows={4}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.mitigationActions && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.mitigationActions.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Residual Risk *</Label>
                <Textarea
                  {...register('residualRisk')}
                  placeholder="Describe the remaining risk after mitigation measures"
                  rows={3}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.residualRisk && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.residualRisk.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Risk Acceptance Criteria *</Label>
                <Textarea
                  {...register('riskAcceptanceCriteria')}
                  placeholder="Define the criteria for accepting residual risks"
                  rows={3}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.riskAcceptanceCriteria && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.riskAcceptanceCriteria.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Risk Owner *</Label>
                <Select onValueChange={(value) => setValue('riskOwner', value)}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select risk owner" />
                  </SelectTrigger>
                  <SelectContent>
                    {riskOwners.map(owner => (
                      <SelectItem key={owner} value={owner}>{owner}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.riskOwner && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.riskOwner.message}
                  </p>
                )}
              </motion.div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Controls Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Zap className="w-6 h-6 text-green-500" />
                Controls Selection
              </CardTitle>
              <CardDescription className="text-base">
                Select the controls that will be implemented to manage risks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {availableControls.map((control, index) => (
                  <motion.div
                    key={control}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.2 + index * 0.05 }}
                    className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 border border-border/50 hover:bg-muted/50 transition-all duration-300"
                  >
                    <Switch
                      id={`control-${control}`}
                      checked={controlsSelected?.includes(control) || false}
                      onCheckedChange={() => toggleControl(control)}
                    />
                    <Label htmlFor={`control-${control}`} className="text-sm font-medium cursor-pointer">
                      {control}
                    </Label>
                  </motion.div>
                ))}
              </div>
              {errors.controlsSelected && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <span className="w-1 h-1 rounded-full bg-destructive"></span>
                  {errors.controlsSelected.message}
                </p>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Related Policies */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <FileText className="w-6 h-6 text-purple-500" />
                Related Policies
              </CardTitle>
              <CardDescription className="text-base">
                Select policies that are related to AI governance
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {relatedPolicies?.map((policy, index) => (
                  <motion.div
                    key={policy}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 1.4 + index * 0.05 }}
                    className="flex items-center space-x-3 p-3 rounded-lg bg-muted/30 border border-border/50 hover:bg-muted/50 transition-all duration-300"
                  >
                    <Switch
                      id={`policy-${policy}`}
                      checked={relatedPolicies?.includes(policy) || false}
                      onCheckedChange={() => togglePolicy(policy)}
                    />
                    <Label htmlFor={`policy-${policy}`} className="text-sm font-medium cursor-pointer">
                      {policy}
                    </Label>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Model Validation & Monitoring */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
        >
          <Card  className="p-6">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center gap-3 text-xl">
                <Shield className="w-6 h-6 text-indigo-500" />
                Model Validation & Monitoring
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.6 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Model Validation Method *</Label>
                <Textarea
                  {...register('modelValidationMethod')}
                  placeholder="Describe how the model will be validated (testing, benchmarking, etc.)"
                  rows={4}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.modelValidationMethod && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.modelValidationMethod.message}
                  </p>
                )}
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.7 }}
                className="space-y-3"
              >
                <Label className="text-sm font-semibold">Continuous Monitoring Plan *</Label>
                <Textarea
                  {...register('continuousMonitoringPlan')}
                  placeholder="Describe the plan for continuous monitoring of the AI system"
                  rows={4}
                  className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                />
                {errors.continuousMonitoringPlan && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.continuousMonitoringPlan.message}
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
          transition={{ delay: 1.8 }}
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
                        <h4 className="font-medium text-sm mb-2">Risk Assessment Template:</h4>
                        <pre className="text-xs bg-background/70 p-4 rounded-lg border border-border/50 overflow-auto max-h-40">
                          {generateRiskAssessment()}
                        </pre>
                      </div>
                      <div>
                        <h4 className="font-medium text-sm mb-2">Model Card Template:</h4>
                        <pre className="text-xs bg-background/70 p-4 rounded-lg border border-border/50 overflow-auto max-h-40">
                          {generateModelCard()}
                        </pre>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Submit Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.9 }}
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
