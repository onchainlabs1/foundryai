# 📄 Como Ver os Documentos Gerados na Interface

## 🎯 **Localização dos Documentos**

### **1. Via Interface Web (Mais Fácil)**

1. **Abra o navegador** e acesse: **http://localhost:3002**

2. **Clique em "Documents"** no menu de navegação superior

3. **Selecione um Sistema** - Você verá os sistemas disponíveis (ex: "Test System")

4. **Visualize os Documentos** - Após selecionar um sistema, você verá:
   - Lista de todos os documentos gerados
   - Tamanho dos arquivos (Markdown e PDF)
   - Data de criação/atualização
   - Botões para Preview, Download MD e Download PDF

### **2. Funcionalidades Disponíveis**

#### **📋 Lista de Documentos**
- **Risk Assessment** 🛡️ - Avaliação de Riscos
- **Impact Assessment** 📊 - Avaliação de Impacto  
- **Model Card** 🤖 - Cartão do Modelo
- **Data Sheet** 📋 - Folha de Dados
- **Logging Plan** 📝 - Plano de Logging
- **Monitoring Report** 📈 - Relatório de Monitoramento
- **Human Oversight** 👥 - Supervisão Humana
- **Appeals Flow** ⚖️ - Fluxo de Recursos
- **Statement of Applicability** 📄 - Declaração de Aplicabilidade
- **Policy Register** 📚 - Registro de Políticas
- **Audit Log** 🔍 - Log de Auditoria

#### **🔧 Ações Disponíveis**
- **👁️ Preview** - Visualizar documento no navegador
- **📥 Download MD** - Baixar versão Markdown
- **📥 Download PDF** - Baixar versão PDF
- **➕ Generate Documents** - Gerar novos documentos

### **3. Via Teste HTML (Alternativa)**

Se preferir uma interface de teste mais simples:

1. **Abra o arquivo**: `test-document-generation.html` no navegador
2. **Execute o "Teste Completo"** para ver tudo funcionando
3. **Use os botões individuais** para testar cada funcionalidade

### **4. Via API (Para Desenvolvedores)**

```bash
# Listar documentos de um sistema
curl -X GET "http://127.0.0.1:8002/documents/systems/2/list" \
  -H "X-API-Key: dev-aims-demo-key"

# Download de documento
curl -X GET "http://127.0.0.1:8002/documents/systems/2/download/risk_assessment?format=markdown" \
  -H "X-API-Key: dev-aims-demo-key" \
  -o risk_assessment.md
```

## 🚀 **Passo a Passo Rápido**

1. **Acesse**: http://localhost:3002
2. **Clique**: "Documents" no menu
3. **Selecione**: Um sistema (ex: "Test System")
4. **Clique**: "Generate Documents" (se não houver documentos)
5. **Visualize**: Os documentos gerados
6. **Baixe**: Clique nos botões de download

## 📁 **Localização dos Arquivos**

Os documentos são salvos em:
```
/Users/fabio/Desktop/foundry/backend/generated_documents/
├── org_1/
│   └── system_2/
│       ├── risk_assessment.md
│       ├── risk_assessment.pdf
│       ├── impact_assessment.md
│       ├── impact_assessment.pdf
│       └── ... (outros documentos)
```

## ✅ **Status Atual**

- ✅ **Backend funcionando** - Porta 8002
- ✅ **Frontend funcionando** - Porta 3002  
- ✅ **Página Documents implementada**
- ✅ **11 documentos sendo gerados**
- ✅ **Downloads funcionando**
- ✅ **Preview funcionando**

## 🎉 **Pronto para Usar!**

O sistema está 100% funcional. Você pode:
- Ver todos os documentos na interface web
- Baixar em Markdown e PDF
- Gerar novos documentos
- Fazer preview dos documentos
- Gerenciar múltiplos sistemas

**Acesse agora: http://localhost:3002/documents**
