#!/usr/bin/env python3
"""
TITANESS Signet Minter v1.0
===========================
The designated tool for generating compliant M-IDs and SIGNET Strings 
according to the MDEC Codex Article X.

This tool ensures Veracity and Standardization in metadata creation.
No more manual typing errors. The Machine (TITANESS) mints the Memory (Mnemosyne-ID).

Usage:
    python TITANESS_Signet_Minter.py --name "Chris Olds" --dob "1962-07-14" --epoch "20xx" --vocation "engineer,musician,author,poet" --origin "USA"

Optional Interactive Mode:
    python TITANESS_Signet_Minter.py
"""

import argparse
import uuid
import datetime
import re
import sys
import os
import json

def sanitize_input(text):
    """Sanitizes input to be safe for ID generation (alphanumeric and dashes only)."""
    # Replace commas with spaces first to separate list items
    text = text.replace(',', ' ')
    # Replace spaces with dashes, remove special chars
    sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    sanitized = re.sub(r'\s+', '-', sanitized)
    return sanitized.strip('-')

def format_dob(dob_str):
    """Ensures DOB is in MM-DD-YYYY format."""
    try:
        # Try parsing various formats
        for fmt in ('%Y-%m-%d', '%m-%d-%Y', '%m/%d/%Y', '%Y/%m/%d'):
            try:
                dt = datetime.datetime.strptime(dob_str, fmt)
                return dt.strftime('%m-%d-%Y')
            except ValueError:
                continue
        raise ValueError("Invalid Date Format")
    except ValueError:
        print("Error: detailed DOB required (YYYY-MM-DD or MM-DD-YYYY)")
        sys.exit(1)

def mint_signet(name, dob, epoch, vocation, origin):
    """Constructs the SIGNET string."""
    s_name = sanitize_input(name)
    s_dob = format_dob(dob)
    s_epoch = sanitize_input(epoch)
    
    # Vocations can be comma separated, need to be dash separated in ID
    s_vocation = sanitize_input(vocation).replace(',', '-')
    # Capitalize each vocation part for readability
    s_vocation = '-'.join([v.capitalize() for v in s_vocation.split('-')])
    
    s_origin = sanitize_input(origin).upper()
    
    # Signet Format: Name-DOB-Epoch-Vocations-Origin
    signet = f"{s_name}-{s_dob}-{s_epoch}-{s_vocation}-{s_origin}"
    return signet

def mint_mid(signet):
    """Generates the Immutable M-ID (UUID v5 based on Signet namespace)."""
    # We use a dedicated MDEC namespace UUID for stability
    # MDEC_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "mdec-consortium.org")
    MDEC_NAMESPACE = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8') # Using DNS namespace for now as base
    
    # Generate deterministic UUID based on the Signet string
    # This ensures that if you enter the same details, you get the same ID (Idempotency)
    # OR should it be random?
    # Codex says "Globally unique, immutable identifier assigned to every DISTINCT data asset."
    # If this is for an Asset Creator, deterministic is good (The Creator ID doesn't change).
    # If this is for a generic Asset, we need a unique salt (timestamp or random).
    
    # Assuming this tool mints Section 10.1.2 "Asset-Creator Tag" Signets principally.
    mid = uuid.uuid5(MDEC_NAMESPACE, signet)
    return str(mid)

def main():
    parser = argparse.ArgumentParser(description="TITANESS Signet Minter - Generate MDEC Compliant Identifiers")
    parser.add_argument("--name", help="Creator Name (e.g. 'Christopher Olds')")
    parser.add_argument("--dob", help="Date of Birth (YYYY-MM-DD)")
    parser.add_argument("--epoch", help="Active Epoch (e.g. '20xx')")
    parser.add_argument("--vocation", help="Vocations (comma separated, e.g. 'engineer,poet')")
    parser.add_argument("--origin", help="Continent/Country of Origin (e.g. 'USA')")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive wizard mode")

    args = parser.parse_args()

    if args.interactive or not (args.name and args.dob and args.epoch and args.vocation and args.origin):
        print("\n🏛️  TITANESS SIGNET MINTER SEQUENCE INITIATED 🏛️")
        print("------------------------------------------------")
        name = input("Enter Creator Name: ")
        dob = input("Enter DOB (YYYY-MM-DD): ")
        epoch = input("Enter Epoch (e.g., 20xx): ")
        vocation = input("Enter Vocations (comma separated): ")
        origin = input("Enter Origin (Country/Continent): ")
    else:
        name = args.name
        dob = args.dob
        epoch = args.epoch
        vocation = args.vocation
        origin = args.origin

    try:
        signet_string = mint_signet(name, dob, epoch, vocation, origin)
        m_id = mint_mid(signet_string)

        print("\n✨ MNEMOSYNE ENGRAM GENERATED ✨")
        print("-----------------------------")
        print(f"🆔 M-ID (Immutable Key): {m_id}")
        print(f"🏷️  SIGNET (Human Readable): {signet_string}")
        print("-----------------------------\n")
        
        # TRANSCODING EVENT: BINDING TO THE GOLDEN LEDGER
        # The M-ID is mathematically derived from the Signet (One-Way).
        # To "remember" what the M-ID means, we must inscribe it in the Registry.
        
        # Spline of Truth: The Single Source of Truth (SSOT)
        registry_file = "TITANESS_CENTRAL_LEDGER_SSOT.json"
        
        # Load existing ledger or create new
        import json
        if not os.path.exists(registry_file):
            ledger = {"_meta": "TITANESS IMMUTABLE LEDGER v1", "entries": {}}
        else:
            try:
                with open(registry_file, 'r') as f:
                    ledger = json.load(f)
            except:
                 ledger = {"_meta": "TITANESS IMMUTABLE LEDGER v1", "entries": {}}

        # Check for existence
        if m_id in ledger["entries"]:
            print(f"⚠️  MEMORY EXISTS: This M-ID is already registered to: {ledger['entries'][m_id]['signet']}")
        else:
            # THE BINDING
            payload = {
                "signet": signet_string,
                "timestamp": datetime.datetime.now().isoformat(),
                "components": {
                    "name": name,
                    "dob": dob,
                    "epoch": epoch,
                    "vocation": vocation,
                    "origin": origin
                }
            }
            ledger["entries"][m_id] = payload
            
            with open(registry_file, 'w') as f:
                json.dump(ledger, f, indent=4)
            print(f"✅ TRANSCODED: M-ID has been permanently bound to the Ledger.")
            print(f"📂 LOCATION: {os.path.abspath(registry_file)}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
