'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import { validateDashboardData, getDataConfidenceIndicator } from '@/lib/data-validation'
import { 
  TrendingUp, 
  TrendingDown, 
  Info, 
  AlertTriangle, 
  ArrowRight,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react'

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [score, setScore] = useState<any>(null)
  const [blockingIssues, setBlockingIssues] = useState<any[]>([])
  const [upcomingDeadlines, setUpcomingDeadlines] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [dataErrors, setDataErrors] = useState<string[]>([])
  const [dataValidation, setDataValidation] = useState<any>(null)

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [summaryData, scoreData, blockingData, deadlinesData] = await Promise.all([
          api.getReportSummary(),
          api.getReportScore(),
          api.getBlockingIssues(),
          api.getUpcomingDeadlines()
        ])
        
        setSummary(summaryData)
        setScore(scoreData)
        setBlockingIssues(blockingData.blocking_issues || [])
        setUpcomingDeadlines(deadlinesData.upcoming_deadlines || [])
        
        // Check evidence coverage status
        const coverageWarnings = []
        if (summaryData.evidence_coverage_status === 'error') {
          coverageWarnings.push('⚠️ Evidence coverage calculation failed - data may be inaccurate')
        } else if (summaryData.evidence_coverage_status === 'no_controls') {
          coverageWarnings.push('ℹ️ No controls found - evidence coverage cannot be calculated')
        } else if (summaryData.evidence_coverage_status === 'calculated_legacy') {
          coverageWarnings.push('⚠️ Evidence coverage using legacy method - may not reflect all evidence')
        } else if (summaryData.evidence_coverage_status === 'no_evidence') {
          coverageWarnings.push('ℹ️ No evidence found - upload evidence to improve coverage metrics')
        }
        
        // Validate all data
        const validation = validateDashboardData({
          summary: summaryData,
          score: scoreData,
          blockingIssues: blockingData,
          upcomingDeadlines: deadlinesData
        })
        setDataValidation(validation)
        
        // Combine validation errors with coverage warnings
        const allErrors = [...validation.errors, ...coverageWarnings]
        if (allErrors.length > 0) {
          setDataErrors(allErrors)
        } else {
          setDataErrors([])
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        setDataErrors([`Failed to load dashboard data: ${error instanceof Error ? error.message : 'Unknown error'}`])
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
            {/* Header */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-foreground">Compliance at a glance</h1>
                  <p className="text-muted-foreground">Monitor your AI governance across all systems</p>
                </div>
                {dataValidation && (
                  <div className="flex items-center gap-2">
                    <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm ${
                      dataValidation.confidence === 'high' 
                        ? 'bg-green-100 text-green-700' 
                        : dataValidation.confidence === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {dataValidation.confidence === 'high' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <AlertCircle className="w-4 h-4" />
                      )}
                      {getDataConfidenceIndicator(dataValidation.confidence).text}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Last updated: {new Date(dataValidation.lastUpdated).toLocaleTimeString()}
                    </div>
                  </div>
                )}
              </div>
            </div>

      {/* KPI Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="kpi-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Compliant Systems</h3>
            </div>
            <div className="text-3xl font-bold mb-2">
              {summary ? `${Math.round((summary.systems - summary.high_risk) / summary.systems * 100)}%` : 'N/A'}
            </div>
            <div className="flex items-center gap-2 text-sm">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-green-foreground">
                {summary ? `${summary.systems - summary.high_risk}/${summary.systems} systems compliant` : 'Loading...'}
              </span>
            </div>
            <div className="flex gap-1 mt-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div 
                  key={i} 
                  className={`h-2 flex-1 rounded ${
                    i < 3 ? 'bg-green-500' : 'bg-muted'
                  }`} 
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Audit-Ready Systems</h3>
              <Info className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="text-3xl font-bold mb-2">
              {summary ? `${summary.systems - summary.high_risk}/${summary.systems}` : 'N/A'}
            </div>
            <div className="text-sm text-muted-foreground mb-4">
              {summary ? `${Math.round((summary.systems - summary.high_risk) / summary.systems * 100)}% of systems ready` : 'Loading...'}
            </div>
            <div className="flex gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <div 
                  key={i} 
                  className={`h-2 flex-1 rounded ${
                    i < 2 ? 'bg-blue-500' : 'bg-muted'
                  }`} 
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Recent Incidents</h3>
            </div>
            <div className="text-3xl font-bold mb-2">
              {summary ? `${summary.last_30d_incidents || 0} incidents` : 'N/A'}
            </div>
            <div className="flex items-center gap-2 text-sm">
              <AlertTriangle className="w-4 h-4 text-orange-500" />
              <span className="text-orange-500">
                {summary ? `Last 30 days` : 'Loading...'}
              </span>
            </div>
            <div className="flex gap-1 mt-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div 
                  key={i} 
                  className={`h-2 flex-1 rounded ${
                    i < 4 ? 'bg-orange-500' : 'bg-muted'
                  }`} 
                />
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="kpi-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-muted-foreground">Compliance Score</h3>
            </div>
            <div className="text-3xl font-bold mb-2">
              {score ? `${Math.round(score.org_score * 100)}%` : 'N/A'}
            </div>
            <div className="flex items-center gap-2 text-sm">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <span className="text-blue-500">
                {score ? `Overall compliance score` : 'Loading...'}
              </span>
            </div>
            <div className="flex gap-1 mt-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div 
                  key={i} 
                  className={`h-2 flex-1 rounded ${
                    i < 3 ? 'bg-purple-500' : 'bg-muted'
                  }`} 
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Validation Errors */}
      {dataErrors.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-red-900">Data Loading Issues</h4>
                <ul className="text-sm text-red-700 mt-1 list-disc list-inside">
                  {dataErrors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bottom Sections */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* What's blocking go-live? */}
        <Card className="kpi-card">
          <CardHeader>
            <CardTitle className="text-lg">What&apos;s blocking go-live?</CardTitle>
            <CardDescription>Critical issues preventing system deployment</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {blockingIssues.length === 0 ? (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 text-green-500">✓</div>
                  <div>
                    <h4 className="font-medium text-green-900">No blocking issues</h4>
                    <p className="text-sm text-green-700 mt-1">
                      All systems are ready for deployment
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              blockingIssues.slice(0, 3).map((issue) => (
                <div 
                  key={issue.id}
                  className={`p-4 border rounded-lg ${
                    issue.severity === 'critical' 
                      ? 'bg-red-50 border-red-200' 
                      : issue.severity === 'high'
                      ? 'bg-orange-50 border-orange-200'
                      : 'bg-yellow-50 border-yellow-200'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <AlertTriangle className={`w-5 h-5 mt-0.5 ${
                      issue.severity === 'critical' 
                        ? 'text-red-500' 
                        : issue.severity === 'high'
                        ? 'text-orange-500'
                        : 'text-yellow-500'
                    }`} />
                    <div className="flex-1">
                      <h4 className={`font-medium ${
                        issue.severity === 'critical' 
                          ? 'text-red-900' 
                          : issue.severity === 'high'
                          ? 'text-orange-900'
                          : 'text-yellow-900'
                      }`}>
                        {issue.title}
                      </h4>
                      <p className={`text-sm mt-1 ${
                        issue.severity === 'critical' 
                          ? 'text-red-700' 
                          : issue.severity === 'high'
                          ? 'text-orange-700'
                          : 'text-yellow-700'
                      }`}>
                        {issue.description}
                      </p>
                      <Link 
                        href={issue.action_url}
                        className="text-sm text-blue-600 hover:text-blue-800 mt-2 flex items-center gap-1"
                      >
                        {issue.action} <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Upcoming deadlines */}
        <Card className="kpi-card">
          <CardHeader>
            <CardTitle className="text-lg">Upcoming deadlines</CardTitle>
            <CardDescription>Critical dates in the next 30 days</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {upcomingDeadlines.length === 0 ? (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-5 h-5 text-green-500">✓</div>
                  <div>
                    <h4 className="font-medium text-green-900">No upcoming deadlines</h4>
                    <p className="text-sm text-green-700 mt-1">
                      All deadlines are met or not applicable
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              upcomingDeadlines.slice(0, 3).map((deadline) => (
                <div 
                  key={deadline.id}
                  className={`flex items-center justify-between p-3 border rounded-lg ${
                    deadline.severity === 'critical' 
                      ? 'border-red-200 bg-red-50' 
                      : deadline.severity === 'high'
                      ? 'border-orange-200 bg-orange-50'
                      : 'border-border bg-background'
                  }`}
                >
                  <div>
                    <h4 className="font-medium">{deadline.title}</h4>
                    <p className="text-sm text-muted-foreground">{deadline.description}</p>
                  </div>
                  <div className="text-right">
                    <div className={`text-sm font-medium ${
                      deadline.severity === 'critical' 
                        ? 'text-red-600' 
                        : deadline.severity === 'high'
                        ? 'text-orange-600'
                        : 'text-foreground'
                    }`}>
                      {deadline.days_until_due === 0 ? 'Due today' : 
                       deadline.days_until_due === 1 ? '1 day' :
                       `${deadline.days_until_due} days`}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(deadline.due_date).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}