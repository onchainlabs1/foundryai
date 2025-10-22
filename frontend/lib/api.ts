  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

function getApiKey(): string | null {
  if (typeof window === 'undefined') return null;
  
  // Try to get from localStorage first
  const storedKey = localStorage.getItem('apiKey') || localStorage.getItem('api_key');
  if (storedKey) {
    return storedKey;
  }
  
  // If no key in localStorage, use development key and store it
  const devKey = 'dev-aims-demo-key';
  localStorage.setItem('apiKey', devKey);
  return devKey;
}

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const apiKey = getApiKey();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  // Systems
  getSystems: () => apiRequest('/systems'),
  getSystem: (systemId: number) => apiRequest(`/systems/${systemId}`),
  
  createSystem: (data: any) => 
    apiRequest('/systems', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  updateSystem: (systemId: number, data: any) =>
    apiRequest(`/systems/${systemId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  patchSystem: (systemId: number, data: any) =>
    apiRequest(`/systems/${systemId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  saveOnboardingData: (systemId: number, data: any) =>
    apiRequest(`/systems/${systemId}/onboarding-data`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getOnboardingData: (systemId: number) =>
    apiRequest(`/systems/${systemId}/onboarding-data`),
  
  importSystems: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const apiKey = getApiKey();
    
    return fetch(`${API_URL}/systems/import`, {
      method: 'POST',
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
      body: formData,
    }).then(async (r) => {
      if (!r.ok) {
        const error = await r.json().catch(() => ({ detail: 'Import failed' }));
        throw new Error(error.detail || 'Import failed');
      }
      return r.json();
    });
  },
  
  assessSystem: (systemId: number) => 
    apiRequest(`/systems/${systemId}/assess`, { method: 'POST' }),
  
  // Evidence
  uploadEvidence: async (systemId: number, label: string, file: File, metadata: any = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('label', label);
    Object.entries(metadata).forEach(([key, value]) => {
      if (value) formData.append(key, String(value));
    });
    
    const apiKey = getApiKey();
    const response = await fetch(`${API_URL}/evidence/${systemId}`, {
      method: 'POST',
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
      body: formData,
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(error.detail || 'Evidence upload failed');
    }
    
    return response.json();
  },
  
  // Reports
  getReportSummary: () => apiRequest('/reports/summary'),
  getReportScore: () => apiRequest('/reports/score'),
  // Deprecated: getBlockingIssues → use getOrgBlockingIssues
  getBlockingIssues: () => apiRequest('/reports/blocking-issues/org'),
  getUpcomingDeadlines: () => apiRequest('/reports/upcoming-deadlines'),
  
  // FRIA
  createFRIA: (systemId: number, data: any) =>
    apiRequest(`/systems/${systemId}/fria`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getLatestFRIA: (systemId: number) =>
    apiRequest(`/systems/${systemId}/fria/latest`),
  
  // Controls
  bulkUpsertControls: (controls: any[]) =>
    apiRequest('/controls/bulk', {
      method: 'POST',
      body: JSON.stringify({ controls }),
    }),
  
  getSystemControls: (systemId: number) =>
    apiRequest(`/systems/${systemId}/controls`),
  
  getSystemEvidence: (systemId: number) =>
    apiRequest(`/controls/${systemId}/evidence`),
  
  getSystemBlockingIssues: (systemId: number) =>
    apiRequest(`/reports/blocking-issues/system?system_id=${systemId}`),
  
  getOrgBlockingIssues: () =>
    apiRequest(`/reports/blocking-issues/org`),
  
  // Approvals
  submitDocumentForReview: (systemId: number, docType: string, submittedBy: string, notes?: string) =>
    apiRequest(`/approvals/systems/${systemId}/documents/submit`, {
      method: 'POST',
      body: JSON.stringify({ doc_type: docType, submitted_by: submittedBy, notes }),
    }),
  
  approveDocument: (systemId: number, docType: string, approverEmail: string, notes?: string) =>
    apiRequest(`/approvals/systems/${systemId}/documents/${docType}/approve`, {
      method: 'POST',
      body: JSON.stringify({ approver_email: approverEmail, notes }),
    }),
  
  rejectDocument: (systemId: number, docType: string, approverEmail: string, rejectionReason: string, notes?: string) =>
    apiRequest(`/approvals/systems/${systemId}/documents/${docType}/reject`, {
      method: 'POST',
      body: JSON.stringify({ approver_email: approverEmail, rejection_reason: rejectionReason, notes }),
    }),
  
  getDocumentApproval: (systemId: number, docType: string) =>
    apiRequest(`/approvals/systems/${systemId}/documents/${docType}/approval`),
  
  listDocumentApprovals: (systemId: number) =>
    apiRequest(`/approvals/systems/${systemId}/documents/approvals`),
  
  // Model Versions
  createModelVersion: (systemId: number, version: string, approverEmail: string, notes?: string, artifactHash?: string) =>
    apiRequest(`/model-versions/systems/${systemId}`, {
      method: 'POST',
      body: JSON.stringify({ version, approver_email: approverEmail, notes, artifact_hash: artifactHash }),
    }),
  
  listModelVersions: (systemId: number) =>
    apiRequest(`/model-versions/systems/${systemId}`),
  
  getLatestModelVersion: (systemId: number) =>
    apiRequest(`/model-versions/systems/${systemId}/latest`),
  
  // Incidents
  createIncident: (data: any) =>
    apiRequest('/incidents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getIncidents: (systemId?: number) =>
    apiRequest(`/incidents${systemId ? `?system_id=${systemId}` : ''}`),
  
  updateIncident: (incidentId: number, data: any) =>
    apiRequest(`/incidents/${incidentId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  // Compliance Suite
  generateComplianceDraft: (systemId?: number, docs?: string[]) =>
    apiRequest('/reports/draft', {
      method: 'POST',
      body: JSON.stringify({
        system_id: systemId,
        docs: docs || ['annex_iv', 'fria', 'pmm', 'soa', 'risk_register'],
      }),
    }),

  exportDocument: async (docType: string, format: 'md' | 'docx' | 'pdf', systemId?: number) => {
    const apiKey = getApiKey();
    const params = new URLSearchParams();
    if (systemId) params.append('system_id', systemId.toString());
    
    const response = await fetch(`${API_URL}/reports/export/${docType}.${format}?${params}`, {
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Export failed' }));
      throw new Error(error.detail || 'Export failed');
    }
    
    return response;
  },

  getEvidenceViewerUrl: (evidenceId: number, page: number) =>
    apiRequest(`/reports/evidence/view?evidence_id=${evidenceId}&page=${page}`),

  refineDocument: (docType: string, systemId: number, sectionKey: string, paragraphs: any[]) =>
    apiRequest('/reports/refine', {
      method: 'POST',
      body: JSON.stringify({
        doc_type: docType,
        system_id: systemId,
        section_key: sectionKey,
        paragraphs,
      }),
    }),

  // Templates
  getTemplates: () => apiRequest('/templates'),
  getTemplateContent: async (templateId: string) => {
    const apiKey = getApiKey();
    const response = await fetch(`${API_URL}/templates/${templateId}`, {
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
    });
    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'Failed to load template');
    }
    return response.text();
  },

  // Documents
  generateSystemDocuments: (systemId: number, onboardingData?: any) =>
    apiRequest(`/documents/systems/${systemId}/generate`, {
      method: 'POST',
      body: onboardingData ? JSON.stringify(onboardingData) : undefined,
    }),

  getSystemDocuments: (systemId: number) =>
    apiRequest(`/documents/systems/${systemId}/list`),

  downloadDocument: async (systemId: number, docType: string, format: 'markdown' | 'pdf') => {
    const apiKey = getApiKey();
    const response = await fetch(`${API_URL}/documents/systems/${systemId}/download/${docType}?format=${format}`, {
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Download failed' }));
      throw new Error(error.detail || 'Download failed');
    }
    
    return response.blob();
  },

  previewDocument: async (systemId: number, docType: string) => {
    const apiKey = getApiKey();
    const response = await fetch(`${API_URL}/documents/systems/${systemId}/preview/${docType}`, {
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Preview failed' }));
      throw new Error(error.detail || 'Preview failed');
    }
    
    return response.text();
  },
  
  // Audit-grade onboarding endpoints
  setupOrganization: (data: any) =>
    apiRequest('/onboarding/org/setup', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  createRisksBulk: (systemId: number, risks: any[]) =>
    apiRequest(`/onboarding/systems/${systemId}/risks/bulk`, {
      method: 'POST',
      body: JSON.stringify({ risks }),
    }),
  
  getRisks: (systemId: number) =>
    apiRequest(`/onboarding/systems/${systemId}/risks`),
  
  createControlsBulk: (controls: any[]) =>
    apiRequest('/onboarding/controls/bulk', {
      method: 'POST',
      body: JSON.stringify({ controls }),
    }),
  
  createOversight: (systemId: number, data: any) =>
    apiRequest(`/onboarding/systems/${systemId}/oversight`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getOversight: (systemId: number) =>
    apiRequest(`/onboarding/systems/${systemId}/oversight`),
  
  createPMM: (systemId: number, data: any) =>
    apiRequest(`/onboarding/systems/${systemId}/pmm`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  getPMM: (systemId: number) =>
    apiRequest(`/onboarding/systems/${systemId}/pmm`),
  
  exportSoA: (systemId: number) =>
    `${API_URL}/systems/${systemId}/soa.csv?x-api-key=${getApiKey()}`,
};

export function setApiKey(key: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('apiKey', key);
  }
}

export function clearApiKey() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('apiKey');
  }
}

export async function downloadFile(endpoint: string, filename: string) {
  const apiKey = getApiKey();
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: apiKey ? { 'X-API-Key': apiKey } : {},
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Download failed' }));
    throw new Error(error.detail || 'Download failed');
  }
  
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

