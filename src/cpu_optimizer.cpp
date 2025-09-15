#include <string>
#include <vector>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <iostream>
#include <immintrin.h>  // For AVX/SSE instructions

extern "C" {
    #include <Python.h>
}

class CPUOptimizer {
private:
    int num_cores;
    int cache_line_size;
    bool has_avx;
    bool has_avx2;
    bool has_fma;
    bool has_sse4_2;
    
    // Performance monitoring
    std::atomic<uint64_t> total_operations{0};
    std::atomic<uint64_t> total_time_ns{0};
    
public:
    CPUOptimizer() {
        detect_cpu_features();
        num_cores = std::thread::hardware_concurrency();
        cache_line_size = 64;  // Typical cache line size
        
        std::cout << "CPU Optimizer initialized:" << std::endl;
        std::cout << "  Cores: " << num_cores << std::endl;
        std::cout << "  AVX: " << (has_avx ? "Yes" : "No") << std::endl;
        std::cout << "  AVX2: " << (has_avx2 ? "Yes" : "No") << std::endl;
        std::cout << "  FMA: " << (has_fma ? "Yes" : "No") << std::endl;
        std::cout << "  SSE4.2: " << (has_sse4_2 ? "Yes" : "No") << std::endl;
    }
    
    // Optimized string processing using SIMD
    std::vector<std::string> process_strings_simd(const std::vector<std::string>& input) {
        std::vector<std::string> result;
        result.reserve(input.size());
        
        for (const auto& str : input) {
            if (has_avx2 && str.length() >= 32) {
                result.push_back(process_string_avx2(str));
            } else if (has_sse4_2 && str.length() >= 16) {
                result.push_back(process_string_sse4_2(str));
            } else {
                result.push_back(process_string_scalar(str));
            }
        }
        
        return result;
    }
    
    // Optimized parallel processing
    template<typename Func>
    void parallel_for(size_t start, size_t end, Func func, size_t chunk_size = 0) {
        if (chunk_size == 0) {
            chunk_size = std::max(size_t(1), (end - start) / (num_cores * 4));
        }
        
        std::vector<std::thread> threads;
        threads.reserve(num_cores);
        
        for (size_t i = start; i < end; i += chunk_size) {
            size_t chunk_end = std::min(i + chunk_size, end);
            
            threads.emplace_back([=]() {
                for (size_t j = i; j < chunk_end; ++j) {
                    func(j);
                }
            });
            
            if (threads.size() >= num_cores) {
                for (auto& t : threads) {
                    t.join();
                }
                threads.clear();
            }
        }
        
        for (auto& t : threads) {
            t.join();
        }
    }
    
    // Memory-aligned allocation
    void* aligned_alloc(size_t size, size_t alignment = 64) {
        void* ptr = nullptr;
        
#ifdef _WIN32
        ptr = _aligned_malloc(size, alignment);
#else
        if (posix_memalign(&ptr, alignment, size) != 0) {
            ptr = nullptr;
        }
#endif
        
        return ptr;
    }
    
    void aligned_free(void* ptr) {
#ifdef _WIN32
        _aligned_free(ptr);
#else
        free(ptr);
#endif
    }
    
    // Cache-friendly data processing
    template<typename T>
    void process_data_cache_friendly(const std::vector<T>& data, 
                                   std::function<void(const T&)> processor) {
        const size_t cache_size = 32768;  // 32KB cache
        const size_t element_size = sizeof(T);
        const size_t elements_per_cache = cache_size / element_size;
        
        for (size_t i = 0; i < data.size(); i += elements_per_cache) {
            size_t end = std::min(i + elements_per_cache, data.size());
            
            // Process cache-sized chunks
            for (size_t j = i; j < end; ++j) {
                processor(data[j]);
            }
        }
    }
    
    // Performance monitoring
    void start_timer() {
        total_operations++;
    }
    
    void end_timer(uint64_t time_ns) {
        total_time_ns += time_ns;
    }
    
    double get_average_time_ns() const {
        if (total_operations == 0) return 0.0;
        return static_cast<double>(total_time_ns) / total_operations;
    }
    
    uint64_t get_total_operations() const {
        return total_operations;
    }
    
    // CPU feature detection
    void detect_cpu_features() {
        // This is a simplified version - in practice, you'd use CPUID
        has_avx = __builtin_cpu_supports("avx");
        has_avx2 = __builtin_cpu_supports("avx2");
        has_fma = __builtin_cpu_supports("fma");
        has_sse4_2 = __builtin_cpu_supports("sse4.2");
    }
    
private:
    std::string process_string_avx2(const std::string& input) {
        // AVX2-optimized string processing
        std::string result = input;
        
        // Simple example: convert to uppercase using AVX2
        if (input.length() >= 32) {
            char* data = result.data();
            size_t len = result.length();
            
            // Process 32-byte chunks with AVX2
            for (size_t i = 0; i < len; i += 32) {
                size_t chunk_size = std::min(size_t(32), len - i);
                
                // Load 32 bytes
                __m256i chunk = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(data + i));
                
                // Convert to uppercase (simplified)
                __m256i mask = _mm256_set1_epi8(0x20);
                __m256i upper = _mm256_and_si256(chunk, _mm256_set1_epi8(0xDF));
                
                // Store result
                _mm256_storeu_si256(reinterpret_cast<__m256i*>(data + i), upper);
            }
        }
        
        return result;
    }
    
    std::string process_string_sse4_2(const std::string& input) {
        // SSE4.2-optimized string processing
        std::string result = input;
        
        if (input.length() >= 16) {
            char* data = result.data();
            size_t len = result.length();
            
            // Process 16-byte chunks with SSE4.2
            for (size_t i = 0; i < len; i += 16) {
                size_t chunk_size = std::min(size_t(16), len - i);
                
                // Load 16 bytes
                __m128i chunk = _mm_loadu_si128(reinterpret_cast<const __m128i*>(data + i));
                
                // Simple processing (convert to uppercase)
                __m128i upper = _mm_and_si128(chunk, _mm_set1_epi8(0xDF));
                
                // Store result
                _mm_storeu_si128(reinterpret_cast<__m128i*>(data + i), upper);
            }
        }
        
        return result;
    }
    
    std::string process_string_scalar(const std::string& input) {
        // Scalar fallback
        std::string result = input;
        std::transform(result.begin(), result.end(), result.begin(), ::toupper);
        return result;
    }
};

// Global instance
static std::unique_ptr<CPUOptimizer> g_cpu_optimizer = nullptr;

// Python C API functions
static PyObject* init_cpu_optimizer(PyObject* self, PyObject* args) {
    if (g_cpu_optimizer) {
        return PyBool_FromLong(1);
    }
    
    g_cpu_optimizer = std::make_unique<CPUOptimizer>();
    return PyBool_FromLong(1);
}

static PyObject* get_cpu_info(PyObject* self, PyObject* args) {
    if (!g_cpu_optimizer) {
        PyErr_SetString(PyExc_RuntimeError, "CPU optimizer not initialized");
        return nullptr;
    }
    
    PyObject* info = PyDict_New();
    PyDict_SetItemString(info, "cores", PyLong_FromLong(std::thread::hardware_concurrency()));
    PyDict_SetItemString(info, "cache_line_size", PyLong_FromLong(64));
    
    return info;
}

static PyObject* process_strings_optimized(PyObject* self, PyObject* args) {
    PyObject* string_list;
    
    if (!PyArg_ParseTuple(args, "O", &string_list)) {
        return nullptr;
    }
    
    if (!PyList_Check(string_list)) {
        PyErr_SetString(PyExc_TypeError, "Expected list of strings");
        return nullptr;
    }
    
    if (!g_cpu_optimizer) {
        PyErr_SetString(PyExc_RuntimeError, "CPU optimizer not initialized");
        return nullptr;
    }
    
    // Convert Python list to C++ vector
    std::vector<std::string> input_strings;
    Py_ssize_t size = PyList_Size(string_list);
    
    for (Py_ssize_t i = 0; i < size; ++i) {
        PyObject* item = PyList_GetItem(string_list, i);
        if (!PyUnicode_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "All items must be strings");
            return nullptr;
        }
        
        const char* str = PyUnicode_AsUTF8(item);
        input_strings.emplace_back(str);
    }
    
    // Process strings
    auto result_strings = g_cpu_optimizer->process_strings_simd(input_strings);
    
    // Convert back to Python list
    PyObject* result_list = PyList_New(result_strings.size());
    for (size_t i = 0; i < result_strings.size(); ++i) {
        PyList_SetItem(result_list, i, PyUnicode_FromString(result_strings[i].c_str()));
    }
    
    return result_list;
}

static PyObject* get_performance_stats(PyObject* self, PyObject* args) {
    if (!g_cpu_optimizer) {
        PyErr_SetString(PyExc_RuntimeError, "CPU optimizer not initialized");
        return nullptr;
    }
    
    PyObject* stats = PyDict_New();
    PyDict_SetItemString(stats, "total_operations", PyLong_FromUnsignedLongLong(g_cpu_optimizer->get_total_operations()));
    PyDict_SetItemString(stats, "average_time_ns", PyFloat_FromDouble(g_cpu_optimizer->get_average_time_ns()));
    
    return stats;
}

static PyMethodDef CPUOptimizerMethods[] = {
    {"init", init_cpu_optimizer, METH_VARARGS, "Initialize CPU optimizer"},
    {"get_cpu_info", get_cpu_info, METH_VARARGS, "Get CPU information"},
    {"process_strings", process_strings_optimized, METH_VARARGS, "Process strings with CPU optimizations"},
    {"get_performance_stats", get_performance_stats, METH_VARARGS, "Get performance statistics"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef cpuoptimizermodule = {
    PyModuleDef_HEAD_INIT,
    "cpu_optimizer",
    "CPU optimization utilities",
    -1,
    CPUOptimizerMethods
};

PyMODINIT_FUNC PyInit_cpu_optimizer(void) {
    return PyModule_Create(&cpuoptimizermodule);
}
