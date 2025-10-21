'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { api } from '@/lib/api'

interface BlockingIssue {
  id: string
  severity: 'critical' | 'high' | 'medium'
  title: string
  description: string
  action: string
  action_url?: string
}

interface BlockingIssuesSummary {
  total_issues: number
  critical_issues: number
  high_issues: number
  medium_issues: number
  can_export: boolean
  issues: BlockingIssue[]
}

interface BlockingIssuesBannerProps {
  systemId: number
  onIssuesChange?: (hasIssues: boolean) => void
}

export function BlockingIssuesBanner({ systemId, onIssuesChange }: BlockingIssuesBannerProps) {
  const [summary, setSummary] = useState<BlockingIssuesSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    loadBlockingIssues()
  }, [systemId])

  const loadBlockingIssues = async () => {
    try {
      const data = await api.getBlockingIssues(systemId)
      setSummary(data)
      onIssuesChange?.(data.total_issues > 0)
    } catch (error) {
      console.error('Failed to load blocking issues:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-500" />
      case 'high':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      default:
        return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-green-100 text-green-800 border-green-200'
    }
  }

  if (loading) {
    return (
      <Card className="mb-4">
        <CardContent className="p-4">
          <div className="text-center">Loading compliance status...</div>
        </CardContent>
      </Card>
    )
  }

  if (!summary || summary.total_issues === 0) {
    return (
      <Card className="mb-4 border-green-200 bg-green-50">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <span className="text-green-800 font-medium">
              ✅ System ready for audit-grade export
            </span>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <>
      <Card className={`mb-4 border-2 ${summary.critical_issues > 0 ? 'border-red-200 bg-red-50' : 'border-orange-200 bg-orange-50'}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              <CardTitle className="text-lg">
                ⚠️ Blocking Issues ({summary.total_issues})
              </CardTitle>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setModalOpen(true)}
            >
              View Details
            </Button>
          </div>
          <CardDescription>
            {summary.critical_issues > 0 && (
              <span className="text-red-600 font-medium">
                {summary.critical_issues} critical issue{summary.critical_issues > 1 ? 's' : ''} must be resolved
              </span>
            )}
            {summary.critical_issues === 0 && summary.high_issues > 0 && (
              <span className="text-orange-600 font-medium">
                {summary.high_issues} high-priority issue{summary.high_issues > 1 ? 's' : ''} should be resolved
              </span>
            )}
            {summary.critical_issues === 0 && summary.high_issues === 0 && (
              <span className="text-yellow-600">
                {summary.medium_issues} minor issue{summary.medium_issues > 1 ? 's' : ''} for improvement
              </span>
            )}
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Blocking Issues Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Blocking Issues</h3>
              <Button variant="outline" onClick={() => setModalOpen(false)}>
                Close
              </Button>
            </div>
            
            <div className="space-y-3">
              {summary.issues.map((issue) => (
                <div key={issue.id} className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}>
                  <div className="flex items-start space-x-3">
                    {getSeverityIcon(issue.severity)}
                    <div className="flex-1">
                      <h4 className="font-medium">{issue.title}</h4>
                      <p className="text-sm mt-1">{issue.description}</p>
                      <div className="mt-2">
                        <Badge variant="outline" className="text-xs">
                          {issue.action}
                        </Badge>
                        {issue.action_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            className="ml-2 text-xs"
                            onClick={() => {
                              if (issue.action_url?.startsWith('http')) {
                                window.open(issue.action_url, '_blank')
                              } else {
                                window.location.href = issue.action_url || '#'
                              }
                            }}
                          >
                            Fix Now
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">Summary</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-red-600 font-medium">{summary.critical_issues} Critical</span>
                </div>
                <div>
                  <span className="text-orange-600 font-medium">{summary.high_issues} High</span>
                </div>
                <div>
                  <span className="text-yellow-600 font-medium">{summary.medium_issues} Medium</span>
                </div>
                <div>
                  <span className="text-gray-600">Total: {summary.total_issues}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
