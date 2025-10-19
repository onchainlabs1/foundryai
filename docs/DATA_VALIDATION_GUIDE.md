# Data Validation & Integrity Guide

## 🎯 **Objetivo**

Garantir que **TODOS** os dados apresentados na plataforma AIMS sejam:
- ✅ **Reais** (não dummy/hardcoded)
- ✅ **Precisos** (calculados corretamente)
- ✅ **Atualizados** (frescos e relevantes)
- ✅ **Auditáveis** (rastreáveis e verificáveis)

## 🔍 **Sistema de Validação Implementado**

### **1. Validação em Tempo Real (Frontend)**

**Arquivo:** `frontend/lib/data-validation.ts`

```typescript
// Validação automática de todos os dados do dashboard
const validation = validateDashboardData({
  summary: summaryData,
  score: scoreData,
  blockingIssues: blockingData,
  upcomingDeadlines: deadlinesData
})

// Indicadores visuais de confiabilidade
if (validation.confidence === 'high') {
  // ✅ Verde: Dados confiáveis
} else if (validation.confidence === 'medium') {
  // ⚠️ Amarelo: Dados com warnings
} else {
  // ❌ Vermelho: Dados com erros
}
```

### **2. Endpoints com Dados Reais (Backend)**

**Arquivo:** `backend/app/api/routes/reports.py`

#### **Antes (Dados Dummy):**
```python
# ❌ HARDCODED - Dados fictícios
"Atlas-Vision FRIA incomplete"
"Nov 1, 2025"
"SYS-002 needs robustness testing"
```

#### **Depois (Dados Reais):**
```python
# ✅ REAL - Dados calculados do banco
systems_without_fria = db.query(AISystem).filter(
    AISystem.org_id == org_id,
    AISystem.ai_act_class == "high",
    AISystem.fria_completed == False
).all()
```

### **3. Auditoria Automática**

**Arquivo:** `backend/app/services/audit_logger.py`

```python
@audit_calculation("compliance_score", "0.6*implemented + 0.4*coverage")
def get_score(org: Organization, db: Session):
    # Todos os cálculos são logados automaticamente
    pass

@audit_data_access
def get_summary(org: Organization, db: Session):
    # Todos os acessos a dados são logados
    pass
```

## 📊 **Dados Validados**

### **Dashboard KPIs**
- ✅ **Compliant Systems:** `(systems - high_risk) / systems * 100`
- ✅ **Audit-Ready Systems:** `systems - high_risk`
- ✅ **Recent Incidents:** `last_30d_incidents` (últimos 30 dias)
- ✅ **Compliance Score:** Fórmula complexa com pesos por classe

### **Blocking Issues**
- ✅ **FRIA Incomplete:** Sistemas high-risk sem FRIA
- ✅ **Robustness Missing:** Sistemas sem avaliação de robustez
- ✅ **Overdue Controls:** Controles vencidos

### **Upcoming Deadlines**
- ✅ **Control Deadlines:** Controles com prazo nos próximos 30 dias
- ✅ **FRIA Deadlines:** Sistemas que precisam de FRIA
- ✅ **Date Calculations:** Cálculos precisos de dias restantes

## 🧪 **Testes Automatizados**

**Arquivo:** `backend/tests/test_data_validation.py`

```python
def test_no_hardcoded_dummy_data(self, db: Session, test_org: Organization):
    """Test that no hardcoded dummy data is returned"""
    # Verifica que não há dados dummy como "Atlas-Vision", "Nov 1, 2025", etc.
    
def test_calculations_accuracy(self, db: Session, test_org: Organization):
    """Test that calculations are mathematically correct"""
    # Valida que os cálculos estão matematicamente corretos
    
def test_data_consistency_across_endpoints(self, db: Session, test_org: Organization):
    """Test that data is consistent across different endpoints"""
    # Garante consistência entre diferentes endpoints
```

## 🚨 **Detecção de Dados Dummy**

### **Padrões Detectados:**
```python
dummy_patterns = [
    "Atlas-Vision",      # Nome de sistema fictício
    "SYS-002",          # ID de sistema fictício
    "Nov 1, 2025",      # Data fictícia
    "Nov 10, 2025",     # Data fictícia
    "Nov 15, 2025",     # Data fictícia
    "OB-009",           # ID de obrigação fictício
    "OB-050",           # ID de obrigação fictício
    "OB-011"            # ID de obrigação fictício
]
```

### **Ações Automáticas:**
1. **Log de Auditoria:** Registra detecção de dados dummy
2. **Alertas Visuais:** Mostra warnings na interface
3. **Fallback para Dados Reais:** Substitui por dados reais quando possível

## 📈 **Indicadores de Confiabilidade**

### **Alta Confiança (Verde)**
- ✅ Todos os dados são reais e calculados
- ✅ Validações passaram sem erros
- ✅ Dados atualizados nas últimas 24h
- ✅ Cálculos matematicamente corretos

### **Média Confiança (Amarelo)**
- ⚠️ Dados reais mas com warnings
- ⚠️ Algumas validações falharam
- ⚠️ Dados podem estar desatualizados
- ⚠️ Cálculos corretos mas com ressalvas

### **Baixa Confiança (Vermelho)**
- ❌ Dados com erros críticos
- ❌ Validações falharam
- ❌ Possível presença de dados dummy
- ❌ Cálculos incorretos ou suspeitos

## 🔧 **Como Usar**

### **1. Verificar Confiabilidade dos Dados**
```typescript
// No dashboard, procure pelo indicador de confiança
{dataValidation && (
  <div className="flex items-center gap-2">
    <div className={`px-3 py-1 rounded-full ${
      dataValidation.confidence === 'high' 
        ? 'bg-green-100 text-green-700' 
        : 'bg-red-100 text-red-700'
    }`}>
      {getDataConfidenceIndicator(dataValidation.confidence).text}
    </div>
  </div>
)}
```

### **2. Verificar Logs de Auditoria**
```bash
# Verificar logs de auditoria
tail -f audit.log | grep "DATA_ACCESS\|CALCULATION\|DUMMY_DATA"

# Exemplo de log:
# 2024-01-15 10:30:00 - audit - INFO - DATA_ACCESS: {"endpoint": "get_summary", "org_id": 1, "record_count": 7}
# 2024-01-15 10:30:01 - audit - INFO - CALCULATION: {"calculation_type": "compliance_score", "formula": "0.6*implemented + 0.4*coverage"}
```

### **3. Executar Testes de Validação**
```bash
# Executar testes de validação de dados
cd backend
python -m pytest tests/test_data_validation.py -v

# Testes específicos:
python -m pytest tests/test_data_validation.py::TestDataValidation::test_no_hardcoded_dummy_data -v
```

## 🛡️ **Garantias de Integridade**

### **1. Validação Automática**
- ✅ Todos os dados são validados em tempo real
- ✅ Cálculos são verificados matematicamente
- ✅ Consistência entre endpoints é garantida

### **2. Auditoria Completa**
- ✅ Todos os acessos a dados são logados
- ✅ Todos os cálculos são rastreados
- ✅ Detecção automática de dados dummy

### **3. Testes Abrangentes**
- ✅ Testes de precisão matemática
- ✅ Testes de consistência de dados
- ✅ Testes de detecção de dados dummy
- ✅ Testes de casos extremos

### **4. Indicadores Visuais**
- ✅ Confiabilidade dos dados visível na interface
- ✅ Timestamps de última atualização
- ✅ Alertas para dados suspeitos

## 🚀 **Próximos Passos**

1. **Monitoramento Contínuo:** Verificar logs de auditoria regularmente
2. **Expansão de Validações:** Adicionar validações para novos endpoints
3. **Alertas Automáticos:** Configurar alertas para dados de baixa confiança
4. **Relatórios de Integridade:** Gerar relatórios periódicos de qualidade dos dados

## 📞 **Suporte**

Se encontrar dados suspeitos ou incorretos:

1. **Verificar Logs:** `tail -f audit.log`
2. **Executar Testes:** `pytest tests/test_data_validation.py`
3. **Verificar Indicadores:** Olhar para o indicador de confiança no dashboard
4. **Reportar Issues:** Documentar o problema com logs relevantes

---

**✅ GARANTIA:** Com este sistema implementado, **TODOS** os dados apresentados são reais, precisos e auditáveis. Não há mais dados dummy ou hardcoded na plataforma.
