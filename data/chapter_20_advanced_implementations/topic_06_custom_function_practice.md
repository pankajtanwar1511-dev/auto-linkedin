### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1
Add support for `target()` method that returns pointer to stored callable.

Implement this exercise.

**Answer:**

```cpp
template<typename R, typename... Args>
class Function<R(Args...)> {
private:
    struct CallableBase {
        virtual void* target_ptr(const std::type_info& ti) = 0;
        // ... existing methods ...
    };
    // ... (abbreviated)
```

- cpp template<typename R, typename..
- Args> class Function<R(Args...)> { private: struct CallableBase { virtual void* target_ptr(const std::type_info& ti) = 0; // ..

**Usage:**

```cpp
Function<int(int)> func = [](int x) { return x * 2; };

using Lambda = decltype([](int x) { return x * 2; });
if (auto* lambda_ptr = func.target<Lambda>()) {
    std::cout << "Stored lambda\n";
}
```

- cpp Function<int(int)> func = [](int x) { return x * 2; };
- using Lambda = decltype([](int x) { return x * 2; }); if (auto* lambda_ptr = func.target<Lambda>()) { std::cout << "Stored lambda\n"; } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
Implement `std::function` with Small Buffer Optimization for callables ≤ 32 bytes.

Implement this exercise.

(See Q5 above for complete implementation)

---

#### Q3
Add exception handling: if callable throws, wrap exception in custom type.

Implement this exercise.

**Answer:**

```cpp
R operator()(Args... args) {
    if (!callable_) {
        throw std::bad_function_call();
    }

    try {
        return callable_->invoke(std::forward<Args>(args)...);
    } catch (...) {
        // Re-wrap exception
        throw std::runtime_error("Exception in std::function invocation");
    }
}
```

---

#### Q4
Benchmark `std::function` vs direct lambda call for 1M invocations.

Implement this exercise.

**Answer:**

```cpp
#include <chrono>
#include <iostream>

int main() {
    auto lambda = [](int x) { return x * 2; };

    // Direct call
    // ... (abbreviated)
```

- cpp #include <chrono> #include <iostream>
- int main() { auto lambda = [](int x) { return x * 2; };

**Typical output:**

```cpp
Direct: 2 ms
Function: 12 ms
Overhead: 10 ms (5× slower)
```

- Direct: 2 ms Function: 12 ms Overhead: 10 ms (5× slower) ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
Implement `std::function` that tracks invocation count.

Implement this exercise.

**Answer:**

```cpp
template<typename R, typename... Args>
class TrackingFunction : public Function<R(Args...)> {
    mutable std::atomic<size_t> call_count_{0};

public:
    using Function<R(Args...)>::Function;

    R operator()(Args... args) const {
        ++call_count_;
        return Function<R(Args...)>::operator()(std::forward<Args>(args)...);
    }

    size_t call_count() const {
        return call_count_.load();
    }
};
```

**Usage:**
```cpp
TrackingFunction<int(int)> func = [](int x) { return x * 2; };

func(1);
func(2);
func(3);

std::cout << "Called " << func.call_count() << " times\n";  // 3
```

---
