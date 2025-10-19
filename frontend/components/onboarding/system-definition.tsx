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
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Bot, Plus, Trash2, AlertTriangle, Shield, Users, ArrowRight, Sparkles } from 'lucide-react'

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
  systemOwner: z.string().email('Valid email is required'),
  tempId: z.string().optional() // Stable UUID for deterministic mapping
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
      systemOwner: '',
      tempId: crypto.randomUUID() // Generate stable UUID for new systems
    })
  }

  const getRiskLevel = (riskCategory: string) => {
    if (riskCategory.includes('Unacceptable')) return { level: 'Critical', color: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300' }
    if (riskCategory.includes('High Risk')) return { level: 'High', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300' }
    if (riskCategory.includes('Limited')) return { level: 'Medium', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300' }
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
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-600 text-white mb-4"
        >
          <Bot className="w-8 h-8" />
        </motion.div>
        <h2 className="text-3xl font-bold gradient-text">AI Systems Definition</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Define your AI systems and their characteristics for compliance assessment
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Systems Header */}
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              AI Systems ({fields.length})
            </h3>
            <p className="text-muted-foreground">
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

        {/* Systems List */}
        <AnimatePresence>
          {fields.map((field, index) => {
            const system = systems[index]
            const riskLevel = getRiskLevel(system?.riskCategory || '')
            
            return (
              <motion.div
                key={field.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                layout
              >
                <Card  className="p-6 border-border/50">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-xl flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-600 text-white">
                          <Bot className="w-5 h-5" />
                        </div>
                        System {index + 1}
                      </CardTitle>
                      {fields.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => remove(index)}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    {system?.riskCategory && (
                      <div className="flex items-center gap-2 mt-2">
                        <Badge variant={riskLevel.level === 'Critical' ? 'destructive' : riskLevel.level === 'High' ? 'secondary' : 'secondary'}>
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
                  <CardContent className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* System Name */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.name`} className="text-sm font-semibold">System Name *</Label>
                        <Input
                          {...register(`systems.${index}.name`)}
                          placeholder="e.g., Customer Support Chatbot"
                          className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                        />
                        {errors.systems?.[index]?.name && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.name?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Domain */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.domain`} className="text-sm font-semibold">Domain *</Label>
                        <Select onValueChange={(value) => setValue(`systems.${index}.domain`, value)}>
                          <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                            <SelectValue placeholder="Select domain" />
                          </SelectTrigger>
                          <SelectContent>
                            {domains.map(domain => (
                              <SelectItem key={domain} value={domain}>{domain}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {errors.systems?.[index]?.domain && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.domain?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Purpose */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="space-y-3 md:col-span-2"
                      >
                        <Label htmlFor={`systems.${index}.purpose`} className="text-sm font-semibold">Purpose / Decision Function *</Label>
                        <Textarea
                          {...register(`systems.${index}.purpose`)}
                          placeholder="Describe what the system does and its decision-making function"
                          rows={4}
                          className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                        />
                        {errors.systems?.[index]?.purpose && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.purpose?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Lifecycle Stage */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.lifecycleStage`} className="text-sm font-semibold">Lifecycle Stage *</Label>
                        <Select onValueChange={(value) => setValue(`systems.${index}.lifecycleStage`, value)}>
                          <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                            <SelectValue placeholder="Select stage" />
                          </SelectTrigger>
                          <SelectContent>
                            {lifecycleStages.map(stage => (
                              <SelectItem key={stage} value={stage}>{stage}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {errors.systems?.[index]?.lifecycleStage && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.lifecycleStage?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Deployment Context */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.deploymentContext`} className="text-sm font-semibold">Deployment Context *</Label>
                        <Select onValueChange={(value) => setValue(`systems.${index}.deploymentContext`, value)}>
                          <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                            <SelectValue placeholder="Select context" />
                          </SelectTrigger>
                          <SelectContent>
                            {deploymentContexts.map(context => (
                              <SelectItem key={context} value={context}>{context}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {errors.systems?.[index]?.deploymentContext && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.deploymentContext?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Third-party Providers */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="space-y-3 md:col-span-2"
                      >
                        <Label htmlFor={`systems.${index}.thirdPartyProviders`} className="text-sm font-semibold">Third-party Providers / Datasets</Label>
                        <Textarea
                          {...register(`systems.${index}.thirdPartyProviders`)}
                          placeholder="List any third-party providers, datasets, or external services used"
                          rows={3}
                          className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                        />
                        <p className="text-xs text-muted-foreground">Optional: External dependencies and data sources</p>
                      </motion.div>

                      {/* Affected Users */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.7 }}
                        className="space-y-3 md:col-span-2"
                      >
                        <Label htmlFor={`systems.${index}.affectedUsers`} className="flex items-center gap-2 text-sm font-semibold">
                          <Users className="w-4 h-4 text-primary" />
                          Affected Users *
                        </Label>
                        <Textarea
                          {...register(`systems.${index}.affectedUsers`)}
                          placeholder="Describe who is affected by this system (employees, customers, public, etc.)"
                          rows={3}
                          className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
                        />
                        {errors.systems?.[index]?.affectedUsers && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.affectedUsers?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* Data Processing Flags */}
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.8 }}
                        className="space-y-4 md:col-span-2"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="flex items-center space-x-3 p-4 rounded-xl bg-muted/30 border border-border/50">
                            <Switch
                              id={`systems.${index}.processesPersonalData`}
                              checked={system?.processesPersonalData || false}
                              onCheckedChange={(checked) => setValue(`systems.${index}.processesPersonalData`, checked)}
                            />
                            <div className="flex items-center gap-2">
                              <Shield className="w-4 h-4 text-primary" />
                              <Label htmlFor={`systems.${index}.processesPersonalData`} className="text-sm">
                                Processes personal data
                              </Label>
                            </div>
                          </div>

                          <div className="flex items-center space-x-3 p-4 rounded-xl bg-muted/30 border border-border/50">
                            <Switch
                              id={`systems.${index}.impactsFundamentalRights`}
                              checked={system?.impactsFundamentalRights || false}
                              onCheckedChange={(checked) => setValue(`systems.${index}.impactsFundamentalRights`, checked)}
                            />
                            <div className="flex items-center gap-2">
                              <AlertTriangle className="w-4 h-4 text-primary" />
                              <Label htmlFor={`systems.${index}.impactsFundamentalRights`} className="text-sm">
                                Impacts fundamental rights
                              </Label>
                            </div>
                          </div>
                        </div>
                      </motion.div>

                      {/* Risk Category */}
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.9 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.riskCategory`} className="text-sm font-semibold">Risk Category *</Label>
                        <Select onValueChange={(value) => setValue(`systems.${index}.riskCategory`, value)}>
                          <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                            <SelectValue placeholder="Select risk category" />
                          </SelectTrigger>
                          <SelectContent>
                            {riskCategories.map(category => (
                              <SelectItem key={category} value={category}>{category}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        {errors.systems?.[index]?.riskCategory && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.riskCategory?.message}
                          </p>
                        )}
                      </motion.div>

                      {/* System Owner */}
                      <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1.0 }}
                        className="space-y-3"
                      >
                        <Label htmlFor={`systems.${index}.systemOwner`} className="text-sm font-semibold">System Owner Email *</Label>
                        <Input
                          {...register(`systems.${index}.systemOwner`)}
                          type="email"
                          placeholder="owner@company.com"
                          className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                        />
                        {errors.systems?.[index]?.systemOwner && (
                          <p className="text-sm text-destructive flex items-center gap-1">
                            <span className="w-1 h-1 rounded-full bg-destructive"></span>
                            {errors.systems[index]?.systemOwner?.message}
                          </p>
                        )}
                      </motion.div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </AnimatePresence>

        {/* AI Act Annex III Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
        >
          <Card  className="border-orange-200/50 bg-orange-50/50 dark:bg-orange-950/20">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg text-orange-800 dark:text-orange-200 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                EU AI Act - High Risk Systems (Annex III)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-orange-700 dark:text-orange-300">
                <p className="mb-3 font-medium">High-risk AI systems include:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {aiActAnnexIIIRisks.map(risk => (
                    <div key={risk} className="flex items-start gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-orange-500 mt-2 flex-shrink-0"></span>
                      <span>{risk}</span>
                    </div>
                  ))}
                </div>
                <p className="mt-3 p-3 rounded-lg bg-orange-100/50 dark:bg-orange-900/20 font-medium">
                  These systems require additional compliance measures under the EU AI Act.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Submit Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
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
