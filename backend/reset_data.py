#!/usr/bin/env python3
"""
Script to clean all registered data while maintaining database structure.

WARNING: This script deletes ALL data but maintains:
- Table structure (schema)
- Applied migrations
- System configuration

Usage:
    python reset_data.py

or with automatic confirmation:
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
    """Ask for user confirmation."""
    if '--yes' in sys.argv or '-y' in sys.argv:
        return True
    
    print("\n" + "="*60)
    print("⚠️  WARNING: COMPLETE DATA RESET")
    print("="*60)
    print("\nThis script will DELETE all data:")
    print("  - All organizations")
    print("  - All AI systems")
    print("  - All risks")
    print("  - All controls")
    print("  - All evidence")
    print("  - All FRIAs")
    print("  - All incidents")
    print("  - All document approvals")
    print("  - All model versions")
    print("  - All onboarding data")
    print("\n❗ Database structure (tables) will be MAINTAINED")
    print("❗ Migrations will NOT be reverted")
    print("\n" + "="*60)
    
    response = input("\nDo you want to continue? Type 'YES' to confirm: ")
    return response.upper() == 'YES'


def delete_generated_documents():
    """Delete generated documents."""
    docs_dir = Path("generated_documents")
    
    if docs_dir.exists():
        print("\n📁 Deleting generated documents...")
        import shutil
        shutil.rmtree(docs_dir)
        print("   ✅ Documents deleted")
    else:
        print("\n📁 No generated documents found")


def reset_database():
    """Clear all database data."""
    db = SessionLocal()
    
    try:
        print("\n🗄️  Starting database cleanup...\n")
        
        # Important order: delete dependent tables first
        tables_to_clear = [
            # Documents and approvals
            ("DocumentApproval", DocumentApproval, "document approvals"),
            
            # Model versions
            ("ModelVersion", ModelVersion, "model versions"),
            
            # Compliance data
            ("Evidence", Evidence, "evidence"),
            ("Control", Control, "controls"),
            ("AIRisk", AIRisk, "risks"),
            ("FRIA", FRIA, "FRIAs"),
            ("Incident", Incident, "incidents"),
            ("Oversight", Oversight, "oversight configurations"),
            ("PMM", PMM, "PMM configurations"),
            ("OnboardingData", OnboardingData, "onboarding data"),
            
            # Systems (after all dependencies)
            ("AISystem", AISystem, "AI systems"),
            
            # Organizations (last)
            ("Organization", Organization, "organizations"),
        ]
        
        total_deleted = 0
        
        for table_name, model, description in tables_to_clear:
            try:
                count = db.query(model).count()
                if count > 0:
                    db.query(model).delete()
                    db.commit()
                    print(f"   ✅ {count:3d} {description} deleted")
                    total_deleted += count
                else:
                    print(f"   ⊘  0   {description} (already empty)")
            except Exception as e:
                print(f"   ⚠️  Error deleting {description}: {e}")
                db.rollback()
        
        # Reset auto-increment counters (SQLite specific)
        print("\n🔄 Resetting ID counters...")
        try:
            db.execute(text("DELETE FROM sqlite_sequence"))
            db.commit()
            print("   ✅ Counters reset")
        except Exception as e:
            print(f"   ⚠️  Warning: {e}")
        
        print("\n" + "="*60)
        print(f"✅ TOTAL: {total_deleted} records deleted successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ ERROR during cleanup: {e}")
        db.rollback()
        return False
    finally:
        db.close()
    
    return True


def verify_clean():
    """Verify if database is clean."""
    db = SessionLocal()
    
    try:
        print("\n🔍 Verifying cleanup...\n")
        
        checks = [
            ("Organizations", Organization),
            ("AI Systems", AISystem),
            ("Risks", AIRisk),
            ("Controls", Control),
            ("Evidence", Evidence),
            ("FRIAs", FRIA),
            ("Incidents", Incident),
            ("Approvals", DocumentApproval),
            ("Model Versions", ModelVersion),
        ]
        
        all_clean = True
        
        for name, model in checks:
            count = db.query(model).count()
            if count == 0:
                print(f"   ✅ {name:20s}: 0 records")
            else:
                print(f"   ❌ {name:20s}: {count} records (STILL EXIST!)")
                all_clean = False
        
        print()
        return all_clean
        
    finally:
        db.close()


def main():
    """Main function."""
    print("\n" + "🧹 " * 20)
    print("   AIMS STUDIO - DATA RESET")
    print("🧹 " * 20)
    
    # Ask for confirmation
    if not confirm_reset():
        print("\n❌ Operation cancelled by user.")
        return 1
    
    print("\n🚀 Starting reset...\n")
    
    # 1. Delete generated documents
    delete_generated_documents()
    
    # 2. Clear database
    success = reset_database()
    
    if not success:
        print("\n❌ Reset failed. Check errors above.")
        return 1
    
    # 3. Verify cleanup
    if verify_clean():
        print("\n" + "="*60)
        print("🎉 COMPLETE RESET SUCCESSFUL!")
        print("="*60)
        print("\n✅ Database cleaned")
        print("✅ Documents removed")
        print("✅ Structure maintained")
        print("✅ Ready for new test\n")
        
        print("💡 Next steps:")
        print("   1. Access: http://localhost:3000")
        print("   2. Clear browser localStorage (F12 → Console):")
        print("      localStorage.clear(); location.reload()")
        print("   3. Start new onboarding\n")
        
        return 0
    else:
        print("\n⚠️  Some tables still have data. Check above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

