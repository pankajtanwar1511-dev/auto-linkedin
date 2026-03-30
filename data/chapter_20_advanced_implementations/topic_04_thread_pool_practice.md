### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1
Add a `wait_for_all()` method that blocks until all submitted tasks complete.

Implement this exercise.

**Answer:**

```cpp
class ThreadPool {
private:
    std::atomic<size_t> active_tasks_{0};
    std::atomic<size_t> queued_tasks_{0};
    std::condition_variable all_done_cv_;
    std::mutex all_done_mutex_;

public:
    void submit(...) {
        // ...
        queued_tasks_.fetch_add(1);
    }

    void worker_loop() {
        // ...
        active_tasks_.fetch_add(1);
        queued_tasks_.fetch_sub(1);

        task();

        active_tasks_.fetch_sub(1);

        if (active_tasks_.load() == 0 && queued_tasks_.load() == 0) {
            all_done_cv_.notify_all();
        }
    }

    void wait_for_all() {
        std::unique_lock<std::mutex> lock(all_done_mutex_);
        all_done_cv_.wait(lock, [this]() {
            return active_tasks_.load() == 0 && queued_tasks_.load() == 0;
        });
    }
};
```

**Usage:**
```cpp
pool.submit(task1);
pool.submit(task2);
pool.wait_for_all();  // Blocks until both complete
std::cout << "All done\n";
```

---

#### Q2
Modify the pool to support task cancellation. How would you implement a `cancel(task_id)` method?

Implement this exercise.

**Answer:**

- struct Task { TaskID id; std::function<void()> func; std::atomic<bool> cancelled{false}; };
- std::atomic<TaskID> next_id_{0}; std::map<TaskID, std::shared_ptr<Task>> tasks_; // Track by ID
- public: TaskID submit(std::function<void()> func) { TaskID id = next_id_.fetch_add(1); auto task = std::make_shared<Task>(Task{id, std::move(func), false});
- { std::lock_guard<std::mutex> lock(mutex_); tasks_[id] = task; task_queue_.push(task); }
- cv_.notify_one(); return id; }

**Usage:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
Implement a thread pool with timeout: tasks that run longer than X seconds are terminated.

Implement this exercise.

**Answer:**

**Not directly possible in C++** (no `pthread_cancel` equivalent).

**Workarounds:**

**Option 1: Cooperative cancellation (token-based):**

```cpp
class CancellationToken {
    std::atomic<bool> cancelled_{false};

public:
    void cancel() { cancelled_.store(true); }
    bool is_cancelled() const { return cancelled_.load(); }
};

void long_task(CancellationToken& token) {
    for (int i = 0; i < 1000000; ++i) {
        if (token.is_cancelled()) {
            std::cout << "Task cancelled\n";
            return;
        }
        // Work...
    }
}

// In pool:
auto token = std::make_shared<CancellationToken>();

auto timeout_future = std::async(std::launch::async, [token]() {
    std::this_thread::sleep_for(std::chrono::seconds(5));
    token->cancel();
});

pool.submit(long_task, std::ref(*token));
```

**Option 2: Separate process (kill via signal):**
- Fork process for each task
- Kill process if timeout
- Heavy overhead

**Best practice:** Design tasks to be interruptible (check flag periodically).

---

#### Q4
Add support for task dependencies: task B cannot run until task A completes.

Implement this exercise.

**Answer:**

- std::map<TaskID, std::shared_ptr<Task>> tasks_; std::multimap<TaskID, TaskID> dependents_; // dep_id → dependent_id
- { std::lock_guard<std::mutex> lock(mutex_); tasks_[id] = task;
- for (TaskID dep : dependencies) { dependents_.insert({dep, id}); }
- if (dependencies.empty()) { task->ready = true; ready_queue_.push(task); cv_.notify_one(); } }
- void on_task_complete(TaskID completed_id) { std::lock_guard<std::mutex> lock(mutex_);

**Usage:**

- */ }); TaskID task_b = pool.submit([]() { /* ..
- */ }, {task_a}); // Depends on A ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
Benchmark thread pool vs serial execution for 1000 small tasks. At what task granularity does parallelism stop being beneficial?

Implement this exercise.

**Answer:**
```cpp
#include <chrono>
#include <iostream>
void benchmark(int task_duration_us) {
    const int NUM_TASKS = 1000;
    auto work = [task_duration_us]() {
        auto start = std::chrono::high_resolution_clock::now();
        while (std::chrono::duration_cast<std::chrono::microseconds>(
                   std::chrono::high_resolution_clock::now() - start
               ).count() < task_duration_us) {
            // Busy wait
    // ... (additional code omitted for brevity)
```
- cpp #include <chrono> #include <iostream>
- void benchmark(int task_duration_us) { const int NUM_TASKS = 1000;
- // Parallel execution ThreadPool pool(std::thread::hardware_concurrency());
**Typical output (8-core CPU):**
```cpp
Task duration: 1 μs
  Serial:   1 ms
  Parallel: 15 ms
  Speedup:  0.07x  ← Slower!
Task duration: 10 μs
  Serial:   10 ms
  Parallel: 8 ms
  Speedup:  1.25x
Task duration: 100 μs
  Serial:   100 ms
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
