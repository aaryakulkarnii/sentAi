import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.models.incident import Incident
from app.models.report import Report
from app.services.reporting import generate_pdf_report, generate_docx_report

async def verify():
    engine = create_async_engine("sqlite+aiosqlite:///backend/sentinel_dev.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get an incident
        q = select(Incident).limit(1)
        incident = (await session.execute(q)).scalars().first()
        if not incident:
            print("No incidents found. Please create one first.")
            return

        print(f"Testing with incident: {incident.title} ({incident.id})")
        
        # Test PDF Generation
        pdf_path = os.path.join("backend", "data", "reports", f"test_report_{incident.id}.pdf")
        generate_pdf_report(incident, [], pdf_path)
        if os.path.exists(pdf_path):
            print(f"✅ PDF generated successfully: {pdf_path}")
            print(f"Size: {os.path.getsize(pdf_path)} bytes")
        else:
            print("❌ Failed to generate PDF")
            
        # Test DOCX Generation
        docx_path = os.path.join("backend", "data", "reports", f"test_report_{incident.id}.docx")
        generate_docx_report(incident, [], docx_path)
        if os.path.exists(docx_path):
            print(f"✅ DOCX generated successfully: {docx_path}")
            print(f"Size: {os.path.getsize(docx_path)} bytes")
        else:
            print("❌ Failed to generate DOCX")

if __name__ == "__main__":
    asyncio.run(verify())
