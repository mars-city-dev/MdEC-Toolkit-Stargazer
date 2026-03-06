#!/usr/bin/env python3
"""
MDEC Metadata Quality Scorer
Analyzes file metadata and assigns quality scores (0-100)

Usage:
    python mdec_quality_scorer.py <file_path>
    python mdec_quality_scorer.py <file_path> --json
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List, Tuple, Any

class MDECQualityScorer:
    """Evaluates metadata quality against MDEC standards"""
    
    def __init__(self):
        self.required_fields = [
            'id', 'name', 'created', 'modified', 
            'category', 'tags', 'author', 'description'
        ]
        self.date_formats = [
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO8601
            r'\d{4}-\d{2}-\d{2}',  # ISO Date only
        ]
    
    def score_file(self, file_path: str) -> Dict[str, Any]:
        """Main scoring function"""
        if not os.path.exists(file_path):
            return {'error': f'File not found: {file_path}'}
        
        metadata = self._extract_metadata(file_path)
        
        scores = {
            'completeness': self._score_completeness(metadata),
            'consistency': self._score_consistency(metadata),
            'accuracy': self._score_accuracy(metadata),
            'richness': self._score_richness(metadata)
        }
        
        # Calculate overall score (weighted average)
        overall = (
            scores['completeness'] * 0.35 +
            scores['consistency'] * 0.25 +
            scores['accuracy'] * 0.25 +
            scores['richness'] * 0.15
        )
        
        return {
            'file': file_path,
            'overall_score': round(overall, 1),
            'scores': scores,
            'metadata': metadata,
            'recommendations': self._generate_recommendations(metadata, scores),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from file"""
        path = Path(file_path)
        stat = path.stat()
        
        metadata = {
            'name': path.name,
            'path': str(path.absolute()),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'extension': path.suffix.lower()
        }
        
        # Try to extract embedded metadata based on file type
        if path.suffix.lower() == '.json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        metadata.update(data)
            except:
                pass
        
        elif path.suffix.lower() == '.md':
            # Extract YAML frontmatter
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            # Parse YAML-like frontmatter
                            frontmatter = parts[1].strip()
                            for line in frontmatter.split('\n'):
                                if ':' in line:
                                    key, value = line.split(':', 1)
                                    metadata[key.strip()] = value.strip()
            except:
                pass
        
        return metadata
    
    def _score_completeness(self, metadata: Dict) -> float:
        """Score based on presence of required fields"""
        present = sum(1 for field in self.required_fields if field in metadata and metadata[field])
        score = (present / len(self.required_fields)) * 100
        return round(score, 1)
    
    def _score_consistency(self, metadata: Dict) -> float:
        """Score based on format consistency"""
        score = 100.0
        issues = 0
        
        # Check date formats
        for field in ['created', 'modified']:
            if field in metadata:
                value = str(metadata[field])
                if not any(re.match(fmt, value) for fmt in self.date_formats):
                    issues += 1
                    score -= 20
        
        # Check ID format (should be UUID or systematic)
        if 'id' in metadata:
            id_val = str(metadata['id'])
            if len(id_val) < 5 or id_val.isdigit():  # Too simple
                issues += 1
                score -= 15
        
        # Check tags format (should be array)
        if 'tags' in metadata:
            if not isinstance(metadata['tags'], (list, tuple)):
                issues += 1
                score -= 15
        
        return max(0, round(score, 1))
    
    def _score_accuracy(self, metadata: Dict) -> float:
        """Score based on logical accuracy"""
        score = 100.0
        
        # Check created vs modified dates
        if 'created' in metadata and 'modified' in metadata:
            try:
                created = datetime.fromisoformat(str(metadata['created']).replace('Z', ''))
                modified = datetime.fromisoformat(str(metadata['modified']).replace('Z', ''))
                if modified < created:
                    score -= 30  # Modified can't be before created
            except:
                score -= 10  # Date parsing failed
        
        # Check file size reasonableness
        if 'size' in metadata:
            size = metadata['size']
            if size == 0:
                score -= 20  # Empty file suspicious
        
        # Check category validity
        if 'category' in metadata:
            cat = str(metadata['category']).lower()
            if len(cat) < 3 or cat in ['unknown', 'misc', 'other', 'na']:
                score -= 15  # Generic category
        
        return max(0, round(score, 1))
    
    def _score_richness(self, metadata: Dict) -> float:
        """Score based on metadata richness/depth"""
        score = 0.0
        
        # More fields = richer metadata
        field_count = len([k for k, v in metadata.items() if v])
        if field_count >= 15:
            score += 40
        elif field_count >= 10:
            score += 30
        elif field_count >= 8:
            score += 20
        else:
            score += 10
        
        # Check tag richness
        if 'tags' in metadata and isinstance(metadata['tags'], (list, tuple)):
            tag_count = len(metadata['tags'])
            if tag_count >= 5:
                score += 30
            elif tag_count >= 3:
                score += 20
            elif tag_count >= 1:
                score += 10
        
        # Check description quality
        if 'description' in metadata:
            desc = str(metadata['description'])
            if len(desc) >= 100:
                score += 30
            elif len(desc) >= 50:
                score += 20
            elif len(desc) >= 20:
                score += 10
        
        return min(100, round(score, 1))
    
    def _generate_recommendations(self, metadata: Dict, scores: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        if scores['completeness'] < 80:
            missing = [f for f in self.required_fields if f not in metadata or not metadata[f]]
            recs.append(f"⚠️  Add missing required fields: {', '.join(missing)}")
        
        if scores['consistency'] < 80:
            recs.append("⚠️  Fix date format inconsistencies (use ISO8601: YYYY-MM-DDTHH:MM:SS)")
            if 'tags' in metadata and not isinstance(metadata['tags'], (list, tuple)):
                recs.append("⚠️  Convert tags to array format")
        
        if scores['accuracy'] < 80:
            recs.append("⚠️  Review date logic (modified should be >= created)")
            if 'category' in metadata and len(str(metadata['category'])) < 3:
                recs.append("⚠️  Replace generic category with specific classification")
        
        if scores['richness'] < 60:
            recs.append("💡 Add more descriptive tags (aim for 3-5 tags)")
            if 'description' not in metadata or len(str(metadata.get('description', ''))) < 50:
                recs.append("💡 Add detailed description (50+ characters)")
        
        if not recs:
            recs.append("✅ Excellent metadata! No improvements needed.")
        
        return recs

def format_report(result: Dict, json_output: bool = False) -> str:
    """Format the scoring result for display"""
    if json_output:
        return json.dumps(result, indent=2)
    
    if 'error' in result:
        return f"❌ Error: {result['error']}"
    
    score = result['overall_score']
    scores = result['scores']
    
    # Determine grade
    if score >= 90:
        grade = "🏆 EXCELLENT"
    elif score >= 75:
        grade = "✅ GOOD"
    elif score >= 60:
        grade = "⚠️  NEEDS IMPROVEMENT"
    else:
        grade = "❌ POOR"
    
    output = [
        "",
        "=" * 70,
        "  MDEC METADATA QUALITY SCORE",
        "=" * 70,
        "",
        f"File: {result['file']}",
        "",
        f"Overall Score: {score}/100 {grade}",
        "",
        "Detailed Scores:",
        f"  • Completeness: {scores['completeness']}/100 {'✅' if scores['completeness'] >= 80 else '⚠️'}",
        f"  • Consistency:  {scores['consistency']}/100 {'✅' if scores['consistency'] >= 80 else '⚠️'}",
        f"  • Accuracy:     {scores['accuracy']}/100 {'✅' if scores['accuracy'] >= 80 else '⚠️'}",
        f"  • Richness:     {scores['richness']}/100 {'✅' if scores['richness'] >= 60 else '⚠️'}",
        "",
        "Recommendations:",
    ]
    
    for rec in result['recommendations']:
        output.append(f"  {rec}")
    
    output.extend([
        "",
        "=" * 70,
        f"Evaluated by MDEC Quality Scorer v1.0 • {result['timestamp']}",
        "=" * 70,
        ""
    ])
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("Usage: python mdec_quality_scorer.py <file_path> [--json]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    json_output = '--json' in sys.argv
    
    scorer = MDECQualityScorer()
    result = scorer.score_file(file_path)
    
    print(format_report(result, json_output))
    
    # Exit with appropriate code
    if 'error' in result:
        sys.exit(1)
    elif result['overall_score'] >= 75:
        sys.exit(0)
    else:
        sys.exit(2)  # Needs improvement

if __name__ == '__main__':
    main()
