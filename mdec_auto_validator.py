#!/usr/bin/env python3
"""
MDEC Auto-Validator
Automatically validates metadata against MDEC standards and FIXES issues in real-time

What it does:
- Scans files/directories for metadata
- Detects violations of MDEC standards
- AUTOMATICALLY CORRECTS common issues
- Generates validation reports
- Can run in watch mode for continuous validation

Usage:
    python mdec_auto_validator.py <path> --validate     # Check only
    python mdec_auto_validator.py <path> --fix          # Fix issues
    python mdec_auto_validator.py <path> --watch        # Continuous monitoring
"""

import json
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import re
import time

class MDECAutoValidator:
    """Validates and auto-fixes metadata against MDEC standards"""
    
    def __init__(self, fix_mode: bool = False):
        self.fix_mode = fix_mode
        self.violations = []
        self.fixes_applied = []
        self.stats = {
            'files_checked': 0,
            'violations_found': 0,
            'fixes_applied': 0,
            'files_fixed': 0
        }
    
    def validate_path(self, path: str) -> Dict[str, Any]:
        """Validate a file or directory"""
        path_obj = Path(path)
        
        if not path_obj.exists():
            return {'error': f'Path not found: {path}'}
        
        if path_obj.is_file():
            self._validate_file(path_obj)
        else:
            # Validate directory recursively
            for file_path in path_obj.rglob('*'):
                if file_path.is_file() and self._should_validate(file_path):
                    self._validate_file(file_path)
        
        return self._generate_report()
    
    def _should_validate(self, file_path: Path) -> bool:
        """Determine if file should be validated"""
        # Validate JSON and Markdown files primarily
        return file_path.suffix.lower() in ['.json', '.md', '.yaml', '.yml']
    
    def _validate_file(self, file_path: Path):
        """Validate a single file"""
        self.stats['files_checked'] += 1
        
        try:
            metadata = self._extract_metadata(file_path)
            violations = self._check_standards(file_path, metadata)
            
            if violations:
                self.stats['violations_found'] += len(violations)
                self.violations.extend(violations)
                
                if self.fix_mode:
                    self._apply_fixes(file_path, metadata, violations)
        
        except Exception as e:
            self.violations.append({
                'file': str(file_path),
                'type': 'ERROR',
                'message': f'Failed to process: {str(e)}',
                'fixable': False
            })
    
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file"""
        metadata = {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_extension': file_path.suffix.lower()
        }
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    metadata.update(data)
        
        elif file_path.suffix.lower() == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        frontmatter = parts[1].strip()
                        for line in frontmatter.split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
        
        return metadata
    
    def _check_standards(self, file_path: Path, metadata: Dict) -> List[Dict]:
        """Check metadata against MDEC standards"""
        violations = []
        
        # Required fields check
        required_fields = ['id', 'created', 'modified', 'category']
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                violations.append({
                    'file': str(file_path),
                    'type': 'MISSING_FIELD',
                    'field': field,
                    'message': f'Required field "{field}" is missing',
                    'fixable': True,
                    'fix_type': 'add_field'
                })
        
        # Date format validation
        date_fields = ['created', 'modified']
        for field in date_fields:
            if field in metadata:
                value = str(metadata[field])
                if not self._is_iso8601(value):
                    violations.append({
                        'file': str(file_path),
                        'type': 'INVALID_DATE_FORMAT',
                        'field': field,
                        'value': value,
                        'message': f'Date "{field}" not in ISO8601 format',
                        'fixable': True,
                        'fix_type': 'fix_date_format'
                    })
        
        # Tags validation
        if 'tags' in metadata:
            if not isinstance(metadata['tags'], (list, tuple)):
                violations.append({
                    'file': str(file_path),
                    'type': 'INVALID_TAGS_FORMAT',
                    'field': 'tags',
                    'value': metadata['tags'],
                    'message': 'Tags should be an array',
                    'fixable': True,
                    'fix_type': 'fix_tags_format'
                })
        
        # Category validation
        if 'category' in metadata:
            cat = str(metadata['category']).lower()
            if cat in ['unknown', 'misc', 'other', 'na', 'n/a', '']:
                violations.append({
                    'file': str(file_path),
                    'type': 'GENERIC_CATEGORY',
                    'field': 'category',
                    'value': metadata['category'],
                    'message': 'Category too generic, needs specific classification',
                    'fixable': False  # Requires human decision
                })
        
        # ID validation
        if 'id' in metadata:
            id_val = str(metadata['id'])
            if len(id_val) < 5:
                violations.append({
                    'file': str(file_path),
                    'type': 'WEAK_ID',
                    'field': 'id',
                    'value': id_val,
                    'message': 'ID too short/simple',
                    'fixable': True,
                    'fix_type': 'generate_id'
                })
        
        return violations
    
    def _apply_fixes(self, file_path: Path, metadata: Dict, violations: List[Dict]):
        """Apply automatic fixes to metadata"""
        fixed = False
        
        # Backup original file
        backup_path = file_path.with_suffix(file_path.suffix + '.mdec_backup')
        shutil.copy2(file_path, backup_path)
        
        for violation in violations:
            if not violation['fixable']:
                continue
            
            fix_type = violation['fix_type']
            
            if fix_type == 'add_field':
                field = violation['field']
                if field == 'id':
                    metadata['id'] = self._generate_id()
                elif field == 'created':
                    metadata['created'] = datetime.utcnow().isoformat() + 'Z'
                elif field == 'modified':
                    metadata['modified'] = datetime.utcnow().isoformat() + 'Z'
                elif field == 'category':
                    metadata['category'] = self._infer_category(file_path)
                fixed = True
                self.fixes_applied.append(f"Added {field} to {file_path.name}")
            
            elif fix_type == 'fix_date_format':
                field = violation['field']
                metadata[field] = self._normalize_date(metadata[field])
                fixed = True
                self.fixes_applied.append(f"Fixed {field} format in {file_path.name}")
            
            elif fix_type == 'fix_tags_format':
                # Convert to array
                tags_val = metadata['tags']
                if isinstance(tags_val, str):
                    metadata['tags'] = [t.strip() for t in tags_val.split(',')]
                fixed = True
                self.fixes_applied.append(f"Fixed tags format in {file_path.name}")
            
            elif fix_type == 'generate_id':
                metadata['id'] = self._generate_id()
                fixed = True
                self.fixes_applied.append(f"Generated new ID for {file_path.name}")
        
        if fixed:
            self._write_metadata(file_path, metadata)
            self.stats['fixes_applied'] += len([v for v in violations if v['fixable']])
            self.stats['files_fixed'] += 1
    
    def _write_metadata(self, file_path: Path, metadata: Dict):
        """Write corrected metadata back to file"""
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        elif file_path.suffix.lower() == '.md':
            # Reconstruct markdown with fixed frontmatter
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    # Rebuild frontmatter
                    frontmatter_lines = ['---']
                    for key, value in metadata.items():
                        if key not in ['file_path', 'file_name', 'file_extension']:
                            frontmatter_lines.append(f"{key}: {value}")
                    frontmatter_lines.append('---')
                    
                    new_content = '\n'.join(frontmatter_lines) + '\n' + parts[2]
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _normalize_date(self, date_str: str) -> str:
        """Convert date to ISO8601 format"""
        try:
            # Try various formats
            dt = None
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            
            if dt:
                return dt.isoformat() + 'Z'
            else:
                return datetime.utcnow().isoformat() + 'Z'
        except:
            return datetime.utcnow().isoformat() + 'Z'
    
    def _infer_category(self, file_path: Path) -> str:
        """Infer category from file path/name"""
        path_str = str(file_path).lower()
        
        if 'doc' in path_str or 'note' in path_str:
            return 'documentation'
        elif 'code' in path_str or 'src' in path_str:
            return 'source_code'
        elif 'data' in path_str:
            return 'dataset'
        elif 'test' in path_str:
            return 'test'
        else:
            return 'general'
    
    def _is_iso8601(self, date_str: str) -> bool:
        """Check if date is in ISO8601 format"""
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        return bool(re.match(pattern, date_str))
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'stats': self.stats,
            'violations': self.violations,
            'fixes_applied': self.fixes_applied,
            'success': self.stats['violations_found'] == 0 or 
                      (self.fix_mode and self.stats['fixes_applied'] > 0)
        }

def format_report(result: Dict) -> str:
    """Format validation report"""
    stats = result['stats']
    
    output = [
        "",
        "=" * 70,
        "  MDEC AUTO-VALIDATOR REPORT",
        "=" * 70,
        "",
        f"Files Checked:      {stats['files_checked']}",
        f"Violations Found:   {stats['violations_found']}",
        f"Fixes Applied:      {stats['fixes_applied']}",
        f"Files Fixed:        {stats['files_fixed']}",
        "",
    ]
    
    if stats['violations_found'] > 0:
        output.append("VIOLATIONS DETECTED:")
        output.append("")
        
        for v in result['violations'][:10]:  # Show first 10
            fixable = "✅ FIXED" if v['fixable'] and stats['fixes_applied'] > 0 else "⚠️  MANUAL FIX NEEDED"
            output.append(f"  {v['type']}: {v['message']}")
            output.append(f"    File: {v['file']}")
            output.append(f"    Status: {fixable}")
            output.append("")
    
    if result['fixes_applied']:
        output.append("FIXES APPLIED:")
        output.append("")
        for fix in result['fixes_applied'][:10]:
            output.append(f"  ✅ {fix}")
        output.append("")
    
    if result['success']:
        output.append("✅ VALIDATION PASSED")
    else:
        output.append("⚠️  VALIDATION FAILED - Manual fixes required")
    
    output.extend([
        "",
        "=" * 70,
        f"MDEC Auto-Validator v1.0 • {result['timestamp']}",
        "=" * 70,
        ""
    ])
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python mdec_auto_validator.py <path> [--fix] [--watch]")
        sys.exit(1)
    
    path = sys.argv[1]
    fix_mode = '--fix' in sys.argv
    watch_mode = '--watch' in sys.argv
    
    if watch_mode:
        print(f"🔍 Watching {path} for metadata changes...")
        print("Press Ctrl+C to stop")
        try:
            while True:
                validator = MDECAutoValidator(fix_mode=fix_mode)
                result = validator.validate_path(path)
                print(format_report(result))
                time.sleep(5)  # Check every 5 seconds
        except KeyboardInterrupt:
            print("\n👋 Stopped watching")
    else:
        validator = MDECAutoValidator(fix_mode=fix_mode)
        result = validator.validate_path(path)
        print(format_report(result))
        
        sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
    main()
