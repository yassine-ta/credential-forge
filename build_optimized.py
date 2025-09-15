#!/usr/bin/env python3
"""
Optimized build script for CredentialForge native components with llama.cpp CPU optimization.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    # Check CMake
    if not shutil.which("cmake"):
        print("❌ CMake not found. Please install CMake.")
        return False
    print("✅ CMake found")
    
    # Check C++ compiler
    cxx_compiler = None
    if platform.system() == "Windows":
        # Try to find a modern compiler
        for compiler in ["g++", "clang++", "cl"]:
            if shutil.which(compiler):
                cxx_compiler = compiler
                break
        
        if not cxx_compiler:
            print("❌ No C++ compiler found. Please install MinGW-w64, Clang, or Visual Studio.")
            return False
    else:
        if not shutil.which("g++") and not shutil.which("clang++"):
            print("❌ No C++ compiler found. Please install g++ or clang++.")
            return False
        cxx_compiler = "g++" if shutil.which("g++") else "clang++"
    
    print(f"✅ C++ compiler found: {cxx_compiler}")
    
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

def install_python_dependencies():
    """Install required Python packages."""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "cmake>=3.16.0",
        "pybind11>=2.10.0", 
        "ninja>=1.10.0",
        "setuptools>=65.0.0",
        "wheel>=0.40.0"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
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
    """Configure CMake build with CPU optimizations."""
    print("⚙️ Configuring CMake with CPU optimizations...")
    
    # Get current Python executable and paths
    python_exe = sys.executable
    python_root = Path(python_exe).parent.parent
    
    cmake_args = [
        "cmake",
        "-B", str(build_dir),
        "-S", ".",
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_CXX_STANDARD=17",
        f"-DPython3_EXECUTABLE={python_exe}",
        f"-DPython3_ROOT_DIR={python_root}",
        f"-DPython3_FIND_STRATEGY=LOCATION"
    ]
    
    # Platform-specific configurations
    if platform.system() == "Windows":
        # Try to use modern MinGW or Visual Studio
        if shutil.which("g++"):
            # Use MinGW with modern settings
            cmake_args.extend([
                "-G", "MinGW Makefiles",
                "-DCMAKE_CXX_COMPILER=g++",
                "-DCMAKE_C_COMPILER=gcc",
                "-DCMAKE_MAKE_PROGRAM=mingw32-make"
            ])
        elif shutil.which("clang++"):
            # Use Clang
            cmake_args.extend([
                "-G", "MinGW Makefiles", 
                "-DCMAKE_CXX_COMPILER=clang++",
                "-DCMAKE_C_COMPILER=clang"
            ])
        else:
            # Fallback to Visual Studio
            cmake_args.extend([
                "-G", "Visual Studio 17 2022",
                "-A", "x64"
            ])
    else:
        # Linux/macOS
        cmake_args.extend([
            "-G", "Ninja",
            "-DCMAKE_CXX_COMPILER=g++",
            "-DCMAKE_C_COMPILER=gcc"
        ])
    
    # CPU optimization flags
    cmake_args.extend([
        "-DLLAMA_CUDA=OFF",
        "-DLLAMA_METAL=OFF", 
        "-DLLAMA_VULKAN=OFF",
        "-DLLAMA_OPENCL=OFF",
        "-DLLAMA_HIPBLAS=OFF",
        "-DLLAMA_CLBLAST=OFF",
        "-DLLAMA_NATIVE=ON",
        "-DLLAMA_AVX=ON",
        "-DLLAMA_AVX2=ON",
        "-DLLAMA_FMA=ON",
        "-DLLAMA_F16C=ON",
        "-DLLAMA_SSE3=ON",
        "-DLLAMA_SSSE3=ON",
        "-DLLAMA_SSE4_1=ON",
        "-DLLAMA_SSE4_2=ON",
        "-DLLAMA_POPCNT=ON"
    ])
    
    # Platform-specific optimizations
    if platform.system() == "Darwin":  # macOS
        cmake_args.append("-DLLAMA_ACCELERATE=ON")
    
    print(f"Running: {' '.join(cmake_args)}")
    
    try:
        result = subprocess.run(cmake_args, check=True, capture_output=True, text=True)
        print("✅ CMake configuration successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ CMake configuration failed")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def build_project(build_dir):
    """Build the project."""
    print("🔨 Building project with CPU optimizations...")
    
    if platform.system() == "Windows":
        if shutil.which("gcc"):
            # Use MinGW Makefiles
            build_cmd = ["cmake", "--build", str(build_dir), "--parallel"]
        else:
            # Use Visual Studio
            build_cmd = ["cmake", "--build", str(build_dir), "--config", "Release"]
    else:
        # Use Ninja for faster builds
        build_cmd = ["cmake", "--build", str(build_dir), "--parallel"]
    
    print(f"Running: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, check=True, capture_output=True, text=True)
        print("✅ Build successful")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False

def test_build():
    """Test the built components."""
    print("🧪 Testing built components...")
    
    try:
        # Test Python import
        import sys
        sys.path.insert(0, str(Path("credentialforge/native")))
        
        # Try to import the native module
        import credentialforge_native
        print("✅ Native module imported successfully")
        
        # Test basic functionality
        if hasattr(credentialforge_native, 'test_cpu_optimization'):
            result = credentialforge_native.test_cpu_optimization()
            print(f"✅ CPU optimization test: {result}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import native module: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main build process."""
    print("🚀 Building CredentialForge Native Components with CPU Optimization")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Setup build directory
    build_dir = setup_build_directory()
    
    # Configure CMake
    if not configure_cmake(build_dir):
        print("❌ CMake configuration failed")
        sys.exit(1)
    
    # Build project
    if not build_project(build_dir):
        print("❌ Build failed")
        sys.exit(1)
    
    # Test build
    if not test_build():
        print("❌ Test failed")
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("🚀 Native components are ready for CPU-optimized LLM performance!")
    
    # Show performance tips
    print("\n💡 Performance Tips:")
    print("   - Use quantized models (Q4_0, Q4_K) for better performance")
    print("   - Set thread count to match your CPU cores")
    print("   - Enable batch processing for multiple requests")
    print("   - Monitor memory usage during large generations")

if __name__ == "__main__":
    main()

