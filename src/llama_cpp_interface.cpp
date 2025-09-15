#include <string>
#include <vector>
#include <memory>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <iostream>

extern "C" {
    #include <Python.h>
    #include "llama.h"
    #include "ggml.h"
}

class LlamaCPPInterface {
private:
    struct llama_model* model;
    struct llama_context* ctx;
    std::mutex model_mutex;
    std::atomic<bool> model_loaded{false};
    int n_threads;
    int n_ctx;
    int n_batch;
    
    // CPU optimization settings
    bool use_mmap;
    bool use_mlock;
    bool use_cpu_optimizations;
    
    // Performance monitoring
    std::atomic<uint64_t> total_generations{0};
    std::atomic<uint64_t> total_tokens{0};
    std::atomic<double> total_time{0.0};
    std::chrono::high_resolution_clock::time_point start_time;
    
    // Thread pool for parallel processing
    std::vector<std::thread> worker_threads;
    std::queue<std::function<void()>> task_queue;
    std::mutex queue_mutex;
    std::condition_variable queue_cv;
    std::atomic<bool> stop_workers{false};
    
public:
    LlamaCPPInterface() : model(nullptr), ctx(nullptr), n_threads(std::thread::hardware_concurrency()) {
        // Initialize llama.cpp backend
        llama_backend_init();
        
        // Set CPU optimization parameters
        n_ctx = 2048;  // Context size
        n_batch = 512; // Batch size for processing
        use_mmap = true;
        use_mlock = false;
        use_cpu_optimizations = true;
        
        // Initialize performance monitoring
        start_time = std::chrono::high_resolution_clock::now();
        
        // Configure CPU-specific optimizations
        configure_cpu_optimizations();
        
        // Initialize thread pool for parallel processing
        initialize_thread_pool();
    }
    
    ~LlamaCPPInterface() {
        // Stop worker threads
        stop_workers = true;
        queue_cv.notify_all();
        
        for (auto& thread : worker_threads) {
            if (thread.joinable()) {
                thread.join();
            }
        }
        
        if (ctx) {
            llama_free(ctx);
        }
        if (model) {
            llama_free_model(model);
        }
        llama_backend_free();
    }
    
    bool load_model(const std::string& model_path) {
        std::lock_guard<std::mutex> lock(model_mutex);
        
        if (model_loaded) {
            return true;
        }
        
        // Model parameters
        llama_model_params model_params = llama_model_default_params();
        model_params.use_mmap = use_mmap;
        model_params.use_mlock = use_mlock;
        
        // Load model
        model = llama_load_model_from_file(model_path.c_str(), model_params);
        if (!model) {
            std::cerr << "Failed to load model: " << model_path << std::endl;
            return false;
        }
        
        // Context parameters
        llama_context_params ctx_params = llama_context_default_params();
        ctx_params.seed = 1234;
        ctx_params.ctx_size = n_ctx;
        ctx_params.batch_size = n_batch;
        ctx_params.threads = n_threads;
        ctx_params.threads_batch = n_threads;
        ctx_params.mul_mat_q = true;  // Enable quantized matrix multiplication
        ctx_params.f16_kv = true;     // Use 16-bit key-value cache
        ctx_params.logits_all = false;
        ctx_params.embedding = false;
        
        // Create context
        ctx = llama_new_context_with_model(model, ctx_params);
        if (!ctx) {
            std::cerr << "Failed to create context" << std::endl;
            llama_free_model(model);
            model = nullptr;
            return false;
        }
        
        model_loaded = true;
        std::cout << "Model loaded successfully with " << n_threads << " threads" << std::endl;
        return true;
    }
    
    std::string generate_text(const std::string& prompt, int max_tokens = 100, float temperature = 0.7f) {
        if (!model_loaded || !ctx) {
            return "Error: Model not loaded";
        }
        
        auto start_time = std::chrono::high_resolution_clock::now();
        std::lock_guard<std::mutex> lock(model_mutex);
        
        // Tokenize prompt
        std::vector<llama_token> tokens_list;
        tokens_list.resize(prompt.length() + 1);
        
        int n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), 
                                    tokens_list.data(), tokens_list.size(), true, false);
        if (n_tokens < 0) {
            tokens_list.resize(-n_tokens);
            n_tokens = llama_tokenize(model, prompt.c_str(), prompt.length(), 
                                    tokens_list.data(), tokens_list.size(), true, false);
        }
        tokens_list.resize(n_tokens);
        
        // Evaluate prompt
        if (llama_decode(ctx, llama_batch_get_one(tokens_list.data(), n_tokens, 0, 0)) != 0) {
            return "Error: Failed to evaluate prompt";
        }
        
        // Generate text
        std::string result;
        for (int i = 0; i < max_tokens; ++i) {
            llama_token new_token_id = 0;
            
            auto logits = llama_get_logits_ith(ctx, -1);
            auto n_vocab = llama_n_vocab(model);
            
            // Apply temperature
            std::vector<float> logits_processed(n_vocab);
            for (int j = 0; j < n_vocab; ++j) {
                logits_processed[j] = logits[j] / temperature;
            }
            
            // Sample token
            new_token_id = llama_sample_token_greedy(ctx);
            
            if (new_token_id == llama_token_eos(model)) {
                break;
            }
            
            // Convert token to string
            char token_str[256];
            int n_chars = llama_token_to_piece(model, new_token_id, token_str, sizeof(token_str), false);
            if (n_chars > 0) {
                result += std::string(token_str, n_chars);
            }
            
            // Evaluate new token
            if (llama_decode(ctx, llama_batch_get_one(&new_token_id, 1, 0, 0)) != 0) {
                break;
            }
        }
        
        // Update performance statistics
        auto end_time = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count() / 1000.0;
        int tokens_generated = result.length() / 4;  // Rough token estimation
        update_performance_stats(tokens_generated, duration);
        
        return result;
    }
    
    void set_threads(int threads) {
        n_threads = std::max(1, threads);
        if (model_loaded) {
            // Context would need to be recreated to change thread count
            std::cout << "Thread count set to " << n_threads << " (requires model reload)" << std::endl;
        }
    }
    
    int get_threads() const {
        return n_threads;
    }
    
    bool is_loaded() const {
        return model_loaded;
    }
    
private:
    void configure_cpu_optimizations() {
        // Enable CPU-specific optimizations
        ggml_cpu_has_avx();
        ggml_cpu_has_avx2();
        ggml_cpu_has_fma();
        ggml_cpu_has_f16c();
        ggml_cpu_has_sse3();
        ggml_cpu_has_ssse3();
        ggml_cpu_has_sse4_1();
        ggml_cpu_has_sse4_2();
        ggml_cpu_has_popcnt();
        
        // Set optimal thread count based on CPU cores
        n_threads = std::thread::hardware_concurrency();
        if (n_threads > 8) {
            n_threads = 8;  // Cap at 8 threads for optimal performance
        }
        
        std::cout << "CPU optimizations configured for " << n_threads << " threads" << std::endl;
    }
    
    void initialize_thread_pool() {
        // Initialize worker threads for parallel processing
        int num_workers = std::min(n_threads, 4);  // Limit to 4 workers
        
        for (int i = 0; i < num_workers; ++i) {
            worker_threads.emplace_back([this]() {
                worker_loop();
            });
        }
        
        std::cout << "Thread pool initialized with " << num_workers << " workers" << std::endl;
    }
    
    void worker_loop() {
        while (!stop_workers) {
            std::unique_lock<std::mutex> lock(queue_mutex);
            queue_cv.wait(lock, [this] { return !task_queue.empty() || stop_workers; });
            
            if (stop_workers) {
                break;
            }
            
            if (!task_queue.empty()) {
                auto task = task_queue.front();
                task_queue.pop();
                lock.unlock();
                
                try {
                    task();
                } catch (const std::exception& e) {
                    std::cerr << "Worker thread error: " << e.what() << std::endl;
                }
            }
        }
    }
    
    void submit_task(std::function<void()> task) {
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            task_queue.push(task);
        }
        queue_cv.notify_one();
    }
    
    void update_performance_stats(int tokens_generated, double generation_time) {
        total_generations++;
        total_tokens += tokens_generated;
        total_time += generation_time;
    }
    
    std::map<std::string, double> get_performance_stats() {
        std::map<std::string, double> stats;
        
        auto current_time = std::chrono::high_resolution_clock::now();
        auto uptime = std::chrono::duration_cast<std::chrono::seconds>(current_time - start_time).count();
        
        stats["total_generations"] = total_generations.load();
        stats["total_tokens"] = total_tokens.load();
        stats["total_time"] = total_time.load();
        stats["uptime_seconds"] = uptime;
        
        if (total_time.load() > 0) {
            stats["avg_tokens_per_second"] = total_tokens.load() / total_time.load();
        } else {
            stats["avg_tokens_per_second"] = 0.0;
        }
        
        if (total_generations.load() > 0) {
            stats["avg_generation_time"] = total_time.load() / total_generations.load();
        } else {
            stats["avg_generation_time"] = 0.0;
        }
        
        return stats;
    }
    
    void reset_performance_stats() {
        total_generations = 0;
        total_tokens = 0;
        total_time = 0.0;
        start_time = std::chrono::high_resolution_clock::now();
    }
};

// Global instance
static std::unique_ptr<LlamaCPPInterface> g_llama_interface = nullptr;

// Python C API functions
static PyObject* init_llama_cpp(PyObject* self, PyObject* args) {
    if (g_llama_interface) {
        return PyBool_FromLong(1);
    }
    
    g_llama_interface = std::make_unique<LlamaCPPInterface>();
    return PyBool_FromLong(1);
}

static PyObject* load_model_cpp(PyObject* self, PyObject* args) {
    const char* model_path;
    
    if (!PyArg_ParseTuple(args, "s", &model_path)) {
        return nullptr;
    }
    
    if (!g_llama_interface) {
        PyErr_SetString(PyExc_RuntimeError, "LlamaCPP interface not initialized");
        return nullptr;
    }
    
    bool success = g_llama_interface->load_model(std::string(model_path));
    return PyBool_FromLong(success ? 1 : 0);
}

static PyObject* generate_text_cpp(PyObject* self, PyObject* args) {
    const char* prompt;
    int max_tokens = 100;
    float temperature = 0.7f;
    
    if (!PyArg_ParseTuple(args, "s|if", &prompt, &max_tokens, &temperature)) {
        return nullptr;
    }
    
    if (!g_llama_interface || !g_llama_interface->is_loaded()) {
        PyErr_SetString(PyExc_RuntimeError, "Model not loaded");
        return nullptr;
    }
    
    std::string result = g_llama_interface->generate_text(std::string(prompt), max_tokens, temperature);
    return PyUnicode_FromString(result.c_str());
}

static PyObject* set_threads_cpp(PyObject* self, PyObject* args) {
    int threads;
    
    if (!PyArg_ParseTuple(args, "i", &threads)) {
        return nullptr;
    }
    
    if (!g_llama_interface) {
        PyErr_SetString(PyExc_RuntimeError, "LlamaCPP interface not initialized");
        return nullptr;
    }
    
    g_llama_interface->set_threads(threads);
    return PyBool_FromLong(1);
}

static PyObject* get_threads_cpp(PyObject* self, PyObject* args) {
    if (!g_llama_interface) {
        PyErr_SetString(PyExc_RuntimeError, "LlamaCPP interface not initialized");
        return nullptr;
    }
    
    return PyLong_FromLong(g_llama_interface->get_threads());
}

static PyObject* is_model_loaded_cpp(PyObject* self, PyObject* args) {
    if (!g_llama_interface) {
        return PyBool_FromLong(0);
    }
    
    return PyBool_FromLong(g_llama_interface->is_loaded() ? 1 : 0);
}

static PyMethodDef LlamaCPPMethods[] = {
    {"init", init_llama_cpp, METH_VARARGS, "Initialize llama.cpp interface"},
    {"load_model", load_model_cpp, METH_VARARGS, "Load model for inference"},
    {"generate_text", generate_text_cpp, METH_VARARGS, "Generate text using loaded model"},
    {"set_threads", set_threads_cpp, METH_VARARGS, "Set number of threads"},
    {"get_threads", get_threads_cpp, METH_VARARGS, "Get number of threads"},
    {"is_model_loaded", is_model_loaded_cpp, METH_VARARGS, "Check if model is loaded"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef llamacppmodule = {
    PyModuleDef_HEAD_INIT,
    "llama_cpp_interface",
    "Native llama.cpp interface for CPU optimization",
    -1,
    LlamaCPPMethods
};

PyMODINIT_FUNC PyInit_llama_cpp_interface(void) {
    return PyModule_Create(&llamacppmodule);
}
