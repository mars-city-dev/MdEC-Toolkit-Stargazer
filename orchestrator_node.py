#!/usr/bin/env python3
"""
TITANESS INGESTION ENGINE (TIE) ORCHESTRATOR
--------------------------------------------
Role: Core lifecycle engine for the Titaness Sentient Systems OS.
5-Phase Bio-Digital Lifecycle:
  1: Ingestion (Sensory Intake) - smart_data_organizer_powerhouse.py
  2: Taxonomy (Perception / Ontology) - MDEC_Tagging_Taxonomy.psm1
  3: Orchestration (Motor Control) - MDEC_Phase3_Orchestrator.psm1
  4: Validation (Critical Reflection) - mdec_auto_validator.py
  5: Indexing (Hippocampus) - Titaness_Data_Hyper_Indexer.py
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime

# Local Windows Paths (Native Deployment)
STAGING_DIR = "E:/MDEC_VAULT_PROOF_CONCEPT"
# Ensure we use a local vault dir within the project or a specified path
VAULT_DIR = "D:/Projects/MdEC-Toolkit-Stargazer/vault/platinum_certified"
METADATA_MANIFEST = "D:/Projects/MdEC-Toolkit-Stargazer/vault/mdec_manifest.json"

class IngestionEnginePipeline:
    def __init__(self):
        os.makedirs(STAGING_DIR, exist_ok=True)
        os.makedirs(VAULT_DIR, exist_ok=True)

    def run_script(self, command, phase_name):
        """Helper to run shell/python/pwsh scripts and log output"""
        print(f"[{phase_name}] Executing...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"[{phase_name}] SUCCESS.")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[{phase_name}] FAILED: {e.stderr}")
            return False, e.stderr

    def phase_1_ingestion(self, file_path):
        """Phase 1: Sensory Intake & Cryptographic Sorting"""
        # Calling smart_data_organizer_powerhouse.py
        cmd = ["python", "smart_data_organizer_powerhouse.py", "--ingest", file_path]
        return self.run_script(cmd, "PHASE 1: INGESTION")

    def phase_2_taxonomy(self, manifest_path):
        """Phase 2: Perception / Ontology"""
        # Calling MDEC_Tagging_Taxonomy.psm1
        pwsh_cmd = f"Import-Module './MDEC_Tagging_Taxonomy.psm1'; Start-MDECTaxonomy -Path '{manifest_path}'"
        cmd = ["pwsh", "-ExecutionPolicy", "Bypass", "-Command", pwsh_cmd]
        return self.run_script(cmd, "PHASE 2: TAXONOMY")

    def phase_3_orchestration(self, manifest_path):
        """Phase 3: Motor Control / Healing"""
        # Calling MDEC_Phase3_Orchestrator.psm1
        pwsh_cmd = f"Import-Module './MDEC_Phase3_Orchestrator.psm1'; Start-MDECPhase3 -Path '{manifest_path}'"
        cmd = ["pwsh", "-ExecutionPolicy", "Bypass", "-Command", pwsh_cmd]
        return self.run_script(cmd, "PHASE 3: ORCHESTRATION")

    def phase_4_validation(self, manifest_path):
        """Phase 4: Critical Reflection / Quality Gate"""
        # Calling mdec_auto_validator.py
        cmd = ["python", "mdec_auto_validator.py", "--validate", manifest_path]
        return self.run_script(cmd, "PHASE 4: VALIDATION")

    def phase_5_indexing(self, manifest_path):
        """Phase 5: Hippocampus / Long-term Memory"""
        # Calling Titaness_Data_Hyper_Indexer.py
        cmd = ["python", "Titaness_Data_Hyper_Indexer.py", "--index", manifest_path]
        return self.run_script(cmd, "PHASE 5: INDEXING")

    def process_file(self, file_path):
        """Main Loop: Process a single file through the 5-phase Bio-Digital pipeline."""
        filename = os.path.basename(file_path)
        print(f"\n{'='*60}\n[TIE] INGESTING PAYLOAD: {filename}\n{'='*60}")

        # Temporary manifest for handoffs between phases
        manifest_path = f"/tmp/manifest_{int(time.time())}.json"
        
        # Phase 1
        success, _ = self.phase_1_ingestion(file_path)
        if not success: return False

        # Phase 2
        success, _ = self.phase_2_taxonomy(manifest_path)
        if not success: return False

        # Phase 3
        success, _ = self.phase_3_orchestration(manifest_path)
        if not success: return False

        # Phase 4
        success, _ = self.phase_4_validation(manifest_path)
        if not success: return False

        # Phase 5
        success, _ = self.phase_5_indexing(manifest_path)
        if not success: return False

        print(f"\n[SUCCESS] Payload {filename} successfully moved to Post-Chaos Long-term Memory.")
        return True

if __name__ == "__main__":
    tie = IngestionEnginePipeline()
    print("================================================================")
    print("   TITANESS INGESTION ENGINE (TIE) CORE ONLINE")
    print("================================================================")
    print(f"Watching for sensory input in: {STAGING_DIR}", flush=True)
    
    while True:
        try:
            for file in os.listdir(STAGING_DIR):
                if not file.endswith('.rejected'):
                    full_path = os.path.join(STAGING_DIR, file)
                    if os.path.isfile(full_path):
                        tie.process_file(full_path)
            
            time.sleep(300)
        except KeyboardInterrupt:
            print("\nTIE Node shutting down.")
            sys.exit(0)
