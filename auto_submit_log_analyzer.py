#!/usr/bin/env python3
"""
Auto-Submit Log Analyzer
Analyzes frontend localStorage and Django logs to debug auto-submission issues

Usage:
    python auto_submit_log_analyzer.py

This script provides tools to analyze auto-submission logs for debugging server vs local issues.
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Any

class AutoSubmitLogAnalyzer:
    def __init__(self):
        self.frontend_logs = []
        self.django_logs = []
        self.analysis_results = {}
    
    def load_frontend_logs_from_json(self, json_file_path: str):
        """Load frontend logs from a JSON file (exported from localStorage)"""
        try:
            with open(json_file_path, 'r') as f:
                self.frontend_logs = json.load(f)
            print(f"✅ Loaded {len(self.frontend_logs)} frontend log entries")
        except FileNotFoundError:
            print(f"❌ Frontend log file not found: {json_file_path}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in frontend log file: {e}")
    
    def load_django_logs_from_file(self, log_file_path: str):
        """Load Django logs from a log file"""
        try:
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
            
            # Parse Django log format
            django_log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} \[(\w+)\] (.+)'
            
            for line in lines:
                if 'auto_submit' in line.lower() or 'FRONTEND_LOG' in line:
                    match = re.match(django_log_pattern, line.strip())
                    if match:
                        timestamp_str, level, message = match.groups()
                        self.django_logs.append({
                            'timestamp': timestamp_str,
                            'level': level,
                            'message': message.strip()
                        })
            
            print(f"✅ Loaded {len(self.django_logs)} Django log entries")
        except FileNotFoundError:
            print(f"❌ Django log file not found: {log_file_path}")
    
    def analyze_frontend_logs(self):
        """Analyze frontend logs for patterns and issues"""
        print("\n🔍 FRONTEND LOG ANALYSIS")
        print("=" * 50)
        
        if not self.frontend_logs:
            print("❌ No frontend logs to analyze")
            return
        
        # Group logs by session
        sessions = defaultdict(list)
        for log in self.frontend_logs:
            session_id = log.get('session', 'unknown')
            sessions[session_id].append(log)
        
        print(f"📊 Found {len(sessions)} unique sessions")
        
        # Analyze each session
        for session_id, logs in sessions.items():
            print(f"\n📋 Session: {session_id}")
            print(f"   Total logs: {len(logs)}")
            
            # Count log levels
            levels = Counter(log.get('level', 'unknown') for log in logs)
            print(f"   Log levels: {dict(levels)}")
            
            # Find auto-submit attempts
            auto_submit_logs = [log for log in logs if 'auto-submit' in log.get('message', '').lower()]
            print(f"   Auto-submit logs: {len(auto_submit_logs)}")
            
            # Find errors
            error_logs = [log for log in logs if log.get('level') == 'ERROR']
            if error_logs:
                print(f"   ❌ ERRORS found: {len(error_logs)}")
                for error in error_logs[:3]:  # Show first 3 errors
                    print(f"      - {error.get('message', 'No message')}")
            
            # Find network issues
            network_logs = [log for log in logs if 'network' in log.get('message', '').lower()]
            if network_logs:
                print(f"   🌐 Network issues: {len(network_logs)}")
            
            # Check for retry patterns
            retry_logs = [log for log in logs if 'retry' in log.get('message', '').lower()]
            if retry_logs:
                print(f"   🔄 Retry attempts: {len(retry_logs)}")
    
    def analyze_django_logs(self):
        """Analyze Django logs for server-side issues"""
        print("\n🔍 DJANGO LOG ANALYSIS")
        print("=" * 50)
        
        if not self.django_logs:
            print("❌ No Django logs to analyze")
            return
        
        # Count log levels
        levels = Counter(log.get('level', 'unknown') for log in self.django_logs)
        print(f"📊 Log levels: {dict(levels)}")
        
        # Find auto-submit related logs
        auto_submit_logs = [log for log in self.django_logs if 'auto-submit' in log.get('message', '').lower()]
        print(f"📋 Auto-submit logs: {len(auto_submit_logs)}")
        
        # Find validation failures
        validation_logs = [log for log in self.django_logs if 'validation' in log.get('message', '').lower()]
        if validation_logs:
            print(f"⚠️  Validation issues: {len(validation_logs)}")
        
        # Find timing issues
        timing_logs = [log for log in self.django_logs if any(word in log.get('message', '').lower() 
                                                            for word in ['remaining', 'expired', 'grace'])]
        if timing_logs:
            print(f"⏰ Timing issues: {len(timing_logs)}")
        
        # Find access denied
        access_logs = [log for log in self.django_logs if 'access denied' in log.get('message', '').lower()]
        if access_logs:
            print(f"🚫 Access denied: {len(access_logs)}")
    
    def compare_frontend_backend_logs(self):
        """Compare frontend and backend logs to find discrepancies"""
        print("\n🔍 FRONTEND vs BACKEND COMPARISON")
        print("=" * 50)
        
        if not self.frontend_logs or not self.django_logs:
            print("❌ Need both frontend and backend logs for comparison")
            return
        
        # Extract timestamps from both logs
        frontend_timestamps = []
        for log in self.frontend_logs:
            if 'auto-submit' in log.get('message', '').lower():
                frontend_timestamps.append(log.get('timestamp'))
        
        django_timestamps = []
        for log in self.django_logs:
            if 'auto-submit' in log.get('message', '').lower():
                django_timestamps.append(log.get('timestamp'))
        
        print(f"📊 Frontend auto-submit attempts: {len(frontend_timestamps)}")
        print(f"📊 Django auto-submit logs: {len(django_timestamps)}")
        
        if len(frontend_timestamps) > len(django_timestamps):
            print("⚠️  More frontend attempts than backend logs - possible network issues")
        elif len(django_timestamps) > len(frontend_timestamps):
            print("⚠️  More backend logs than frontend attempts - possible duplicate requests")
        else:
            print("✅ Frontend and backend log counts match")
    
    def generate_recommendations(self):
        """Generate recommendations based on log analysis"""
        print("\n🎯 RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = []
        
        # Check for common issues
        if self.frontend_logs:
            error_count = sum(1 for log in self.frontend_logs if log.get('level') == 'ERROR')
            if error_count > 0:
                recommendations.append(f"🔧 Fix {error_count} frontend errors found in logs")
        
        if self.django_logs:
            validation_count = sum(1 for log in self.django_logs if 'validation' in log.get('message', '').lower())
            if validation_count > 0:
                recommendations.append(f"⏰ Investigate {validation_count} timing validation issues")
        
        # Add general recommendations
        recommendations.extend([
            "📝 Enable more detailed logging on production server",
            "🔄 Implement retry mechanism with exponential backoff",
            "🌐 Add network connectivity checks before auto-submit",
            "⏱️  Add server time synchronization checks",
            "🔐 Verify CSRF token handling for long sessions"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    def export_analysis_report(self, output_file: str = "auto_submit_analysis_report.txt"):
        """Export analysis results to a file"""
        with open(output_file, 'w') as f:
            f.write("AUTO-SUBMIT LOG ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Frontend logs analyzed: {len(self.frontend_logs)}\n")
            f.write(f"Django logs analyzed: {len(self.django_logs)}\n\n")
            
            # Add detailed analysis results here
            f.write("See console output for detailed analysis results.\n")
        
        print(f"✅ Analysis report exported to: {output_file}")


def main():
    """Main function to run the log analyzer"""
    analyzer = AutoSubmitLogAnalyzer()
    
    print("🔍 AUTO-SUBMIT LOG ANALYZER")
    print("=" * 50)
    
    # Instructions for users
    print("\n📋 INSTRUCTIONS:")
    print("1. Export frontend logs from browser localStorage:")
    print("   - Open browser console on test page")
    print("   - Run: console.log(JSON.stringify(JSON.parse(localStorage.getItem('autoSubmitLogs')), null, 2))")
    print("   - Copy output to a file named 'frontend_logs.json'")
    print("\n2. Export Django logs:")
    print("   - Copy Django log file to 'django_logs.txt'")
    print("   - Or use: python manage.py logs > django_logs.txt")
    print("\n3. Run this analyzer with both files in the same directory")
    
    # Try to load logs automatically
    print("\n🔄 ATTEMPTING TO LOAD LOGS...")
    
    # Check for frontend logs
    frontend_files = ['frontend_logs.json', 'autoSubmitLogs.json', 'logs.json']
    for file in frontend_files:
        if os.path.exists(file):
            analyzer.load_frontend_logs_from_json(file)
            break
    
    # Check for Django logs
    django_files = ['django_logs.txt', 'django.log', 'logs/django.log']
    for file in django_files:
        if os.path.exists(file):
            analyzer.load_django_logs_from_file(file)
            break
    
    # Run analysis
    analyzer.analyze_frontend_logs()
    analyzer.analyze_django_logs()
    analyzer.compare_frontend_backend_logs()
    analyzer.generate_recommendations()
    
    # Export report
    analyzer.export_analysis_report()
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()