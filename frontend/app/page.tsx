'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { Database, ShieldAlert, Bot, Target, FileText, AlarmClock, Activity, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [score, setScore] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showScoreModal, setShowScoreModal] = useState(false)

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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 p-6 space-y-8">
        <div>
          <Skeleton className="h-10 w-64 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 p-6 space-y-8">
      <div>
        <h1 className="text-2xl md:text-3xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          ISO/IEC 42001 + EU AI Act compliance overview
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Link href="/inventory">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <Database className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">Total AI Systems</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Registered in inventory</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold" aria-label={`${summary?.systems || 0} total AI systems`}>
                {summary?.systems || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to view all systems →</div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory?filter=high-risk">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <ShieldAlert className="h-5 w-5 text-red-600 dark:text-red-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">High-Risk Systems</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">EU AI Act classification</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold text-red-600" aria-label={`${summary?.high_risk || 0} high-risk systems`}>
                {summary?.high_risk || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to view high-risk →</div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory?filter=gpai">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <Bot className="h-5 w-5 text-purple-600 dark:text-purple-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">GPAI Systems</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">General Purpose AI</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold text-purple-600" aria-label={`${summary?.gpai_count || 0} GPAI systems`}>
                {summary?.gpai_count || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to view GPAI →</div>
            </CardContent>
          </Card>
        </Link>

        <Card 
          className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer"
          onClick={() => setShowScoreModal(true)}
        >
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <Target className="h-5 w-5 text-green-600 dark:text-green-400" aria-hidden="true" />
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                Compliance Score
                <button 
                  className="text-xs text-muted-foreground hover:text-foreground"
                  title={score?.tooltip || ''}
                  onClick={(e) => {
                    e.stopPropagation()
                    setShowScoreModal(true)
                  }}
                  aria-label="Show score calculation details"
                >
                  ℹ️
                </button>
              </CardTitle>
            </div>
            <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Overall readiness</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl md:text-4xl font-bold text-green-600" aria-label={`Compliance score ${score?.org_score ? Math.round(score.org_score * 100) : 'N/A'} percent`}>
              {score?.org_score ? `${Math.round(score.org_score * 100)}%` : 'N/A'}
            </div>
            {score?.tooltip && (
              <div className="mt-2 text-xs text-muted-foreground">
                {score.tooltip}
              </div>
            )}
            <div className="text-xs text-muted-foreground mt-1">Click for detailed breakdown →</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Link href="/inventory?tab=evidence">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">Evidence Coverage</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Controls with evidence</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold text-blue-600" aria-label={`Evidence coverage ${score?.coverage_pct ? Math.round(score.coverage_pct * 100) : 'N/A'} percent`}>
                {score?.coverage_pct ? `${Math.round(score.coverage_pct * 100)}%` : 'N/A'}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to manage evidence →</div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/inventory?tab=controls&filter=due">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <AlarmClock className="h-5 w-5 text-orange-600 dark:text-orange-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">Open Actions</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Due within 7 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold text-orange-600" aria-label={`${summary?.open_actions_7d || 0} open actions`}>
                {summary?.open_actions_7d || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to view actions →</div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/reports?tab=incidents">
          <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800 motion-safe:hover:shadow-lg transition-all duration-200 motion-safe:hover:scale-[1.01] cursor-pointer">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <Activity className="h-5 w-5 text-yellow-600 dark:text-yellow-400" aria-hidden="true" />
                <CardTitle className="text-lg font-semibold">Recent Incidents</CardTitle>
              </div>
              <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Last 30 days</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-3xl md:text-4xl font-bold text-yellow-600" aria-label={`${summary?.last_30d_incidents || 0} recent incidents`}>
                {summary?.last_30d_incidents || 0}
              </div>
              <div className="text-xs text-muted-foreground mt-1">Click to view incidents →</div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800">
        <CardHeader className="pb-2">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
            <CardTitle className="text-lg font-semibold">Readiness Trend</CardTitle>
          </div>
          <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Compliance progress over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-32 flex items-center justify-center">
            <div className="w-full h-full relative">
              <svg className="w-full h-full" aria-label="Readiness trend chart">
                <defs>
                  <linearGradient id="trendGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stopColor="rgb(79, 70, 229)" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="rgb(79, 70, 229)" stopOpacity="0.05" />
                  </linearGradient>
                </defs>
                <path
                  d="M 0 100 L 0 80 L 50 70 L 100 65 L 150 55 L 200 50 L 250 45 L 300 40 L 300 100 Z"
                  fill="url(#trendGradient)"
                  stroke="rgb(79, 70, 229)"
                  strokeWidth="2"
                />
              </svg>
              <div className="absolute bottom-2 right-2 text-xs text-gray-400 dark:text-gray-500">
                Sample data
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold">System Breakdown</CardTitle>
            <CardDescription className="text-sm text-gray-500 dark:text-gray-400">By compliance score</CardDescription>
          </CardHeader>
          <CardContent>
            {score?.by_system && score.by_system.length > 0 ? (
              <div className="space-y-3">
                {score.by_system.map((sys: any) => (
                  <div key={sys.id} className="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <span className="text-sm font-medium">System #{sys.id}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-300"
                          style={{ width: `${Math.round(sys.score * 100)}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold w-12 text-right">
                        {Math.round(sys.score * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-400">No systems assessed yet</p>
            )}
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-md bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl border border-gray-100/70 dark:border-gray-800">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-semibold">Upcoming Actions</CardTitle>
            <CardDescription className="text-sm text-gray-500 dark:text-gray-400">Required compliance activities</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {summary?.open_actions_7d > 0 && (
                <li className="flex items-center gap-2 p-2 rounded-lg hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors">
                  <span className="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0"></span>
                  <span className="text-sm">{summary.open_actions_7d} controls due within 7 days</span>
                </li>
              )}
              {summary?.high_risk > 0 && (
                <li className="flex items-center gap-2 p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                  <span className="w-2 h-2 bg-red-500 rounded-full flex-shrink-0"></span>
                  <span className="text-sm">Complete FRIA for {summary.high_risk} high-risk systems</span>
                </li>
              )}
              {score?.coverage_pct < 0.5 && (
                <li className="flex items-center gap-2 p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors">
                  <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></span>
                  <span className="text-sm">Upload evidence to improve coverage ({Math.round((score?.coverage_pct || 0) * 100)}%)</span>
                </li>
              )}
              {(!summary?.open_actions_7d && !summary?.high_risk && score?.coverage_pct >= 0.5) && (
                <li className="flex items-center gap-2 p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
                  <span className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0"></span>
                  <span className="text-sm text-green-700 dark:text-green-300 font-medium">All critical actions completed ✓</span>
                </li>
              )}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Score Details Modal */}
      {showScoreModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto border border-gray-200 dark:border-gray-800">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl md:text-2xl font-semibold tracking-tight">Compliance Score Breakdown</h2>
              <button 
                onClick={() => setShowScoreModal(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl transition-colors"
                aria-label="Close modal"
              >
                ×
              </button>
            </div>
            
            {score && (
              <div className="space-y-6">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 p-4 rounded-xl border border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold mb-2 text-lg">Overall Score: {Math.round(score.org_score * 100)}%</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">{score.tooltip}</p>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <strong className="text-gray-700 dark:text-gray-200">Controls Implemented:</strong>
                      <br />
                      <span className="text-lg font-bold text-green-600">{Math.round((score.controls_pct || 0) * 100)}%</span>
                    </div>
                    <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <strong className="text-gray-700 dark:text-gray-200">Evidence Coverage:</strong>
                      <br />
                      <span className="text-lg font-bold text-blue-600">{Math.round((score.coverage_pct || 0) * 100)}%</span>
                    </div>
                  </div>
                </div>

                {score.by_system && score.by_system.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-3 text-lg">System Breakdown</h3>
                    <div className="space-y-3">
                      {score.by_system.map((sys: any) => (
                        <div key={sys.id} className="border border-gray-200 dark:border-gray-700 rounded-xl p-4 bg-gray-50 dark:bg-gray-800/50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-700 dark:text-gray-200">System #{sys.id}</span>
                            <span className="text-lg font-bold text-green-600 dark:text-green-400">
                              {Math.round(sys.score * 100)}%
                            </span>
                          </div>
                          <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all duration-300"
                              style={{ width: `${Math.round(sys.score * 100)}%` }}
                            />
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                            Weight: {sys.weight}x | Controls: {Math.round((sys.controls_pct || 0) * 100)}% | Evidence: {Math.round((sys.evidence_pct || 0) * 100)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-xl border border-blue-200 dark:border-blue-800">
                  <h4 className="font-semibold mb-2 text-gray-700 dark:text-gray-200">How to Improve</h4>
                  <ul className="text-sm space-y-1 text-gray-600 dark:text-gray-300">
                    {score.coverage_pct < 0.7 && (
                      <li>• Upload evidence for missing controls</li>
                    )}
                    {score.controls_pct < 0.8 && (
                      <li>• Implement missing controls</li>
                    )}
                    <li>• Complete FRIA for high-risk systems</li>
                    <li>• Update control owners and due dates</li>
                  </ul>
                </div>
              </div>
            )}
            
            <div className="flex justify-end mt-6">
              <button 
                onClick={() => setShowScoreModal(false)}
                className="px-6 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 shadow-md motion-safe:hover:scale-105"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

