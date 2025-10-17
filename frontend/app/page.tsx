'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { api } from '@/lib/api'
import { Database, ShieldAlert, Bot, Target, FileText, AlarmClock, Activity, TrendingUp, Info, Brain, Filter, RefreshCw } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer } from 'recharts'
// import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null)
  const [score, setScore] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [showScoreModal, setShowScoreModal] = useState(false)
  const [darkMode, setDarkMode] = useState(false)

  // Sample data for readiness trend chart
  const readinessData = [
    { date: 'Jan', readiness: 45 },
    { date: 'Feb', readiness: 52 },
    { date: 'Mar', readiness: 58 },
    { date: 'Apr', readiness: 65 },
    { date: 'May', readiness: 72 },
    { date: 'Jun', readiness: 78 },
    { date: 'Jul', readiness: 82 },
    { date: 'Aug', readiness: 85 },
    { date: 'Sep', readiness: 88 },
    { date: 'Oct', readiness: 91 },
  ]

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

  // Toggle dark mode
  useEffect(() => {
    const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    setDarkMode(isDark)
    document.documentElement.classList.toggle('dark', isDark)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950 p-6 space-y-8">
        <div>
          <Skeleton className="h-10 w-64 mb-2 bg-white/50 dark:bg-gray-800/50" />
          <Skeleton className="h-4 w-96 bg-white/50 dark:bg-gray-800/50" />
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <Skeleton className="h-40 rounded-2xl bg-white/30 dark:bg-gray-800/30 backdrop-blur-xl border border-white/20 dark:border-gray-700/50" />
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950 p-6 space-y-8">
        {/* Header with Theme Toggle */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              AIMS Readiness
            </h1>
            <p className="text-sm text-gray-700 dark:text-gray-300 mt-1 font-medium">
              ISO/IEC 42001 + EU AI Act compliance overview
            </p>
          </div>
          
          {/* Theme Toggle */}
          <button
            onClick={() => {
              setDarkMode(!darkMode)
              document.documentElement.classList.toggle('dark')
            }}
            className="p-2 rounded-xl bg-white/20 dark:bg-gray-800/20 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 hover:bg-white/30 dark:hover:bg-gray-800/30 transition-all duration-300"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </motion.div>

        {/* Main KPI Cards */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-4"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            whileHover={{ y: -8, scale: 1.02 }}
            className="group"
          >
            <Link href="/inventory">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-blue-500/20 backdrop-blur-xl">
                      <Database className="h-6 w-6 text-blue-600 dark:text-blue-400" aria-hidden="true" />
                    </div>
                    <Info className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors" title="Total number of AI systems registered in your inventory" />
                  </div>
                  <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200 mt-2">Total AI Systems</CardTitle>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Registered in inventory</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-4xl md:text-5xl font-black text-gray-900 dark:text-gray-100"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 }}
                    aria-label={`${summary?.systems || 0} total AI systems`}
                  >
                    {summary?.systems || 0}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to view all systems</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>

          {/* High-Risk Systems Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            whileHover={{ y: -8, scale: 1.02 }}
            className="group"
          >
            <Link href="/inventory?filter=high-risk">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-orange-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-red-500/20 backdrop-blur-xl">
                      <ShieldAlert className="h-6 w-6 text-red-600 dark:text-red-400" aria-hidden="true" />
                    </div>
                    <Info className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors" title="Systems classified as high-risk under EU AI Act" />
                  </div>
                  <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200 mt-2">High-Risk Systems</CardTitle>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">EU AI Act classification</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-4xl md:text-5xl font-black text-red-600 dark:text-red-400"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 }}
                    aria-label={`${summary?.high_risk || 0} high-risk systems`}
                  >
                    {summary?.high_risk || 0}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to view high-risk</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>

          {/* GPAI Systems Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            whileHover={{ y: -8, scale: 1.02 }}
            className="group"
          >
            <Link href="/inventory?filter=gpai">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative">
                <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center justify-between">
                    <div className="p-3 rounded-2xl bg-purple-500/20 backdrop-blur-xl">
                      <Bot className="h-6 w-6 text-purple-600 dark:text-purple-400" aria-hidden="true" />
                    </div>
                    <Info className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors" title="General Purpose AI systems requiring special attention" />
                  </div>
                  <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200 mt-2">GPAI Systems</CardTitle>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">General Purpose AI</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-4xl md:text-5xl font-black text-purple-600 dark:text-purple-400"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.8 }}
                    aria-label={`${summary?.gpai_count || 0} GPAI systems`}
                  >
                    {summary?.gpai_count || 0}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to view GPAI</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          </motion.div>

          {/* Compliance Score Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            whileHover={{ y: -8, scale: 1.02 }}
            className="group"
          >
            <Card 
              className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative"
              onClick={() => setShowScoreModal(true)}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <CardHeader className="pb-3 relative z-10">
                <div className="flex items-center justify-between">
                  <div className="p-3 rounded-2xl bg-green-500/20 backdrop-blur-xl">
                    <Target className="h-6 w-6 text-green-600 dark:text-green-400" aria-hidden="true" />
                  </div>
                  <button 
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowScoreModal(true)
                    }}
                    aria-label="Show score calculation details"
                    title="Click to see detailed breakdown"
                  >
                    <Info className="h-4 w-4" />
                  </button>
                </div>
                <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200 mt-2">Compliance Score</CardTitle>
                <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Overall readiness</CardDescription>
              </CardHeader>
              <CardContent className="relative z-10">
                <motion.div 
                  className="text-4xl md:text-5xl font-black text-green-600 dark:text-green-400"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.5, delay: 0.8 }}
                  aria-label={`Compliance score ${score?.org_score ? Math.round(score.org_score * 100) : 'N/A'} percent`}
                >
                  {score?.org_score ? `${Math.round(score.org_score * 100)}%` : 'N/A'}
                </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                  <span>Click for detailed breakdown</span>
                  <motion.span
                    animate={{ x: [0, 4, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    →
                  </motion.span>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>


        {/* AI Insights Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="grid gap-6 md:grid-cols-3"
        >
          <Link href="/inventory?tab=evidence">
            <motion.div whileHover={{ y: -4, scale: 1.02 }} className="h-full">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-blue-500/20 backdrop-blur-xl">
                      <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
                    </div>
                    <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200">Evidence Coverage</CardTitle>
                  </div>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Controls with evidence</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-3xl md:text-4xl font-black text-blue-600 dark:text-blue-400"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 1.0 }}
                    aria-label={`Evidence coverage ${score?.coverage_pct ? Math.round(score.coverage_pct * 100) : 'N/A'} percent`}
                  >
                    {score?.coverage_pct ? `${Math.round(score.coverage_pct * 100)}%` : 'N/A'}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to manage evidence</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </Link>

          <Link href="/inventory?tab=controls&filter=due">
            <motion.div whileHover={{ y: -4, scale: 1.02 }} className="h-full">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-red-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-orange-500/20 backdrop-blur-xl">
                      <AlarmClock className="h-5 w-5 text-orange-600 dark:text-orange-400" aria-hidden="true" />
                    </div>
                    <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200">Open Actions</CardTitle>
                  </div>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Due within 7 days</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-3xl md:text-4xl font-black text-orange-600 dark:text-orange-400"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 1.0 }}
                    aria-label={`${summary?.open_actions_7d || 0} open actions`}
                  >
                    {summary?.open_actions_7d || 0}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to view actions</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </Link>

          <Link href="/reports?tab=incidents">
            <motion.div whileHover={{ y: -4, scale: 1.02 }} className="h-full">
              <Card className="h-full rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 cursor-pointer overflow-hidden relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/10 to-amber-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-yellow-500/20 backdrop-blur-xl">
                      <Activity className="h-5 w-5 text-yellow-600 dark:text-yellow-400" aria-hidden="true" />
                    </div>
                    <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200">Recent Incidents</CardTitle>
                  </div>
                  <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Last 30 days</CardDescription>
                </CardHeader>
                <CardContent className="relative z-10">
                  <motion.div 
                    className="text-3xl md:text-4xl font-black text-yellow-600 dark:text-yellow-400"
                    initial={{ scale: 0.5 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.5, delay: 1.0 }}
                    aria-label={`${summary?.last_30d_incidents || 0} recent incidents`}
                  >
                    {summary?.last_30d_incidents || 0}
                  </motion.div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-gray-600 dark:text-gray-300 font-medium">
                    <span>Click to view incidents</span>
                    <motion.span
                      animate={{ x: [0, 4, 0] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    >
                      →
                    </motion.span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </Link>
        </motion.div>

        {/* Readiness Trend Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.0 }}
        >
          <Card className="rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-indigo-500/20 backdrop-blur-xl">
                    <TrendingUp className="h-5 w-5 text-indigo-600 dark:text-indigo-400" aria-hidden="true" />
                  </div>
                  <div>
                    <CardTitle className="text-xl font-bold text-gray-800 dark:text-gray-200">Readiness Trend</CardTitle>
                    <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">Compliance progress over time</CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="p-2 rounded-lg bg-white/20 dark:bg-gray-800/20 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 hover:bg-white/30 dark:hover:bg-gray-800/30 transition-all duration-300">
                    <Filter className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  </button>
                  <button className="p-2 rounded-lg bg-white/20 dark:bg-gray-800/20 backdrop-blur-xl border border-white/30 dark:border-gray-700/30 hover:bg-white/30 dark:hover:bg-gray-800/30 transition-all duration-300">
                    <RefreshCw className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                  </button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={readinessData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="readinessGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0.05}/>
                      </linearGradient>
                    </defs>
                    <XAxis 
                      dataKey="date" 
                      tickLine={false} 
                      axisLine={false}
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                    />
                    <YAxis 
                      tickLine={false} 
                      axisLine={false}
                      tick={{ fontSize: 12, fill: '#6b7280' }}
                      domain={[0, 100]}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="readiness" 
                      stroke="#6366f1" 
                      strokeWidth={3}
                      fill="url(#readinessGradient)"
                      dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
                      activeDot={{ r: 6, stroke: '#6366f1', strokeWidth: 2 }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="flex items-center justify-between mt-4 text-xs text-gray-500 dark:text-gray-400">
                <span>Showing last 10 months</span>
                <span className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-indigo-500"></div>
                  Readiness Score
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Bottom Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
          className="grid gap-6 md:grid-cols-2"
        >
          <Card className="rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-emerald-500/20 backdrop-blur-xl">
                  <Brain className="h-5 w-5 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold text-gray-800 dark:text-gray-200">System Breakdown</CardTitle>
                  <CardDescription className="text-sm text-gray-600 dark:text-gray-400">By compliance score</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {score?.by_system && score.by_system.length > 0 ? (
                <div className="space-y-4">
                  {score.by_system.map((sys: any, index: number) => (
                    <motion.div 
                      key={sys.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 1.4 + index * 0.1 }}
                      className="flex items-center justify-between p-3 rounded-xl bg-white/10 dark:bg-gray-800/10 backdrop-blur-xl hover:bg-white/20 dark:hover:bg-gray-800/20 transition-all duration-300 group"
                    >
                      <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">System #{sys.id}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-3 bg-gray-200/50 dark:bg-gray-700/50 rounded-full overflow-hidden">
                          <motion.div 
                            className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: `${Math.round(sys.score * 100)}%` }}
                            transition={{ duration: 1, delay: 1.6 + index * 0.1 }}
                          />
                        </div>
                        <span className="text-sm font-bold w-12 text-right text-emerald-600 dark:text-emerald-400">
                          {Math.round(sys.score * 100)}%
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                    <Brain className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">No systems assessed yet</p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="rounded-3xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl overflow-hidden">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-amber-500/20 backdrop-blur-xl">
                  <AlarmClock className="h-5 w-5 text-amber-600 dark:text-amber-400" aria-hidden="true" />
                </div>
                <div>
                  <CardTitle className="text-xl font-bold text-gray-800 dark:text-gray-200">Upcoming Actions</CardTitle>
                  <CardDescription className="text-sm text-gray-600 dark:text-gray-400">Required compliance activities</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <AnimatePresence>
                  {summary?.open_actions_7d > 0 && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 1.4 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-orange-50/50 dark:bg-orange-900/20 backdrop-blur-xl hover:bg-orange-50 dark:hover:bg-orange-900/30 transition-all duration-300 group"
                    >
                      <div className="w-3 h-3 bg-orange-500 rounded-full flex-shrink-0 animate-pulse"></div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{summary.open_actions_7d} controls due within 7 days</span>
                    </motion.div>
                  )}
                  {summary?.high_risk > 0 && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 1.5 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-red-50/50 dark:bg-red-900/20 backdrop-blur-xl hover:bg-red-50 dark:hover:bg-red-900/30 transition-all duration-300 group"
                    >
                      <div className="w-3 h-3 bg-red-500 rounded-full flex-shrink-0 animate-pulse"></div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Complete FRIA for {summary.high_risk} high-risk systems</span>
                    </motion.div>
                  )}
                  {score?.coverage_pct < 0.5 && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 1.6 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-blue-50/50 dark:bg-blue-900/20 backdrop-blur-xl hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-all duration-300 group"
                    >
                      <div className="w-3 h-3 bg-blue-500 rounded-full flex-shrink-0 animate-pulse"></div>
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Upload evidence to improve coverage ({Math.round((score?.coverage_pct || 0) * 100)}%)</span>
                    </motion.div>
                  )}
                  {(!summary?.open_actions_7d && !summary?.high_risk && score?.coverage_pct >= 0.5) && (
                    <motion.div
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 1.4 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-green-50/50 dark:bg-green-900/20 backdrop-blur-xl"
                    >
                      <div className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"></div>
                      <span className="text-sm font-medium text-green-700 dark:text-green-300">All critical actions completed ✓</span>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Score Details Modal */}
        <AnimatePresence>
          {showScoreModal && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4"
              onClick={() => setShowScoreModal(false)}
            >
              <motion.div 
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                transition={{ duration: 0.3 }}
                className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-2xl rounded-3xl shadow-2xl p-8 max-w-3xl w-full mx-4 max-h-[85vh] overflow-y-auto border border-white/30 dark:border-gray-700/30"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-green-500/20 backdrop-blur-xl">
                      <Target className="h-6 w-6 text-green-600 dark:text-green-400" />
                    </div>
                    <h2 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                      Compliance Score Breakdown
                    </h2>
                  </div>
                  <motion.button 
                    whileHover={{ scale: 1.1, rotate: 90 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setShowScoreModal(false)}
                    className="p-2 rounded-xl bg-gray-100/50 dark:bg-gray-800/50 backdrop-blur-xl hover:bg-gray-200/50 dark:hover:bg-gray-700/50 transition-all duration-300 text-gray-600 dark:text-gray-400"
                    aria-label="Close modal"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </motion.button>
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
            
                <div className="flex justify-end mt-8">
                  <motion.button 
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowScoreModal(false)}
                    className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-300 shadow-lg font-semibold"
                  >
                    Close
                  </motion.button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
  )
}

