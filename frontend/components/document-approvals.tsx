'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { CheckCircle, Clock, FileCheck, XCircle } from 'lucide-react'
import { api } from '@/lib/api'

interface DocumentApproval {
  doc_type: string
  status: string
  submitted_by?: string
  submitted_at?: string
  approver_email?: string
  approved_at?: string
  document_hash?: string
  notes?: string
}

interface DocumentApprovalsProps {
  systemId: number
  docType: string
  docTitle: string
}

export function DocumentApprovals({ systemId, docType, docTitle }: DocumentApprovalsProps) {
  const [approval, setApproval] = useState<DocumentApproval | null>(null)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [approving, setApproving] = useState(false)
  const [submitterEmail, setSubmitterEmail] = useState('')
  const [approverEmail, setApproverEmail] = useState('')
  const [notes, setNotes] = useState('')

  useEffect(() => {
    loadApproval()
  }, [systemId, docType])

  const loadApproval = async () => {
    try {
      const data = await api.getDocumentApproval(systemId, docType)
      setApproval(data)
    } catch (error) {
      console.error('Failed to load approval:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmitForReview = async () => {
    if (!submitterEmail) {
      alert('Please enter your email')
      return
    }

    setSubmitting(true)
    try {
      await api.submitDocumentForReview(systemId, docType, submitterEmail, notes)
      alert('Document submitted for review successfully!')
      setNotes('')
      await loadApproval()
    } catch (error) {
      alert('Failed to submit: ' + error)
    } finally {
      setSubmitting(false)
    }
  }

  const handleApprove = async () => {
    if (!approverEmail) {
      alert('Please enter approver email')
      return
    }

    setApproving(true)
    try {
      await api.approveDocument(systemId, docType, approverEmail, notes)
      alert('Document approved successfully!')
      setNotes('')
      setApproverEmail('')
      await loadApproval()
    } catch (error) {
      alert('Failed to approve: ' + error)
    } finally {
      setApproving(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <Badge className="bg-green-100 text-green-800 border-green-200"><CheckCircle className="h-3 w-3 mr-1" />Approved</Badge>
      case 'submitted':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200"><Clock className="h-3 w-3 mr-1" />Pending Review</Badge>
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800 border-red-200"><XCircle className="h-3 w-3 mr-1" />Rejected</Badge>
      default:
        return <Badge className="bg-gray-100 text-gray-800 border-gray-200">Draft</Badge>
    }
  }

  if (loading) {
    return <div className="text-sm text-gray-500">Loading approval status...</div>
  }

  const status = approval?.status || 'draft'

  return (
    <Card className="mt-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Document Approval</CardTitle>
            <CardDescription>{docTitle}</CardDescription>
          </div>
          {getStatusBadge(status)}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Status Display */}
        {status === 'approved' && (
          <div className="p-4 bg-green-50 border border-green-200 rounded">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-medium text-green-800">Document Approved</span>
            </div>
            <div className="text-sm text-green-700 space-y-1">
              <p><strong>Approved By:</strong> {approval?.approver_email}</p>
              <p><strong>Approved At:</strong> {new Date(approval?.approved_at || '').toLocaleString()}</p>
              {approval?.document_hash && (
                <p><strong>Document Hash:</strong> {approval.document_hash.substring(0, 16)}...</p>
              )}
            </div>
          </div>
        )}

        {status === 'submitted' && (
          <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-5 w-5 text-yellow-600" />
              <span className="font-medium text-yellow-800">Awaiting Approval</span>
            </div>
            <div className="text-sm text-yellow-700 space-y-1">
              <p><strong>Submitted By:</strong> {approval?.submitted_by}</p>
              <p><strong>Submitted At:</strong> {new Date(approval?.submitted_at || '').toLocaleString()}</p>
            </div>
          </div>
        )}

        {/* Submit for Review */}
        {status === 'draft' && (
          <div className="space-y-3">
            <h4 className="font-medium">Submit for Review</h4>
            <Input
              type="email"
              placeholder="Your email"
              value={submitterEmail}
              onChange={(e) => setSubmitterEmail(e.target.value)}
            />
            <Textarea
              placeholder="Notes (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
            <Button onClick={handleSubmitForReview} disabled={submitting}>
              <FileCheck className="h-4 w-4 mr-2" />
              {submitting ? 'Submitting...' : 'Submit for Review'}
            </Button>
          </div>
        )}

        {/* Approve/Reject */}
        {status === 'submitted' && (
          <div className="space-y-3">
            <h4 className="font-medium">Review Actions</h4>
            <Input
              type="email"
              placeholder="Approver email"
              value={approverEmail}
              onChange={(e) => setApproverEmail(e.target.value)}
            />
            <Textarea
              placeholder="Approval notes (optional)"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
            <div className="flex space-x-2">
              <Button onClick={handleApprove} disabled={approving}>
                <CheckCircle className="h-4 w-4 mr-2" />
                {approving ? 'Approving...' : 'Approve'}
              </Button>
              <Button 
                variant="outline" 
                onClick={async () => {
                  if (!approverEmail) {
                    alert('Please enter approver email')
                    return
                  }
                  const reason = prompt('Rejection reason:')
                  if (!reason) return
                  
                  try {
                    await api.rejectDocument(systemId, docType, approverEmail, reason, notes)
                    alert('Document rejected')
                    await loadApproval()
                  } catch (error) {
                    alert('Failed to reject: ' + error)
                  }
                }}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </div>
          </div>
        )}

        {/* Notes Display */}
        {approval?.notes && (
          <div className="mt-4 p-3 bg-gray-50 rounded">
            <p className="text-sm font-medium mb-1">Notes:</p>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{approval.notes}</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
