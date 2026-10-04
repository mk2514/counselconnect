import asyncio
import os
import sys

# Add the apps/api directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import delete, select
from app.database import async_session_factory
from app.config import settings
from app.models.user import User, PoliceProfile, LawyerProfile, CourtAuthorityProfile
from app.models.court import Court
from app.models.case import Case, Party
from app.security.password import hash_password

async def run_reset():
    if settings.python_env == "production":
        print("ERROR: Cannot run demo reset script in production environment.")
        sys.exit(1)

    print("Starting DEMONSTRATION DATA reset...")

    print("Initializing Database Tables...")
    import app.models  # Ensure all models are registered
    from app.models.base import Base
    from app.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # 1. Find and delete existing demo data
        # We identify demo users by their unique codes starting with 'DEMO-'
        print("Cleaning up old demo cases...")
        stmt_cases = select(Case).where(Case.csr_number.like("CSR-DEMO-%"))
        cases = (await session.execute(stmt_cases)).scalars().all()
        for case in cases:
            await session.delete(case)
            
        print("Cleaning up old demo profiles and users...")
        # Delete Police
        stmt_police = select(PoliceProfile).where(PoliceProfile.station_code == "DEMO-POLICE")
        p = (await session.execute(stmt_police)).scalar_one_or_none()
        if p:
            user = await session.get(User, p.user_id)
            if user: await session.delete(user)
            
        # Delete Lawyer
        stmt_lawyer = select(LawyerProfile).where(LawyerProfile.bar_registration_id == "DEMO-LAWYER")
        l = (await session.execute(stmt_lawyer)).scalar_one_or_none()
        if l:
            user = await session.get(User, l.user_id)
            if user: await session.delete(user)
            
        # Delete Court Auth
        stmt_ca = select(CourtAuthorityProfile).where(CourtAuthorityProfile.jo_code == "DEMO-COURT")
        c = (await session.execute(stmt_ca)).scalar_one_or_none()
        if c:
            user = await session.get(User, c.user_id)
            if user: await session.delete(user)
            
        await session.commit()

        # 2. Create foundational demo data
        print("Creating demo Court...")
        stmt_court = select(Court).where(Court.court_name == "Demonstration District Court")
        demo_court = (await session.execute(stmt_court)).scalar_one_or_none()
        if not demo_court:
            demo_court = Court(
                court_name="Demonstration District Court",
                court_type="DISTRICT",
                jurisdiction="Demo City",
                address="Demo City"
            )
            session.add(demo_court)
            await session.flush()

        print("Creating demo Users...")
        # Police User
        police_user = User(role="POLICE", status="ACTIVE", password_hash=hash_password("demo"))
        session.add(police_user)
        await session.flush()
        police_profile = PoliceProfile(
            user_id=police_user.id,
            station_code="DEMO-POLICE",
            officer_name="Sgt. Demo (DEMONSTRATION)",
            station_name="Demo Central Station",
            jurisdiction="Demo City Limits",
            verification_status="VERIFIED"
        )
        session.add(police_profile)

        # Lawyer User
        lawyer_user = User(role="LAWYER", status="ACTIVE", password_hash=hash_password("demo"))
        session.add(lawyer_user)
        await session.flush()
        lawyer_profile = LawyerProfile(
            user_id=lawyer_user.id,
            full_name="Adv. Demo (DEMONSTRATION)",
            bar_registration_id="DEMO-LAWYER",
            phone="555-DEMO-LAW",
            verification_status="VERIFIED"
        )
        session.add(lawyer_profile)

        # Court Authority User
        court_user = User(role="COURT_AUTHORITY", status="ACTIVE", password_hash=hash_password("demo"))
        session.add(court_user)
        await session.flush()
        court_profile = CourtAuthorityProfile(
            user_id=court_user.id,
            full_name="Hon. Demo (DEMONSTRATION)",
            jo_code="DEMO-COURT",
            court_id=demo_court.id,
            verification_status="VERIFIED"
        )
        session.add(court_profile)
        
        await session.commit()
        print("DEMONSTRATION DATA reset successfully.")
        print("Demo Credentials:")
        print("  Police:")
        print("    Code: DEMO-POLICE")
        print("    Pass: demo")
        print("  Lawyer:")
        print("    Bar ID: DEMO-LAWYER")
        print("    Pass: demo")
        print("  Court Authority:")
        print("    JO Code: DEMO-COURT")
        print("    Pass: demo")

if __name__ == "__main__":
    asyncio.run(run_reset())
