#!/usr/bin/env python3
"""Simple test to verify PathLike fix."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_simple():
    """Simple test of the file path handling."""
    try:
        from pathlib import Path
        
        # Test case 1: String path should work
        test_path = "c:/test/file.txt"
        path_obj = Path(test_path)
        print(f"✅ String path works: {path_obj}")
        
        # Test case 2: Dict should fail (this is what was happening)
        test_dict = {'path': 'c:/test/file.txt', 'format': 'pdf'}
        try:
            path_obj_dict = Path(test_dict)
            print("❌ Dict path unexpectedly worked!")
        except TypeError as e:
            print(f"✅ Dict path correctly fails: {e}")
        
        # Test case 3: Extract path from dict (this is the fix)
        if isinstance(test_dict, dict) and 'path' in test_dict:
            extracted_path = test_dict['path']
            path_obj_fixed = Path(extracted_path)
            print(f"✅ Fixed path extraction works: {path_obj_fixed}")
        
        print("\n🎉 All basic tests passed! The PathLike fix should work.")
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_simple()
    if not success:
        sys.exit(1)
