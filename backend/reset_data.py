#!/usr/bin/env python3
"""
Script para limpar todos os dados cadastrados mantendo a estrutura do banco.

ATENÇÃO: Este script deleta TODOS os dados mas mantém:
- Estrutura das tabelas (schema)
- Migrations aplicadas
- Configuração do sistema

Uso:
    python reset_data.py

ou com confirmação automática:
    python reset_data.py --yes
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from app.database import SessionLocal, engine
from app.models import (
    Organization, AISystem, AIRisk, Control, Evidence, 
    FRIA, Incident, Oversight, PMM, OnboardingData,
    DocumentApproval, ModelVersion
)


def confirm_reset():
    """Pedir confirmação do usuário."""
    if '--yes' in sys.argv or '-y' in sys.argv:
        return True
    
    print("\n" + "="*60)
    print("⚠️  ATENÇÃO: RESET COMPLETO DE DADOS")
    print("="*60)
    print("\nEste script irá DELETAR todos os dados:")
    print("  - Todas as organizações")
    print("  - Todos os sistemas AI")
    print("  - Todos os riscos")
    print("  - Todos os controles")
    print("  - Todas as evidências")
    print("  - Todos os FRIAs")
    print("  - Todos os incidentes")
    print("  - Todas as aprovações de documentos")
    print("  - Todas as versões de modelo")
    print("  - Todos os dados de onboarding")
    print("\n❗ A estrutura do banco (tabelas) será MANTIDA")
    print("❗ As migrations NÃO serão revertidas")
    print("\n" + "="*60)
    
    response = input("\nDeseja continuar? Digite 'SIM' para confirmar: ")
    return response.upper() == 'SIM'


def delete_generated_documents():
    """Deletar documentos gerados."""
    docs_dir = Path("generated_documents")
    
    if docs_dir.exists():
        print("\n📁 Deletando documentos gerados...")
        import shutil
        shutil.rmtree(docs_dir)
        print("   ✅ Documentos deletados")
    else:
        print("\n📁 Nenhum documento gerado encontrado")


def reset_database():
    """Limpar todos os dados do banco."""
    db = SessionLocal()
    
    try:
        print("\n🗄️  Iniciando limpeza do banco de dados...\n")
        
        # Ordem importante: deletar tabelas dependentes primeiro
        tables_to_clear = [
            # Documentos e aprovações
            ("DocumentApproval", DocumentApproval, "aprovações de documentos"),
            
            # Model versions
            ("ModelVersion", ModelVersion, "versões de modelo"),
            
            # Dados de compliance
            ("Evidence", Evidence, "evidências"),
            ("Control", Control, "controles"),
            ("AIRisk", AIRisk, "riscos"),
            ("FRIA", FRIA, "FRIAs"),
            ("Incident", Incident, "incidentes"),
            ("Oversight", Oversight, "configurações de oversight"),
            ("PMM", PMM, "configurações de PMM"),
            ("OnboardingData", OnboardingData, "dados de onboarding"),
            
            # Sistemas (depois de todas as dependências)
            ("AISystem", AISystem, "sistemas AI"),
            
            # Organizações (por último)
            ("Organization", Organization, "organizações"),
        ]
        
        total_deleted = 0
        
        for table_name, model, description in tables_to_clear:
            try:
                count = db.query(model).count()
                if count > 0:
                    db.query(model).delete()
                    db.commit()
                    print(f"   ✅ {count:3d} {description} deletado(s)")
                    total_deleted += count
                else:
                    print(f"   ⊘  0   {description} (já vazio)")
            except Exception as e:
                print(f"   ⚠️  Erro ao deletar {description}: {e}")
                db.rollback()
        
        # Reset auto-increment counters (SQLite specific)
        print("\n🔄 Resetando contadores de ID...")
        try:
            db.execute(text("DELETE FROM sqlite_sequence"))
            db.commit()
            print("   ✅ Contadores resetados")
        except Exception as e:
            print(f"   ⚠️  Aviso: {e}")
        
        print("\n" + "="*60)
        print(f"✅ TOTAL: {total_deleted} registros deletados com sucesso!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERRO durante limpeza: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


def verify_clean():
    """Verificar se o banco está limpo."""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verificando limpeza...\n")
        
        checks = [
            ("Organizações", Organization),
            ("Sistemas AI", AISystem),
            ("Riscos", AIRisk),
            ("Controles", Control),
            ("Evidências", Evidence),
            ("FRIAs", FRIA),
            ("Incidentes", Incident),
            ("Aprovações", DocumentApproval),
            ("Versões Modelo", ModelVersion),
        ]
        
        all_clean = True
        
        for name, model in checks:
            count = db.query(model).count()
            if count == 0:
                print(f"   ✅ {name:20s}: 0 registros")
            else:
                print(f"   ❌ {name:20s}: {count} registros (AINDA EXISTEM!)")
                all_clean = False
        
        print()
        return all_clean
        
    finally:
        db.close()


def main():
    """Função principal."""
    print("\n" + "🧹 " * 20)
    print("   AIMS STUDIO - RESET DE DADOS")
    print("🧹 " * 20)
    
    # Pedir confirmação
    if not confirm_reset():
        print("\n❌ Operação cancelada pelo usuário.")
        return 1
    
    print("\n🚀 Iniciando reset...\n")
    
    # 1. Deletar documentos gerados
    delete_generated_documents()
    
    # 2. Limpar banco de dados
    success = reset_database()
    
    if not success:
        print("\n❌ Reset falhou. Verifique os erros acima.")
        return 1
    
    # 3. Verificar limpeza
    if verify_clean():
        print("\n" + "="*60)
        print("🎉 RESET COMPLETO COM SUCESSO!")
        print("="*60)
        print("\n✅ Banco de dados limpo")
        print("✅ Documentos removidos")
        print("✅ Estrutura mantida")
        print("✅ Pronto para novo teste\n")
        
        print("💡 Próximos passos:")
        print("   1. Acesse: http://localhost:3000")
        print("   2. Limpe localStorage do navegador (F12 → Console):")
        print("      localStorage.clear(); location.reload()")
        print("   3. Comece novo onboarding\n")
        
        return 0
    else:
        print("\n⚠️  Algumas tabelas ainda têm dados. Verifique acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

