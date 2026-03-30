## TOPIC: Async, Promise, and Future - Asynchronous Task Management

### PRACTICE_TASKS: Output Prediction and Code Analysis

#### Q1
```cpp
auto fut = std::async(std::launch::deferred, []{ return 42; });
std::cout << "Before get\n";
int val = fut.get();
std::cout << "After get: " << val << "\n";

// When does the lambda execute?
```

**Answer:**

```cpp
Lambda executes during fut.get()
```

- Lambda executes during fut.get() ```

**Explanation:**

- **std::launch::deferred:** Lazy execution policy
- **Execution timeline:**

```cpp
auto fut = std::async(std::launch::async, []{ return 42; });
// Lambda starts immediately in new thread
```

- cpp auto fut = std::async(std::launch::async, []{ return 42; }); // Lambda starts immediately in new thread ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

prom.set_value(10);
int a = fut.get();
int b = fut.get();

// What happens at the second get()?
```

**Answer:**



**Explanation:**

- **Future is single-use** - can only call get() once
- **Execution flow:**
- **Exception details:**
- **After first get():**
- Future becomes invalid

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
auto fut = std::async(std::launch::async, []{
    std::this_thread::sleep_for(std::chrono::seconds(2));
    return 100;
});

// fut goes out of scope here

std::cout << "Done\n";

// When does "Done" print?
```

**Answer:**

```cpp
"Done" prints after 2 seconds
```

- "Done" prints after 2 seconds ```

**Explanation:**

- **Future destructor from std::async is BLOCKING** - critical behavior
- **Execution timeline:**
1. async() launches task in new thread
2. Thread starts executing (sleeps 2 seconds)

```cpp
void process() {
      std::async(std::launch::async, []{
          std::this_thread::sleep_for(std::chrono::seconds(5));
      });  // Temporary future destroyed here - BLOCKS 5 seconds!
      std::cout << "Done\n";  // Prints after 5 seconds
  }
```

- cpp void process() { std::async(std::launch::async, []{ std::this_thread::sleep_for(std::chrono::seconds(5)); }); // Temporary future destroyed here - BLOCKS 5 seconds
- std::cout << "Done\n"; // Prints after 5 seconds } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

std::thread t([prom = std::move(prom)]() mutable {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    prom.set_value(42);
});

int val = fut.get();
t.join();

// Is this code correct? What is val?
```

**Answer:**



**Explanation:**

- **Promise-future communication across threads** - correct pattern
- **Step-by-step execution:**
- **Why move is necessary:**
- Promise is move-only (non-copyable)
- Transfer ownership to thread

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
auto fut = std::async(std::launch::async, []{
    throw std::runtime_error("Error!");
    return 42;
});

std::this_thread::sleep_for(std::chrono::seconds(1));
// What happens here? Is exception thrown?

int val = fut.get();

// When is the exception thrown?
```

**Answer:**

```cpp
Exception not thrown during sleep
Exception thrown on fut.get()
```

- Exception not thrown during sleep Exception thrown on fut.get() ```

**Explanation:**

- **Exception propagation through futures** - stored and rethrown pattern
- **Execution timeline:**
1. async() launches task in new thread
2. Task throws std::runtime_error

```cpp
try {
      int val = fut.get();  // Rethrows stored exception
  } catch (const std::runtime_error& e) {
      std::cout << e.what();  // "Error!"
  }
```

- cpp try { int val = fut.get(); // Rethrows stored exception } catch (const std::runtime_error& e) { std::cout << e.what(); // "Error!" } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
std::future<int> fut;
std::cout << fut.valid() << "\n";

fut = std::async([]{ return 10; });
std::cout << fut.valid() << "\n";

fut.get();
std::cout << fut.valid() << "\n";

// What are the three outputs?
```

**Answer:**
```cpp
0, 1, 0
```
**Explanation:**
- **Future validity states** - tracks whether future has shared state
- **Execution breakdown:**
```cpp
std::future<int> fut;  // No shared state
  std::cout << fut.valid();  // 0 (false)
```
- cpp std::future<int> fut; // No shared state std::cout << fut.valid(); // 0 (false) ```
**Valid future can:**
```cpp
if (fut.valid()) {
      fut.get();        // OK
      fut.wait();       // OK
      fut.wait_for(...); // OK
      fut.share();      // OK
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

{
    std::thread t([&prom] {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        prom.set_value(100);
    });
    t.detach();
}

int val = fut.get();

// Is this code safe? What could go wrong?
```

**Answer:**

```cpp
Unsafe: race condition and use-after-scope
```

- Unsafe: race condition and use-after-scope ```

**Explanation:**

- **Multiple safety issues** - dangerous pattern
**Issue 1: Promise capture by reference with detached thread**
- Lambda captures prom by reference: `[&prom]`
- Thread detached: runs independently

```cpp
T0: Thread created, prom captured by reference
  T1: Thread detached
  T2: Block scope ends → prom destroyed
  T3: Thread wakes from sleep
  T4: Thread accesses &prom → DANGLING REFERENCE!
  T5: Undefined behavior (crash/corruption/silent failure)
```

- T0: Thread created, prom captured by reference T1: Thread detached T2: Block scope ends → prom destroyed T3: Thread wakes from sleep T4: Thread accesses &prom → DANGLING REFERENCE
- T5: Undefined behavior (crash/corruption/silent failure) ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
auto fut = std::async(std::launch::async, []{ return 42; });

if (fut.wait_for(std::chrono::milliseconds(10)) == std::future_status::ready) {
    std::cout << "Ready\n";
} else {
    std::cout << "Not ready\n";
}

int val = fut.get();

// Can we still call get() after wait_for()?
```

**Answer:**

```cpp
Yes, future remains valid after wait_for()
```

- Yes, future remains valid after wait_for() ```

**Explanation:**

- **wait_for() is non-destructive** - doesn't consume future
- **Execution flow:**
1. async() launches task
2. wait_for(10ms) called

```cpp
enum class future_status {
      ready,     // Task completed
      timeout,   // Timeout elapsed, task not done
      deferred   // Task deferred (launch::deferred)
  };
```

- cpp enum class future_status { ready, // Task completed timeout, // Timeout elapsed, task not done deferred // Task deferred (launch::deferred) }; ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
std::promise<void> prom;
std::future<void> fut = prom.get_future();

std::thread t([prom = std::move(prom)]() mutable {
    std::cout << "Task done\n";
    prom.set_value();
});

fut.get();
std::cout << "Main done\n";
t.join();

// What is the order of output?
```

**Answer:**

```cpp
"Task done"
"Main done"
```

- "Task done" "Main done" ```

**Explanation:**

- **Promise<void> for signaling** - no value, just notification
- **Synchronization timeline:**
1. Promise and future created
2. Thread starts with moved promise

```cpp
std::promise<void> p;
  p.set_value();  // No argument!

  std::future<void> f = p.get_future();
  f.get();  // Returns void, just waits
```

- cpp std::promise<void> p; p.set_value(); // No argument
- std::future<void> f = p.get_future(); f.get(); // Returns void, just waits ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
std::packaged_task<int()> task([]{ return 42; });
std::future<int> fut = task.get_future();

// Task not executed yet

int val = fut.get();

// What happens? Will this block forever?
```

**Answer:**

```cpp
Blocks forever (deadlock)
```

- Blocks forever (deadlock) ```

**Explanation:**

- **packaged_task is manual execution** - must be called explicitly
- **What packaged_task does:**
- Wraps callable (function, lambda, functor)
- Provides future for result

```cpp
std::packaged_task<int()> task([]{ return 42; });
  std::future<int> fut = task.get_future();

  task();  // EXECUTE the task! Returns void

  int val = fut.get();  // Now works, val = 42
```

- cpp std::packaged_task<int()> task([]{ return 42; }); std::future<int> fut = task.get_future();
- task(); // EXECUTE the task
- int val = fut.get(); // Now works, val = 42 ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

prom.set_value(10);
prom.set_value(20);

// What happens at the second set_value?
```

**Answer:**

```cpp
Throws std::future_error (promise_already_satisfied)
```

- Throws std::future_error (promise_already_satisfied) ```

**Explanation:**

- **Promise can only be satisfied once** - single-shot mechanism
- **Execution flow:**
1. Promise created
2. Future obtained

```cpp
try {
      prom.set_value(10);  // OK
      prom.set_value(20);  // Throws
  } catch (const std::future_error& e) {
      // e.code() == std::future_errc::promise_already_satisfied
      std::cout << "Promise already set!\n";
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
std::shared_future<int> create_shared() {
    std::promise<int> prom;
    prom.set_value(42);
    return prom.get_future().share();
}

auto sf = create_shared();
int a = sf.get();
int b = sf.get();

// Can we call get() twice on shared_future?
```

**Answer:**

```cpp
Yes, both get() calls succeed, a=42, b=42
```

- Yes, both get() calls succeed, a=42, b=42 ```

**Explanation:**

- **shared_future allows multiple get() calls** - unlike regular future
- **Execution flow:**
1. Promise created and set to 42
2. Future obtained and converted to shared_future via share()

```cpp
// Regular future: Single-use
  std::future<int> fut = ...;
  int a = fut.get();  // OK, fut becomes invalid
  int b = fut.get();  // Throws no_state

  // Shared future: Multi-use
  std::shared_future<int> sf = ...;
  int a = sf.get();   // OK, sf still valid
  int b = sf.get();   // OK, returns same value
```

- cpp // Regular future: Single-use std::future<int> fut = ...; int a = fut.get(); // OK, fut becomes invalid int b = fut.get(); // Throws no_state
- // Shared future: Multi-use std::shared_future<int> sf = ...; int a = sf.get(); // OK, sf still valid int b = sf.get(); // OK, returns same value ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
auto fut1 = std::async(std::launch::async, []{ return 1; });
auto fut2 = std::move(fut1);

std::cout << fut1.valid() << " " << fut2.valid() << "\n";

// What is the output?
```

**Answer:**

```cpp
0 1
```

**Explanation:**

- **Future is move-only, not copyable** - ownership transfer
- **Step-by-step:**
1. fut1 created, owns shared state from async
2. fut1.valid() would be true (if checked)

```cpp
std::future<int> fut1 = std::async([]{ return 42; });
  // fut1 valid

  std::future<int> fut2 = std::move(fut1);
  // fut1 invalid (moved-from)
  // fut2 valid (new owner)

  // fut1.get();  // Would throw no_state
  int val = fut2.get();  // Works
```

- cpp std::future<int> fut1 = std::async([]{ return 42; }); // fut1 valid
- std::future<int> fut2 = std::move(fut1); // fut1 invalid (moved-from) // fut2 valid (new owner)
- // fut1.get(); // Would throw no_state int val = fut2.get(); // Works ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

std::promise<int> prom2 = std::move(prom);

prom2.set_value(42);
int val = fut.get();

// Does moving the promise affect the future?
```

**Answer:**

```cpp
No effect on future, val = 42
```

- No effect on future, val = 42 ```

**Explanation:**

- **Promise move doesn't invalidate associated future** - shared state persists
- **Execution flow:**
1. Promise and future created, linked via shared state
2. Promise moved to prom2

```cpp
Promise → Shared State ← Future

  After move:
  prom (invalid)
  prom2 (valid) → Shared State ← fut (still valid)
```

- Promise → Shared State ← Future
- After move: prom (invalid) prom2 (valid) → Shared State ← fut (still valid) ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
auto fut = std::async([]{ return 42; });  // Default policy

// Is this guaranteed to run in a separate thread?
```

**Answer:**

```cpp
No guarantee - implementation-defined
```

- No guarantee - implementation-defined ```

**Explanation:**

- **Default launch policy is ambiguous** - can be deferred OR async
- **What the standard says:**

```cpp
std::async(fn);  // Equivalent to:
  std::async(std::launch::async | std::launch::deferred, fn);
```

- cpp std::async(fn); // Equivalent to: std::async(std::launch::async | std::launch::deferred, fn); ``` - Implementation chooses - May launch thread (async) - May defer (lazy) -

**For guaranteed async (separate thread):**

```cpp
auto fut = std::async(std::launch::async, []{ return 42; });
  // Guaranteed to launch thread
  // May throw if thread creation fails
```

- cpp auto fut = std::async(std::launch::async, []{ return 42; }); // Guaranteed to launch thread // May throw if thread creation fails ```

**For guaranteed deferred (lazy):**

```cpp
auto fut = std::async(std::launch::deferred, []{ return 42; });
  // Guaranteed lazy execution
  // Runs on fut.get() or fut.wait()
```

- cpp auto fut = std::async(std::launch::deferred, []{ return 42; }); // Guaranteed lazy execution // Runs on fut.get() or fut.wait() ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

// Promise destroyed without setting value

try {
    int val = fut.get();
} catch (const std::future_error& e) {
    std::cout << "Error\n";
}

// What exception is thrown?
```

**Answer:**

```cpp
future_error with code broken_promise
```

- future_error with code broken_promise ```

**Explanation:**

- **Broken promise:** Promise destroyed without fulfilling obligation
- **Execution flow:**
1. Promise created
2. Future obtained

```cpp
try {
      int val = fut.get();
  } catch (const std::future_error& e) {
      if (e.code() == std::future_errc::broken_promise) {
          std::cout << "Promise was broken!\n";
      }
      std::cout << e.what() << "\n";  // "broken promise"
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
std::future<int> create_future() {
    return std::async(std::launch::deferred, []{ return 42; });
}

auto fut = create_future();
std::cout << "After create\n";
int val = fut.get();
std::cout << "After get: " << val << "\n";

// When does the task execute?
```

**Answer:**

```cpp
Task executes during fut.get() call
```

- Task executes during fut.get() call ```

**Explanation:**

- **Deferred execution with function return** - lazy evaluation preserved
- **Timeline:**
1. create_future() called
2. async(launch::deferred) creates task

```cpp
std::future<ExpensiveObject> lazy_init() {
      return std::async(std::launch::deferred, [] {
          return ExpensiveObject{};  // Not created yet
      });
  }

  auto fut = lazy_init();  // Cheap
  // ... do other work

  auto obj = fut.get();  // NOW create expensive object
```

- cpp std::future<ExpensiveObject> lazy_init() { return std::async(std::launch::deferred, [] { return ExpensiveObject{}; // Not created yet }); }
- auto fut = lazy_init(); // Cheap // ..
- auto obj = fut.get(); // NOW create expensive object ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

try {
    prom.set_exception(std::make_exception_ptr(std::runtime_error("Error")));
    int val = fut.get();
} catch (const std::runtime_error& e) {
    std::cout << "Caught: " << e.what() << "\n";
}

// What is the output?
```

**Answer:**

```cpp
"Caught: Error"
```

**Explanation:**

- **Manual exception propagation** - set_exception instead of set_value
- **Execution flow:**
1. Promise and future created
2. **set_exception called** with runtime_error

```cpp
std::promise<int> prom;

  try {
      int result = risky_work();
      prom.set_value(result);
  } catch (...) {
      // Capture current exception
      prom.set_exception(std::current_exception());
  }
```

- cpp std::promise<int> prom;
- try { int result = risky_work(); prom.set_value(result); } catch (...) { // Capture current exception prom.set_exception(std::current_exception()); } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
std::vector<std::future<int>> futures;

for (int i = 0; i < 5; ++i) {
    futures.push_back(std::async(std::launch::async, [i]{ return i * 2; }));
}

for (auto& fut : futures) {
    std::cout << fut.get() << " ";
}

// What is the output pattern?
```

**Answer:**

```cpp
0 2 4 6 8 (in order, but tasks may run in parallel)
```

- 0 2 4 6 8 (in order, but tasks may run in parallel) ```

**Explanation:**

- **Parallel task collection pattern** - common async use case
- **Execution timeline:**
1. Loop 1: Create 5 async tasks
- All tasks launched simultaneously

```cpp
Time: 0ms    100ms   200ms
  Task0: [====] done
  Task1:   [====] done
  Task2:     [====] done
  Task3:   [====] done
  Task4: [====] done

  All run concurrently!
```

- Time: 0ms 100ms 200ms Task0: [====] done Task1: [====] done Task2: [====] done Task3: [====] done Task4: [====] done

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
std::promise<int> prom;
std::future<int> fut = prom.get_future();

std::thread t([&prom] {
    prom.set_value(42);
    prom.set_value(100);  // Second set
});

t.join();
int val = fut.get();

// What happens in the thread?
```

**Answer:**

```cpp
Thread throws future_error (promise_already_satisfied)
Likely terminates program
```

- Thread throws future_error (promise_already_satisfied) Likely terminates program ```

**Explanation:**

- **Unhandled exception in thread** - program termination
- **Execution flow:**
1. Thread starts
2. prom.set_value(42) succeeds

```cpp
terminate called after throwing an instance of 'std::future_error'
    what():  Promise already satisfied
  Aborted (core dumped)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
