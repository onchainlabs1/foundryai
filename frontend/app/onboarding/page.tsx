'use client'

import React, { useState, useEffect } from 'react'

// Utility function to convert camelCase to snake_case
const toSnakeCase = (obj: any): any => {
  if (obj === null || obj === undefined) return obj
  if (typeof obj !== 'object') return obj
  if (Array.isArray(obj)) return obj.map(toSnakeCase)
  
  const result: any = {}
  for (const [key, value] of Object.entries(obj)) {
    const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
    result[snakeKey] = toSnakeCase(value)
  }
  return result
}

import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Bot, 
  Shield, 
  Users, 
  BarChart3,
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  Save,
  SkipForward,
  Sparkles,
  Zap,
  Target,
  FileText,
  Settings,
  Play
} from 'lucide-react'
import { api } from '@/lib/api'

// Step Components
import CompanySetup from '@/components/onboarding/company-setup'
import SystemDefinition from '@/components/onboarding/system-definition'
import RiskControls from '@/components/onboarding/risk-controls'
import HumanOversight from '@/components/onboarding/human-oversight'
import MonitoringImprovement from '@/components/onboarding/monitoring-improvement'
import OnboardingSummary from '@/components/onboarding/onboarding-summary'

const STORAGE_KEY = 'onboarding-draft'

interface OnboardingData {
  step: number
  company?: any
  systems?: any[]
  risks?: any
  oversight?: any
  monitoring?: any
  evidence?: any[]
  controls?: any[]
}

export default function OnboardingPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<OnboardingData>({ step: 1 })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [systemIdMapping, setSystemIdMapping] = useState<Map<string, number>>(new Map())

  const steps = [
    { id: 1, title: 'Company Setup', icon: Building2, description: 'Basic organization information' },
    { id: 2, title: 'AI System Definition', icon: Bot, description: 'Define your AI systems' },
    { id: 3, title: 'Risk & Controls', icon: Shield, description: 'Risk assessment and controls' },
    { id: 4, title: 'Human Oversight', icon: Users, description: 'Governance and oversight' },
    { id: 5, title: 'Monitoring & Improvement', icon: BarChart3, description: 'Continuous monitoring' }
  ]

  // Load saved data on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        setData(parsed)
        setCurrentStep(parsed.step || 1)
      } catch (error) {
        console.error('Failed to load saved onboarding data:', error)
      }
    }
    
    // Load system ID mapping
    const savedMapping = localStorage.getItem('system-id-mapping')
    if (savedMapping) {
      try {
        const mappingData = JSON.parse(savedMapping)
        const mapping = new Map<string, number>()
        Object.entries(mappingData).forEach(([key, value]) => {
          mapping.set(key, value as number)
        })
        setSystemIdMapping(mapping)
      } catch (error) {
        console.error('Failed to load system ID mapping:', error)
      }
    }
  }, [])

  // Save data whenever it changes
  useEffect(() => {
    if (data.step > 1) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    }
  }, [data])

  const updateData = (newData: any) => {
    setData(prev => ({ ...prev, ...newData, step: currentStep }))
  }

  const nextStep = async () => {
    if (currentStep < steps.length) {
      setCurrentStep(prev => prev + 1)
      setData(prev => ({ ...prev, step: currentStep + 1 }))
    } else {
      await handleComplete()
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1)
      setData(prev => ({ ...prev, step: currentStep - 1 }))
    }
  }

  const handleSaveAndContinue = async (stepData: any) => {
    setSaving(true)
    try {
      updateData(stepData)
      
      // Handle step-specific saves
      if (currentStep === 2 && stepData.systems) {
        // Check for existing systems to reuse or create new ones
        const existingSystems = await api.getSystems()
        
        // Create systems with proper field mapping and capture returned IDs
        const createdSystems: any[] = []
        const newIdMapping = new Map<string, number>()
        
        for (let i = 0; i < stepData.systems.length; i++) {
          const system = stepData.systems[i]
          
          // Check for existing systems with the same name
          const existingSystem = existingSystems.find((existing: any) => 
            existing.name.toLowerCase() === system.name.toLowerCase()
          )
          
          if (existingSystem) {
            // System already exists - update it with new data
            console.log(`Updating existing system: ${system.name} (ID: ${existingSystem.id})`)
            
            // Generate a stable UUID-based tempId for mapping
            const tempId = system.tempId || `temp_${i}_${system.name}_${system.purpose}_${crypto.randomUUID()}`
            
            // Update the existing system with new form data using PATCH
            const updatedSystem = await api.patchSystem(existingSystem.id, toSnakeCase(system))
            
            // Store the mapping: tempId -> existing backendId
            newIdMapping.set(tempId, existingSystem.id)
            
            // Add the updated system to createdSystems (keep form data, add backend ID)
            createdSystems.push({
              ...system, // Keep form data from frontend
              id: existingSystem.id, // Use existing backend ID
              tempId: tempId,
            })
            
            // Show user feedback about updating existing system
            console.log(`✅ System "${system.name}" already existed and was reused (ID: ${existingSystem.id})`)
            toast({
              title: "System Updated",
              description: `System "${system.name}" was updated with new information.`,
              variant: "default",
            })
            
            // Continue to next system (don't create duplicate)
            continue
          }
          
          // System doesn't exist - create new one
          // Generate a stable UUID-based tempId that persists across refreshes
          const tempId = system.tempId || `temp_${crypto.randomUUID()}`
          
          // Create the system with proper field mapping
          const newSystemPayload = {
            ...system,
            tempId: tempId, // Ensure tempId is part of the payload for mapping
            company_id: data.company?.id,
            impacts_fundamental_rights: system.impacts_fundamental_rights || false,
          }
          
          const createdSystem = await api.createSystem(toSnakeCase(newSystemPayload))
          
          // Store the mapping: tempId -> backendId
          newIdMapping.set(tempId, createdSystem.id)
          
          // Add the created system to our list (keep form data, add only necessary backend ID)
          createdSystems.push({
            ...system, // Keep form data from frontend
            id: createdSystem.id, // Only add the backend ID
            tempId: tempId,
          })
          
          console.log(`✅ Created new system: ${system.name} (ID: ${createdSystem.id})`)
          
          // Save onboarding data for this system
          if (data.company || data.risks || data.oversight || data.monitoring) {
            await api.saveOnboardingData(createdSystem.id, {
              company: data.company,
              risks: data.risks,
              oversight: data.oversight,
              monitoring: data.monitoring,
              org_id: createdSystem.org_id,
              ai_act_class: createdSystem.ai_act_class
            })
          }
        }
        
        // Show user feedback about systems processed
        const newCount = createdSystems.length
        
        console.log(`✅ Processed ${newCount} systems successfully`)
        
        // Show friendly message to user
        console.log(`✅ ${newCount} system(s) processed and ready for document generation.`)
        
        // Update the ID mapping state
        setSystemIdMapping(newIdMapping)
        
        // Persist the mapping to localStorage
        const mappingObject = Object.fromEntries(newIdMapping)
        localStorage.setItem('system-id-mapping', JSON.stringify(mappingObject))
        
        // Update the data state with systems that have real IDs
        setData(prevData => ({
          ...prevData,
          systems: createdSystems
        }))
      }
      
      await nextStep()
    } catch (error) {
      console.error('Failed to save step data:', error)
      toast({
        title: "Error",
        description: "Failed to save. Please try again.",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const handleComplete = async () => {
    setLoading(true)
    try {
      // Use deterministic mapping to ensure correct IDs
      const syncedSystems = data.systems?.map((localSystem: any) => {
        // If system already has a real ID, keep it
        if (localSystem.id && localSystem.id > 0) {
          return localSystem
        }
        
        // If system has a tempId, try to get the backend ID from mapping
        if (localSystem.tempId && systemIdMapping.has(localSystem.tempId)) {
          const backendId = systemIdMapping.get(localSystem.tempId)!
          return {
            ...localSystem,
            id: backendId
          }
        }
        
        // If no mapping found, return as is (will be handled by summary)
        return localSystem
      }) || []
      
      // Update data with synced systems
      setData(prevData => ({
        ...prevData,
        systems: syncedSystems
      }))
      
      // Save onboarding data to localStorage for document generation
      const onboardingData = {
        company: data.company,
        systems: syncedSystems,
        risks: data.risks,
        oversight: data.oversight,
        monitoring: data.monitoring,
        evidence: data.evidence,
        controls: data.controls
      }
      
      localStorage.setItem('onboardingData', JSON.stringify(onboardingData))
      
      // Save onboarding data to backend for each system
      for (const system of syncedSystems) {
        if (system.id && system.id > 0) {
          try {
            await api.saveOnboardingData(system.id, {
              company: data.company,
              risks: data.risks,
              oversight: data.oversight,
              monitoring: data.monitoring,
              org_id: system.org_id,
              ai_act_class: system.ai_act_class
            })
          } catch (error) {
            console.error(`Failed to save onboarding data for system ${system.id}:`, error)
          }
        }
      }
      
      setCompleted(true)
      setCurrentStep(steps.length + 1)
      
      toast({
        title: "Onboarding Complete!",
        description: "Your AI systems have been successfully configured. You can now generate compliance documents.",
        variant: "success",
      })
    } catch (error) {
      console.error('Failed to complete onboarding:', error)
      toast({
        title: "Error",
        description: "Failed to complete onboarding. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <CompanySetup data={data.company} onUpdate={(company) => updateData({ company })} />
      case 2:
        return <SystemDefinition data={data.systems} onUpdate={(systems) => updateData({ systems })} />
      case 3:
        return <RiskControls data={data.risks} onUpdate={(risks) => updateData({ risks })} />
      case 4:
        return <HumanOversight data={data.oversight} onUpdate={(oversight) => updateData({ oversight })} />
      case 5:
        return <MonitoringImprovement data={data.monitoring} onUpdate={(monitoring) => updateData({ monitoring })} />
      case 6:
        return <OnboardingSummary data={data} onRestart={() => setCurrentStep(1)} />
      default:
        return null
    }
  }

  const progress = (currentStep / steps.length) * 100

  if (completed) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-md w-full"
        >
          <Card className="text-center">
            <CardHeader>
              <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <CardTitle className="text-2xl">Onboarding Complete!</CardTitle>
              <CardDescription>
                Your AI systems have been successfully configured and are ready for compliance monitoring.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button 
                onClick={() => router.push('/documents')}
                className="w-full"
              >
                <FileText className="w-4 h-4 mr-2" />
                View Generated Documents
              </Button>
              <Button 
                variant="outline" 
                onClick={() => router.push('/')}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              AI System Onboarding
            </h1>
            <p className="text-lg text-gray-600">
              Configure your AI systems for compliance monitoring
            </p>
          </motion.div>
          
          {/* Progress Bar */}
          <div className="max-w-2xl mx-auto mb-8">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>Step {currentStep} of {steps.length}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
          
          {/* Step Indicators */}
          <div className="flex justify-center space-x-4 mb-8">
            {steps.map((step, index) => {
              const StepIcon = step.icon
              const isActive = currentStep === step.id
              const isCompleted = currentStep > step.id
              
              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className={`flex flex-col items-center p-3 rounded-lg transition-all ${
                    isActive 
                      ? 'bg-blue-100 text-blue-600' 
                      : isCompleted 
                        ? 'bg-green-100 text-green-600' 
                        : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  <StepIcon className="w-6 h-6 mb-1" />
                  <span className="text-xs font-medium">{step.title}</span>
                </motion.div>
              )
            })}
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderStep()}
            </motion.div>
          </AnimatePresence>

          {/* Navigation */}
          <div className="flex justify-between items-center mt-8">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="flex items-center"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>

            <div className="flex space-x-3">
              {currentStep < steps.length ? (
                <Button
                  onClick={() => handleSaveAndContinue(data)}
                  disabled={saving}
                  className="flex items-center"
                >
                  {saving ? (
                    <>
                      <Save className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Continue
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  onClick={handleComplete}
                  disabled={loading}
                  className="flex items-center"
                >
                  {loading ? (
                    <>
                      <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                      Completing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Complete Onboarding
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}