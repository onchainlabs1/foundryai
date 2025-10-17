'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
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
  SkipForward
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
  const [currentStep, setCurrentStep] = useState(1)
  const [data, setData] = useState<OnboardingData>({ step: 1 })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [completed, setCompleted] = useState(false)

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
  }, [])

  // Autosave data changes
  useEffect(() => {
    if (data.step > 0) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    }
  }, [data])

  const updateData = (stepData: any) => {
    setData(prev => ({
      ...prev,
      ...stepData,
      step: currentStep
    }))
  }

  const goToStep = (step: number) => {
    if (step >= 1 && step <= 5) {
      setCurrentStep(step)
      setData(prev => ({ ...prev, step }))
    }
  }

  const nextStep = async () => {
    if (currentStep < 5) {
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
        // Create systems
        for (const system of stepData.systems) {
          await api.createSystem(system)
        }
      }
      
      await nextStep()
    } catch (error) {
      console.error('Failed to save step data:', error)
      alert('Failed to save. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleComplete = async () => {
    setLoading(true)
    try {
      // Generate evidence from templates
      const evidencePromises = []
      
      if (data.systems && data.systems.length > 0) {
        const systemId = data.systems[0].id || 1 // Use first system
        
        // Risk Assessment
        if (data.risks) {
          const riskContent = generateRiskAssessment(data.risks)
          const riskBlob = new Blob([riskContent], { type: 'text/markdown' })
          const riskFile = new File([riskBlob], 'risk-assessment.md', { type: 'text/markdown' })
          evidencePromises.push(
            api.uploadEvidence(systemId, 'Risk Assessment', riskFile, {
              template_type: 'risk_assessment',
              iso_clauses: ['6.1', '6.2'],
              ai_act: ['Art. 27']
            })
          )
        }
        
        // Model Card
        if (data.systems[0]) {
          const modelContent = generateModelCard(data.systems[0])
          const modelBlob = new Blob([modelContent], { type: 'text/markdown' })
          const modelFile = new File([modelBlob], 'model-card.md', { type: 'text/markdown' })
          evidencePromises.push(
            api.uploadEvidence(systemId, 'Model Card', modelFile, {
              template_type: 'model_card',
              iso_clauses: ['6.3'],
              ai_act: ['Annex IV']
            })
          )
        }
      }
      
      await Promise.all(evidencePromises)
      
      // Clear saved data
      localStorage.removeItem(STORAGE_KEY)
      setCompleted(true)
      
    } catch (error) {
      console.error('Failed to complete onboarding:', error)
      alert('Failed to complete onboarding. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <CompanySetup data={data.company} onUpdate={updateData} />
      case 2:
        return <SystemDefinition data={data.systems} onUpdate={updateData} />
      case 3:
        return <RiskControls data={data.risks} onUpdate={updateData} />
      case 4:
        return <HumanOversight data={data.oversight} onUpdate={updateData} />
      case 5:
        return <MonitoringImprovement data={data.monitoring} onUpdate={updateData} />
      default:
        return null
    }
  }

  if (completed) {
    return <OnboardingSummary data={data} onRestart={() => {
      setCompleted(false)
      setCurrentStep(1)
      setData({ step: 1 })
    }} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            AI Governance Onboarding
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Let's set up your AI governance framework step by step. This wizard will guide you through ISO/IEC 42001 and EU AI Act compliance.
          </p>
        </motion.div>

        {/* Progress Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`
                  flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300
                  ${currentStep >= step.id 
                    ? 'bg-blue-600 border-blue-600 text-white' 
                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-500'
                  }
                `}>
                  {currentStep > step.id ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <step.icon className="w-5 h-5" />
                  )}
                </div>
                {index < steps.length - 1 && (
                  <div className={`
                    w-16 h-0.5 mx-2 transition-all duration-300
                    ${currentStep > step.id ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'}
                  `} />
                )}
              </div>
            ))}
          </div>
          
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            {steps.map(step => (
              <div key={step.id} className="text-center max-w-24">
                <div className="font-medium">{step.title}</div>
                <div className="text-xs mt-1">{step.description}</div>
              </div>
            ))}
          </div>
          
          <Progress value={(currentStep / 5) * 100} className="mt-4" />
        </motion.div>

        {/* Step Content */}
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="rounded-2xl bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-3">
                {React.createElement(steps[currentStep - 1].icon, { className: "w-6 h-6 text-blue-600" })}
                Step {currentStep}: {steps[currentStep - 1].title}
              </CardTitle>
              <CardDescription>
                {steps[currentStep - 1].description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatePresence mode="wait">
                {renderStep()}
              </AnimatePresence>
            </CardContent>
          </Card>
        </motion.div>

        {/* Navigation */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex justify-between items-center mt-8"
        >
          <Button
            variant="outline"
            onClick={prevStep}
            disabled={currentStep === 1}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>

          <div className="flex gap-3">
            <Button
              variant="ghost"
              onClick={() => {
                localStorage.removeItem(STORAGE_KEY)
                router.push('/')
              }}
              className="flex items-center gap-2"
            >
              <SkipForward className="w-4 h-4" />
              Skip for later
            </Button>
            
            <Button
              onClick={nextStep}
              disabled={loading || saving}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700"
            >
              {saving && <Save className="w-4 h-4 animate-spin" />}
              {currentStep === 5 ? 'Complete Setup' : 'Continue'}
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

// Template generators
function generateRiskAssessment(risks: any): string {
  return `# Risk Assessment

## Identified Risks
${risks.topRisks?.map((risk: string) => `- ${risk}`).join('\n') || 'No risks identified'}

## Risk Analysis
- Likelihood: ${risks.likelihood || 'Not assessed'}
- Impact: ${risks.impact || 'Not assessed'}

## Mitigation Actions
${risks.mitigationActions || 'No mitigation actions defined'}

## Residual Risk
${risks.residualRisk || 'Not assessed'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
}

function generateModelCard(system: any): string {
  return `# Model Card

## System Information
- **Name**: ${system.name || 'Not specified'}
- **Purpose**: ${system.purpose || 'Not specified'}
- **Domain**: ${system.domain || 'Not specified'}
- **Lifecycle Stage**: ${system.lifecycleStage || 'Not specified'}

## Deployment Context
- **Context**: ${system.deploymentContext || 'Not specified'}
- **Affected Users**: ${system.affectedUsers || 'Not specified'}

## Data Processing
- **Processes Personal Data**: ${system.processesPersonalData ? 'Yes' : 'No'}
- **Impacts Fundamental Rights**: ${system.impactsFundamentalRights ? 'Yes' : 'No'}

---
*Generated by AIMS Readiness Onboarding Wizard*`
}
