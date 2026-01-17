import asyncio
import sys
from sqlalchemy import text

# Add the parent directory to sys.path
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import create_tables, engine, get_db
from app.core.config import settings

async def verify_setup():
    print(f"🔧 Testing configuration for {settings.app_name}...")
    
    # 1. Check configuration
    print(f"✅ Configuration loaded. Env: {settings.app_env}")
    print(f"   Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else '***'}")
    
    # 2. Check database connection
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # 3. Create tables
    try:
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return
        
    print("\n🎉 Backend verification complete! The system is ready to start.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_setup())
