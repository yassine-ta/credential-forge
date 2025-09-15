#include <thread>
#include <vector>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <future>
#include <functional>
#include <chrono>
#include <iostream>
#include <algorithm>

extern "C" {
    #include <Python.h>
}

class ParallelExecutor {
private:
    std::vector<std::thread> workers;
    std::queue<std::function<void()>> tasks;
    std::mutex queue_mutex;
    std::condition_variable condition;
    std::atomic<bool> stop{false};
    std::atomic<int> active_tasks{0};
    std::atomic<uint64_t> completed_tasks{0};
    std::atomic<uint64_t> total_execution_time{0};
    
    int num_threads;
    
public:
    ParallelExecutor(int threads = 0) : num_threads(threads) {
        if (num_threads <= 0) {
            num_threads = std::thread::hardware_concurrency();
        }
        
        // Start worker threads
        for (int i = 0; i < num_threads; ++i) {
            workers.emplace_back([this]() {
                worker_loop();
            });
        }
        
        std::cout << "Parallel Executor initialized with " << num_threads << " threads" << std::endl;
    }
    
    ~ParallelExecutor() {
        shutdown();
    }
    
    // Submit task for execution
    template<typename F, typename... Args>
    auto submit(F&& f, Args&&... args) -> std::future<decltype(f(args...))> {
        using ReturnType = decltype(f(args...));
        
        auto task = std::make_shared<std::packaged_task<ReturnType()>>(
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );
        
        std::future<ReturnType> result = task->get_future();
        
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            if (stop) {
                throw std::runtime_error("Executor has been stopped");
            }
            
            tasks.emplace([task]() {
                (*task)();
            });
        }
        
        condition.notify_one();
        return result;
    }
    
    // Submit multiple tasks in batch
    template<typename F, typename Iterator>
    std::vector<std::future<void>> submit_batch(F&& f, Iterator begin, Iterator end) {
        std::vector<std::future<void>> futures;
        futures.reserve(std::distance(begin, end));
        
        for (auto it = begin; it != end; ++it) {
            futures.push_back(submit(f, *it));
        }
        
        return futures;
    }
    
    // Wait for all tasks to complete
    void wait_for_all() {
        std::unique_lock<std::mutex> lock(queue_mutex);
        condition.wait(lock, [this]() {
            return tasks.empty() && active_tasks == 0;
        });
    }
    
    // Get execution statistics
    struct Stats {
        int num_threads;
        int active_tasks;
        uint64_t completed_tasks;
        uint64_t total_execution_time;
        double average_task_time;
    };
    
    Stats get_stats() const {
        Stats stats;
        stats.num_threads = num_threads;
        stats.active_tasks = active_tasks;
        stats.completed_tasks = completed_tasks;
        stats.total_execution_time = total_execution_time;
        stats.average_task_time = (completed_tasks > 0) ? 
            static_cast<double>(total_execution_time) / completed_tasks : 0.0;
        return stats;
    }
    
    // Shutdown executor
    void shutdown() {
        {
            std::unique_lock<std::mutex> lock(queue_mutex);
            stop = true;
        }
        
        condition.notify_all();
        
        for (std::thread& worker : workers) {
            if (worker.joinable()) {
                worker.join();
            }
        }
        
        workers.clear();
    }
    
private:
    void worker_loop() {
        while (true) {
            std::function<void()> task;
            
            {
                std::unique_lock<std::mutex> lock(queue_mutex);
                condition.wait(lock, [this]() {
                    return stop || !tasks.empty();
                });
                
                if (stop && tasks.empty()) {
                    return;
                }
                
                task = std::move(tasks.front());
                tasks.pop();
                active_tasks++;
            }
            
            // Execute task
            auto start_time = std::chrono::high_resolution_clock::now();
            task();
            auto end_time = std::chrono::high_resolution_clock::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::microseconds>(
                end_time - start_time).count();
            
            total_execution_time += duration;
            completed_tasks++;
            active_tasks--;
        }
    }
};

// Task scheduler for load balancing
class TaskScheduler {
private:
    std::vector<std::unique_ptr<ParallelExecutor>> executors;
    std::atomic<int> current_executor{0};
    
public:
    TaskScheduler(int num_executors = 1, int threads_per_executor = 0) {
        if (threads_per_executor <= 0) {
            threads_per_executor = std::thread::hardware_concurrency() / num_executors;
        }
        
        for (int i = 0; i < num_executors; ++i) {
            executors.push_back(std::make_unique<ParallelExecutor>(threads_per_executor));
        }
        
        std::cout << "Task Scheduler initialized with " << num_executors 
                  << " executors, " << threads_per_executor << " threads each" << std::endl;
    }
    
    ~TaskScheduler() {
        for (auto& executor : executors) {
            executor->shutdown();
        }
    }
    
    template<typename F, typename... Args>
    auto submit(F&& f, Args&&... args) -> std::future<decltype(f(args...))> {
        // Round-robin load balancing
        int executor_id = current_executor.fetch_add(1) % executors.size();
        return executors[executor_id]->submit(std::forward<F>(f), std::forward<Args>(args)...);
    }
    
    void wait_for_all() {
        for (auto& executor : executors) {
            executor->wait_for_all();
        }
    }
    
    std::vector<ParallelExecutor::Stats> get_all_stats() const {
        std::vector<ParallelExecutor::Stats> stats;
        for (const auto& executor : executors) {
            stats.push_back(executor->get_stats());
        }
        return stats;
    }
};

// Global instances
static std::unique_ptr<ParallelExecutor> g_executor = nullptr;
static std::unique_ptr<TaskScheduler> g_scheduler = nullptr;

// Python C API functions
static PyObject* init_parallel_executor(PyObject* self, PyObject* args) {
    int num_threads = 0;
    
    if (!PyArg_ParseTuple(args, "|i", &num_threads)) {
        return nullptr;
    }
    
    if (g_executor) {
        return PyBool_FromLong(1);
    }
    
    g_executor = std::make_unique<ParallelExecutor>(num_threads);
    return PyBool_FromLong(1);
}

static PyObject* init_task_scheduler(PyObject* self, PyObject* args) {
    int num_executors = 1;
    int threads_per_executor = 0;
    
    if (!PyArg_ParseTuple(args, "|ii", &num_executors, &threads_per_executor)) {
        return nullptr;
    }
    
    if (g_scheduler) {
        return PyBool_FromLong(1);
    }
    
    g_scheduler = std::make_unique<TaskScheduler>(num_executors, threads_per_executor);
    return PyBool_FromLong(1);
}

static PyObject* submit_task(PyObject* self, PyObject* args) {
    PyObject* callable;
    PyObject* args_tuple;
    
    if (!PyArg_ParseTuple(args, "OO", &callable, &args_tuple)) {
        return nullptr;
    }
    
    if (!PyCallable_Check(callable)) {
        PyErr_SetString(PyExc_TypeError, "First argument must be callable");
        return nullptr;
    }
    
    if (!g_executor) {
        PyErr_SetString(PyExc_RuntimeError, "Parallel executor not initialized");
        return nullptr;
    }
    
    // Create a wrapper function that calls the Python function
    auto wrapper = [callable, args_tuple]() {
        PyGILState_STATE gstate = PyGILState_Ensure();
        PyObject* result = PyObject_Call(callable, args_tuple, nullptr);
        PyGILState_Release(gstate);
        
        if (result) {
            Py_DECREF(result);
        }
    };
    
    try {
        auto future = g_executor->submit(wrapper);
        // For simplicity, we'll just return True
        // In a real implementation, you'd want to return a future object
        return PyBool_FromLong(1);
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

static PyObject* wait_for_completion(PyObject* self, PyObject* args) {
    if (!g_executor) {
        PyErr_SetString(PyExc_RuntimeError, "Parallel executor not initialized");
        return nullptr;
    }
    
    g_executor->wait_for_all();
    Py_RETURN_NONE;
}

static PyObject* get_executor_stats(PyObject* self, PyObject* args) {
    if (!g_executor) {
        PyErr_SetString(PyExc_RuntimeError, "Parallel executor not initialized");
        return nullptr;
    }
    
    auto stats = g_executor->get_stats();
    
    PyObject* result = PyDict_New();
    PyDict_SetItemString(result, "num_threads", PyLong_FromLong(stats.num_threads));
    PyDict_SetItemString(result, "active_tasks", PyLong_FromLong(stats.active_tasks));
    PyDict_SetItemString(result, "completed_tasks", PyLong_FromUnsignedLongLong(stats.completed_tasks));
    PyDict_SetItemString(result, "total_execution_time", PyLong_FromUnsignedLongLong(stats.total_execution_time));
    PyDict_SetItemString(result, "average_task_time", PyFloat_FromDouble(stats.average_task_time));
    
    return result;
}

static PyObject* shutdown_executor(PyObject* self, PyObject* args) {
    if (g_executor) {
        g_executor->shutdown();
        g_executor.reset();
    }
    
    if (g_scheduler) {
        g_scheduler.reset();
    }
    
    Py_RETURN_NONE;
}

static PyMethodDef ParallelExecutorMethods[] = {
    {"init_executor", init_parallel_executor, METH_VARARGS, "Initialize parallel executor"},
    {"init_scheduler", init_task_scheduler, METH_VARARGS, "Initialize task scheduler"},
    {"submit_task", submit_task, METH_VARARGS, "Submit task for parallel execution"},
    {"wait_for_completion", wait_for_completion, METH_VARARGS, "Wait for all tasks to complete"},
    {"get_stats", get_executor_stats, METH_VARARGS, "Get executor statistics"},
    {"shutdown", shutdown_executor, METH_VARARGS, "Shutdown executor"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef parallelexecutormodule = {
    PyModuleDef_HEAD_INIT,
    "parallel_executor",
    "Parallel execution utilities",
    -1,
    ParallelExecutorMethods
};

PyMODINIT_FUNC PyInit_parallel_executor(void) {
    return PyModule_Create(&parallelexecutormodule);
}