'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { IncidentsTable } from '@/components/incidents-modal'
import ComplianceSuite from '@/components/compliance-suite'

export default function ReportsPage() {
  const [summary, setSummary] = useState<any>(null)
  const [score, setScore] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getReportSummary(),
      api.getReportScore()
    ])
      .then(([summaryData, scoreData]) => {
        setSummary(summaryData)
        setScore(scoreData)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reports & Exports</h1>
        <p className="text-muted-foreground">
          Generate compliance reports and documentation
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Compliance Overview</CardTitle>
            <CardDescription>Key metrics</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Total Systems</span>
              <span className="text-2xl font-bold">{summary?.systems || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">High-Risk</span>
              <span className="text-2xl font-bold text-red-600">{summary?.high_risk || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">GPAI Systems</span>
              <span className="text-2xl font-bold text-purple-600">{summary?.gpai_count || 0}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Org Score</span>
              <span className="text-2xl font-bold text-green-600">
                {score?.org_score ? `${Math.round(score.org_score * 100)}%` : 'N/A'}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>CSV Templates</CardTitle>
            <CardDescription>Download templates for data import</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <a href="/assets/templates/aims_inventory_template.csv" download>
              <Button variant="outline" className="w-full" size="sm">
                AI Systems Inventory
              </Button>
            </a>
            <a href="/assets/templates/aims_control_plan_raci_template.csv" download>
              <Button variant="outline" className="w-full" size="sm">
                RACI Control Plan
              </Button>
            </a>
            <a href="/assets/templates/aims_evidence_manifest_template.csv" download>
              <Button variant="outline" className="w-full" size="sm">
                Evidence Manifest
              </Button>
            </a>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Export Reports</CardTitle>
            <CardDescription>Generate compliance documentation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button 
              variant="outline" 
              className="w-full" 
              size="sm"
              onClick={() => {
                window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002'}/reports/deck.pptx`, '_blank')
              }}
            >
              Executive Deck (.pptx)
            </Button>
            <Button 
              variant="outline" 
              className="w-full" 
              size="sm"
              onClick={() => {
                window.open(`${process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8002'}/reports/annex-iv.zip?system_id=1`, '_blank')
              }}
            >
              Annex IV Package (.zip)
            </Button>
            <a href="/assets/mock/aims_readiness_mock.html" target="_blank">
              <Button variant="outline" className="w-full" size="sm">
                View Sample Report
              </Button>
            </a>
          </CardContent>
        </Card>
      </div>

      <ComplianceSuite />

      <IncidentsTable />
    </div>
  )
}

