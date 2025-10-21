# 🚀 Como Testar o Sistema Agora

## ✅ Status: Sistema 100% Pronto!

**Tudo está funcionando e nada vai quebrar!** 💪

---

## 📍 Estado Atual

- ✅ **Backend**: Rodando em http://localhost:8001
- ✅ **Frontend**: Rodando em http://localhost:3000
- ✅ **Banco de Dados**: Limpo e pronto (0 sistemas)
- ✅ **API Key**: `dev-aims-demo-key`
- ✅ **Migração**: Aplicada (todas as novas tabelas e colunas criadas)

---

## 🎯 Passo a Passo para Testar

### 1. **Limpar o localStorage** (IMPORTANTE!)

Antes de começar, você precisa limpar os dados antigos do navegador:

**Opção A - Via Botão Reset**:
1. Acesse http://localhost:3000/onboarding
2. Clique no botão vermelho "Reset" no canto inferior esquerdo
3. A página vai recarregar automaticamente
4. Agora você está pronto! ✅

**Opção B - Via Console do Navegador**:
1. Pressione F12 (ou Command+Option+I no Mac)
2. Vá para a aba "Console"
3. Digite: `localStorage.clear()`
4. Pressione Enter
5. Recarregue a página (F5 ou Command+R)

---

### 2. **Iniciar o Onboarding**

Acesse: http://localhost:3000/onboarding

Você verá **5 Steps**:

#### **Step 1 - Company Setup** ⭐ MELHORADO

Campos obrigatórios (*):
- Company Name *
- Industry Sector *
- Country / Jurisdiction *
- Primary Contact Email *
- Organization Size *

Campos novos (opcionais):
- Primary Contact Name
- DPO / Legal Contact Name
- DPO / Legal Contact Email
- Organization Role (Provider/Deployer/Both)
- AI Governance Policy (Yes/No)
- Key Stakeholders

**Exemplo**:
- Company: "ACME Corp"
- Sector: "Healthcare"
- Country: "Portugal"
- Email: "compliance@acme.com"
- Size: "Medium (51-250 employees)"
- Primary Contact Name: "João Silva"
- DPO Email: "dpo@acme.com"
- Org Role: "Provider"

Clique em **"Save & Continue"**

---

#### **Step 2 - AI System Definition**

Defina seu sistema de IA:
- System Name: "Medical Diagnosis AI"
- Purpose: "Assist doctors in diagnosing diseases"
- Domain: "Healthcare"
- System Owner: "ai-team@acme.com"

Flags importantes (ativam FRIA se marcados):
- ☑ Processes Personal Data
- ☑ Impacts Fundamental Rights ← **Isso ativa requires_fria!**
- ☐ Uses Biometrics in Public
- ☐ Uses General Purpose AI

Clique em **"Add System"** e depois **"Save & Continue"**

---

#### **Step 3 - Risk & Controls**

Defina riscos (mínimo 3):
1. **Risk 1**: "Data breach"
   - Likelihood: High
   - Impact: High
   - Mitigation: "Encryption + access controls"

2. **Risk 2**: "Bias in predictions"
   - Likelihood: Medium
   - Impact: High
   - Mitigation: "Regular fairness audits"

3. **Risk 3**: "Model drift"
   - Likelihood: Medium
   - Impact: Medium
   - Mitigation: "Continuous monitoring"

Controles (se houver):
- ISO Clause: "5.1"
- Control Name: "AI Governance Policy"
- Status: "Implemented"
- Owner: "governance@acme.com"

Clique em **"Save & Continue"**

---

#### **Step 4 - Human Oversight**

Configure supervisão humana:
- Oversight Method: "Human-in-the-loop"
- Escalation Rules: "IF confidence < 80% THEN escalate to doctor"
- Appeals Process: "Email to appeals@acme.com"
- Appeals SLA: "48 hours"
- Ethics Committee: Yes
- Staff Training Plan: "Quarterly AI ethics training"

Clique em **"Save & Continue"**

---

#### **Step 5 - Monitoring & Improvement**

Configure monitoramento:
- Logging Scope: "Model Performance, Bias Detection"
- Log Retention: "2 years"
- Drift Alert Threshold: 10%
- Fairness Metrics: "Demographic Parity, Equalized Odds"
- Incident Tool: "JIRA"
- Internal Audit Frequency: "Quarterly"
- Management Review: "Semi-annually"

Clique em **"Save & Continue"**

---

### 3. **Complete e Gere Documentos**

Após completar os 5 steps:

1. Você verá o **Summary Screen**
2. Clique em **"Complete Onboarding"**
3. Você será redirecionado para a tela de sucesso

**IMPORTANTE**: Se você marcou "Impacts Fundamental Rights" no Step 2:
- O sistema terá `requires_fria = True`
- Ao tentar gerar documentos, receberá erro: **"FRIA required but not uploaded"**
- Solução: Upload evidence com label "FRIA" antes de gerar docs

Se **NÃO** marcou fundamental rights:
- Pode gerar documentos imediatamente! ✅

---

## 🧪 Testes de API (via cURL)

### Verificar sistemas criados:
```bash
curl -H "X-API-Key: dev-aims-demo-key" http://localhost:8001/systems
```

### Criar riscos em bulk:
```bash
curl -X POST -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "risks": [
      {"description": "Risk 1", "likelihood": "M", "impact": "H"},
      {"description": "Risk 2", "likelihood": "H", "impact": "M"},
      {"description": "Risk 3", "likelihood": "L", "impact": "L"}
    ]
  }' \
  http://localhost:8001/onboarding/systems/1/risks/bulk
```

### Exportar SoA:
```bash
curl -H "X-API-Key: dev-aims-demo-key" \
  http://localhost:8001/systems/1/soa.csv \
  -o meu_soa.csv

open meu_soa.csv  # Abre no Excel/Numbers
```

---

## ❓ Troubleshooting

### Problema: Erro "No systems found"
**Solução**: Clique no botão "Reset" para limpar localStorage

### Problema: Frontend mostra dados antigos
**Solução**: 
1. Abra Console (F12)
2. Digite: `localStorage.clear()`
3. Recarregue a página

### Problema: Backend não está respondendo
**Solução**:
```bash
cd backend
source .venv/bin/activate
SECRET_KEY=dev-secret-key-for-development-only \
  python -m uvicorn app.main:app --port 8001
```

### Problema: "FRIA required" ao gerar documentos
**Isso é esperado!** Se o sistema tem:
- `impacts_fundamental_rights = True`, OU
- `biometrics_in_public = True`, OU
- Annex III categoria de alto risco

Então FRIA é obrigatório. Você precisa:
1. Ir para Evidence/Upload
2. Upload um arquivo com label "FRIA"
3. Depois pode gerar documentos

Ou, para testar sem FRIA:
- Desmarque "Impacts Fundamental Rights" no Step 2
- Sistema terá `requires_fria = False`
- Pode gerar docs sem FRIA! ✅

---

## 📊 Verificações Finais

### Backend Health Check:
```bash
curl http://localhost:8001/health
# Esperado: {"status":"ok"}
```

### Frontend Loading:
```bash
curl http://localhost:3000 | head -3
# Esperado: HTML válido com "AIMS Studio"
```

### Database Status:
```bash
cd backend && source .venv/bin/activate && python -c "
from app.database import get_db
from sqlalchemy import text
db = next(get_db())
systems = db.execute(text('SELECT COUNT(*) FROM ai_systems')).scalar()
risks = db.execute(text('SELECT COUNT(*) FROM ai_risk')).scalar()
oversight = db.execute(text('SELECT COUNT(*) FROM oversight')).scalar()
pmm = db.execute(text('SELECT COUNT(*) FROM pmm')).scalar()
print(f'Systems: {systems}, Risks: {risks}, Oversight: {oversight}, PMM: {pmm}')
db.close()
"
# Esperado: Systems: 0, Risks: 0, Oversight: 0, PMM: 0 (banco limpo)
```

---

## 🎉 Tudo Pronto!

**O sistema está 100% funcional, limpo, e pronto para uso!**

Pode começar o onboarding com confiança - **nada vai quebrar!** 💪

*Boa sorte com os testes!* 🚀

