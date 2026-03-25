import os
import shutil
import time
import logging
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import sys

# VNN Organ Integration
try:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if PROJECT_ROOT not in sys.path: sys.path.append(PROJECT_ROOT)
    from bio_digital.hippocampus import log_signal, NeuralSignalType, SeverityLevel
    from bio_digital.endocrine_system import endocrine_system, Hormone
    VNN_ORGANS_AVAILABLE = True
except ImportError:
    VNN_ORGANS_AVAILABLE = False
    log_signal = None

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [SMART-DOP] - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("smart_dop_activity.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Ensure stdout uses UTF-8 on Windows so emoji and unicode prints don't fail
try:
    if sys.stdout is not None:
        try:
            # Python 3.7+ has reconfigure
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            import io
            try:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            except Exception:
                # fallback: set PYTHONIOENCODING if possible (best-effort)
                os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
except Exception:
    pass

# --- MDEC CODEX DEFINITION ---
MDEC_STRUCTURE = {
    "01_Documents": {
        "extensions": {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.md', '.epub', '.xlsx', '.xls', '.csv', '.pptx', '.ppt', '.key', '.pages', '.numbers'},
        "desc": "Textual information, reports, books, and presentations."
    },
    "02_Media": {
        "extensions": {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.mp4', '.mov', '.avi', '.mkv', '.mp3', '.wav', '.flac', '.aiff', '.aac', '.ogg', '.webm', '.raw', '.nef', '.cr2', '.dng'},
        "desc": "Visual and Audio content."
    },
    "03_Data": {
        "extensions": {'.json', '.xml', '.sql', '.db', '.sqlite', '.parquet', '.yaml', '.yml', '.ini', '.cfg', '.dat', '.pkl'},
        "desc": "Raw data, databases, and configuration files."
    },
    "04_Code": {
        "extensions": {'.py', '.js', '.ts', '.html', '.css', '.java', '.c', '.cpp', '.cs', '.go', '.rs', '.php', '.rb', '.sh', '.ps1', '.bat', '.cmd', '.h', '.hpp'},
        "desc": "Source code and scripts."
    },
    "05_Archives": {
        "extensions": {'.zip', '.rar', '.7z', '.tar', '.gz', '.iso', '.dmg', '.pkg'},
        "desc": "Compressed files and disk images."
    },
    "06_Assets": {
        "extensions": {'.psd', '.ai', '.xd', '.fig', '.blend', '.obj', '.fbx', '.stl', '.unitypackage', '.prefab', '.mat', '.meta'},
        "desc": "Creative assets, 3D models, and design files."
    },
    "07_Communications": {
        "extensions": {'.msg', '.eml', '.vcf', '.ics'},
        "desc": "Emails, contacts, and calendar events."
    },
    "08_References": {
        "extensions": {'_shortcuts', '.lnk', '.url', '.webloc'},
        "desc": "Links, shortcuts, and citation markers."
    },
    "09_Uncategorized": {
        "extensions": {'_mdec_catchall'},
        "desc": "Files that do not fit into the standard 8 Universal Categories."
    },
    "99_System": {
        "extensions": {'.dll', '.sys', '.ini', '.db', '.dat', '.tmp', '.log', '.bak', '.swp', '.ds_store', 'thumbs.db'},
        "desc": "Operating system files, logs, and temporary artifacts (Do Not Touch)."
    }
}

class SmartDataOrganizerPowerhouse:
    def __init__(self, source_dir, dest_dir, dry_run=True, target_category=None, force_rescan=False):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.dry_run = dry_run
        self.target_category = target_category
        self.force_rescan = force_rescan

        # Metadata and tracking
        self.metadata_dir = self.dest_dir / ".metadata"
        # Override metadata dir if MDEC_VAULT_ROOT is set
        vault_root = os.getenv("MDEC_VAULT_ROOT")
        if vault_root:
            self.metadata_dir = Path(vault_root) / ".metadata"
            
        self.metadata_file = self.metadata_dir / "smart_metadata.json"
        self.processed_files = self.load_metadata()

        self.metrics = Counter()
        self.new_files = []
        self.updated_files = []
        self.unchanged_files = []
        self.start_time = time.time()

    def calculate_file_hash(self, file_path, chunk_size=8192):
        """Calculate SHA256 hash of file for change detection"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, IOError):
            return None

    def load_metadata(self):
        """Load previously processed files metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logging.warning("Could not load metadata file, starting fresh")
                return {}
        return {}

    def save_metadata(self):
        """Save processed files metadata"""
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_files, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to save metadata: {e}")

    def get_file_info(self, file_path):
        """Get file modification time and size"""
        try:
            stat = file_path.stat()
            return {
                'mtime': stat.st_mtime,
                'size': stat.st_size,
                'hash': self.calculate_file_hash(file_path) if not self.force_rescan else None
            }
        except OSError:
            return None

    def is_file_changed(self, src_path, rel_path_str):
        """Check if file has changed since last processing"""
        if rel_path_str not in self.processed_files:
            return True, "new"

        old_info = self.processed_files[rel_path_str]
        new_info = self.get_file_info(src_path)

        if not new_info:
            return False, "error"

        # Check if file size changed
        if new_info['size'] != old_info.get('size', 0):
            return True, "size_changed"

        # Check if modification time changed
        if abs(new_info['mtime'] - old_info.get('mtime', 0)) > 1:  # 1 second tolerance
            return True, "mtime_changed"

        # If we have hashes, compare them
        if new_info.get('hash') and old_info.get('hash'):
            if new_info['hash'] != old_info['hash']:
                return True, "hash_changed"

        return False, "unchanged"

    def identify_category(self, file_path):
        ext = file_path.suffix.lower()
        if not ext:
            return "99_Unclassified"

        for category, rules in MDEC_STRUCTURE.items():
            if ext in rules['extensions']:
                return category
        return "99_Unclassified"

    def smart_scan(self):
        """Smart scan that only processes changed/new files"""
        print(f"\n--- [ SMART SCANNING NEURAL PATHWAYS in {self.source_dir} ] ---")
        count = 0
        total_scanned = 0
        dest_abs = self.dest_dir.resolve()

        for root, dirs, files in os.walk(self.source_dir):
            root_path = Path(root).resolve()
            if dest_abs in root_path.parents or root_path == dest_abs:
                dirs[:] = []
                continue

            for file in files:
                if file == "smart_dop_activity.log" or file == "data_organizer_powerhouse.py":
                    continue

                src_path = Path(root) / file
                rel_path = src_path.relative_to(self.source_dir)
                rel_path_str = str(rel_path)

                total_scanned += 1

                # Check if file needs processing
                needs_processing, reason = self.is_file_changed(src_path, rel_path_str)

                if not needs_processing and not self.force_rescan:
                    self.unchanged_files.append(rel_path_str)
                    continue

                category = self.identify_category(src_path)
                dest_path = self.dest_dir / category / rel_path

                file_info = self.get_file_info(src_path)
                if not file_info:
                    continue

                file_data = {
                    "src": str(src_path),
                    "dest": str(dest_path),
                    "cat": category,
                    "size": file_info['size'],
                    "rel_path": rel_path_str,
                    "change_reason": reason,
                    "mtime": file_info['mtime'],
                    "hash": file_info.get('hash')
                }

                if reason == "new":
                    self.new_files.append(file_data)
                else:
                    self.updated_files.append(file_data)

                # --- AUTONOMOUS ADAPTATION: STRESS VETO ---
                if VNN_ORGANS_AVAILABLE:
                    cortisol = endocrine_system.get_hormone_levels().get(Hormone.CORTISOL, 0.0)
                    if cortisol > 0.7 and category in ["02_Media", "06_Assets"]:
                        logging.warning(f"🚫 [ADAPTIVE VETO] High Stress (Cortisol: {cortisol:.2f}). Suppressing non-essential move of {file}")
                        if log_signal:
                            log_signal(
                                NeuralSignalType.ETHICAL_VETO, 
                                "SMART-DOP", 
                                f"Inhibited Media move to conserve homeostasis",
                                SeverityLevel.INFO,
                                {"file": file, "hormone": "CORTISOL"}
                            )
                        continue

                self.metrics[category] += 1
                count += 1
                
                # --- RESONANCE LOGGING ---
                if VNN_ORGANS_AVAILABLE and count % 50 == 0:
                    resonance_type = "Cognitive Growth" if category in ["01_Documents", "04_Code"] else "Homeostasis"
                    log_signal(
                        NeuralSignalType.INFO,
                        "SMART-DOP",
                        f"Processed {count} files. Resonance: {resonance_type}",
                        SeverityLevel.INFO
                    )

                if total_scanned % 1000 == 0:
                    print(f" scanned {total_scanned} files, {count} need processing...", end='\r')

        print(f"✅ Smart Scan Complete. Found {len(self.new_files)} new, {len(self.updated_files)} updated, {len(self.unchanged_files)} unchanged files.")

    def duplicate_check(self, dest_path):
        """Handle filename collisions by appending timestamp"""
        if dest_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return dest_path.with_name(f"{dest_path.stem}_{timestamp}{dest_path.suffix}")
        return dest_path

    def execute_smart_ingest(self, move_mode=False):
        """Execute smart ingestion - only process changed files"""
        mode_str = "MOVE" if move_mode else "COPY"

        if self.dry_run:
            print(f"\n--- [ SMART DRY RUN: SIMULATION MODE ({mode_str}) ] ---")
        else:
            print(f"\n--- [ SMART EXECUTING MDEC REORGANIZATION ({mode_str}) ] ---")

        # Create Category Folders
        for cat in MDEC_STRUCTURE.keys():
            (self.dest_dir / cat).mkdir(parents=True, exist_ok=True)
        (self.dest_dir / "99_Unclassified").mkdir(parents=True, exist_ok=True)

        total_to_process = len(self.new_files) + len(self.updated_files)
        processed = 0
        bytes_transferred = 0

        # Process new files
        for item in self.new_files + self.updated_files:
            src = Path(item['src'])
            target = Path(item['dest'])
            cat = item['cat']
            rel_path_str = item['rel_path']

            if self.target_category and cat != self.target_category:
                continue

            processed += 1
            if not self.dry_run:
                try:
                    target = self.duplicate_check(target)
                    target.parent.mkdir(parents=True, exist_ok=True)

                    if str(target).startswith("gs://"):
                        # Cloud Storage Stub
                        logging.info(f"☁️ [CLOUD STUB] Uploading {src.name} to {target}")
                        # In real implementation: storage.Client().bucket(b).blob(p).upload_from_filename(src)
                        pass
                    elif move_mode:
                        shutil.move(src, target)
                    else:
                        shutil.copy2(src, target)

                    bytes_transferred += item['size']

                    # Update metadata
                    self.processed_files[rel_path_str] = {
                        'size': item['size'],
                        'mtime': item['mtime'],
                        'hash': item.get('hash'),
                        'category': cat,
                        'dest_path': str(target),
                        'last_processed': datetime.now().isoformat()
                    }

                    if processed % 50 == 0:
                        print(f"Processing: {int((processed/total_to_process)*100)}% - {cat} - {src.name[:30]}...        ", end='\r')

                except Exception as e:
                    logging.error(f"Failed to {mode_str} {src}: {e}")
            else:
                # Dry run - just update metadata structure
                self.processed_files[rel_path_str] = {
                    'size': item['size'],
                    'mtime': item['mtime'],
                    'hash': item.get('hash'),
                    'category': cat,
                    'dest_path': str(target),
                    'last_processed': datetime.now().isoformat()
                }

        # Save metadata
        if not self.dry_run:
            self.save_metadata()

        duration = time.time() - self.start_time
        self.smart_report(total_to_process, bytes_transferred, duration, mode_str)

    def smart_report(self, total_files, total_bytes, duration, mode_str):
        """Generate smart processing report"""
        print("\n\n" + "="*70)
        print(f"🧠 SMART DATA ORGANIZER POWERHOUSE (SMART-DOP) REPORT 🧠")
        print("="*70)
        print(f"Source:         {self.source_dir}")
        print(f"Destination:    {self.dest_dir}")
        print(f"Execution:      {'DRY RUN' if self.dry_run else 'LIVE ' + mode_str}")
        print(f"Time Taken:     {duration:.2f} seconds")
        print(f"Files Processed: {total_files}")
        print(f"New Files:      {len(self.new_files)}")
        print(f"Updated Files:  {len(self.updated_files)}")
        print(f"Unchanged:      {len(self.unchanged_files)}")

        if not self.dry_run:
            print(f"Data Moved:     {total_bytes / (1024*1024):.2f} MB")

        print("-" * 70)
        print("📂 FILES BY MDEC_CATEGORY:")
        print("-" * 70)
        for cat, curr_count in sorted(self.metrics.items()):
            icon = "📄"
            if "Media" in cat: icon = "🖼️"
            if "Code" in cat: icon = "💻"
            if "Data" in cat: icon = "📊"
            print(f"{icon} {cat:<20}: {curr_count}")

        print("="*70)
        print("🎯 Smart Processing Complete. Only changed files processed!")
        print("💾 Metadata saved for future incremental updates.")

def main():
    parser = argparse.ArgumentParser(description="Smart MDEC Data Organizer Powerhouse")
    parser.add_argument("--source", default=os.getenv("MDEC_SOURCE_PATH"), help="Source directory to scan (defaults to MDEC_SOURCE_PATH env var)")
    parser.add_argument("--dest", default=os.getenv("MDEC_DEST_PATH"), help="Destination directory for MDEC structure (defaults to MDEC_DEST_PATH env var)")
    parser.add_argument("--live", action="store_true", help="DISABLE Dry Run and perform actual copy/move")
    parser.add_argument("--move", action="store_true", help="Move files instead of Copying (Saves space)")
    parser.add_argument("--category", help="Only process this category (e.g., 01_Documents)")
    parser.add_argument("--force-rescan", action="store_true", help="Force rescan of all files (ignore metadata)")
    parser.add_argument("--status", action="store_true", help="Show current vault status")

    args = parser.parse_args()

    if args.status:
        # Show vault status
        dest_dir = Path(args.dest)
        metadata_file = dest_dir / ".metadata" / "smart_metadata.json"

        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                total_files = len(metadata)
                categories = Counter()
                total_size = 0

                for file_info in metadata.values():
                    categories[file_info.get('category', 'unknown')] += 1
                    total_size += file_info.get('size', 0)

                print(f"\n📊 MDEC VAULT STATUS: {dest_dir}")
                print(f"Total Files Tracked: {total_files}")
                print(f"Total Size: {total_size / (1024**3):.2f} GB")
                print("\n📂 Files by Category:")
                for cat, count in sorted(categories.items()):
                    print(f"  {cat}: {count} files")

            except Exception as e:
                print(f"Error reading metadata: {e}")
        else:
            print("No metadata found. Run with --live to initialize tracking.")

        return

    # Require source for non-status operations
    if not args.source:
        print("❌ Error: --source is required (or set MDEC_SOURCE_PATH environment variable)")
        sys.exit(1)
    
    if not args.dest:
        print("❌ Error: --dest is required (or set MDEC_DEST_PATH environment variable)")
        sys.exit(1)

    print("🧠 SMART DATA ORGANIZER POWERHOUSE - INTELLIGENT MODE")
    print("=" * 60)

    smart_dop = SmartDataOrganizerPowerhouse(
        args.source,
        args.dest,
        dry_run=not args.live,
        target_category=args.category,
        force_rescan=args.force_rescan
    )

    smart_dop.smart_scan()
    smart_dop.execute_smart_ingest(move_mode=args.move)

if __name__ == "__main__":
    main()