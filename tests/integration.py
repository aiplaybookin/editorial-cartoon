import httpx
import asyncio
import time
import json
import re
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded environment from {env_path}")
else:
    print(f"⚠ Warning: .env file not found at {env_path}")
    print("  Please create .env from .env.example and set ANTHROPIC_API_KEY")

async def complete_workflow_test():
    """
    Test complete workflow:
    1. Register user
    2. Create campaign
    3. Generate email content
    4. Create template
    5. Refine content
    6. Generate subject lines
    """

    # Check environment setup
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        print("✗ Error: ANTHROPIC_API_KEY not set properly in .env file")
        print("  Expected format: ANTHROPIC_API_KEY=sk-ant-api03-...")
        print("  Please set it in .env file before running tests")
        return
    print(f"✓ ANTHROPIC_API_KEY found (starts with: {api_key[:15]}...)")

    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Use timestamp to ensure unique email and organization domain
        timestamp = int(time.time())
        email = f"test{timestamp}@testcorp{timestamp}.com"
        print(f"Registering user: {email}")
        
        try:
            response = await client.post(
                f"{base_url}/auth/register",
                json={
                    "email": email,
                    "password": "SecurePass123!",
                    "full_name": "Varad Patil",
                    "organization_name": "Relentlessstrength Inc.",
                    "industry": "Sports and Training"
                }
            )
            response.raise_for_status()
            token = response.json().get("access_token")
            if not token:
                print(f"Registration failed, no token. Status: {response.status_code}")
                print(response.text)
                return
            headers = {"Authorization": f"Bearer {token}"}
            print("✓ User registered")
        except Exception as e:
            print(f"Registration failed: {e}")
            if 'response' in locals():
                print(response.text)
            return
        
        print("\n=== STEP 2: Create Campaign ===")
        response = await client.post(
            f"{base_url}/campaigns",
            headers=headers,
            json={
                "name": "New Branch Opening Event",
                "primary_goal": "event_promotion",
                "target_audience_description": "Bodybuilders and fitness enthusiasts",
                "objectives": [
                    {
                        "objective_type": "primary",
                        "description": "Drive demo signups",
                        "kpi_name": "conversion",
                        "target_value": 3.0,
                        "priority": 1
                    }
                ]
            }
        )
        if response.status_code != 201:
            print(f"Create campaign failed: {response.text}")
            return
            
        campaign_id = response.json()["id"]
        print(f"✓ Campaign created: {campaign_id}")
        
        print("\n=== STEP 3: Generate Email Content ===")
        response = await client.post(
            f"{base_url}/campaigns/{campaign_id}/generate",
            headers=headers,
            json={
                "user_prompt": "Create an engaging email for our new branch opening event.",
                "generation_options": {
                    "tone": "casual",
                    "length": "medium",
                    "variants_count": 2
                }
            }
        )
        if response.status_code != 202:
            print(f"Generation request failed: {response.text}")
            return
            
        # Fix: The API returns `id` for the job, not `job_id`
        job_id = response.json()["id"]
        print(f"✓ Generation job started: {job_id}")
        
        # Poll for completion
        print("Waiting for generation to complete...")
        for i in range(30):
            await asyncio.sleep(2)
            response = await client.get(
                f"{base_url}/campaigns/{campaign_id}/generate/{job_id}",
                headers=headers
            )
            data = response.json()
            status = data["status"]
            print(f"Poll {i+1}: {status}")
            
            if status == "completed":
                print("✓ Content generated successfully")
                variants = data.get("generated_content", {}).get("variants", [])
                print(f"Received {len(variants)} variants")
                break
            elif status == "failed":
                print(f"Generation failed: {data.get('error_message')}")
                return
        else:
            print("Timeout waiting for generation")
            return
        
        print("\n=== STEP 4: Create Template ===")
        response = await client.post(
            f"{base_url}/campaigns/{campaign_id}/generate/{job_id}/create-template",
            headers=headers,
            params={"variant_id": 1}
        )
        if response.status_code != 201:
            print(f"Create template failed: {response.text}")
            return
            
        template_message = response.json()["message"]
        # Extract template ID from message
        template_id_match = re.search(r'ID: ([a-f0-9-]+)', template_message)
        if template_id_match:
            template_id = template_id_match.group(1)
            print(f"✓ Template created: {template_id}")
        else:
            print(f"Could not extract template ID from: {template_message}")
            return
        
        print("\n=== STEP 5: Refine Content ===")
        response = await client.post(
            f"{base_url}/campaigns/{campaign_id}/templates/{template_id}/refine",
            headers=headers,
            json={
                "template_id": template_id,
                "refinement_instructions": "Make it more energetic, concise and add urgency"
            }
        )
        if response.status_code != 202:
            print(f"Refinement request failed: {response.text}")
            return
            
        # Fix: API returns `id`   
        refine_job_id = response.json()["id"]
        print(f"✓ Refinement job started: {refine_job_id}")
        
        # Poll for refinement
        print("Waiting for refinement...")
        for i in range(30):
            await asyncio.sleep(2)
            response = await client.get(
                f"{base_url}/campaigns/{campaign_id}/generate/{refine_job_id}",
                headers=headers
            )
            if response.json()["status"] == "completed":
                print("✓ Content refined")
                break
        
        print("\n=== STEP 6: Generate Subject Lines ===")
        response = await client.post(
            f"{base_url}/campaigns/{campaign_id}/subject-lines",
            headers=headers,
            json={
                "template_id": template_id,
                "count": 5
            }
        )
        if response.status_code != 202:
            print(f"Subject line generation failed: {response.text}")
            return

        # Fix: API returns `id`
        subject_job_id = response.json()["id"]
        print(f"✓ Subject line job started: {subject_job_id}")
        
        # Poll for subject lines
        print("Waiting for subject lines...")
        for i in range(30):
            await asyncio.sleep(2)
            response = await client.get(
                f"{base_url}/campaigns/{campaign_id}/generate/{subject_job_id}",
                headers=headers
            )
            if response.json()["status"] == "completed":
                print("✓ Subject lines generated")
                break
        
        print("\n=== Workflow Complete ===")
        print("All steps executed successfully!")


# Run complete workflow test
if __name__ == "__main__":
    asyncio.run(complete_workflow_test())