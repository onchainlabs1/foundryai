'use client'

import { useState, useEffect } from 'react'
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
import { Building2, Globe, Users, Mail, Shield } from 'lucide-react'

const companySchema = z.object({
  companyName: z.string().min(1, 'Company name is required'),
  sector: z.string().min(1, 'Sector is required'),
  country: z.string().min(1, 'Country is required'),
  primaryContactEmail: z.string().email('Valid email is required'),
  organizationSize: z.string().min(1, 'Organization size is required'),
  hasGovernancePolicy: z.boolean(),
  keyStakeholders: z.string().optional()
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
    defaultValues: {
      companyName: data?.companyName || '',
      sector: data?.sector || '',
      country: data?.country || '',
      primaryContactEmail: data?.primaryContactEmail || '',
      organizationSize: data?.organizationSize || '',
      hasGovernancePolicy: data?.hasGovernancePolicy || false,
      keyStakeholders: data?.keyStakeholders || ''
    }
  })

  const hasGovernancePolicy = watch('hasGovernancePolicy')

  const onSubmit = async (formData: CompanyFormData) => {
    setIsSubmitting(true)
    try {
      onUpdate({ company: formData })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Company Name */}
        <div className="space-y-2">
          <Label htmlFor="companyName" className="flex items-center gap-2">
            <Building2 className="w-4 h-4" />
            Company Name *
          </Label>
          <Input
            id="companyName"
            {...register('companyName')}
            placeholder="Enter your company name"
            className="bg-white/50 dark:bg-gray-800/50"
          />
          {errors.companyName && (
            <p className="text-sm text-red-500">{errors.companyName.message}</p>
          )}
        </div>

        {/* Sector */}
        <div className="space-y-2">
          <Label htmlFor="sector">Sector *</Label>
          <Select onValueChange={(value) => setValue('sector', value)} defaultValue={data?.sector}>
            <SelectTrigger className="bg-white/50 dark:bg-gray-800/50">
              <SelectValue placeholder="Select your sector" />
            </SelectTrigger>
            <SelectContent>
              {sectors.map(sector => (
                <SelectItem key={sector} value={sector}>{sector}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.sector && (
            <p className="text-sm text-red-500">{errors.sector.message}</p>
          )}
        </div>

        {/* Country */}
        <div className="space-y-2">
          <Label htmlFor="country" className="flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Country / Jurisdiction *
          </Label>
          <Select onValueChange={(value) => setValue('country', value)} defaultValue={data?.country}>
            <SelectTrigger className="bg-white/50 dark:bg-gray-800/50">
              <SelectValue placeholder="Select your country" />
            </SelectTrigger>
            <SelectContent>
              {countries.map(country => (
                <SelectItem key={country} value={country}>{country}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.country && (
            <p className="text-sm text-red-500">{errors.country.message}</p>
          )}
        </div>

        {/* Primary Contact Email */}
        <div className="space-y-2">
          <Label htmlFor="primaryContactEmail" className="flex items-center gap-2">
            <Mail className="w-4 h-4" />
            Primary Contact Email *
          </Label>
          <Input
            id="primaryContactEmail"
            type="email"
            {...register('primaryContactEmail')}
            placeholder="contact@company.com"
            className="bg-white/50 dark:bg-gray-800/50"
          />
          {errors.primaryContactEmail && (
            <p className="text-sm text-red-500">{errors.primaryContactEmail.message}</p>
          )}
        </div>

        {/* Organization Size */}
        <div className="space-y-2">
          <Label htmlFor="organizationSize" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Organization Size *
          </Label>
          <Select onValueChange={(value) => setValue('organizationSize', value)} defaultValue={data?.organizationSize}>
            <SelectTrigger className="bg-white/50 dark:bg-gray-800/50">
              <SelectValue placeholder="Select organization size" />
            </SelectTrigger>
            <SelectContent>
              {organizationSizes.map(size => (
                <SelectItem key={size} value={size}>{size}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.organizationSize && (
            <p className="text-sm text-red-500">{errors.organizationSize.message}</p>
          )}
        </div>

        {/* AI Governance Policy */}
        <div className="space-y-2">
          <Label htmlFor="hasGovernancePolicy" className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            AI Governance Policy in place?
          </Label>
          <div className="flex items-center space-x-2">
            <Switch
              id="hasGovernancePolicy"
              checked={hasGovernancePolicy}
              onCheckedChange={(checked) => setValue('hasGovernancePolicy', checked)}
            />
            <Label htmlFor="hasGovernancePolicy">
              {hasGovernancePolicy ? 'Yes' : 'No'}
            </Label>
          </div>
        </div>
      </div>

      {/* Key Stakeholders */}
      <div className="space-y-2">
        <Label htmlFor="keyStakeholders">Key Stakeholders</Label>
        <Textarea
          id="keyStakeholders"
          {...register('keyStakeholders')}
          placeholder="List key stakeholders involved in AI governance (e.g., CTO, Legal, Ethics Officer, etc.)"
          rows={3}
          className="bg-white/50 dark:bg-gray-800/50"
        />
      </div>

      {/* ISO Coverage Info */}
      <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm text-blue-800 dark:text-blue-200">
            📋 ISO/IEC 42001 Coverage
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="text-sm text-blue-700 dark:text-blue-300">
            <p className="mb-2">This step covers:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Clause 4.1: Understanding the organization and its context</li>
              <li>Clause 4.2: Understanding the needs and expectations of interested parties</li>
              <li>Clause 5.1: Leadership and commitment</li>
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
