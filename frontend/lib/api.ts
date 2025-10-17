const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://foundryai.onrender.com';

function getApiKey(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('apiKey');
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
  
  createSystem: (data: any) => 
    apiRequest('/systems', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
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
  uploadEvidence: (systemId: number, label: string, file: File, metadata: any = {}) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('label', label);
    Object.entries(metadata).forEach(([key, value]) => {
      if (value) formData.append(key, String(value));
    });
    
    const apiKey = getApiKey();
    return fetch(`${API_URL}/evidence/${systemId}`, {
      method: 'POST',
      headers: apiKey ? { 'X-API-Key': apiKey } : {},
      body: formData,
    }).then(r => r.json());
  },
  
  // Reports
  getReportSummary: () => apiRequest('/reports/summary'),
  getReportScore: () => apiRequest('/reports/score'),
  
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

