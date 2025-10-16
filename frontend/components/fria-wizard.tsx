'use client'

import { useState } from 'react'
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

  const currentQuestion = FRIA_QUESTIONS[currentStep]
  const progress = ((currentStep + 1) / FRIA_QUESTIONS.length) * 100

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
      const result = await api.createFRIA(systemId, {
        system_id: systemId,
        applicable: !notApplicable,
        answers: notApplicable ? {} : answers,
        justification: notApplicable ? justification : undefined,
      })
      setFriaResult(result)
      setCompleted(true)
      onComplete?.()
    } catch (error) {
      alert('Failed to submit FRIA: ' + error)
    } finally {
      setLoading(false)
    }
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
                <Button 
                  onClick={handleSubmit} 
                  disabled={loading || Object.keys(answers).length < FRIA_QUESTIONS.length}
                >
                  {loading ? 'Submitting...' : 'Submit Assessment'}
                </Button>
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

