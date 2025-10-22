# 🧪 ROTEIRO DE TESTE COMPLETO - PONTA A PONTA

**Objetivo:** Validar todas as funcionalidades do AIMS Studio  
**Tempo estimado:** 30-40 minutos  
**Pré-requisitos:** Frontend (port 3000) e Backend (port 8001) rodando

---

## 📋 CHECKLIST RÁPIDO

Antes de começar, verifique:
- [ ] Backend rodando em http://localhost:8001
- [ ] Frontend rodando em http://localhost:3000
- [ ] Banco de dados limpo (ou pronto para novo teste)

---

## 🎬 PARTE 1: SETUP INICIAL (5 minutos)

### 1.1 Acesse o Sistema
1. Abra o navegador
2. Acesse: `http://localhost:3000`
3. **✅ VERIFICAR:** Página de onboarding carrega

### 1.2 Limpar Dados Anteriores (Opcional)
Se quiser começar do zero:

**No navegador (Console F12):**
```javascript
localStorage.clear()
location.reload()
```

**Ou no backend:**
```bash
cd /Users/fabio/Desktop/foundry/backend
rm aims.db  # Remove database
alembic upgrade head  # Recria
```

---

## 🏢 PARTE 2: ONBOARDING COMPLETO (10 minutos)

### 2.1 Step 1 - Company Setup

**Preencha:**
- Company Name: `TechCorp AI Solutions`
- Organization Role: `Provider`
- Primary Contact: `John Doe`
- Primary Email: `john@techcorp.ai`
- DPO Name: `Jane Smith`
- DPO Email: `dpo@techcorp.ai`

**Clique:** `Continue`

**✅ VERIFICAR:**
- Dados salvos no localStorage
- Avança para Step 2
- Progress bar: 20%

---

### 2.2 Step 2 - AI System Definition

**Clique:** `Add System` (se necessário)

**Preencha Sistema 1:**
- System Name: `Credit Scoring AI`
- Domain: `Finance`
- Purpose: `Automated credit risk assessment for loan applications`
- Lifecycle Stage: `Production`
- Deployment Context: `Public-facing application`
- Third-party Providers: `Experian credit bureau data, internal transaction history`
- Affected Users: `Loan applicants (consumers and small businesses)`
- ✓ Processes personal data
- ✓ Impacts fundamental rights
- Risk Category: `High`
- System Owner Email: `ai-owner@techcorp.ai`

**Clique:** `Save & Continue`

**✅ VERIFICAR:**
- Sistema salvo
- Console mostra: `✅ Created new system: Credit Scoring AI (ID: 1)`
- Avança para Step 3
- Progress bar: 40%

---

### 2.3 Step 3 - Risk & Controls

**Adicione 3 Riscos:**

**Risco 1:**
- Description: `Algorithmic bias against protected demographic groups`
- Impact: `High`
- Likelihood: `Medium`
- Mitigation: `Regular fairness audits, demographic parity testing, bias correction algorithms`
- Owner Email: `ml-lead@techcorp.ai`

**Risco 2:**
- Description: `Data privacy breach exposing sensitive financial information`
- Impact: `High`
- Likelihood: `Low`
- Mitigation: `End-to-end encryption, access controls, regular security audits, DPIA compliance`
- Owner Email: `security@techcorp.ai`

**Risco 3:**
- Description: `Model drift reducing prediction accuracy over time`
- Impact: `Medium`
- Likelihood: `High`
- Mitigation: `Continuous monitoring, automated drift detection, quarterly model retraining`
- Owner Email: `ml-lead@techcorp.ai`

**Clique:** `Save & Continue`

**✅ VERIFICAR:**
- 3 riscos salvos
- Console mostra: `✅ Saved 3 risks`
- Avança para Step 4
- Progress bar: 60%

---

### 2.4 Step 4 - Human Oversight

**Preencha:**
- Oversight Mode: `Human-in-the-loop`
- Review Trigger: `Score confidence < 0.8 OR rejection decision`
- ✓ Override Rights: Enabled
- Intervention Rules: `Human review required for: 1) Low confidence scores, 2) All rejections, 3) High-value loans (>$100k)`
- Appeals Channel: `appeals@techcorp.ai`
- Appeals SLA: `5` business days
- Appeals Responsible: `compliance@techcorp.ai`

**Clique:** `Save & Continue`

**✅ VERIFICAR:**
- Oversight salvo
- Console mostra: `✅ Saved oversight configuration`
- Avança para Step 5
- Progress bar: 80%

---

### 2.5 Step 5 - Monitoring & Improvement

**Preencha:**
- Logging Scope: `All credit decisions, input features (anonymized), model predictions, confidence scores, human overrides, user feedback`
- Retention Months: `60`
- Fairness Metrics: `Demographic parity, equal opportunity, predictive parity across age, gender, ethnicity`
- Drift Threshold: `0.05` (5%)
- Incident Tool: `Jira - Project: AI-INCIDENTS`
- Incident Severity: `P0 (Critical), P1 (High), P2 (Medium), P3 (Low)`
- CAPA Process: `Root cause analysis within 48h, corrective actions within 7 days, preventive actions tracked quarterly`
- Audit Frequency: `Quarterly`
- Management Review: `Semi-annual`
- Improvement Plan: `Quarterly model performance review, annual fairness audit, continuous feedback loop from appeals`

**Clique:** `Complete Setup`

**✅ VERIFICAR:**
- PMM salvo
- Console mostra: `✅ Saved PMM configuration`
- Mensagem de sucesso aparece
- Sistema criado aparece na lista
- Progress bar: 100%

---

## 📊 PARTE 3: SYSTEM OVERVIEW & MODEL VERSIONING (5 minutos)

### 3.1 Navegar para o Sistema

**Clique no sistema criado** ou acesse: `http://localhost:3000/systems/1`

**✅ VERIFICAR:**
- Tab "Overview" está ativa
- Dados do sistema aparecem:
  - System Name: Credit Scoring AI
  - Purpose, Domain, Lifecycle
  - AI Act Classification badge
  - EU Database Status badge

---

### 3.2 Criar Primeira Versão do Modelo

**Scroll até o painel "Model Versions"**

**Clique:** `+ Create Version`

**Preencha:**
- Version: `1.0.0`
- Approver Email: `tech-lead@techcorp.ai`
- Notes: `Initial production release. Trained on 2023-2024 data. Accuracy: 92.5%. Deployed 2025-01-15.`
- Artifact Hash: `a3f5e9d2b8c4f1a6e7d9c2b5a8f3e1d4c9b6a2f7e3d8c1b4a9f6e2d5c8b3a1f7` (opcional)

**Clique:** `Create Version`

**✅ VERIFICAR:**
- Alert: "✅ Model version 1.0.0 created successfully!"
- Banner azul "Current Version" aparece
- Mostra: v1.0.0, tech-lead@techcorp.ai, data de hoje
- Version History mostra a versão criada

---

### 3.3 Criar Segunda Versão (Opcional)

**Clique:** `+ Create Version` novamente

**Preencha:**
- Version: `1.1.0`
- Approver Email: `tech-lead@techcorp.ai`
- Notes: `Bug fix release. Improved handling of edge cases. Performance maintained.`

**Clique:** `Create Version`

**✅ VERIFICAR:**
- Banner atualiza para v1.1.0
- History mostra 2 versões (1.1.0 primeiro)

---

## 🎯 PARTE 4: CONTROLS & EVIDENCE (8 minutos)

### 4.1 Ir para Controls Tab

**Clique:** Tab `Controls`

**✅ VERIFICAR:**
- Tabela de 43 controles ISO 42001 carrega
- Colunas: ISO Clause, Control Name, Applicable, Justification, Owner Email, Status, Due Date, Evidence

---

### 4.2 Configurar Controles Críticos

**Controle A.5.1 (Policies for AI management):**
- Applicable: ✓ Yes
- Justification: `Essential for governance framework`
- Owner Email: `compliance@techcorp.ai`
- Status: `Implemented`
- Due Date: (deixe vazio ou escolha uma data futura)

**Controle A.6.1.1 (Screening of data):**
- Applicable: ✓ Yes
- Justification: `Critical for data quality and bias prevention`
- Owner Email: `data-team@techcorp.ai`
- Status: `Implemented`
- Due Date: (deixe vazio)

**Controle A.7.1.1 (Suitability of data sets):**
- Applicable: ✓ Yes
- Justification: `Required for fair credit decisions`
- Owner Email: `ml-lead@techcorp.ai`
- Status: `In Progress`
- Due Date: `2025-12-31`

**Clique:** `Save All Controls`

**✅ VERIFICAR:**
- Console mostra: `✅ Saved X controls`
- Toast/mensagem de sucesso
- Dados persistem na tabela

---

### 4.3 Upload de Evidências

**Scroll até "Upload Evidence"**

**Upload Evidência 1:**
- Arquivo: (qualquer PDF ou imagem, ex: `screenshot.png`)
- Label: `AI Governance Policy v1.2`
- ISO Clause: `A.5.1` (opcional)

**Clique:** `Upload Evidence`

**✅ VERIFICAR:**
- Upload bem-sucedido
- Evidência aparece na lista

**Upload Evidência 2:**
- Arquivo: (outro arquivo)
- Label: `Data Quality Audit Report Q1 2025`
- ISO Clause: `A.6.1.1`

**Upload Evidência 3:**
- Arquivo: (outro arquivo)
- Label: `Fairness Testing Results`
- ISO Clause: `A.7.1.1`

**✅ VERIFICAR:**
- 3 evidências carregadas
- SHA-256 hash calculado automaticamente

---

### 4.4 Linkar Evidências aos Controles

**Na tabela de Controls, coluna "Evidence":**

**Para A.5.1:**
- Clique `Add Evidence`
- Selecione: `AI Governance Policy v1.2`
- Clique `Link Selected`

**Para A.6.1.1:**
- Clique `Add Evidence`
- Selecione: `Data Quality Audit Report Q1 2025`
- Clique `Link Selected`

**✅ VERIFICAR:**
- Evidências aparecem na coluna "Evidence"
- Badge com número de evidências

---

## 🔍 PARTE 5: FRIA (Fundamental Rights Impact Assessment) (7 minutos)

### 5.1 Ir para FRIA Tab

**Clique:** Tab `FRIA`

**✅ VERIFICAR:**
- FRIA Wizard carrega
- Mostra 20 questões
- Progress bar em 0%

---

### 5.2 Responder Questionário

**Responda todas as 20 perguntas.** Exemplos de respostas:

**Q1: Does the system process personal data?**
→ `Yes`

**Q2: Does the system make decisions that affect individuals' rights?**
→ `Yes`

**Q3: Are there vulnerable groups affected?**
→ `Yes` (ou `No`, dependendo do cenário)

**Q4-20:** Continue respondendo conforme o contexto do sistema.

**Dica:** Use `Next` para avançar após cada resposta.

**✅ VERIFICAR:**
- Progress bar aumenta a cada questão
- Questão atual muda
- Botão `Previous` funciona

---

### 5.3 Preencher Campos Estendidos (Última Tela)

**Após responder todas as 20 questões, aparece:**

**Extended Assessment Fields:**

- **Proportionality Assessment:** 
  ```
  The safeguards implemented (human oversight, fairness monitoring, appeals process, 
  regular audits) are proportionate to the high-risk nature of automated credit decisions. 
  The system provides explanations, allows human intervention, and has robust governance.
  ```

- **Residual Risk Level:** `Low`

- **DPIA Reference:** `https://docs.techcorp.ai/dpia/credit-scoring-2024`

- **Review Notes:**
  ```
  FRIA completed in collaboration with legal, compliance, and engineering teams. 
  All identified risks have mitigation measures. Next review scheduled for Q3 2025.
  ```

**Clique:** `Submit Assessment`

**✅ VERIFICAR:**
- Console mostra: `✅ FRIA submitted successfully`
- Mensagem de conclusão aparece
- FRIA salvo (você pode recarregar a página e ver existing FRIAs)

---

## 📄 PARTE 6: DOCUMENT APPROVALS (5 minutos)

### 6.1 Ir para Reports Tab

**Clique:** Tab `Reports`

**✅ VERIFICAR:**
- Seção "System Reports & Exports" aparece
- 5 componentes "Document Approval" aparecem:
  1. Annex IV Technical Documentation
  2. Fundamental Rights Impact Assessment (FRIA)
  3. Statement of Applicability (SoA)
  4. Post-Market Monitoring Report
  5. Instructions for Use

---

### 6.2 Submit Annex IV para Review

**No card "Annex IV Technical Documentation":**

**Preencha:**
- Your email: `author@techcorp.ai`
- Notes: `Annex IV documentation complete and ready for compliance review`

**Clique:** `Submit for Review`

**✅ VERIFICAR:**
- Status muda para: "PENDING REVIEW"
- Badge amarelo "Awaiting Approval"
- Mostra submitted by e submitted at

---

### 6.3 Approve Annex IV

**No mesmo card:**

**Preencha:**
- Approver email: `compliance-director@techcorp.ai`
- Approval notes: `Reviewed and approved. All sections complete and accurate.`

**Clique:** `Approve`

**✅ VERIFICAR:**
- Status muda para: "APPROVED"
- Badge verde com checkmark
- Mostra approved by e approved at
- Document hash aparece

---

### 6.4 Submit FRIA e Reject (Teste de Reject)

**No card "FRIA":**

**Submit:**
- Email: `author@techcorp.ai`
- Notes: `FRIA assessment complete`
- Clique `Submit for Review`

**✅ VERIFICAR:** Status "Pending Review"

**Reject (para testar):**
- Approver email: `compliance-director@techcorp.ai`
- Clique `Reject`
- Quando prompt aparecer, digite: `Additional stakeholder consultation required`

**✅ VERIFICAR:**
- Status muda para "REJECTED"
- Badge vermelho
- Rejection reason aparece

---

## 🚨 PARTE 7: BLOCKING ISSUES (3 minutos)

### 7.1 Verificar Blocking Issues

**No topo da página (qualquer tab):**

**✅ VERIFICAR:**
- Banner amarelo/vermelho "Blocking Issues" aparece (se houver)
- Mostra número de issues
- Exemplo: "⚠️ 3 blocking issues prevent export"

**Clique:** `View Details` (ou no banner)

**✅ VERIFICAR:**
- Modal abre
- Lista issues, exemplo:
  - ❌ Controls missing owners (2 controls)
  - ❌ PMM missing retention policy
  - ✅ FRIA completed

---

### 7.2 Resolver Issues

**Volte para Controls tab e:**
- Atribua owners aos controles restantes
- Defina status

**Volte para Reports tab:**

**✅ VERIFICAR:**
- Banner de blocking issues desaparece (ou número diminui)
- Botão "Export Annex IV" fica habilitado

---

## 📦 PARTE 8: EXPORT & MANIFEST (5 minutos)

### 8.1 Generate Documents

**Na Reports tab:**

**Clique:** `Export Annex IV (.zip)`

**✅ VERIFICAR:**
- Download inicia
- Arquivo `annex-iv.zip` baixado

---

### 8.2 Extrair e Inspecionar ZIP

**Extraia o ZIP e verifique:**

**Arquivos esperados:**
```
📦 annex-iv.zip
├── annex_iv.md                  ✅
├── fria.md                      ✅ NOVO
├── soa.md                       ✅
├── monitoring_report.md         ✅
├── instructions_for_use.md      ✅
├── risk_assessment.md           ✅
├── human_oversight.md           ✅
├── logging_plan.md              ✅
├── appeals_flow.md              ✅
├── model_card.md                ✅
├── data_sheet.md                ✅
├── policy_register.md           ✅
├── audit_log.md                 ✅
├── manifest.json                ✅
├── evidence/                    ✅
│   ├── ai-governance-policy.pdf
│   ├── data-quality-audit.pdf
│   └── fairness-testing.pdf
```

---

### 8.3 Verificar manifest.json

**Abra `manifest.json` e verifique:**

```json
{
  "system_id": 1,
  "generated_at": "2025-10-21T...",
  "generator_version": "1.0.0",
  "artifacts": [
    {
      "name": "annex_iv.md",
      "sha256": "...",
      "bytes": 12345
    },
    {
      "name": "fria.md",
      "sha256": "...",
      "bytes": 8901
    },
    // ... outros arquivos
  ],
  "approvals": [
    {
      "doc": "annex_iv",
      "status": "approved",
      "email": "compliance-director@techcorp.ai",
      "timestamp": "2025-10-21T..."
    }
  ],
  "sources": [
    {
      "doc": "annex_iv",
      "evidence": [
        {
          "id": 1,
          "sha256": "..."
        }
      ]
    }
  ]
}
```

**✅ VERIFICAR:**
- Todos os documentos têm SHA-256
- Tamanhos (bytes) estão corretos
- Approvals incluídas
- Evidence sources mapeadas

---

### 8.4 Verificar Documentos - Zero Placeholders

**Abra `annex_iv.md` e busque:**

**❌ NÃO DEVE TER:**
- `TBD`
- `TODO`
- `[Insert ...]`
- `{{ variable }}` não renderizado
- `Not specified` (em campos obrigatórios)

**✅ DEVE TER:**
- Nome do sistema: `Credit Scoring AI`
- Empresa: `TechCorp AI Solutions`
- Riscos reais (os 3 que você adicionou)
- Controles com owners reais
- Evidence citations: `[EV-1 | AI Governance Policy | sha256:...]`
- Model version: `v1.1.0` (ou a última)
- Approval status no topo

**Abra `fria.md` (NOVO) e verifique:**
- Contexto do sistema
- Respostas do questionário
- Campos estendidos (proportionality, residual risk, DPIA)
- Approval status

**Abra `model_card.md` e verifique:**
- Model version aparece: `v1.1.0`
- Approved by: `tech-lead@techcorp.ai`
- Version history mostra ambas versões

---

## ✅ PARTE 9: VALIDAÇÃO FINAL (2 minutos)

### 9.1 Checklist Completo

Marque cada item:

**Onboarding:**
- [x] Company setup completo
- [x] Sistema criado (Credit Scoring AI)
- [x] 3 riscos adicionados
- [x] Human oversight configurado
- [x] PMM configurado

**Model Versioning:**
- [x] Versão 1.0.0 criada
- [x] Versão 1.1.0 criada
- [x] Latest version exibida
- [x] History mostra todas versões

**Controls & Evidence:**
- [x] Controles configurados (3+)
- [x] Owners atribuídos
- [x] 3 evidências uploaded
- [x] Evidências linkadas aos controles
- [x] SHA-256 calculado automaticamente

**FRIA:**
- [x] 20 questões respondidas
- [x] Campos estendidos preenchidos
- [x] FRIA submetido com sucesso
- [x] Campos persistidos no backend

**Approvals:**
- [x] Annex IV: submitted → approved
- [x] FRIA: submitted → rejected (teste)
- [x] 5 componentes de approval visíveis
- [x] Status persistidos

**Blocking Issues:**
- [x] Issues detectadas
- [x] Modal com detalhes funciona
- [x] Issues resolvidas após ações

**Export:**
- [x] ZIP gerado com sucesso
- [x] 15 documentos incluídos
- [x] manifest.json completo
- [x] Evidências incluídas
- [x] SHA-256 hashes corretos
- [x] Approvals no manifest
- [x] ZERO placeholders
- [x] Dados reais em todos os templates

---

## 🎯 RESULTADOS ESPERADOS

### ✅ SUCESSO COMPLETO SE:

1. **Todos os steps completados sem erros**
2. **ZIP gerado contém:**
   - 15 documentos MD
   - manifest.json válido
   - 3 evidências
   - Zero placeholders
3. **Documentos mostram dados reais:**
   - Nome do sistema correto
   - Riscos que você adicionou
   - Controles com owners
   - Model versions
   - Evidence citations
4. **Approvals funcionando:**
   - Submit, approve, reject todos funcionais
   - Status persiste e aparece nos documentos
5. **Model Versioning funcional:**
   - Create version funciona
   - Validation funciona
   - History atualiza
   - Latest version exibida

---

## 🐛 TROUBLESHOOTING

### Problema: "Failed to load system"
**Solução:**
```bash
# Verificar backend
curl http://localhost:8001/systems/1 -H "X-API-Key: dev-key-123"

# Verificar logs backend
cd backend
tail -f logs/api.log
```

### Problema: "Cannot create version"
**Solução:**
- Verificar formato: `1.0.0` ou `1.0` (não `v1.0`)
- Verificar email válido
- Ver console do navegador (F12) para erro específico

### Problema: "ZIP sem fria.md"
**Solução:**
- Verificar se FRIA foi submetido
- Regenerar documentos: POST `/documents/systems/1/generate`
- Verificar `DocumentGenerator.document_templates` inclui FRIA

### Problema: "Placeholders no documento"
**Solução:**
- Verificar qual template
- Verificar `DocumentContextService` expõe dados
- Reprocessar documentos

---

## 📊 TEMPO TOTAL ESTIMADO

- Parte 1 (Setup): 5 min
- Parte 2 (Onboarding): 10 min
- Parte 3 (Model Versioning): 5 min
- Parte 4 (Controls & Evidence): 8 min
- Parte 5 (FRIA): 7 min
- Parte 6 (Approvals): 5 min
- Parte 7 (Blocking Issues): 3 min
- Parte 8 (Export): 5 min
- Parte 9 (Validação): 2 min

**TOTAL: ~50 minutos** (teste completo e minucioso)

---

## 🎉 PRÓXIMO PASSO

**Se tudo passou:** Seu sistema está **100% PRONTO PARA PRODUÇÃO!** 🚀

**Deploy:**
1. Backend → Railway/Render
2. Frontend → Vercel
3. Configure domínio
4. **Primeiro cliente!**

---

**Criado por:** Cursor AI + Claude Sonnet 4.5  
**Data:** October 21, 2025  
**Versão:** 1.0.0
