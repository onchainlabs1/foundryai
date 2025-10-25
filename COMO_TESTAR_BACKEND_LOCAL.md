# 🚀 Como Testar o Backend Localmente

## ✅ Status Atual
- **Frontend rodando:** http://localhost:3000 ✅
- **Backend rodando:** http://localhost:8000 ✅
- **Health check:** ✅ Funcionando
- **API Key:** `dev-aims-demo-key`
- **Banco de dados:** SQLite local (`aims.db`)
- **Conexão Frontend ↔ Backend:** ✅ Configurada

## 🔗 URLs Importantes

### 🎯 **PRINCIPAL - Use este link:**
- **Aplicação Completa:** http://localhost:3000

### Documentação da API
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints Principais
- **Health Check:** http://localhost:8000/health
- **Sistemas:** http://localhost:8000/systems
- **Relatórios:** http://localhost:8000/reports/summary

## 🧪 Testes Rápidos

### 1. Health Check
```bash
curl http://localhost:8000/health
```
**Resposta esperada:** `{"status":"ok"}`

### 2. Listar Sistemas (vazio inicialmente)
```bash
curl -H "X-API-Key: dev-aims-demo-key" http://localhost:8000/systems
```
**Resposta esperada:** `[]`

### 3. Criar um Sistema de IA
```bash
curl -X POST http://localhost:8000/systems \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sistema de Teste",
    "purpose": "Teste de funcionalidade",
    "domain": "healthcare",
    "ai_act_class": "high"
  }'
```

### 4. Verificar Relatório
```bash
curl -H "X-API-Key: dev-aims-demo-key" http://localhost:8000/reports/summary
```

### 5. Exportar Annex IV (ZIP)
```bash
curl -H "X-API-Key: dev-aims-demo-key" \
  -o annex-iv-test.zip \
  http://localhost:8000/reports/annex-iv.zip
```

## 🎯 Fluxo Completo de Teste

### Passo 1: Criar Sistema
```bash
curl -X POST http://localhost:8000/systems \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sistema de Diagnóstico Médico",
    "purpose": "Diagnóstico de imagens médicas",
    "domain": "healthcare",
    "ai_act_class": "high",
    "description": "Sistema para análise de raios-X"
  }'
```

### Passo 2: Avaliar Sistema (Classificação AI Act)
```bash
# Use o ID retornado no passo anterior
curl -X POST http://localhost:8000/systems/1/assess \
  -H "X-API-Key: dev-aims-demo-key"
```

### Passo 3: Upload de Evidência
```bash
# Criar arquivo de teste
echo "Evidência de teste" > evidencia.txt

# Upload
curl -X POST http://localhost:8000/evidence/1 \
  -H "X-API-Key: dev-aims-demo-key" \
  -F "file=@evidencia.txt" \
  -F "description=Documentação de teste"
```

### Passo 4: Criar FRIA (Fundamental Rights Impact Assessment)
```bash
curl -X POST http://localhost:8000/systems/1/fria \
  -H "X-API-Key: dev-aims-demo-key" \
  -H "Content-Type: application/json" \
  -d '{
    "applicable": true,
    "answers": {
      "biometric_data": "No",
      "fundamental_rights": "Yes",
      "critical_infrastructure": "No",
      "vulnerable_groups": "Yes"
    }
  }'
```

### Passo 5: Exportar Documentos
```bash
# Annex IV completo
curl -H "X-API-Key: dev-aims-demo-key" \
  -o annex-iv-completo.zip \
  http://localhost:8000/reports/annex-iv.zip

# FRIA em HTML
curl -H "X-API-Key: dev-aims-demo-key" \
  -o fria.html \
  http://localhost:8000/fria/1.html
```

## 🔧 Comandos de Gerenciamento

### Parar o Servidor
```bash
# Encontrar o processo
ps aux | grep uvicorn

# Matar o processo (substitua PID pelo número do processo)
kill PID
```

### Reiniciar o Servidor
```bash
cd /Users/fabio/Desktop/foundry/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Ver Logs
```bash
# Logs do servidor aparecem no terminal onde foi iniciado
# Para logs de aplicação, verificar:
tail -f /Users/fabio/Desktop/foundry/backend/audit.log
```

## 🐛 Troubleshooting

### Erro 403 Forbidden
- Verificar se o header `X-API-Key: dev-aims-demo-key` está presente
- Confirmar que a API key está correta

### Erro 500 Internal Server Error
- Verificar logs do servidor
- Confirmar que o banco de dados existe: `ls -la aims.db`

### Servidor não inicia
- Verificar se a porta 8000 está livre: `lsof -i :8000`
- Usar porta diferente: `--port 8001`

## 📊 Monitoramento

### Verificar Status
```bash
# Health check
curl http://localhost:8000/health

# Estatísticas
curl -H "X-API-Key: dev-aims-demo-key" http://localhost:8000/reports/summary
```

### Banco de Dados
```bash
# Verificar tamanho do banco
ls -lh aims.db

# Backup do banco
cp aims.db aims-backup-$(date +%Y%m%d).db
```

## 🎉 Próximos Passos

1. **Testar Frontend:** Se tiver o frontend rodando, conectar em http://localhost:3002
2. **Integração:** Testar fluxo completo Onboarding → Documentos → Export
3. **Performance:** Testar com múltiplos sistemas e evidências
4. **Segurança:** Testar diferentes API keys e permissões

---

**Servidor rodando em:** http://localhost:8000  
**API Key para testes:** `dev-aims-demo-key`  
**Documentação:** http://localhost:8000/docs
