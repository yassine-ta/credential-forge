#!/usr/bin/env python3
"""Script to handle large generation operations and provide recommendations."""

import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def analyze_generation_issue():
    """Analyze the current generation issue and provide recommendations."""
    print("🔍 Analyzing Large Generation Issue")
    print("=" * 50)
    
    print("📊 Current Configuration Analysis:")
    print("  • Number of Files: 3400")
    print("  • Batch Size: 55")
    print("  • File Formats: 5 (eml, msg, xlsx, pptx, vsdx)")
    print("  • Credential Types: 3 (db_connection, mongodb_uri, password)")
    print("  • Topics: 12 different topics")
    print("  • LLM Model: Qwen2-0.5B")
    
    print("\n⚠️  Issues Identified:")
    print("  1. Too many files (3400) - system overwhelmed")
    print("  2. Large batch size (55) - memory pressure")
    print("  3. Multiple complex formats - processing overhead")
    print("  4. LLM generation for each file - slow operation")
    
    print("\n💡 Recommendations:")
    print("  1. Reduce number of files to 100-500 for testing")
    print("  2. Use smaller batch size (10-20)")
    print("  3. Start with simpler formats (eml only)")
    print("  4. Consider disabling LLM for large operations")
    
    print("\n🚀 Suggested Commands:")
    print("  # Small test (recommended)")
    print("  python -m credentialforge generate --output-dir ./output --num-files 10 --formats eml --credential-types aws_access_key --regex-db ./data/regex_db.json --topics 'test generation'")
    
    print("  # Medium test")
    print("  python -m credentialforge generate --output-dir ./output --num-files 100 --formats eml,xlsx --credential-types aws_access_key,jwt_token --regex-db ./data/regex_db.json --topics 'security audit,API documentation'")
    
    print("\n⏱️  Expected Generation Times:")
    print("  • 10 files: ~30 seconds")
    print("  • 100 files: ~5 minutes")
    print("  • 1000 files: ~50 minutes")
    print("  • 3400 files: ~3+ hours (not recommended)")
    
    print("\n🛠️  Current Process Status:")
    print("  The current process is likely:")
    print("  • Processing the first batch of 55 files")
    print("  • Using LLM for content generation (slow)")
    print("  • May be running out of memory")
    print("  • Could take 10-30 minutes per batch")
    
    print("\n🔄 Recovery Options:")
    print("  1. Wait for current batch to complete (10-30 min)")
    print("  2. Cancel current process (Ctrl+C)")
    print("  3. Start with smaller test")
    print("  4. Use template-based generation (faster)")
    
    return True


def provide_optimized_config():
    """Provide optimized configuration for large operations."""
    print("\n🎯 Optimized Configuration for Large Operations")
    print("=" * 50)
    
    print("📋 Recommended Settings:")
    print("  • Max Files: 500 (for testing)")
    print("  • Batch Size: 20")
    print("  • Formats: Start with 1-2 formats")
    print("  • LLM: Disable for large operations")
    print("  • Credentials: 2-3 types max")
    
    print("\n⚡ Performance Tips:")
    print("  1. Use template-based generation for large batches")
    print("  2. Process formats sequentially")
    print("  3. Monitor system resources")
    print("  4. Use smaller batch sizes")
    print("  5. Consider parallel processing")
    
    print("\n🔧 System Requirements:")
    print("  • RAM: 8GB+ recommended for 1000+ files")
    print("  • Storage: 1GB+ for 1000 files")
    print("  • Time: Allow 1-2 hours for 1000 files")
    
    return True


if __name__ == "__main__":
    try:
        analyze_generation_issue()
        provide_optimized_config()
        
        print("\n✅ Analysis complete!")
        print("💡 Start with smaller tests before attempting large operations.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
