'use client'

import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Building2, Globe, Users, Mail, Shield, CheckCircle, ArrowRight } from 'lucide-react'

const companySchema = z.object({
  companyName: z.string().min(1, 'Company name is required'),
  sector: z.string().min(1, 'Sector is required'),
  country: z.string().min(1, 'Country is required'),
  primaryContactEmail: z.string().email('Valid email is required'),
  organizationSize: z.string().min(1, 'Organization size is required'),
  hasGovernancePolicy: z.boolean(),
  keyStakeholders: z.string().optional(),
  // New audit-grade fields
  primaryContactName: z.string().optional(),
  dpoContactName: z.string().optional(),
  dpoContactEmail: z.string().email('Valid email required').optional().or(z.literal('')),
  orgRole: z.enum(['provider', 'deployer', 'both']).optional(),
  // Critical fields for launch
  dpiaLink: z.string().optional(),
  dpiaStatus: z.string().optional().or(z.undefined()),
  isGpai: z.boolean().optional(),
  usesGenerativeModel: z.boolean().optional()
})

type CompanyFormData = z.infer<typeof companySchema>

interface CompanySetupProps {
  data?: any
  onUpdate: (data: any) => void
}

const sectors = [
  'Financial Services',
  'Healthcare',
  'Technology',
  'Manufacturing',
  'Retail',
  'Education',
  'Government',
  'Non-profit',
  'Other'
]

const organizationSizes = [
  'Startup (1-10 employees)',
  'Small (11-50 employees)',
  'Medium (51-250 employees)',
  'Large (251-1000 employees)',
  'Enterprise (1000+ employees)'
]

const countries = [
  'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
  'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece',
  'Hungary', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg',
  'Malta', 'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia',
  'Slovenia', 'Spain', 'Sweden', 'United Kingdom', 'United States', 'Canada'
]

const dpiaOptions = [
  { value: 'em_andamento', label: '🔄 DPIA em andamento' },
  { value: 'nao_aplicavel', label: '❌ N/A - Não processa dados pessoais' },
  { value: 'planejado', label: '📅 Será conduzido antes do deploy' },
  { value: 'concluido', label: '✅ DPIA já concluído' },
  { value: 'nao_necessario', label: 'ℹ️ Não necessário para este sistema' }
]

export default function CompanySetup({ data, onUpdate }: CompanySetupProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid }
  } = useForm<CompanyFormData>({
    resolver: zodResolver(companySchema),
    mode: 'onChange',
    defaultValues: {
      companyName: data?.companyName || '',
      sector: data?.sector || '',
      country: data?.country || '',
      primaryContactEmail: data?.primaryContactEmail || '',
      organizationSize: data?.organizationSize || '',
      hasGovernancePolicy: data?.hasGovernancePolicy || false,
      keyStakeholders: data?.keyStakeholders || '',
      primaryContactName: data?.primaryContactName || '',
      dpoContactName: data?.dpoContactName || '',
      dpoContactEmail: data?.dpoContactEmail || '',
      orgRole: data?.orgRole || undefined,
      dpiaLink: data?.dpiaLink || '',
      dpiaStatus: data?.dpiaStatus || undefined,
      isGpai: data?.isGpai || false,
      usesGenerativeModel: data?.usesGenerativeModel || false
    }
  })

  const hasGovernancePolicy = watch('hasGovernancePolicy')
  const watchedValues = watch()

  // Manual validation for button state - only required fields
  const isFormValid = 
    watchedValues.companyName?.trim() &&
    watchedValues.sector &&
    watchedValues.country &&
    watchedValues.primaryContactEmail?.trim() &&
    watchedValues.organizationSize

  const onSubmit = async (formData: CompanyFormData) => {
    setIsSubmitting(true)
    try {
      onUpdate({ company: formData })
    } finally {
      setIsSubmitting(false)
    }
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
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 text-white mb-4"
        >
          <Building2 className="w-8 h-8" />
        </motion.div>
        <h2 className="text-3xl font-bold gradient-text">Company Setup</h2>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Tell us about your organization to personalize your AI governance framework
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Main Form Card */}
        <Card  className="p-8">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center gap-3 text-xl">
              <Building2 className="w-6 h-6 text-primary" />
              Organization Information
            </CardTitle>
            <CardDescription className="text-base">
              Basic information about your company and governance structure
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Company Name */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                className="space-y-3"
              >
                <Label htmlFor="companyName" className="flex items-center gap-2 text-sm font-semibold">
                  <Building2 className="w-4 h-4 text-primary" />
                  Company Name *
                </Label>
                <Input
                  id="companyName"
                  {...register('companyName')}
                  placeholder="Enter your company name"
                  className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                />
                {errors.companyName && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.companyName.message}
                  </p>
                )}
              </motion.div>

              {/* Sector */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="space-y-3"
              >
                <Label htmlFor="sector" className="text-sm font-semibold">Industry Sector *</Label>
                <Select onValueChange={(value) => setValue('sector', value)} defaultValue={data?.sector}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select your sector" />
                  </SelectTrigger>
                  <SelectContent>
                    {sectors.map(sector => (
                      <SelectItem key={sector} value={sector}>{sector}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.sector && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.sector.message}
                  </p>
                )}
              </motion.div>

              {/* Country */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="space-y-3"
              >
                <Label htmlFor="country" className="flex items-center gap-2 text-sm font-semibold">
                  <Globe className="w-4 h-4 text-primary" />
                  Country / Jurisdiction *
                </Label>
                <Select onValueChange={(value) => setValue('country', value)} defaultValue={data?.country}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select your country" />
                  </SelectTrigger>
                  <SelectContent>
                    {countries.map(country => (
                      <SelectItem key={country} value={country}>{country}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.country && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.country.message}
                  </p>
                )}
              </motion.div>

              {/* Primary Contact Email */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="space-y-3"
              >
                <Label htmlFor="primaryContactEmail" className="flex items-center gap-2 text-sm font-semibold">
                  <Mail className="w-4 h-4 text-primary" />
                  Primary Contact Email *
                </Label>
                <Input
                  id="primaryContactEmail"
                  type="email"
                  {...register('primaryContactEmail')}
                  placeholder="contact@company.com"
                  className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                />
                {errors.primaryContactEmail && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.primaryContactEmail.message}
                  </p>
                )}
              </motion.div>

              {/* Primary Contact Name */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.65 }}
                className="space-y-3"
              >
                <Label htmlFor="primaryContactName" className="flex items-center gap-2 text-sm font-semibold">
                  <Users className="w-4 h-4 text-primary" />
                  Primary Contact Name
                </Label>
                <Input
                  id="primaryContactName"
                  {...register('primaryContactName')}
                  placeholder="John Doe"
                  className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                />
              </motion.div>

              {/* Organization Size */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 }}
                className="space-y-3"
              >
                <Label htmlFor="organizationSize" className="flex items-center gap-2 text-sm font-semibold">
                  <Users className="w-4 h-4 text-primary" />
                  Organization Size *
                </Label>
                <Select onValueChange={(value) => setValue('organizationSize', value)} defaultValue={data?.organizationSize}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select organization size" />
                  </SelectTrigger>
                  <SelectContent>
                    {organizationSizes.map(size => (
                      <SelectItem key={size} value={size}>{size}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.organizationSize && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.organizationSize.message}
                  </p>
                )}
              </motion.div>

              {/* DPO Contact Name */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.75 }}
                className="space-y-3"
              >
                <Label htmlFor="dpoContactName" className="flex items-center gap-2 text-sm font-semibold">
                  <Shield className="w-4 h-4 text-primary" />
                  DPO / Legal Contact Name
                </Label>
                <Input
                  id="dpoContactName"
                  {...register('dpoContactName')}
                  placeholder="Jane Smith (optional)"
                  className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                />
              </motion.div>

              {/* DPO Contact Email */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                className="space-y-3"
              >
                <Label htmlFor="dpoContactEmail" className="flex items-center gap-2 text-sm font-semibold">
                  <Mail className="w-4 h-4 text-primary" />
                  DPO / Legal Contact Email
                </Label>
                <Input
                  id="dpoContactEmail"
                  type="email"
                  {...register('dpoContactEmail')}
                  placeholder="dpo@company.com (optional)"
                  className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300"
                />
                {errors.dpoContactEmail && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <span className="w-1 h-1 rounded-full bg-destructive"></span>
                    {errors.dpoContactEmail.message}
                  </p>
                )}
              </motion.div>

              {/* Organization Role */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.85 }}
                className="space-y-3"
              >
                <Label htmlFor="orgRole" className="flex items-center gap-2 text-sm font-semibold">
                  <Building2 className="w-4 h-4 text-primary" />
                  Organization Role (EU AI Act)
                </Label>
                <Select onValueChange={(value) => setValue('orgRole', value as any)} defaultValue={data?.orgRole}>
                  <SelectTrigger className="h-12 bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300">
                    <SelectValue placeholder="Select your role (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="provider">AI Provider (develop/distribute AI systems)</SelectItem>
                    <SelectItem value="deployer">AI Deployer (use AI systems)</SelectItem>
                    <SelectItem value="both">Both Provider and Deployer</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Defines compliance obligations under EU AI Act
                </p>
              </motion.div>

              {/* AI Governance Policy */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                className="space-y-3"
              >
                <Label htmlFor="hasGovernancePolicy" className="flex items-center gap-2 text-sm font-semibold">
                  <Shield className="w-4 h-4 text-primary" />
                  AI Governance Policy
                </Label>
                <div className="flex items-center space-x-3 p-4 rounded-xl bg-muted/30 border border-border/50">
                  <Switch
                    id="hasGovernancePolicy"
                    checked={hasGovernancePolicy}
                    onCheckedChange={(checked) => setValue('hasGovernancePolicy', checked)}
                  />
                  <div className="flex items-center gap-2">
                    <Label htmlFor="hasGovernancePolicy" className="text-sm">
                      {hasGovernancePolicy ? 'Policy in place' : 'No policy yet'}
                    </Label>
                    <Badge variant={hasGovernancePolicy ? "default" : "secondary"}>
                      {hasGovernancePolicy ? 'Yes' : 'No'}
                    </Badge>
                  </div>
                </div>
              </motion.div>
            </div>

            {/* Key Stakeholders */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
              className="space-y-3"
            >
              <Label htmlFor="keyStakeholders" className="text-sm font-semibold">Key Stakeholders</Label>
              <Textarea
                id="keyStakeholders"
                {...register('keyStakeholders')}
                placeholder="List key stakeholders involved in AI governance (e.g., CTO, Legal, Ethics Officer, etc.)"
                rows={4}
                className="bg-background/50 border-border/50 focus:border-primary/50 transition-all duration-300 resize-none"
              />
              <p className="text-xs text-muted-foreground">
                Optional: Help us understand your governance structure
              </p>
            </motion.div>
          </CardContent>
        </Card>

        {/* Critical Compliance Fields */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.95 }}
        >
          <Card className="border-amber-200 bg-amber-50">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg text-amber-800 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Critical Compliance Fields
              </CardTitle>
              <CardDescription className="text-amber-700">
                Required for EU AI Act compliance and audit readiness
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* DPIA Status */}
              <div className="space-y-3">
                <Label htmlFor="dpiaStatus" className="text-sm font-semibold text-amber-800">
                  DPIA Status <span className="text-red-500">*</span>
                </Label>
                <Select
                  value={watch('dpiaStatus') || undefined}
                  onValueChange={(value) => setValue('dpiaStatus', value)}
                >
                  <SelectTrigger className="bg-background/50 border-amber-200 focus:border-amber-400">
                    <SelectValue placeholder="Selecione o status do DPIA..." />
                  </SelectTrigger>
                  <SelectContent>
                    {dpiaOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-amber-600">
                  Data Protection Impact Assessment (GDPR Art. 35) - selecione o status atual
                </p>
                {errors.dpiaStatus && (
                  <p className="text-xs text-red-500">{errors.dpiaStatus.message}</p>
                )}
              </div>

              {/* DPIA Link (condicional) */}
              {watch('dpiaStatus') === 'concluido' && (
                <div className="space-y-3">
                  <Label htmlFor="dpiaLink" className="text-sm font-semibold text-amber-800">
                    DPIA Link (opcional)
                  </Label>
                  <Input
                    id="dpiaLink"
                    {...register('dpiaLink')}
                    placeholder="https://example.com/dpia ou referência interna"
                    className="bg-background/50 border-amber-200 focus:border-amber-400"
                  />
                  <p className="text-xs text-amber-600">
                    Link ou referência para o DPIA concluído (opcional)
                  </p>
                </div>
              )}

              {/* GPAI Classification */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="isGpai" className="text-sm font-semibold text-amber-800">
                      General Purpose AI (GPAI)
                    </Label>
                    <p className="text-xs text-amber-600">
                      Is your organization developing/deploying GPAI systems?
                    </p>
                  </div>
                  <Switch
                    id="isGpai"
                    checked={watch('isGpai')}
                    onCheckedChange={(checked) => setValue('isGpai', checked)}
                    className="data-[state=checked]:bg-amber-500"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="usesGenerativeModel" className="text-sm font-semibold text-amber-800">
                      Uses Generative Models
                    </Label>
                    <p className="text-xs text-amber-600">
                      Does your system use generative AI models (LLMs, image generators, etc.)?
                    </p>
                  </div>
                  <Switch
                    id="usesGenerativeModel"
                    checked={watch('usesGenerativeModel')}
                    onCheckedChange={(checked) => setValue('usesGenerativeModel', checked)}
                    className="data-[state=checked]:bg-amber-500"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* ISO Coverage Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0 }}
        >
          <Card  className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg text-primary flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                ISO/IEC 42001 Coverage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                <p className="mb-3 font-medium">This step covers the following ISO/IEC 42001 clauses:</p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">4.1</Badge>
                    <span>Understanding the organization and its context</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">4.2</Badge>
                    <span>Understanding the needs and expectations of interested parties</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <Badge variant="secondary" className="text-xs">5.1</Badge>
                    <span>Leadership and commitment</span>
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
          transition={{ delay: 1.1 }}
          className="flex justify-end"
        >
          <Button
            type="submit"
            disabled={!isFormValid || isSubmitting}
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
