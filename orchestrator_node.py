#!/usr/bin/env python3
"""
MDEC THRESHER ORCHESTRATOR - SWARM WORKER NODE
----------------------------------------------
Role: Containerized Daemon that binds the MdEC Toolkit to the Docker Swarm.
Phases: 
  0: Signet Minting (Identity)
  1: Self-Healing Corrections (Phase 3 Core)
  2: Predictive Categorization (Phase 3 Core)
  3: AI Auto-Tagging (Phase 3 Core)
  4: Quality Validation & Scoring
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

# Import the existing Minter and Scorer
try:
    from TITANESS_Signet_Minter import mint_signet
except ImportError:
    # Fallback if execution context slightly differs
    pass

try:
    from mdec_quality_scorer import MDECQualityScorer
except ImportError:
    pass

# Directories mapped in Docker Volumes
STAGING_DIR = "/app/vault/staging"
VAULT_DIR = "/app/vault/platinum_certified"
METADATA_MANIFEST = "/app/vault/mdec_manifest.json"

class ThresherPipeline:
    def __init__(self):
        try:
            self.scorer = MDECQualityScorer()
        except NameError:
            self.scorer = None
            print("[WARN] Scorer module not loaded properly.")
            
        os.makedirs(STAGING_DIR, exist_ok=True)
        os.makedirs(VAULT_DIR, exist_ok=True)

    def phase_zero_mint(self, file_path, creator_name):
        """Phase 0: Establish immutable Nano-NFT / Signet Identity"""
        print(f"[PHASE 0] Minting Signet for: {file_path}")
        
        # We pass the required metadata for the Signet. 
        # Inside the appliance, we pull this from the file or standard pipeline context.
        # Fallback to a placeholder dict if mint_signet is pure CLI in some branches.
        try:
            signet_data = mint_signet(
                name=creator_name, 
                dob="1962-07-14", 
                epoch=datetime.utcnow().strftime("%Y"), 
                vocation="Engineered System", 
                origin="MdEC Thresher"
            )
            # Normalize to dictionary if string returned
            if isinstance(signet_data, str):
                return {"m_id": f"urn:mdec:{os.urandom(16).hex()}", "signet_string": signet_data}
            return signet_data
        except Exception as e:
            print(f"[WARN] Using default identity generation due to: {e}")
            import uuid
            mock_id = str(uuid.uuid4())
            return {
                "m_id": f"urn:mdec:{mock_id}", 
                "signet_string": f"{creator_name}-07-14-1962-Engineered-System-Thresher"
            }

    def phase_one_to_three_automation(self, manifest_path):
        """Phases 1-3: Trigger the existing PowerShell Phase 3 Orchestrator"""
        print(f"[PHASE 1-3] Engaging PowerShell AI Automation Pipeline...")
        
        ps_module = os.path.join(os.path.dirname(__file__), "MDEC_Phase3_Orchestrator.psm1")
        
        # We invoke PowerShell to import your module and run your exact Phase 3 function.
        pwsh_command = f"Import-Module '{ps_module}'; Start-MDECAIAutomation -MetadataPath '{manifest_path}' -FullCycle"
        
        result = subprocess.run([
            "pwsh", "-ExecutionPolicy", "Bypass", "-Command", pwsh_command
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[ERROR] PS Core Pipeline Failed: {result.stderr}")
            return False
        
        print(f"[SUCCESS] Core Phases Complete:\n{result.stdout}")
        return True

    def phase_four_validation(self, file_path):
        """Phase 4: Run the Quality Scorer"""
        print(f"[PHASE 4] Executing Final Validation & Quality Scoring")
        if self.scorer:
            score_report = self.scorer.score_file(file_path)
            return score_report
        else:
            return {'overall_score': 0, 'error': 'Scorer not initialized'}

    def phase_five_smart_organization(self, file_path, category):
        """Phase 5: Run the Smart Data Organizer Powerhouse"""
        print(f"[PHASE 5] Engaging Smart Data Organizer for Vault placement...")
        
        try:
            # We call the python script directly to organize the single file
            # Or we utilize its internal mapping logic
            # For this appliance flow, we replicate its core MDEC_STRUCTURE routing
            import smart_data_organizer_powerhouse as sdop
            
            # Use the SDOP logic to determine the correct subfolder
            ext = os.path.splitext(file_path)[1].lower()
            target_folder = "09_Uncategorized"
            for folder, metadata in sdop.MDEC_STRUCTURE.items():
                if ext in metadata['extensions']:
                    target_folder = folder
                    break
            
            final_vault_path = os.path.join(VAULT_DIR, target_folder)
            os.makedirs(final_vault_path, exist_ok=True)
            
            filename = os.path.basename(file_path)
            dest_path = os.path.join(final_vault_path, filename)
            
            import shutil
            shutil.move(file_path, dest_path)
            print(f"[VAULT] Sealed via Smart Organizer at {dest_path}")
            return dest_path
            
        except Exception as e:
            print(f"[ERROR] Smart Organizer Failed: {e}")
            # Fallback to base vault
            filename = os.path.basename(file_path)
            dest_path = os.path.join(VAULT_DIR, filename)
            import shutil
            shutil.move(file_path, dest_path)
            print(f"[VAULT] Sealed (Fallback mapping) at {dest_path}")
            return dest_path

    def process_file(self, file_path):
        """Main Loop: Process a single file through the pipeline."""
        filename = os.path.basename(file_path)
        print(f"\n{'='*50}\n[THRESHER] Ingesting: {filename}\n{'='*50}")

        # 0. Minting Identity
        identity = self.phase_zero_mint(file_path, "Auto-Ingest-Daemon")

        # Create a temporary JSON payload wrapper mapping your mdec_manifest.json standard
        payload = {
            "m-id": identity.get('m_id', 'unknown'),
            "file_name": filename,
            "signet_creator": identity.get('signet_string', 'unknown'),
            "status": "PROCESSING",
            "file_path": file_path,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        temp_manifest = f"/tmp/manifest_{identity.get('m_id', 'xxx')}.json"
        with open(temp_manifest, 'w') as f:
            json.dump([payload], f, indent=4)

        # 1-3. PowerShell Auto-Tagging, Predictive Categorization & Healing
        success = self.phase_one_to_three_automation(temp_manifest)
        
        if not success:
            print(f"[FAIL] {filename} rejected during Phase 1-3 Engine processing.")
            return

        # 4. Grading
        final_score = self.phase_four_validation(temp_manifest)
        overall = final_score.get('overall_score', 0)

        print(f"[RESULT] Final MdEC Quality Score: {overall}/100")

        # 5. Archival Logic & Smart Organization
        if overall >= 90:
            print(f"[VAULT] Platinum Certified. Initiating Phase 5.")
            category = "Unknown" # Ideally pulled from the payload
            self.phase_five_smart_organization(file_path, category)
        else:
            print(f"[REJECTED] Score ({overall}) too low. File remains in Staging for manual review/deep healing.")
            # Rename the file so the loop doesn't infinitely re-process the exact same failure
            try:
                os.rename(file_path, file_path + ".rejected")
            except Exception as e:
                pass



if __name__ == "__main__":
    thresher = ThresherPipeline()
    print("================================================")
    print("   MDEC THRESHER ORCHESTRATOR NODE ONLINE")
    print("================================================")
    print(f"Watching for drops in: {STAGING_DIR}", flush=True)
    
    # Polling loop representing the container's heartbeat
    while True:
        try:
            for file in os.listdir(STAGING_DIR):
                # Only process files that haven't been marked as rejected
                if not file.endswith('.rejected'):
                    full_path = os.path.join(STAGING_DIR, file)
                    if os.path.isfile(full_path):
                        thresher.process_file(full_path)
            
            # Check the directory every 5 minutes (300 seconds) vs rapid polling
            time.sleep(300)
        except KeyboardInterrupt:
            print("\nThresher Node shutting down.")
            sys.exit(0)
