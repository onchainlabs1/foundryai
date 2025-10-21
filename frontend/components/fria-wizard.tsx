'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { api, downloadFile } from '@/lib/api'

const FRIA_QUESTIONS = [
  { id: 'q1', text: 'Does the system process biometric data?', key: 'biometric_data' },
  { id: 'q2', text: 'Does it impact fundamental rights (privacy, non-discrimination)?', key: 'fundamental_rights' },
  { id: 'q3', text: 'Is it used for critical infrastructure?', key: 'critical_infrastructure' },
  { id: 'q4', text: 'Does it involve vulnerable groups (children, disabilities)?', key: 'vulnerable_groups' },
  { id: 'q5', text: 'Does it make automated decisions affecting individuals?', key: 'automated_decisions' },
  { id: 'q6', text: 'Is there human oversight in the decision loop?', key: 'human_oversight' },
  { id: 'q7', text: 'Are data subjects informed about AI usage?', key: 'subjects_informed' },
  { id: 'q8', text: 'Can decisions be explained/contested?', key: 'explainable_contestable' },
  { id: 'q9', text: 'Is there a data protection impact assessment (DPIA)?', key: 'dpia_exists' },
  { id: 'q10', text: 'Are there safeguards against bias and discrimination?', key: 'bias_safeguards' },
]

interface FRIAWizardProps {
  systemId: number
  onComplete?: () => void
}

export function FRIAWizard({ systemId, onComplete }: FRIAWizardProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [notApplicable, setNotApplicable] = useState(false)
  const [justification, setJustification] = useState('')
  const [loading, setLoading] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [friaResult, setFriaResult] = useState<any>(null)
  const [existingFRIA, setExistingFRIA] = useState<any>(null)
  // Extended fields
  const [proportionality, setProportionality] = useState('')
  const [residualRisk, setResidualRisk] = useState('Low')
  const [reviewNotes, setReviewNotes] = useState('')
  const [dpiaReference, setDpiaReference] = useState('')
  const [checkingExisting, setCheckingExisting] = useState(true)

  const currentQuestion = FRIA_QUESTIONS[currentStep]
  const progress = ((currentStep + 1) / FRIA_QUESTIONS.length) * 100

  // Check for existing FRIA on component mount
  useEffect(() => {
    const checkExistingFRIA = async () => {
      try {
        console.log('🔍 Checking for existing FRIA for system:', systemId)
        const existing = await api.getLatestFRIA(systemId)
        console.log('📋 Found existing FRIA:', existing)
        setExistingFRIA(existing)
      } catch (error) {
        console.log('ℹ️ No existing FRIA found (this is normal for new systems)')
        setExistingFRIA(null)
      } finally {
        setCheckingExisting(false)
      }
    }
    
    checkExistingFRIA()
  }, [systemId])

  const handleAnswer = (value: string) => {
    setAnswers({ ...answers, [currentQuestion.key]: value })
  }

  const handleNext = () => {
    if (currentStep < FRIA_QUESTIONS.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleSubmit = async () => {
    setLoading(true)
    try {
      console.log('🚀 Submitting FRIA for system:', systemId)
      console.log('📋 FRIA data:', {
        applicable: !notApplicable,
        answers: notApplicable ? {} : answers,
        justification: notApplicable ? justification : undefined,
      })
      
      // Build extended FRIA payload
      const payload: any = {
        applicable: !notApplicable,
        answers: notApplicable ? {} : answers,
        justification: notApplicable ? justification : undefined,
      }
      
      // Add extended fields if applicable
      if (!notApplicable) {
        // Extract risks from answers
        const risks = Object.entries(answers)
          .filter(([key, value]) => key.includes('risk') || key.includes('impact'))
          .map(([key, value]) => ({ question: key, answer: value }))
        
        // Extract safeguards from answers  
        const safeguards = Object.entries(answers)
          .filter(([key, value]) => key.includes('safeguard') || key.includes('mitigation') || key.includes('measure'))
          .map(([key, value]) => ({ question: key, answer: value }))
        
        payload.ctx_json = JSON.stringify({ system_id: systemId, timestamp: new Date().toISOString() })
        payload.risks_json = JSON.stringify(risks)
        payload.safeguards_json = JSON.stringify(safeguards)
        payload.proportionality = proportionality || "Assessment indicates proportionate measures for identified risks"
        payload.residual_risk = residualRisk || "Low"
        payload.review_notes = reviewNotes
        
        // Check if DPIA is indicated in answers or manual input
        const needsDPIA = Object.values(answers).some(answer => 
          answer.toLowerCase().includes('personal data') || 
          answer.toLowerCase().includes('privacy')
        )
        if (needsDPIA || dpiaReference) {
          payload.dpia_reference = dpiaReference || "DPIA required - see system settings"
        }
      }
      
      const result = await api.createFRIA(systemId, payload)
      
      console.log('✅ FRIA submitted successfully:', result)
      setFriaResult(result)
      setCompleted(true)
      onComplete?.()
    } catch (error) {
      console.error('❌ FRIA submission failed:', error)
      alert('Failed to submit FRIA: ' + error)
    } finally {
      setLoading(false)
    }
  }

  // Show loading while checking for existing FRIA
  if (checkingExisting) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>FRIA Assessment</CardTitle>
          <CardDescription>Checking for existing assessments...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
            <span>Loading...</span>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Show existing FRIA if found
  if (existingFRIA && !completed) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Existing FRIA Assessment</CardTitle>
          <CardDescription>This system already has a FRIA assessment</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-blue-50 border border-blue-200 rounded">
            <p className="text-blue-800 font-medium">📋 FRIA Assessment Found</p>
            <p className="text-sm text-blue-700 mt-1">
              Status: {existingFRIA.status} | Applicable: {existingFRIA.applicable ? 'Yes' : 'No'}
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium">Download your FRIA:</p>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={async () => {
                  try {
                    await downloadFile(existingFRIA.md_url, 'fria-document.md');
                  } catch (error) {
                    console.error('FRIA download failed:', error);
                    alert('Download failed. Please check your API key.');
                  }
                }}
              >
                Download Markdown
              </Button>
              <Button 
                variant="outline"
                onClick={async () => {
                  try {
                    await downloadFile(existingFRIA.html_url, 'fria-document.html');
                  } catch (error) {
                    console.error('FRIA download failed:', error);
                    alert('Download failed. Please check your API key.');
                  }
                }}
              >
                Download HTML
              </Button>
            </div>
          </div>

          <div className="flex gap-2">
            <Button onClick={() => { setExistingFRIA(null); }}>
              Create New Assessment
            </Button>
            <Button variant="outline" onClick={() => window.location.reload()}>
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (completed && friaResult) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>FRIA Completed</CardTitle>
          <CardDescription>Your assessment has been submitted</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-green-50 border border-green-200 rounded">
            <p className="text-green-800 font-medium">✓ FRIA assessment submitted successfully</p>
            <p className="text-sm text-green-700 mt-1">
              Status: {friaResult.status} | Applicable: {friaResult.applicable ? 'Yes' : 'No'}
            </p>
          </div>
          
          <div className="space-y-2">
            <p className="text-sm font-medium">Download your FRIA:</p>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                onClick={async () => {
                  try {
                    await downloadFile(friaResult.md_url, 'fria-document.md');
                  } catch (error) {
                    console.error('FRIA download failed:', error);
                    alert('Download failed. Please check your API key.');
                  }
                }}
              >
                Download Markdown
              </Button>
              <Button 
                variant="outline"
                onClick={async () => {
                  try {
                    await downloadFile(friaResult.html_url, 'fria-document.html');
                  } catch (error) {
                    console.error('FRIA download failed:', error);
                    alert('Download failed. Please check your API key.');
                  }
                }}
              >
                Download HTML
              </Button>
            </div>
          </div>

          <Button onClick={() => { setCompleted(false); setCurrentStep(0); setAnswers({}); }}>
            Start New Assessment
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fundamental Rights Impact Assessment (FRIA)</CardTitle>
        <CardDescription>Article 27 EU AI Act - 10 Questions</CardDescription>
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all" 
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            Question {currentStep + 1} of {FRIA_QUESTIONS.length}
          </p>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-start gap-2 mb-4">
          <input
            type="checkbox"
            id="not-applicable"
            checked={notApplicable}
            onChange={(e) => setNotApplicable(e.target.checked)}
            className="mt-1"
          />
          <label htmlFor="not-applicable" className="text-sm">
            FRIA not applicable (provide justification below)
          </label>
        </div>

        {notApplicable ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Justification</label>
              <textarea
                value={justification}
                onChange={(e) => setJustification(e.target.value)}
                className="w-full p-3 border rounded-md min-h-[120px]"
                placeholder="Explain why FRIA is not applicable for this system..."
              />
            </div>
            <Button onClick={handleSubmit} disabled={loading || !justification}>
              {loading ? 'Submitting...' : 'Submit'}
            </Button>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">{currentQuestion.text}</h3>
              
              <div className="space-y-2">
                {['Yes', 'No', 'N/A'].map((option) => (
                  <label key={option} className="flex items-center gap-3 p-3 border rounded-md cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name={currentQuestion.key}
                      value={option}
                      checked={answers[currentQuestion.key] === option}
                      onChange={() => handleAnswer(option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <Button 
                variant="outline" 
                onClick={handlePrevious} 
                disabled={currentStep === 0}
              >
                Previous
              </Button>
              
              {currentStep === FRIA_QUESTIONS.length - 1 ? (
                <div className="space-y-4">
                  <div className="p-4 border rounded bg-gray-50">
                    <h4 className="font-medium mb-3">Extended Assessment Fields</h4>
                    
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium mb-1">Proportionality Assessment</label>
                        <textarea
                          className="w-full border rounded p-2"
                          rows={2}
                          placeholder="Assess if safeguards are proportionate to risks..."
                          value={proportionality}
                          onChange={(e) => setProportionality(e.target.value)}
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-1">Residual Risk Level</label>
                        <select
                          className="w-full border rounded p-2"
                          value={residualRisk}
                          onChange={(e) => setResidualRisk(e.target.value)}
                        >
                          <option value="Low">Low</option>
                          <option value="Medium">Medium</option>
                          <option value="High">High</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-1">DPIA Reference (if applicable)</label>
                        <input
                          type="text"
                          className="w-full border rounded p-2"
                          placeholder="Link to DPIA document..."
                          value={dpiaReference}
                          onChange={(e) => setDpiaReference(e.target.value)}
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium mb-1">Review Notes</label>
                        <textarea
                          className="w-full border rounded p-2"
                          rows={2}
                          placeholder="Additional notes for review..."
                          value={reviewNotes}
                          onChange={(e) => setReviewNotes(e.target.value)}
                        />
                      </div>
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleSubmit} 
                    disabled={loading || Object.keys(answers).length < FRIA_QUESTIONS.length}
                  >
                    {loading ? 'Submitting...' : 'Submit Assessment'}
                  </Button>
                </div>
              ) : (
                <Button 
                  onClick={handleNext}
                  disabled={!answers[currentQuestion.key]}
                >
                  Next
                </Button>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

