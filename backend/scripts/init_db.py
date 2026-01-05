"""
Database initialization script
Run this to create all tables
"""
import sys
import os
import argparse

# Parse arguments FIRST, before any imports
parser = argparse.ArgumentParser(description="Initialize Otomasyon CRM database")
parser.add_argument("--seed", action="store_true", help="Seed initial data")
parser.add_argument("--test", action="store_true", help="Use test database (SQLite)")

args = parser.parse_args()

# Set environment BEFORE importing app modules
if args.test:
    os.environ["ENVIRONMENT"] = "testing"

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import app modules (they will use the correct environment)
from app.database import Base, engine, create_tables
from app.models import *  # Import all models to register them
from app.config import settings


def init_db():
    """Initialize database with all tables"""
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    print(f"📦 Database: {settings.active_database_url}")
    print()
    
    print("📊 Creating tables...")
    create_tables()
    
    print("✅ Tables created successfully!")
    print()
    
    # List created tables
    print("📋 Created tables:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")


def seed_initial_data():
    """Seed initial data (roles, admin user, etc.)"""
    from app.database import SessionLocal
    from app.models import Role, User
    from app.utils.security import get_password_hash
    
    db = SessionLocal()
    
    try:
        # Check if roles exist
        if db.query(Role).count() == 0:
            print("\n🌱 Seeding initial data...")
            
            # Create roles
            roles = [
                Role(name="admin", description="Sistem Yöneticisi", permissions={"all": ["read", "write", "delete"]}),
                Role(name="manager", description="Proje Yöneticisi", permissions={"projects": ["read", "write"], "stock": ["read", "write"]}),
                Role(name="technician", description="Teknik Servis", permissions={"service_forms": ["read", "write"], "stock": ["read"]}),
                Role(name="accountant", description="Muhasebe", permissions={"invoices": ["read", "write"], "expenses": ["read", "write"]}),
            ]
            
            for role in roles:
                db.add(role)
            
            db.commit()
            print("   ✅ Roles created")
            
            # Create admin user
            admin_role = db.query(Role).filter(Role.name == "admin").first()
            admin_user = User(
                email="admin@otomasyon.com",
                password_hash=get_password_hash("admin123"),
                full_name="Sistem Yöneticisi",
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("   ✅ Admin user created (admin@otomasyon.com / admin123)")
        else:
            print("\n📌 Initial data already exists, skipping...")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    
    if args.seed:
        seed_initial_data()
    
    print("\n🚀 Database initialization complete!")
