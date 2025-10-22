# 🧹 RESET COMPLETO - LIMPAR TODOS OS DADOS

**Objetivo:** Limpar todos os dados cadastrados mantendo o sistema funcionando  
**Tempo:** ~2 minutos  
**Seguro:** ✅ Não quebra nada, mantém estrutura

---

## 📋 O QUE SERÁ DELETADO:

### Backend (Banco de Dados):
- ❌ Todas as organizações
- ❌ Todos os sistemas AI
- ❌ Todos os riscos
- ❌ Todos os controles
- ❌ Todas as evidências
- ❌ Todos os FRIAs
- ❌ Todos os incidentes
- ❌ Todas as aprovações
- ❌ Todas as versões de modelo
- ❌ Todos os dados de onboarding
- ❌ Todos os documentos gerados (`generated_documents/`)

### Frontend (Browser):
- ❌ Dados do localStorage
- ❌ Cache da sessão

---

## ✅ O QUE SERÁ MANTIDO:

- ✅ Estrutura do banco (tabelas)
- ✅ Migrations aplicadas (6 migrations)
- ✅ Código fonte
- ✅ Configurações
- ✅ Backend e Frontend rodando

---

## 🚀 MÉTODO 1: Reset Automático (Recomendado)

### Passo 1: Reset do Backend

```bash
cd /Users/fabio/Desktop/foundry/backend

# Executar script de reset
python reset_data.py
```

**Você verá:**
```
⚠️  ATENÇÃO: RESET COMPLETO DE DADOS

Este script irá DELETAR todos os dados:
  - Todas as organizações
  - Todos os sistemas AI
  ...

Deseja continuar? Digite 'SIM' para confirmar:
```

**Digite:** `SIM` e pressione Enter

**Resultado esperado:**
```
✅ 15 organizações deletado(s)
✅ 12 sistemas AI deletado(s)
✅ 24 riscos deletado(s)
...
🎉 RESET COMPLETO COM SUCESSO!
```

---

### Passo 2: Reset do Frontend

**Opção A - Via Navegador (Mais Fácil):**

1. Abra: http://localhost:3000
2. Pressione `F12` (Developer Tools)
3. Vá para tab **Console**
4. Cole e execute:

```javascript
localStorage.clear();
sessionStorage.clear();
console.log('✅ Storage limpo!');
location.reload();
```

**Resultado:** Página recarrega limpa

---

**Opção B - Via Script (Se tiver muitas tabs abertas):**

```bash
# Fechar navegador completamente
# Reabrir e acessar http://localhost:3000
```

---

## 🚀 MÉTODO 2: Reset Rápido (Sem Confirmação)

**Se você tem CERTEZA e quer mais rápido:**

```bash
cd /Users/fabio/Desktop/foundry/backend

# Reset automático (pula confirmação)
python reset_data.py --yes
```

---

## 🚀 MÉTODO 3: Reset Manual (Se script falhar)

### Backend - Deletar banco e recriar:

```bash
cd /Users/fabio/Desktop/foundry/backend

# 1. Backup do banco (opcional)
cp aims.db aims.db.backup

# 2. Deletar banco
rm aims.db

# 3. Recriar com migrations
alembic upgrade head

# 4. Verificar
python -c "from app.database import engine; from app.models import Base; print('✅ Banco recriado')"
```

### Frontend - Limpar storage:

```javascript
// No Console do navegador (F12)
localStorage.clear();
sessionStorage.clear();
caches.keys().then(keys => keys.forEach(key => caches.delete(key)));
location.reload();
```

---

## 🔍 VERIFICAÇÃO PÓS-RESET

### 1. Verificar Backend

```bash
cd /Users/fabio/Desktop/foundry/backend

# Verificar se banco está vazio
python -c "
from app.database import SessionLocal
from app.models import Organization, AISystem

db = SessionLocal()
orgs = db.query(Organization).count()
systems = db.query(AISystem).count()

print(f'Organizações: {orgs}')
print(f'Sistemas: {systems}')

if orgs == 0 and systems == 0:
    print('✅ Banco limpo com sucesso!')
else:
    print('⚠️  Ainda existem dados')
"
```

**Esperado:**
```
Organizações: 0
Sistemas: 0
✅ Banco limpo com sucesso!
```

---

### 2. Verificar Frontend

1. Acesse: http://localhost:3000
2. Pressione `F12` → Console
3. Execute:

```javascript
console.log('localStorage:', localStorage.length);
console.log('sessionStorage:', sessionStorage.length);
```

**Esperado:**
```
localStorage: 0
sessionStorage: 0
```

---

### 3. Verificar Documentos

```bash
cd /Users/fabio/Desktop/foundry/backend

# Verificar se pasta foi deletada
ls -la generated_documents/ 2>/dev/null || echo "✅ Pasta não existe (limpo)"
```

**Esperado:**
```
✅ Pasta não existe (limpo)
```

---

## ✅ PRONTO PARA NOVO TESTE

Após o reset, você pode:

1. **Acessar:** http://localhost:3000
2. **Ver:** Tela de onboarding limpa
3. **Começar:** Novo teste do zero

**Use o guia:** `TESTE_GUIADO_COMPLETO.md`

---

## 🐛 TROUBLESHOOTING

### Erro: "Permission denied" ao deletar aims.db

**Solução:**
```bash
# Parar backend primeiro
# Ctrl+C no terminal do backend

# Depois deletar
rm aims.db
```

---

### Erro: "Foreign key constraint"

**Solução:** Use o script Python (`reset_data.py`) que deleta na ordem correta.

---

### Erro: Script não encontra módulos

**Solução:**
```bash
cd /Users/fabio/Desktop/foundry/backend
source .venv/bin/activate
python reset_data.py
```

---

### Frontend ainda mostra dados antigos

**Solução:**
```bash
# Hard refresh
Cmd+Shift+R (Mac)
Ctrl+Shift+R (Windows/Linux)

# Ou modo anônimo
Cmd+Shift+N (Mac)
Ctrl+Shift+N (Windows/Linux)
```

---

## 📊 SCRIPT DE RESET - DETALHES

O script `reset_data.py`:

✅ **Seguro:**
- Pede confirmação
- Deleta na ordem correta (dependências primeiro)
- Mantém estrutura do banco

✅ **Completo:**
- Deleta todos os dados
- Remove documentos gerados
- Reseta IDs auto-increment
- Verifica limpeza

✅ **Informativo:**
- Mostra quantos registros foram deletados
- Lista o que foi limpo
- Confirma sucesso

---

## 🎯 RESUMO RÁPIDO

**Para reset completo em 1 minuto:**

```bash
# Terminal 1 - Backend
cd /Users/fabio/Desktop/foundry/backend
python reset_data.py --yes

# Terminal 2 - Frontend (Console do navegador)
localStorage.clear(); location.reload();
```

**Pronto! Sistema limpo e pronto para novo teste.** ✅

---

## 💡 DICA PRO

**Se você vai fazer múltiplos testes:**

Crie um alias no seu shell:

```bash
# Adicione ao ~/.zshrc ou ~/.bashrc
alias aims-reset='cd /Users/fabio/Desktop/foundry/backend && python reset_data.py --yes'
```

**Uso:**
```bash
aims-reset
```

---

**Criado por:** Cursor AI + Claude Sonnet 4.5  
**Data:** October 21, 2025  
**Status:** ✅ Testado e Seguro
