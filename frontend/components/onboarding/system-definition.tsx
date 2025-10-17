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
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Bot, Plus, Trash2, AlertTriangle, Shield, Users } from 'lucide-react'

const systemSchema = z.object({
  name: z.string().min(1, 'System name is required'),
  purpose: z.string().min(1, 'Purpose is required'),
  domain: z.string().min(1, 'Domain is required'),
  lifecycleStage: z.string().min(1, 'Lifecycle stage is required'),
  thirdPartyProviders: z.string().optional(),
  deploymentContext: z.string().min(1, 'Deployment context is required'),
  affectedUsers: z.string().min(1, 'Affected users description is required'),
  processesPersonalData: z.boolean(),
  impactsFundamentalRights: z.boolean(),
  riskCategory: z.string().min(1, 'Risk category is required'),
  systemOwner: z.string().email('Valid email is required')
})

const systemsSchema = z.object({
  systems: z.array(systemSchema).min(1, 'At least one system is required')
})

type SystemsFormData = z.infer<typeof systemsSchema>

interface SystemDefinitionProps {
  data?: any[]
  onUpdate: (data: any) => void
}

const domains = [
  'Healthcare',
  'Finance',
  'Education',
  'Transportation',
  'Public Services',
  'Marketing',
  'Human Resources',
  'Customer Service',
  'Research',
  'Other'
]

const lifecycleStages = [
  'Design',
  'Development',
  'Deployment',
  'Use',
  'Maintenance',
  'Decommissioning'
]

const deploymentContexts = [
  'Internal use only',
  'Public-facing application',
  'Embedded in products',
  'Third-party integration',
  'Research and development'
]

const riskCategories = [
  'Unacceptable Risk (Prohibited)',
  'High Risk (Annex III)',
  'Limited Risk (Transparency)',
  'Minimal Risk (No specific obligations)'
]

const aiActAnnexIIIRisks = [
  'Biometric identification and categorization',
  'Critical infrastructure',
  'Education and vocational training',
  'Employment, worker management',
  'Access to essential private services',
  'Law enforcement',
  'Migration, asylum and border control',
  'Administration of justice and democratic processes'
]

export default function SystemDefinition({ data, onUpdate }: SystemDefinitionProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<SystemsFormData>({
    resolver: zodResolver(systemsSchema),
    defaultValues: {
      systems: data && data.length > 0 ? data : [{
        name: '',
        purpose: '',
        domain: '',
        lifecycleStage: '',
        thirdPartyProviders: '',
        deploymentContext: '',
        affectedUsers: '',
        processesPersonalData: false,
        impactsFundamentalRights: false,
        riskCategory: '',
        systemOwner: ''
      }]
    }
  })

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'systems'
  })

  const systems = watch('systems')

  const onSubmit = async (formData: SystemsFormData) => {
    setIsSubmitting(true)
    try {
      onUpdate({ systems: formData.systems })
    } finally {
      setIsSubmitting(false)
    }
  }

  const addSystem = () => {
    append({
      name: '',
      purpose: '',
      domain: '',
      lifecycleStage: '',
      thirdPartyProviders: '',
      deploymentContext: '',
      affectedUsers: '',
      processesPersonalData: false,
      impactsFundamentalRights: false,
      riskCategory: '',
      systemOwner: ''
    })
  }

  const getRiskLevel = (riskCategory: string) => {
    if (riskCategory.includes('Unacceptable')) return { level: 'Critical', color: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' }
    if (riskCategory.includes('High Risk')) return { level: 'High', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300' }
    if (riskCategory.includes('Limited')) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' }
    return { level: 'Low', color: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300' }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold">AI Systems Definition</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Define your AI systems and their characteristics
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={addSystem}
          className="flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add System
        </Button>
      </div>

      {fields.map((field, index) => {
        const system = systems[index]
        const riskLevel = getRiskLevel(system?.riskCategory || '')
        
        return (
          <Card key={field.id} className="bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Bot className="w-5 h-5" />
                  System {index + 1}
                </CardTitle>
                {fields.length > 1 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => remove(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
              {system?.riskCategory && (
                <div className="flex items-center gap-2">
                  <Badge className={riskLevel.color}>
                    {riskLevel.level} Risk
                  </Badge>
                  {system.riskCategory.includes('High Risk') && (
                    <Badge variant="outline" className="text-orange-600 border-orange-300">
                      <AlertTriangle className="w-3 h-3 mr-1" />
                      AI Act Annex III
                    </Badge>
                  )}
                </div>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* System Name */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.name`}>System Name *</Label>
                  <Input
                    {...register(`systems.${index}.name`)}
                    placeholder="e.g., Customer Support Chatbot"
                    className="bg-white/70 dark:bg-gray-700/70"
                  />
                  {errors.systems?.[index]?.name && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.name?.message}</p>
                  )}
                </div>

                {/* Domain */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.domain`}>Domain *</Label>
                  <Select onValueChange={(value) => setValue(`systems.${index}.domain`, value)}>
                    <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                      <SelectValue placeholder="Select domain" />
                    </SelectTrigger>
                    <SelectContent>
                      {domains.map(domain => (
                        <SelectItem key={domain} value={domain}>{domain}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.systems?.[index]?.domain && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.domain?.message}</p>
                  )}
                </div>

                {/* Purpose */}
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor={`systems.${index}.purpose`}>Purpose / Decision Function *</Label>
                  <Textarea
                    {...register(`systems.${index}.purpose`)}
                    placeholder="Describe what the system does and its decision-making function"
                    rows={3}
                    className="bg-white/70 dark:bg-gray-700/70"
                  />
                  {errors.systems?.[index]?.purpose && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.purpose?.message}</p>
                  )}
                </div>

                {/* Lifecycle Stage */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.lifecycleStage`}>Lifecycle Stage *</Label>
                  <Select onValueChange={(value) => setValue(`systems.${index}.lifecycleStage`, value)}>
                    <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                      <SelectValue placeholder="Select stage" />
                    </SelectTrigger>
                    <SelectContent>
                      {lifecycleStages.map(stage => (
                        <SelectItem key={stage} value={stage}>{stage}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.systems?.[index]?.lifecycleStage && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.lifecycleStage?.message}</p>
                  )}
                </div>

                {/* Deployment Context */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.deploymentContext`}>Deployment Context *</Label>
                  <Select onValueChange={(value) => setValue(`systems.${index}.deploymentContext`, value)}>
                    <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                      <SelectValue placeholder="Select context" />
                    </SelectTrigger>
                    <SelectContent>
                      {deploymentContexts.map(context => (
                        <SelectItem key={context} value={context}>{context}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.systems?.[index]?.deploymentContext && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.deploymentContext?.message}</p>
                  )}
                </div>

                {/* Third-party Providers */}
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor={`systems.${index}.thirdPartyProviders`}>Third-party Providers / Datasets</Label>
                  <Textarea
                    {...register(`systems.${index}.thirdPartyProviders`)}
                    placeholder="List any third-party providers, datasets, or external services used"
                    rows={2}
                    className="bg-white/70 dark:bg-gray-700/70"
                  />
                </div>

                {/* Affected Users */}
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor={`systems.${index}.affectedUsers`} className="flex items-center gap-2">
                    <Users className="w-4 h-4" />
                    Affected Users *
                  </Label>
                  <Textarea
                    {...register(`systems.${index}.affectedUsers`)}
                    placeholder="Describe who is affected by this system (employees, customers, public, etc.)"
                    rows={2}
                    className="bg-white/70 dark:bg-gray-700/70"
                  />
                  {errors.systems?.[index]?.affectedUsers && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.affectedUsers?.message}</p>
                  )}
                </div>

                {/* Data Processing Flags */}
                <div className="space-y-4 md:col-span-2">
                  <div className="flex items-center space-x-2">
                    <Switch
                      id={`systems.${index}.processesPersonalData`}
                      checked={system?.processesPersonalData || false}
                      onCheckedChange={(checked) => setValue(`systems.${index}.processesPersonalData`, checked)}
                    />
                    <Label htmlFor={`systems.${index}.processesPersonalData`} className="flex items-center gap-2">
                      <Shield className="w-4 h-4" />
                      Processes personal data
                    </Label>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id={`systems.${index}.impactsFundamentalRights`}
                      checked={system?.impactsFundamentalRights || false}
                      onCheckedChange={(checked) => setValue(`systems.${index}.impactsFundamentalRights`, checked)}
                    />
                    <Label htmlFor={`systems.${index}.impactsFundamentalRights`} className="flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      Impacts fundamental rights
                    </Label>
                  </div>
                </div>

                {/* Risk Category */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.riskCategory`}>Risk Category *</Label>
                  <Select onValueChange={(value) => setValue(`systems.${index}.riskCategory`, value)}>
                    <SelectTrigger className="bg-white/70 dark:bg-gray-700/70">
                      <SelectValue placeholder="Select risk category" />
                    </SelectTrigger>
                    <SelectContent>
                      {riskCategories.map(category => (
                        <SelectItem key={category} value={category}>{category}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {errors.systems?.[index]?.riskCategory && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.riskCategory?.message}</p>
                  )}
                </div>

                {/* System Owner */}
                <div className="space-y-2">
                  <Label htmlFor={`systems.${index}.systemOwner`}>System Owner Email *</Label>
                  <Input
                    {...register(`systems.${index}.systemOwner`)}
                    type="email"
                    placeholder="owner@company.com"
                    className="bg-white/70 dark:bg-gray-700/70"
                  />
                  {errors.systems?.[index]?.systemOwner && (
                    <p className="text-sm text-red-500">{errors.systems[index]?.systemOwner?.message}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}

      {/* AI Act Annex III Info */}
      <Card className="bg-orange-50 dark:bg-orange-950/20 border-orange-200 dark:border-orange-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-orange-800 dark:text-orange-200 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            EU AI Act - High Risk Systems (Annex III)
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="text-sm text-orange-700 dark:text-orange-300">
            <p className="mb-2">High-risk AI systems include:</p>
            <ul className="list-disc list-inside space-y-1">
              {aiActAnnexIIIRisks.map(risk => (
                <li key={risk}>{risk}</li>
              ))}
            </ul>
            <p className="mt-2 font-medium">These systems require additional compliance measures under the EU AI Act.</p>
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
