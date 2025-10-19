'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
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
  Filter,
  Sparkles,
  ArrowRight,
  X,
  FileCode,
  BookOpen
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
      <div className="space-y-8">
        {/* Header Skeleton */}
        <div className="text-center space-y-4">
          <Skeleton className="h-16 w-96 mx-auto" />
          <Skeleton className="h-6 w-80 mx-auto" />
        </div>

        {/* Search Skeleton */}
        <div className="flex gap-4">
          <Skeleton className="h-12 w-80" />
          <Skeleton className="h-12 w-40" />
        </div>

        {/* Grid Skeleton */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-80 rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center space-y-4"
      >
        <div className="flex items-center justify-center gap-3 mb-4">
          <Sparkles className="h-8 w-8 text-primary" />
          <h1 className="text-5xl font-bold gradient-text">
            ISO/IEC 42001 Templates
          </h1>
          <Sparkles className="h-8 w-8 text-primary" />
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Ready-to-use compliance templates for AI governance. Download, customize, and implement.
        </p>
      </motion.div>

      {/* Search and Filter */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 glass-card"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <select
            value={filterClause}
            onChange={(e) => setFilterClause(e.target.value)}
            className="pl-10 pr-8 py-3 border border-border rounded-xl bg-card/50 backdrop-blur-xl focus:ring-2 focus:ring-primary focus:border-transparent text-sm font-medium"
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
            whileHover={{ y: -8, scale: 1.02 }}
          >
            <Card  className="h-full overflow-hidden group cursor-pointer">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-3 rounded-xl bg-primary/20">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-lg font-bold truncate">
                      {template.filename.replace('.md', '')}
                    </CardTitle>
                    <CardDescription className="font-medium">
                      v{template.version} • {Math.round(template.size / 1024)}KB
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* ISO Clauses */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <Code className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-semibold">ISO Clauses</span>
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
                    <Shield className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-semibold">AI Act</span>
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
                    className="flex-1 gap-2"
                  >
                    <Eye className="h-4 w-4" />
                    Preview
                  </Button>
                  <Button
                    size="sm"
                    variant="default"
                    onClick={() => handleDownload(template)}
                    className="flex-1 gap-2"
                  >
                    <Download className="h-4 w-4" />
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
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-muted/50 flex items-center justify-center">
            <FileText className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-bold mb-2">
            No templates found
          </h3>
          <p className="text-muted-foreground">
            Try adjusting your search or filter criteria.
          </p>
        </motion.div>
      )}

      {/* Preview Modal */}
      <AnimatePresence>
        {selectedTemplate && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedTemplate(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ duration: 0.3 }}
              className="bg-card/90 backdrop-blur-2xl rounded-3xl shadow-2xl border border-border/30 max-w-4xl w-full max-h-[90vh] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6 border-b border-border/50">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-primary/20">
                    <FileText className="h-6 w-6 text-primary" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold gradient-text">
                      {selectedTemplate.filename}
                    </h2>
                    <p className="text-sm text-muted-foreground">
                      v{selectedTemplate.version} • {Math.round(selectedTemplate.size / 1024)}KB
                    </p>
                  </div>
                </div>
                <motion.button 
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setSelectedTemplate(null)}
                  className="p-2 rounded-xl bg-muted/50 backdrop-blur-xl hover:bg-muted/70 transition-all duration-300 text-muted-foreground"
                  aria-label="Close modal"
                >
                  <X className="h-5 w-5" />
                </motion.button>
              </div>
              
              <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
                {previewLoading ? (
                  <div className="space-y-4">
                    <Skeleton className="h-4 w-full" />
                    <Skeleton className="h-4 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                ) : (
                  <div className="prose prose-gray dark:prose-invert max-w-none">
                    <pre className="whitespace-pre-wrap font-mono text-sm bg-muted/30 p-4 rounded-xl">
                      {previewContent}
                    </pre>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-between p-6 border-t border-border/50">
                <div className="flex gap-2">
                  {selectedTemplate.iso_clauses.map((clause, i) => (
                    <Badge key={i} variant="secondary" className="text-xs">
                      {clause}
                    </Badge>
                  ))}
                </div>
                <Button
                  variant="default"
                  onClick={() => handleDownload(selectedTemplate)}
                  className="gap-2"
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
