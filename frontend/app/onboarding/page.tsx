'use client'

import React, { useState, useEffect } from 'react'

// Utility function to convert camelCase to snake_case
const toSnakeCase = (obj: any): any => {
  if (obj === null || obj === undefined) return obj
  if (typeof obj !== 'object') return obj
  if (Array.isArray(obj)) return obj.map(toSnakeCase)
  
  const result: any = {}
  for (const [key, value] of Object.entries(obj)) {
    let snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`)
    
    // Special mappings for backend compatibility
    if (key === 'systemOwner') {
      snakeKey = 'owner_email'
    } else if (key === 'processesPersonalData') {
      snakeKey = 'personal_data_processed'
    } else if (key === 'impactsFundamentalRights') {
      snakeKey = 'impacts_fundamental_rights'
    } else if (key === 'lifecycleStage') {
      snakeKey = 'lifecycle_stage'
    } else if (key === 'deploymentContext') {
      snakeKey = 'deployment_context'
    } else if (key === 'affectedUsers') {
      snakeKey = 'affected_users'
    } else if (key === 'thirdPartyProviders') {
      snakeKey = 'third_party_providers'
    } else if (key === 'riskCategory') {
      snakeKey = 'risk_category'
    }
    
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

  // Function to reset onboarding state
  const resetOnboarding = () => {
    
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem('system-id-mapping')
    setCurrentStep(1)
    setData({ step: 1 })
    setCompleted(false)
    setSystemIdMapping(new Map())
    console.log('Onboarding state reset')
    
    // Reload page to ensure clean state
    setTimeout(() => window.location.reload(), 100)
  }

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
        // Only load data if it's a valid ongoing session with meaningful data
        if (parsed.step && 
            parsed.step >= 1 && 
            parsed.step <= steps.length && 
            !parsed.completed &&
            parsed.systems && 
            parsed.systems.length > 0 && 
            parsed.systems[0].name) {
          setData(parsed)
          setCurrentStep(parsed.step)
          setCompleted(false)
          console.log(`Loaded onboarding data: step ${parsed.step}`)
        } else {
          // Clear old completed or empty data
          localStorage.removeItem(STORAGE_KEY)
          localStorage.removeItem('system-id-mapping')
          setCurrentStep(1)
          setData({ step: 1 })
          setCompleted(false)
          console.log('Cleared old or empty onboarding data')
        }
      } catch (error) {
        console.error('Failed to load saved onboarding data:', error)
        // Clear corrupted data
        localStorage.removeItem(STORAGE_KEY)
        localStorage.removeItem('system-id-mapping')
        setCurrentStep(1)
        setData({ step: 1 })
        setCompleted(false)
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
      console.log(`🔄 handleSaveAndContinue called for step ${currentStep}`)
      console.log('stepData received:', stepData)
      
      updateData(stepData)
      
      // Handle step-specific saves
      if (currentStep === 2 && stepData.systems && stepData.systems.length > 0) {
        console.log('📍 Step 2 detected - creating systems...')
        console.log('stepData.systems:', stepData.systems)
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
          // Remove fields that don't belong to the backend schema
          const { tempId: _, company_id: __, ...systemData } = system
          
          const newSystemPayload = {
            ...systemData,
            impacts_fundamental_rights: system.impacts_fundamental_rights || false,
            processes_personal_data: system.processesPersonalData || false,
          }
          
          console.log(`📤 Creating system "${system.name}"...`)
          console.log('Payload before snake_case:', newSystemPayload)
          const snakeCasePayload = toSnakeCase(newSystemPayload)
          console.log('Payload after snake_case:', snakeCasePayload)
          
          try {
            const createdSystem = await api.createSystem(snakeCasePayload)
            
            // Validate that the system was created with a valid ID
            if (!createdSystem || !createdSystem.id) {
              console.error(`❌ Failed to create system: ${system.name} - No ID returned`)
              console.error('API Response:', createdSystem)
              toast({
                title: "Error",
                description: `Failed to create system "${system.name}". Please try again.`,
                variant: "destructive",
              })
              continue
            }
            
            // Store the mapping: tempId -> backendId
            newIdMapping.set(tempId, createdSystem.id)
            
            // Add the created system to our list (keep form data, add only necessary backend ID)
            createdSystems.push({
              ...system, // Keep form data from frontend
              id: createdSystem.id, // Only add the backend ID
              tempId: tempId,
            })
            
            console.log(`✅ Created new system: ${system.name} (ID: ${createdSystem.id})`)
            
            // Show success toast for each system
            toast({
              title: "Success",
              description: `System "${system.name}" created successfully!`,
              variant: "default",
            })
            
            // Save onboarding data for this system
            if (data.company || data.risks || data.oversight || data.monitoring) {
              try {
                await api.saveOnboardingData(createdSystem.id, {
                  company: data.company,
                  risks: data.risks,
                  oversight: data.oversight,
                  monitoring: data.monitoring,
                  org_id: createdSystem.org_id,
                  ai_act_class: createdSystem.ai_act_class
                })
                console.log(`✅ Saved onboarding data for system ${createdSystem.id}`)
              } catch (saveError) {
                console.error(`⚠️ Failed to save onboarding data for system ${createdSystem.id}:`, saveError)
                // Don't throw - system is created, data save can be retried
              }
            }
          } catch (createError) {
            console.error(`❌ Exception creating system: ${system.name}`, createError)
            toast({
              title: "Error",
              description: `Failed to create system "${system.name}". ${createError}`,
              variant: "destructive",
            })
            continue
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
      console.log('=== Starting handleComplete ===')
      console.log('Current data:', JSON.stringify(data, null, 2))
      console.log('System ID mapping:', systemIdMapping)
      
      // Check if systems were created in Step 2, if not, try to fetch from backend
      let systemsToUse = data.systems || []
      
      if (systemsToUse.length === 0) {
        console.log('No systems in local data, fetching from backend...')
        try {
          const backendSystems = await api.getSystems()
          console.log('Backend systems found:', backendSystems)
          
          if (backendSystems && backendSystems.length > 0) {
            // Use backend systems as fallback
            systemsToUse = backendSystems.map((system: any) => ({
              ...system,
              tempId: `backend_${system.id}`, // Create a tempId for backend systems
            }))
            console.log('Using backend systems as fallback:', systemsToUse)
          } else {
            // If no systems exist, that's ok - just complete with empty data
            console.warn('No systems found - completing onboarding without systems')
            toast({
              title: "Warning",
              description: "No systems were created during onboarding. You can create systems later from the Inventory page.",
              variant: "default",
            })
          }
        } catch (error) {
          console.error('Failed to fetch systems from backend:', error)
          // Don't throw error - allow completion anyway
          toast({
            title: "Warning",
            description: "Could not verify systems. Completing onboarding anyway.",
            variant: "default",
          })
        }
      }
      
      console.log(`Found ${systemsToUse.length} systems to use`)
      
      // Use deterministic mapping to ensure correct IDs
      const syncedSystems = systemsToUse?.map((localSystem: any) => {
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
      
      // Onboarding data is now stored in backend - no localStorage needed
      
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
      
      // Validate that systems were created successfully
      const systemsWithIds = syncedSystems.filter(s => s.id && s.id > 0)
      
      console.log('=== Systems Validation ===')
      console.log('Synced systems:', syncedSystems)
      console.log('Systems with IDs:', systemsWithIds)
      console.log('Validation details:', {
        totalSystems: syncedSystems.length,
        systemsWithIds: systemsWithIds.length,
        systems: syncedSystems.map(s => ({ name: s.name, id: s.id, tempId: s.tempId }))
      })
      
      if (systemsWithIds.length === 0) {
        console.warn('⚠️ No systems with valid IDs found - completing anyway')
        console.warn('Synced systems details:', syncedSystems.map(s => ({
          name: s.name,
          id: s.id,
          tempId: s.tempId,
          hasId: !!s.id,
          idType: typeof s.id,
          idValue: s.id
        })))
        
        toast({
          title: "Onboarding Complete!",
          description: "Onboarding completed. You can create systems from the Inventory page.",
          variant: "default",
        })
      } else {
        console.log('✅ Systems validation passed!')
        
        toast({
          title: "Onboarding Complete!",
          description: `Your AI systems (${systemsWithIds.length}) have been successfully configured. You can now generate compliance documents.`,
          variant: "success",
        })
      }
      
      setCompleted(true)
      setCurrentStep(steps.length + 1)
    } catch (error) {
      console.error('❌ Failed to complete onboarding:', error)
      console.error('Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace',
        error: error
      })
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to complete onboarding. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <CompanySetup data={data.company} onUpdate={(company) => handleSaveAndContinue({ company })} />
      case 2:
        return <SystemDefinition data={data.systems} onUpdate={(stepData) => handleSaveAndContinue(stepData)} />
      case 3:
        return <RiskControls data={data.risks} onUpdate={(risks) => handleSaveAndContinue({ risks })} />
      case 4:
        return <HumanOversight data={data.oversight} onUpdate={(oversight) => handleSaveAndContinue({ oversight })} />
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
            <div className="flex space-x-3">
              <Button
                variant="outline"
                onClick={prevStep}
                disabled={currentStep === 1}
                className="flex items-center"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Previous
              </Button>
              
              {/* Emergency Reset Button */}
              <Button
                onClick={resetOnboarding}
                variant="destructive"
                size="sm"
                className="flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reset
              </Button>
            </div>

            <div className="flex space-x-3">
              
              {/* Show Continue button only for step 5 (monitoring) */}
              {currentStep === 5 ? (
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