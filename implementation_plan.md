# Implementation Plan: Unified MDEC 12-Step Toolchain & UI Integration

This plan codifies the diverse MDEC toolchains (5 phases, 8 tiers, 12/15 steps) into a single, authoritative **12-Step Neural Protocol** and wires it to a "Glass Box" UI for granular control.

## Proposed Changes

### 1. Process Standardization
- **Nail Down the "Steps":** Formally define the 12 steps in [TITANESS_Hypervisor.py](file:///d:/Projects/Titaness-Metadata-Faktory/services/TITANESS_Hypervisor.py) as the canonical implementation, mapping them to the 5 High-Level Phases and 8-Tier Storage.

| Phase | Step | Tool / Action | Tier |
| :--- | :--- | :--- | :--- |
| **1: Intake** | 1. Ingest | [smart_data_organizer_powerhouse.py](file:///d:/Projects/MdEC-Toolkit-Stargazer/smart_data_organizer_powerhouse.py) | 01_Ingest |
| | 2. Hash | `hashlib` (SHA256) | 02_Validate |
| **2: Identity** | 3. Inspect | [TITANESS_MdEC_Inspector.py](file:///d:/Projects/MDEC-Consortium/tools/Core/TITANESS_MdEC_Inspector.py) | 02_Validate |
| | 4. Mint | [TITANESS_Signet_Minter.py](file:///d:/Projects/MdEC-Toolkit-Stargazer/TITANESS_Signet_Minter.py) | 02_Validate |
| | 5. Quarantine | `check_hazardous.py` (New) | 02_Quarantine |
| | 6. Deep Scan | `content_scanner.py` (New) | 02_Validate |
| **3: Structure**| 7. Organize | [smart_data_organizer_powerhouse.py](file:///d:/Projects/MdEC-Toolkit-Stargazer/smart_data_organizer_powerhouse.py) | 03_Normalize |
| | 8. Vault | `vault_transfer.py` (New) | 07_Vault |
| | 9. Normalize | `athena_transform.py` (Call [run_athena_export.ps1](file:///d:/Projects/Mars-City-Infrastructure/tools/athena/run_athena_export.ps1)) | 03_Normalize |
| **4: Integrity**| 10. Score | [mdec_quality_scorer.py](file:///d:/Projects/Mars-City-Stargazer/mdec_quality_scorer.py) | 04_Enrich |
| | 11. Validate | [mdec_auto_validator.py](file:///d:/Projects/Mars-City-Stargazer/mdec_auto_validator.py) | 04_Enrich |
| **5: Ledger** | 12. Ledger | `TITANESS_Bridge_Ingest_to_Ledger.py` | 06_Canonical |

### 2. Backend Enhancements [EXECUTION]
- **[MODIFY] [TITANESS_Hypervisor.py](file:///d:/Projects/Titaness-Metadata-Faktory/services/TITANESS_Hypervisor.py):**
    - Replace simulated strings with calls to real logic or shell scripts.
    - Add a `--step-by-step` flag to wait for user acknowledgment between steps (via API signal).
- **[MODIFY] [pipeline_server.py](file:///d:/Projects/Titaness-Metadata-Faktory/pipeline_server.py):**
    - Add an endpoint `POST /api/v1/jobs/{job_id}/acknowledge` to allow the user to advance the pipeline when in step-by-step mode.

### 3. UI/UX Convergence [EXECUTION]
- **[MODIFY] [index.html](file:///d:/Projects/Titaness-Metadata-Faktory/index.html):**
    - Implement a "Neural Pipeline Stepper" component showing all 12 steps.
    - Add a "Manual Override / Step-by-Step" toggle.
    - Improve the "Swarm Console" to show granular progress bars for each step.

## Verification Plan

### Automated Tests
1. **Hypervisor Smoke Test:**
   ```powershell
   python d:\Projects\Titaness-Metadata-Faktory\services\TITANESS_Hypervisor.py --target d:\test_file.txt --mode dry-run
   ```
   Verify that all 12 steps report successfully in the console.

2. **API Integration Test:**
   ```powershell
   # Start the pipeline server
   python d:\Projects\Titaness-Metadata-Faktory\pipeline_server.py
   # Trigger a job
   curl -X POST http://localhost:8000/api/v1/jobs -H "Content-Type: application/json" -d '{"target_path": "d:/test_file.txt"}'
   ```
   Verify the job is created and stages are updated.

### Manual Verification
1. Open [index.html](file:///d:/Projects/MDEC-Consortium/index.html) in the browser.
2. Toggle "Manual Override" ON.
3. Drag a file into the Thalamus Injection zone.
4. Verify the UI stops after Step 1 and waits for an "Advance" command.
5. Click "Advance" and observe the transition to Step 2 with live log updates.
6. Complete all 12 steps and verify the final "MDEC GOLD" status.
