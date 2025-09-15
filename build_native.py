#!/usr/bin/env python3
"""Build script for native components with CMake and llama.cpp integration."""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def check_dependencies():
    """Check if required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Check CMake
    if not shutil.which("cmake"):
        print("❌ CMake not found. Please install CMake 3.16 or later.")
        return False
    print("✅ CMake found")
    
    # Check compiler
    if platform.system() == "Windows":
        if not shutil.which("cl") and not shutil.which("gcc"):
            print("❌ No C++ compiler found. Please install Visual Studio or MinGW.")
            return False
    else:
        if not shutil.which("gcc") and not shutil.which("clang"):
            print("❌ No C++ compiler found. Please install GCC or Clang.")
            return False
    print("✅ C++ compiler found")
    
    # Check Python development headers
    try:
        import distutils.sysconfig
        include_dir = distutils.sysconfig.get_python_inc()
        if not os.path.exists(include_dir):
            print("❌ Python development headers not found.")
            return False
        print("✅ Python development headers found")
    except ImportError:
        print("❌ Python development headers not found.")
        return False
    
    return True

def setup_build_directory():
    """Setup build directory."""
    print("📁 Setting up build directory...")
    
    build_dir = Path("build")
    if build_dir.exists():
        try:
            shutil.rmtree(build_dir)
        except PermissionError:
            print("⚠️ Permission denied, trying alternative cleanup...")
            # Try to remove individual files that might be locked
            import time
            time.sleep(1)
            try:
                shutil.rmtree(build_dir)
            except PermissionError:
                print("❌ Cannot remove build directory. Please close any programs using it and try again.")
                sys.exit(1)
    
    build_dir.mkdir()
    return build_dir

def configure_cmake(build_dir):
    """Configure CMake build."""
    print("⚙️ Configuring CMake...")
    
    # Get current Python executable and paths
    python_exe = sys.executable
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    
    cmake_args = [
        "cmake",
        "-B", str(build_dir),
        "-S", ".",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_STANDARD=17",
        f"-DPython3_EXECUTABLE={python_exe}",
        f"-DPython3_ROOT_DIR={Path(python_exe).parent.parent}",
        f"-DPython3_FIND_STRATEGY=LOCATION"
    ]
    
    # Platform-specific configurations
    if platform.system() == "Windows":
        # Try MinGW first, fallback to Visual Studio
        if shutil.which("gcc"):
            cmake_args.extend([
                "-G", "MinGW Makefiles",
                "-DCMAKE_CXX_COMPILER=g++",
                "-DCMAKE_C_COMPILER=gcc"
            ])
        else:
            cmake_args.extend([
                "-G", "Visual Studio 17 2022",
                "-A", "x64"
            ])
    else:
        cmake_args.extend([
            "-DCMAKE_CXX_COMPILER=g++",
            "-DCMAKE_C_COMPILER=gcc"
        ])
    
    return run_command(cmake_args)

def build_project(build_dir):
    """Build the project."""
    print("🔨 Building project...")
    
    # Determine build command based on platform
    if platform.system() == "Windows":
        if shutil.which("gcc"):
            # Use MinGW Makefiles
            build_cmd = ["cmake", "--build", str(build_dir), "--parallel"]
        else:
            # Use Visual Studio
            build_cmd = ["cmake", "--build", str(build_dir), "--config", "Release"]
    else:
        build_cmd = ["cmake", "--build", str(build_dir), "--parallel"]
    
    return run_command(build_cmd)

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    # Install build dependencies
    build_deps = [
        "cmake",
        "ninja",
        "pybind11",
        "setuptools",
        "wheel"
    ]
    
    for dep in build_deps:
        print(f"Installing {dep}...")
        if not run_command([sys.executable, "-m", "pip", "install", dep]):
            print(f"Warning: Failed to install {dep}")
    
    return True

def create_python_bindings():
    """Create Python bindings for native modules."""
    print("🐍 Creating Python bindings...")
    
    # Create native directory
    native_dir = Path("credentialforge/native")
    native_dir.mkdir(exist_ok=True)
    
    # Create __init__.py
    init_file = native_dir / "__init__.py"
    init_content = '''"""Native components for CredentialForge."""

try:
    from .credential_utils import *
    from .llama_cpp_interface import *
    from .cpu_optimizer import *
    from .memory_manager import *
    from .parallel_executor import *
    
    NATIVE_AVAILABLE = True
except ImportError as e:
    NATIVE_AVAILABLE = False
    print(f"Native components not available: {e}")

__all__ = ['NATIVE_AVAILABLE']
'''
    
    with open(init_file, 'w') as f:
        f.write(init_content)
    
    return True

def test_build():
    """Test the built components."""
    print("🧪 Testing build...")
    
    try:
        # Test import
        sys.path.insert(0, str(Path.cwd()))
        import credentialforge.native
        
        if credentialforge.native.NATIVE_AVAILABLE:
            print("✅ Native components loaded successfully")
            return True
        else:
            print("❌ Native components failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main build process."""
    print("🚀 Building CredentialForge Native Components")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        return 1
    
    # Install Python dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return 1
    
    # Setup build directory
    build_dir = setup_build_directory()
    
    # Configure CMake
    if not configure_cmake(build_dir):
        print("❌ CMake configuration failed")
        return 1
    
    # Build project
    if not build_project(build_dir):
        print("❌ Build failed")
        return 1
    
    # Create Python bindings
    if not create_python_bindings():
        print("❌ Failed to create Python bindings")
        return 1
    
    # Test build
    if not test_build():
        print("❌ Build test failed")
        return 1
    
    print("\n✅ Build completed successfully!")
    print("🎉 Native components are ready to use")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
