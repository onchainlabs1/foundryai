# 🆕 Configuração para Novo Cliente

## Instância Zerada Criada com Sucesso! ✅

A instância foi completamente limpa e está pronta para um novo cliente.

### 📋 O que foi limpo:
- ✅ Banco de dados (aims.db removido)
- ✅ Arquivos de evidência (pasta evidence/ limpa)
- ✅ Dados de templates (pasta data/ limpa)
- ✅ Serviços parados

### 🔧 Próximos Passos para Configurar Novo Cliente:

#### 1. **Criar arquivo `.env` com dados do novo cliente:**

```bash
# Copie e cole no arquivo .env
ORG_NAME="Nome da Empresa Cliente"
ORG_API_KEY="cliente-api-key-$(date +%s)"
SECRET_KEY="$(openssl rand -hex 32)"
DATABASE_URL="sqlite:///./aims.db"
FRONTEND_ORIGIN="http://localhost:3002"
EVIDENCE_LOCAL_STORAGE="true"
RATE_LIMIT="100"
ENABLE_PDF_GENERATION="true"
```

#### 2. **Iniciar os serviços:**

```bash
# Terminal 1 - Backend
cd /Users/fabio/Desktop/foundry/backend
source .venv/bin/activate
export SECRET_KEY="$(openssl rand -hex 32)"
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 2 - Frontend  
cd /Users/fabio/Desktop/foundry/frontend
PORT=3002 NEXT_PUBLIC_API_URL=http://127.0.0.1:8002 npm run dev
```

#### 3. **Acessar a aplicação:**
- **Frontend:** http://localhost:3002
- **Backend API:** http://localhost:8002/health

### 🎯 Funcionalidades Disponíveis para Novo Cliente:

1. **Dashboard Limpo** - Sem dados pré-existentes
2. **Onboarding Wizard** - http://localhost:3002/onboarding
3. **Templates ISO/IEC 42001** - http://localhost:3002/templates
4. **Sistema de Inventário** - http://localhost:3002/inventory
5. **Relatórios** - http://localhost:3002/reports

### 🔐 Segurança:
- Nova API key será gerada automaticamente
- SECRET_KEY seguro será criado
- Banco de dados limpo sem dados de teste
- Evidências anteriores removidas

### 📊 Status da Instância:
- **Estado:** Zerada e pronta
- **Banco:** Limpo (será recriado na primeira execução)
- **Evidências:** Removidas
- **Templates:** Serão recarregados automaticamente
- **Configuração:** Pronta para novo cliente

**A instância está 100% limpa e pronta para configuração do novo cliente!** 🚀
