#!/usr/bin/env python3
"""
Phase 2 Endpoint Diagnostics - Identify Incomplete Endpoints

Scans all route files to identify:
1. Endpoints that are stubs (only pass or raise NotImplementedError)
2. Endpoints with TODO comments
3. Endpoints with incomplete logic
4. Endpoints that need to be added

Author: GitHub Copilot
Date: October 22, 2025
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
BACKEND_PATH = Path("D:/ConversationalAI/language-learning-platform")
ROUTES_DIR = BACKEND_PATH / "app/routes"

class EndpointDiagnostics:
    def __init__(self):
        self.results = {}
        self.incomplete_endpoints = []
        self.stubs = []
        self.todos = []
    
    def scan_file(self, filepath: Path) -> Dict:
        """Scan a route file for incomplete endpoints."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        file_results = {
            'filepath': str(filepath.relative_to(BACKEND_PATH)),
            'endpoints': [],
            'incomplete_count': 0,
            'stub_count': 0,
            'todo_count': 0
        }
        
        # Find all route decorators
        route_pattern = r"@\w+_bp\.route\(['\"]([^'\"]+)['\"],\s*methods=\[([^\]]+)\]\)"
        
        for i, line in enumerate(lines, 1):
            route_match = re.search(route_pattern, line)
            if route_match:
                endpoint_path = route_match.group(1)
                methods = route_match.group(2).replace("'", "").replace('"', "").replace(' ', '')
                
                # Get function name (next non-comment, non-decorator line)
                func_name = None
                func_line = i + 1
                for j in range(i, min(i + 10, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith('@') and not lines[j].strip().startswith('"'):
                        func_match = re.search(r"def\s+(\w+)", lines[j])
                        if func_match:
                            func_name = func_match.group(1)
                            func_line = j + 1
                            break
                
                # Analyze function body
                body_lines = []
                indent_level = None
                for j in range(i, len(lines)):
                    if 'def ' in lines[j]:
                        # Found function definition
                        indent_level = len(lines[j]) - len(lines[j].lstrip())
                        # Get body
                        for k in range(j + 1, len(lines)):
                            current_line = lines[k]
                            if current_line.strip() and not current_line.startswith(' ' * (indent_level + 1)) and current_line.strip() != '':
                                if not current_line.strip().startswith('@'):
                                    break
                            if current_line.strip():
                                body_lines.append(current_line.strip())
                        break
                
                # Check for incomplete indicators
                is_stub = any('pass' in line for line in body_lines)
                is_incomplete = any('NotImplementedError' in line or 'TODO' in line or 'FIXME' in line for line in body_lines)
                is_empty = len(body_lines) <= 2
                
                endpoint_info = {
                    'path': endpoint_path,
                    'methods': methods,
                    'function': func_name,
                    'line': i,
                    'is_stub': is_stub,
                    'is_incomplete': is_incomplete,
                    'is_empty': is_empty,
                    'body_lines': len(body_lines),
                    'status': 'COMPLETE'
                }
                
                # Determine status
                if is_stub and is_empty:
                    endpoint_info['status'] = 'STUB'
                    file_results['stub_count'] += 1
                    self.stubs.append({
                        'file': filepath.name,
                        'endpoint': endpoint_path,
                        'function': func_name
                    })
                elif is_incomplete or is_empty:
                    endpoint_info['status'] = 'INCOMPLETE'
                    file_results['incomplete_count'] += 1
                    self.incomplete_endpoints.append({
                        'file': filepath.name,
                        'endpoint': endpoint_path,
                        'function': func_name,
                        'line': i,
                        'reason': 'stub' if is_stub else 'empty' if is_empty else 'has TODOs'
                    })
                
                if 'TODO' in ''.join(body_lines) or 'FIXME' in ''.join(body_lines):
                    file_results['todo_count'] += 1
                    self.todos.append({
                        'file': filepath.name,
                        'endpoint': endpoint_path,
                        'function': func_name
                    })
                
                file_results['endpoints'].append(endpoint_info)
        
        return file_results
    
    def run_diagnostics(self):
        """Run diagnostics on all route files."""
        if not ROUTES_DIR.exists():
            print(f"❌ Routes directory not found: {ROUTES_DIR}")
            return
        
        print("🔍 PHASE 2: ENDPOINT DIAGNOSTICS")
        print("=" * 70)
        print()
        
        route_files = sorted(ROUTES_DIR.glob("*_routes.py"))
        
        for route_file in route_files:
            if route_file.name.startswith('__'):
                continue
            
            print(f"📄 Scanning: {route_file.name}")
            file_results = self.scan_file(route_file)
            self.results[route_file.name] = file_results
            
            print(f"   ✅ Complete: {len(file_results['endpoints']) - file_results['incomplete_count'] - file_results['stub_count']}")
            print(f"   ⚠️  Incomplete: {file_results['incomplete_count']}")
            print(f"   🔴 Stubs: {file_results['stub_count']}")
            print(f"   📝 TODOs: {file_results['todo_count']}")
            print()
        
        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        
        total_endpoints = sum(len(f['endpoints']) for f in self.results.values())
        total_complete = sum(len(f['endpoints']) - f['incomplete_count'] - f['stub_count'] for f in self.results.values())
        total_incomplete = sum(f['incomplete_count'] for f in self.results.values())
        total_stubs = sum(f['stub_count'] for f in self.results.values())
        
        print(f"Total Endpoints: {total_endpoints}")
        print(f"✅ Complete: {total_complete}")
        print(f"⚠️  Incomplete: {total_incomplete}")
        print(f"🔴 Stubs: {total_stubs}")
        print()
        
        # Priority 1 Assessment Routes
        print("=" * 70)
        print("🎯 PRIORITY 1: ASSESSMENT ROUTES")
        print("=" * 70)
        
        if 'assessment_routes.py' in self.results:
            assessment_data = self.results['assessment_routes.py']
            print(f"Total endpoints: {len(assessment_data['endpoints'])}")
            print(f"Complete: {len(assessment_data['endpoints']) - assessment_data['incomplete_count'] - assessment_data['stub_count']}")
            print(f"Incomplete: {assessment_data['incomplete_count']}")
            print(f"Stubs: {assessment_data['stub_count']}")
            print()
            
            # List incomplete assessment endpoints
            if assessment_data['incomplete_count'] > 0:
                print("Incomplete Assessment Endpoints:")
                for endpoint in assessment_data['endpoints']:
                    if endpoint['status'] != 'COMPLETE':
                        print(f"  - {endpoint['methods']} {endpoint['path']}")
                        print(f"    Function: {endpoint['function']} (Line {endpoint['line']})")
                        print(f"    Status: {endpoint['status']}")
            print()
        
        # Detailed list of all incomplete endpoints by priority
        print("=" * 70)
        print("📋 ALL INCOMPLETE ENDPOINTS (By File)")
        print("=" * 70)
        
        if self.incomplete_endpoints:
            for endpoint in self.incomplete_endpoints:
                print(f"  {endpoint['file']}")
                print(f"    Endpoint: {endpoint['endpoint']}")
                print(f"    Function: {endpoint['function']}")
                print(f"    Line: {endpoint['line']}")
                print(f"    Reason: {endpoint['reason']}")
                print()
        
        # Save detailed report
        report = {
            'summary': {
                'total_endpoints': total_endpoints,
                'complete': total_complete,
                'incomplete': total_incomplete,
                'stubs': total_stubs
            },
            'incomplete_endpoints': self.incomplete_endpoints,
            'stubs': self.stubs,
            'todos': self.todos,
            'file_details': self.results
        }
        
        report_path = Path("D:/ConversationalAI/PHASE2_DIAGNOSTICS_REPORT.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"📁 Detailed report saved to: {report_path}")
        print()
        
        return report

if __name__ == '__main__':
    diagnostics = EndpointDiagnostics()
    diagnostics.run_diagnostics()
