#include <memory>
#include <vector>
#include <unordered_map>
#include <mutex>
#include <atomic>
#include <chrono>
#include <iostream>
#include <algorithm>

extern "C" {
    #include <Python.h>
}

class MemoryManager {
private:
    struct MemoryBlock {
        void* ptr;
        size_t size;
        std::chrono::steady_clock::time_point allocated_time;
        bool in_use;
        
        MemoryBlock(void* p, size_t s) : ptr(p), size(s), in_use(true) {
            allocated_time = std::chrono::steady_clock::now();
        }
    };
    
    std::unordered_map<void*, MemoryBlock> allocated_blocks;
    std::mutex memory_mutex;
    std::atomic<size_t> total_allocated{0};
    std::atomic<size_t> peak_allocated{0};
    std::atomic<size_t> allocation_count{0};
    std::atomic<size_t> deallocation_count{0};
    
    size_t max_memory_limit;
    bool enable_tracking;
    
public:
    MemoryManager(size_t max_mem = 1024 * 1024 * 1024) : max_memory_limit(max_mem), enable_tracking(true) {
        std::cout << "Memory Manager initialized with limit: " << max_mem / (1024 * 1024) << " MB" << std::endl;
    }
    
    ~MemoryManager() {
        cleanup_all();
    }
    
    void* allocate(size_t size, size_t alignment = 64) {
        if (!enable_tracking) {
            return std::aligned_alloc(alignment, size);
        }
        
        std::lock_guard<std::mutex> lock(memory_mutex);
        
        // Check memory limit
        if (total_allocated + size > max_memory_limit) {
            std::cerr << "Memory limit exceeded: " << total_allocated << " + " << size 
                      << " > " << max_memory_limit << std::endl;
            return nullptr;
        }
        
        void* ptr = std::aligned_alloc(alignment, size);
        if (!ptr) {
            return nullptr;
        }
        
        // Track allocation
        allocated_blocks[ptr] = MemoryBlock(ptr, size);
        total_allocated += size;
        peak_allocated = std::max(peak_allocated.load(), total_allocated.load());
        allocation_count++;
        
        return ptr;
    }
    
    void deallocate(void* ptr) {
        if (!ptr) return;
        
        if (!enable_tracking) {
            std::free(ptr);
            return;
        }
        
        std::lock_guard<std::mutex> lock(memory_mutex);
        
        auto it = allocated_blocks.find(ptr);
        if (it != allocated_blocks.end()) {
            total_allocated -= it->second.size;
            allocated_blocks.erase(it);
            deallocation_count++;
        }
        
        std::free(ptr);
    }
    
    void cleanup_unused() {
        std::lock_guard<std::mutex> lock(memory_mutex);
        
        auto now = std::chrono::steady_clock::now();
        auto timeout = std::chrono::minutes(5);  // 5 minute timeout
        
        auto it = allocated_blocks.begin();
        while (it != allocated_blocks.end()) {
            if (!it->second.in_use && 
                (now - it->second.allocated_time) > timeout) {
                std::free(it->first);
                total_allocated -= it->second.size;
                it = allocated_blocks.erase(it);
            } else {
                ++it;
            }
        }
    }
    
    void cleanup_all() {
        std::lock_guard<std::mutex> lock(memory_mutex);
        
        for (auto& pair : allocated_blocks) {
            std::free(pair.first);
        }
        allocated_blocks.clear();
        total_allocated = 0;
    }
    
    size_t get_total_allocated() const {
        return total_allocated;
    }
    
    size_t get_peak_allocated() const {
        return peak_allocated;
    }
    
    size_t get_allocation_count() const {
        return allocation_count;
    }
    
    size_t get_deallocation_count() const {
        return deallocation_count;
    }
    
    size_t get_active_blocks() const {
        std::lock_guard<std::mutex> lock(memory_mutex);
        return allocated_blocks.size();
    }
    
    void set_memory_limit(size_t limit) {
        max_memory_limit = limit;
    }
    
    void set_tracking(bool enable) {
        enable_tracking = enable;
    }
    
    // Memory pool for frequent allocations
    class MemoryPool {
    private:
        std::vector<void*> free_blocks;
        size_t block_size;
        size_t pool_size;
        std::mutex pool_mutex;
        
    public:
        MemoryPool(size_t block_sz, size_t initial_blocks = 100) 
            : block_size(block_sz), pool_size(initial_blocks) {
            for (size_t i = 0; i < initial_blocks; ++i) {
                void* block = std::aligned_alloc(64, block_size);
                if (block) {
                    free_blocks.push_back(block);
                }
            }
        }
        
        ~MemoryPool() {
            std::lock_guard<std::mutex> lock(pool_mutex);
            for (void* block : free_blocks) {
                std::free(block);
            }
        }
        
        void* get_block() {
            std::lock_guard<std::mutex> lock(pool_mutex);
            if (free_blocks.empty()) {
                return std::aligned_alloc(64, block_size);
            }
            
            void* block = free_blocks.back();
            free_blocks.pop_back();
            return block;
        }
        
        void return_block(void* block) {
            if (!block) return;
            
            std::lock_guard<std::mutex> lock(pool_mutex);
            if (free_blocks.size() < pool_size * 2) {  // Limit pool size
                free_blocks.push_back(block);
            } else {
                std::free(block);
            }
        }
    };
    
    // Get memory pool for specific block size
    MemoryPool& get_pool(size_t block_size) {
        static std::unordered_map<size_t, std::unique_ptr<MemoryPool>> pools;
        static std::mutex pools_mutex;
        
        std::lock_guard<std::mutex> lock(pools_mutex);
        
        auto it = pools.find(block_size);
        if (it == pools.end()) {
            pools[block_size] = std::make_unique<MemoryPool>(block_size);
            it = pools.find(block_size);
        }
        
        return *it->second;
    }
};

// Global instance
static std::unique_ptr<MemoryManager> g_memory_manager = nullptr;

// Python C API functions
static PyObject* init_memory_manager(PyObject* self, PyObject* args) {
    size_t max_memory = 1024 * 1024 * 1024;  // 1GB default
    
    if (!PyArg_ParseTuple(args, "|K", &max_memory)) {
        return nullptr;
    }
    
    if (g_memory_manager) {
        return PyBool_FromLong(1);
    }
    
    g_memory_manager = std::make_unique<MemoryManager>(max_memory);
    return PyBool_FromLong(1);
}

static PyObject* allocate_memory(PyObject* self, PyObject* args) {
    size_t size;
    size_t alignment = 64;
    
    if (!PyArg_ParseTuple(args, "K|K", &size, &alignment)) {
        return nullptr;
    }
    
    if (!g_memory_manager) {
        PyErr_SetString(PyExc_RuntimeError, "Memory manager not initialized");
        return nullptr;
    }
    
    void* ptr = g_memory_manager->allocate(size, alignment);
    if (!ptr) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory");
        return nullptr;
    }
    
    return PyLong_FromVoidPtr(ptr);
}

static PyObject* deallocate_memory(PyObject* self, PyObject* args) {
    void* ptr;
    
    if (!PyArg_ParseTuple(args, "L", &ptr)) {
        return nullptr;
    }
    
    if (!g_memory_manager) {
        PyErr_SetString(PyExc_RuntimeError, "Memory manager not initialized");
        return nullptr;
    }
    
    g_memory_manager->deallocate(ptr);
    Py_RETURN_NONE;
}

static PyObject* get_memory_stats(PyObject* self, PyObject* args) {
    if (!g_memory_manager) {
        PyErr_SetString(PyExc_RuntimeError, "Memory manager not initialized");
        return nullptr;
    }
    
    PyObject* stats = PyDict_New();
    PyDict_SetItemString(stats, "total_allocated", PyLong_FromUnsignedLongLong(g_memory_manager->get_total_allocated()));
    PyDict_SetItemString(stats, "peak_allocated", PyLong_FromUnsignedLongLong(g_memory_manager->get_peak_allocated()));
    PyDict_SetItemString(stats, "allocation_count", PyLong_FromUnsignedLongLong(g_memory_manager->get_allocation_count()));
    PyDict_SetItemString(stats, "deallocation_count", PyLong_FromUnsignedLongLong(g_memory_manager->get_deallocation_count()));
    PyDict_SetItemString(stats, "active_blocks", PyLong_FromUnsignedLongLong(g_memory_manager->get_active_blocks()));
    
    return stats;
}

static PyObject* cleanup_memory(PyObject* self, PyObject* args) {
    if (!g_memory_manager) {
        PyErr_SetString(PyExc_RuntimeError, "Memory manager not initialized");
        return nullptr;
    }
    
    g_memory_manager->cleanup_unused();
    Py_RETURN_NONE;
}

static PyMethodDef MemoryManagerMethods[] = {
    {"init", init_memory_manager, METH_VARARGS, "Initialize memory manager"},
    {"allocate", allocate_memory, METH_VARARGS, "Allocate aligned memory"},
    {"deallocate", deallocate_memory, METH_VARARGS, "Deallocate memory"},
    {"get_stats", get_memory_stats, METH_VARARGS, "Get memory statistics"},
    {"cleanup", cleanup_memory, METH_VARARGS, "Cleanup unused memory"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef memorymanagermodule = {
    PyModuleDef_HEAD_INIT,
    "memory_manager",
    "Memory management utilities",
    -1,
    MemoryManagerMethods
};

PyMODINIT_FUNC PyInit_memory_manager(void) {
    return PyModule_Create(&memorymanagermodule);
}
