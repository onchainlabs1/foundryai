'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { api, downloadFile } from '@/lib/api'
import { 
  FileText, 
  Download, 
  Eye, 
  ExternalLink, 
  Calendar,
  Code,
  Shield,
  ArrowLeft,
  Search,
  Filter
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface Template {
  filename: string
  template_id: string
  iso_clauses: string[]
  ai_act: string[]
  version: string
  language: string
  generated_at: string
  size: number
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [previewContent, setPreviewContent] = useState<string>('')
  const [previewLoading, setPreviewLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterClause, setFilterClause] = useState('')

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await api.getTemplates()
      setTemplates(response.templates || [])
    } catch (error) {
      console.error('Failed to load templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePreview = async (template: Template) => {
    setSelectedTemplate(template)
    setPreviewLoading(true)
    
    try {
      const content = await api.getTemplateContent(template.template_id)
      setPreviewContent(content)
    } catch (error) {
      console.error('Failed to load template content:', error)
      setPreviewContent('Error loading template content.')
    } finally {
      setPreviewLoading(false)
    }
  }

  const handleDownload = async (template: Template) => {
    try {
      await downloadFile(`/templates/${template.template_id}`, template.filename)
    } catch (error) {
      console.error('Download failed:', error)
      alert('Download failed. Please check your API key.')
    }
  }

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.template_id.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = !filterClause || 
                         template.iso_clauses.some(clause => clause.includes(filterClause)) ||
                         template.ai_act.some(act => act.toLowerCase().includes(filterClause.toLowerCase()))
    
    return matchesSearch && matchesFilter
  })

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950 p-6">
        <div className="max-w-7xl mx-auto space-y-8">
          {/* Header Skeleton */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton className="h-8 w-64" />
              <Skeleton className="h-4 w-96" />
            </div>
            <Skeleton className="h-10 w-32" />
          </div>

          {/* Search Skeleton */}
          <div className="flex gap-4">
            <Skeleton className="h-10 w-80" />
            <Skeleton className="h-10 w-40" />
          </div>

          {/* Grid Skeleton */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i} className="rounded-2xl">
                <CardHeader>
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-32" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-20 w-full" />
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-blue-950 dark:to-indigo-950 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between"
        >
          <div>
            <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              ISO/IEC 42001 Templates
            </h1>
            <p className="text-sm text-gray-700 dark:text-gray-300 mt-1 font-medium">
              Ready-to-use compliance templates for AI governance
            </p>
          </div>
          
          <Link href="/">
            <Button variant="outline" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
        </motion.div>

        {/* Search and Filter */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <select
              value={filterClause}
              onChange={(e) => setFilterClause(e.target.value)}
              className="pl-10 pr-8 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white/70 dark:bg-gray-900/60 backdrop-blur-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Clauses</option>
              <option value="6.1">ISO 6.1</option>
              <option value="Annex">Annex</option>
              <option value="Art. 27">AI Act Art. 27</option>
              <option value="Annex IV">AI Act Annex IV</option>
            </select>
          </div>
        </motion.div>

        {/* Templates Grid */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
        >
          {filteredTemplates.map((template, index) => (
            <motion.div
              key={template.template_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 * index }}
              whileHover={{ y: -4, scale: 1.02 }}
            >
              <Card className="h-full rounded-2xl bg-white/20 dark:bg-gray-900/20 backdrop-blur-2xl border border-white/30 dark:border-gray-700/30 shadow-xl hover:shadow-2xl transition-all duration-500 overflow-hidden relative group">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                <CardHeader className="pb-3 relative z-10">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-blue-500/20 backdrop-blur-xl">
                      <FileText className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg font-bold text-gray-800 dark:text-gray-200 truncate">
                        {template.filename.replace('.md', '')}
                      </CardTitle>
                      <CardDescription className="text-sm text-gray-700 dark:text-gray-300 font-medium">
                        v{template.version} • {Math.round(template.size / 1024)}KB
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="relative z-10 space-y-4">
                  {/* ISO Clauses */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Code className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">ISO Clauses</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {template.iso_clauses.map((clause, i) => (
                        <Badge key={i} variant="secondary" className="text-xs">
                          {clause}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* AI Act References */}
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">AI Act</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {template.ai_act.map((act, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {act}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handlePreview(template)}
                      className="flex-1"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleDownload(template)}
                      className="flex-1"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {filteredTemplates.length === 0 && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              No templates found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Try adjusting your search or filter criteria.
            </p>
          </motion.div>
        )}
      </div>

      {/* Preview Modal */}
      <AnimatePresence>
        {selectedTemplate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedTemplate(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-2xl rounded-3xl shadow-2xl border border-white/30 dark:border-gray-700/30 max-w-4xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200">
                    {selectedTemplate.filename}
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    v{selectedTemplate.version} • {Math.round(selectedTemplate.size / 1024)}KB
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedTemplate(null)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  ✕
                </Button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
                {previewLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                ) : (
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap font-mono text-sm">
                      {previewContent}
                    </pre>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-2">
                  {selectedTemplate.iso_clauses.map((clause, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {clause}
                    </Badge>
                  ))}
                </div>
                <Button
                  onClick={() => handleDownload(selectedTemplate)}
                  className="flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Download Template
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
