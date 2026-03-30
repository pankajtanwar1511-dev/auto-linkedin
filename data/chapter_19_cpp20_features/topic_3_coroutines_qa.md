## TOPIC: C++20 Coroutines - Stackless Cooperative Multitasking

### INTERVIEW_QA: Comprehensive Coroutine Questions

---

#### Q1: What makes a function a coroutine in C++20?

**Answer:**

A function becomes a coroutine if its body contains **any** of these three keywords:
1. `co_await` - Suspend and wait for an awaitable
2. `co_yield` - Produce a value and suspend
3. `co_return` - Return a value and complete

**Key Point:** It's not the return type that makes it a coroutine, but the presence of these keywords in the function body.

```cpp
// Regular function
int regular() {
    return 42;
}

// Coroutine (has co_return)
Task<int> coro1() {
    co_return 42;  // This makes it a coroutine
}

// Coroutine (has co_yield)
Generator<int> coro2() {
    co_yield 1;  // This makes it a coroutine
}

// Coroutine (has co_await)
Task<int> coro3() {
    co_await something();  // This makes it a coroutine
    return 42;  // Regular return is also valid after co_await
}
```

**What the Compiler Does:**

When it sees a coroutine keyword:
1. Allocates a coroutine frame (heap memory)
2. Copies parameters and local variables to the frame
3. Creates a promise object based on the return type's `promise_type`
4. Transforms the function body into a state machine

---

#### Q2: Explain the purpose of the promise type in coroutines.


**Answer:**

- The promise type is a customization point that controls the behavior of a coroutine throughout its lifetime.

**Required Methods:**

- Create the return object (what the caller gets) ReturnType get_return_object();
- Initial suspension (suspend before first statement?) auto initial_suspend(); // Returns std::suspend_always or suspend_never
- Final suspension (suspend after last statement?) auto final_suspend() noexcept;
- Handle return value (choose ONE) void return_void(); // For coroutines without return value void return_value(T value); // For coroutines with return value
- Handle exceptions void unhandled_exception(); }; ```

**What Each Method Controls:**

- `return_value()` / `return_void()`: Stores the result ```cpp void return_value(int value) { result_ = value; // Store for later retrieval } ```
- `unhandled_exception()`: Captures exceptions ```cpp void unhandled_exception() { exception_ = std::current_exception(); // Store for re-throwing } ```

**How the Compiler Finds It:**

- For a coroutine returning `Task<T>`, the compiler looks for: ```cpp typename Task<T>::promise_type ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3: What is the difference between co_yield and co_return?


**Answer:**



**co_yield - Produce and Suspend:**

- // Caller can iterate: for (int n : count_to_five()) { std::cout << n << " "; // 1 2 3 4 5 } ```

**co_return - Complete:**

- // Caller gets the result: auto task = compute(); int value = task.get(); // Resumes coroutine to completion ```

**Transformation:**

- // co_return value; transforms to: promise.return_value(value); goto final_suspend; ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4: How does co_await work? What makes something "awaitable"?


**Answer:**
**co_await Mechanism:**
When you write `co_await expr`, the compiler transforms it into a series of calls on the awaitable:
```cpp
auto result = co_await my_awaitable;
// Transforms roughly to:
{
    auto&& awaitable = my_awaitable;
    if (!awaitable.await_ready()) {  // Should we suspend?
        // Suspend coroutine
        awaitable.await_suspend(coroutine_handle);  // What to do when suspended?
        // Coroutine is now suspended, control returns to caller
        // ...
        // Later, someone calls coroutine_handle.resume()
    // ... (additional code omitted for brevity)
```
- cpp auto result = co_await my_awaitable;
- // Transforms roughly to: { auto&& awaitable = my_awaitable;
- if (!awaitable.await_ready()) { // Should we suspend
**Awaitable Interface:**
An awaitable must provide three methods:
```cpp
struct MyAwaitable {
    // 1. Should we suspend?
    bool await_ready() const noexcept {
        return false;  // true = skip suspension, false = suspend
    }
    // 2. What to do when suspending?
    void await_suspend(std::coroutine_handle<> handle) {
        // Schedule resumption (e.g., on thread pool, after I/O completes)
        // Can also return:

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5: What is a coroutine handle and when would you use it?


**Answer:**
- A coroutine handle (`std::coroutine_handle<PromiseType>`) is a low-level, non-owning handle to a suspended coroutine.
**Interface:**
```cpp
template<typename Promise = void>
struct coroutine_handle {
    // Create from promise
    static coroutine_handle from_promise(Promise& p);
    // Resume coroutine execution
    void resume();
    // Check if coroutine finished
    bool done() const;
    // Destroy coroutine frame
    // ... (additional code omitted for brevity)
```
- cpp template<typename Promise = void> struct coroutine_handle { // Create from promise static coroutine_handle from_promise(Promise& p);
- // Resume coroutine execution void resume();
- // Check if coroutine finished bool done() const;
**When to Use:**
1. **In Promise Types**: Return handle in `get_return_object()`
```cpp
struct promise_type {
       Task get_return_object() {
           return Task{std::coroutine_handle<promise_type>::from_promise(*this)};
       }
   };
```
- cpp struct promise_type { Task get_return_object() { return Task{std::coroutine_handle<promise_type>::from_promise(*this)}; } }; ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: Explain the difference between std::suspend_always and std::suspend_never.


**Answer:**

- These are the two standard awaitable types that control suspension behavior.

**std::suspend_always:**

- **Effect**: Coroutine **always suspends** at this point
- **Use in `initial_suspend()`**: Coroutine starts suspended (lazy execution)
- **Use in `final_suspend()`**: Coroutine stays suspended after completion (frame kept alive)

**std::suspend_never:**

- **Effect**: Coroutine **never suspends** at this point
- **Use in `initial_suspend()`**: Coroutine starts immediately (eager execution)
- **Use in `final_suspend()`**: Coroutine destroys frame immediately after completion

**Practical Impact:**



**Example:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: How do coroutines handle exceptions?


**Answer:**
- Exceptions in coroutines are handled through the promise's `unhandled_exception()` method.
**Exception Flow:**
```cpp
Task<int> may_throw() {
    if (error_condition) {
        throw std::runtime_error("Error!");  // Exception thrown
    }
    co_return 42;
}
// Compiler transforms the coroutine body to:
void coroutine_body() {
    try {
        // Original coroutine code
        if (error_condition) {
    // ... (additional code omitted for brevity)
```
- cpp Task<int> may_throw() { if (error_condition) { throw std::runtime_error("Error!"); // Exception thrown } co_return 42; }
**Promise Implementation:**
```cpp
struct promise_type {
    std::exception_ptr exception_;
    void unhandled_exception() {
        exception_ = std::current_exception();  // Store exception
    }
    T get_result() {
        if (exception_)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: What is symmetric transfer and why is it important?


**Answer:**
- Symmetric transfer is a technique where a coroutine directly transfers control to another coroutine without growing the call stack.
**The Problem: Stack Overflow:**
```cpp
Task<int> recursive_task(int n) {
    if (n == 0) co_return 1;
    auto result = co_await recursive_task(n - 1);  // Each co_await uses stack space
    co_return result + 1;
}
// recursive_task(100000) → stack overflow!
```
- cpp Task<int> recursive_task(int n) { if (n == 0) co_return 1;
- auto result = co_await recursive_task(n - 1); // Each co_await uses stack space co_return result + 1; }
- // recursive_task(100000) → stack overflow
**Without Symmetric Transfer:**
```cpp
Call Stack:
recursive_task(3).resume()
  → recursive_task(2).resume()  // Stack grows
    → recursive_task(1).resume()  // Stack grows
      → recursive_task(0).resume()  // Stack grows
        → returns
      ← returns
    ← returns
  ← returns
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: Can you have a coroutine that both co_yields and co_returns?


**Answer:**

- Yes, but the promise type must support both `yield_value()` and `return_value()`/`return_void()`.

**Example:**

- // Support co_yield std::suspend_always yield_value(T value) { current_value_ = std::move(value); return {}; }
- // Support co_return void return_value(T value) { final_value_ = std::move(value); }
- GeneratorWithFinalValue<int> example() { co_yield 1; co_yield 2; co_yield 3; co_return 999; // Final value }
- int main() { auto gen = example();
- for (int val : gen) { std::cout << val << " "; // 1 2 3 }

**Use Cases:**

- Generators that return a final status/summary
- Iterators that produce elements and a final count
- Streams that yield data and return total bytes processed

**Note:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: How is memory managed for coroutine frames?


**Answer:**
**Default Allocation:**
By default, the coroutine frame is allocated on the **heap**:
```cpp
Task<int> my_coroutine() {
    // Frame allocated on heap (contains locals, params, promise)
    co_return 42;
}
// Roughly transforms to:
void* frame = operator new(sizeof(CoroutineFrame));
// ... use frame
operator delete(frame);  // When destroyed
```
- cpp Task<int> my_coroutine() { // Frame allocated on heap (contains locals, params, promise) co_return 42; }
- // Roughly transforms to: void* frame = operator new(sizeof(CoroutineFrame)); // ..
- use frame operator delete(frame); // When destroyed ```
**Custom Allocation:**
You can override allocation in the promise type:
```cpp
struct promise_type {
    void* operator new(std::size_t size) {
        std::cout << "Allocating frame: " << size << " bytes\n";
        return my_custom_allocator().allocate(size);
    }
    void operator delete(void* ptr, std::size_t size) {
        std::cout << "Deallocating frame: " << size << " bytes\n";
        my_custom_allocator().deallocate(ptr, size);
    }
};
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
