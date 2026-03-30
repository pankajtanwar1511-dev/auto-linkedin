### PRACTICE_TASKS: Output Prediction and Code Analysis

#### Q1
Analyze the following functor and identify the issue:
```cpp
class Counter {
    int count;
public:
    Counter() : count(0) {}
    void operator()(int x) const { count++; }
    int getCount() const { return count; }
};
```

**Answer:**



**Explanation:**

- **The problem:**
- `operator()` declared `const`
- Attempts to modify `count` with `count++`
- **const member functions cannot modify non-mutable members**
- Compilation error: "discards qualifiers" or "cannot assign to non-static data member within const member function"

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
What will be the output of this code? Explain why.
```cpp
class Multiplier {
    int factor;
public:
    Multiplier(int f) : factor(f) {}
    int operator()(int x) { return x * factor; }
};

std::vector<int> vec = {1, 2, 3};
Multiplier m(2);
std::for_each(vec.begin(), vec.end(), m);
std::cout << m(5);
```

**Answer:**



**Explanation:**

- **Code execution flow:**
- **Why output is 10:**
- operator() returns result, doesn't store it
- for_each discards return values (designed for side effects, not transformations)
- Original m unchanged (for_each uses copy)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
Fix the following thread-unsafe functor:
```cpp
class Cache {
    std::unordered_map<int, int> data;
public:
    int operator()(int key) {
        if (data.count(key)) return data[key];
        int value = expensiveCompute(key);
        data[key] = value;
        return value;
    }
};
```

**Answer:**

```cpp
class Cache {
    std::unordered_map<int, int> data;
    mutable std::shared_mutex mtx;  // Reader-writer lock
public:
    int operator()(int key) const {
        // Try read-only path first (shared lock)
        {
            std::shared_lock lock(mtx);
            auto it = data.find(key);
            if (it != data.end()) return it->second;
        }

    // ... (additional code omitted for brevity)
```

- int value = expensiveCompute(key); data[key] = value; return value; } }; ```

**Explanation:**

- **Original problems:**
1. **Data race on unordered_map:**
- Multiple threads call operator() simultaneously
- Concurrent reads + writes to data map

```cpp
// Multiple threads can hold shared_lock (read)
  // Only one thread can hold unique_lock (write)
  // Exclusive with each other
```

- cpp // Multiple threads can hold shared_lock (read) // Only one thread can hold unique_lock (write) // Exclusive with each other ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
Optimize this memoization functor to avoid double hash lookup:
```cpp
int operator()(int x) const {
    if (cache.count(x)) {
        return cache[x];
    }
    int result = compute(x);
    cache[x] = result;
    return result;
}
```

**Answer:**

```cpp
int operator()(int x) const {
    auto [it, inserted] = cache.try_emplace(x, compute(x));  // C++17
    return it->second;
}

// OR for C++11/14:
int operator()(int x) const {
    auto it = cache.find(x);
    if (it != cache.end()) {
        return it->second;  // Found, return cached value
    }
    // Not found, compute and insert
    // ... (additional code omitted for brevity)
```

- cpp int operator()(int x) const { auto [it, inserted] = cache.try_emplace(x, compute(x)); // C++17 return it->second; }

**Explanation:**

- **Original problem: Double hash lookup**

```cpp
if (cache.count(x)) {        // Lookup 1: Search hash table
      return cache[x];          // Lookup 2: Search hash table AGAIN
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
Complete this generic accumulator functor that works with any type supporting `operator+`:
```cpp
template <typename T>
class Accumulator {
    // Your code here
public:
    void operator()(const T& value) {
        // Your code here
    }
    T getSum() const {
        // Your code here
    }
};
```

**Answer:**

```cpp
template <typename T>
class Accumulator {
    T sum;

public:
    Accumulator() : sum(T{}) {}  // Value-initialize to zero

    void operator()(const T& value) {
        sum += value;
    }

    T getSum() const {
    // ... (additional code omitted for brevity)
```

- cpp template <typename T> class Accumulator { T sum;
- public: Accumulator() : sum(T{}) {} // Value-initialize to zero
- void operator()(const T& value) { sum += value; }

**Explanation:**

- **Key design decisions:**
1. **Value-initialization: `T{}`**
- Zero-initializes for built-in types: `int{}` → 0, `double{}` → 0.0
- Default-constructs for class types

```cpp
// Accumulate integers
  Accumulator<int> intAcc;
  std::vector<int> nums = {1, 2, 3, 4, 5};
  std::for_each(nums.begin(), nums.end(), std::ref(intAcc));
  std::cout << intAcc.getSum();  // 15

  // Accumulate strings
  Accumulator<std::string> strAcc;
  std::vector<std::string> words = {"Hello", " ", "World"};
  std::for_each(words.begin(), words.end(), std::ref(strAcc));
  std::cout << strAcc.getSum();  // "Hello World"

    // ... (additional code omitted for brevity)
```

- cpp // Accumulate integers Accumulator<int> intAcc; std::vector<int> nums = {1, 2, 3, 4, 5}; std::for_each(nums.begin(), nums.end(), std::ref(intAcc)); std::cout << intAcc.getSum(); // 15

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
What's wrong with this comparison functor? How would you fix it?
```cpp
class GreaterThan {
    int threshold;
public:
    GreaterThan(int t) : threshold(t) {}
    bool operator()(int a, int b) { return a > b && a > threshold; }
};
```

**Answer:**

```cpp
Wrong signature: STL comparison functors are binary predicates on same type
Should compare two elements, not filter by threshold
Mixing comparison with filtering logic
```

- Wrong signature: STL comparison functors are binary predicates on same type Should compare two elements, not filter by threshold Mixing comparison with filtering logic ```

**Explanation:**

- **What's wrong:**

```cpp
bool operator()(int a, int b) { return a > b && a > threshold; }
  //                                     ^^^^^^   ^^^^^^^^^^^^^^
  //                                     Compare  Filter (wrong!)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
Implement move semantics for this resource-owning functor:
```cpp
class FileProcessor {
    std::unique_ptr<std::ofstream> file;
public:
    FileProcessor(const std::string& filename);
    // Add move constructor and move assignment
    void operator()(const std::string& data);
};
```

**Answer:**

```cpp
class FileProcessor {
    std::unique_ptr<std::ofstream> file;

public:
    FileProcessor(const std::string& filename)
        : file(std::make_unique<std::ofstream>(filename)) {
        if (!file->is_open()) {
            throw std::runtime_error("Failed to open file");
        }
    }

    // Move constructor
    // ... (additional code omitted for brevity)
```

- cpp class FileProcessor { std::unique_ptr<std::ofstream> file;
- // Move constructor FileProcessor(FileProcessor&& other) noexcept : file(std::move(other.file)) {}
- // Move assignment FileProcessor& operator=(FileProcessor&& other) noexcept { if (this != &other) { file = std::move(other.file); } return *this; }

**Explanation:**

- **Why move semantics needed:**
- `unique_ptr` represents unique ownership
- Cannot be copied (copy constructor deleted)
- Must use move to transfer ownership

```cpp
FileProcessor(FileProcessor&& other) noexcept
      : file(std::move(other.file)) {}
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
Why doesn't this code compile? Fix it.
```cpp
class Transformer {
    std::vector<int> history;
public:
    int operator()(int x) const {
        history.push_back(x);  // Error!
        return x * 2;
    }
};
```

**Answer:**

```cpp
class Transformer {
    mutable std::vector<int> history;  // Add mutable
public:
    int operator()(int x) const {
        history.push_back(x);  // OK now
        return x * 2;
    }
};
```

- cpp class Transformer { mutable std::vector<int> history; // Add mutable public: int operator()(int x) const { history.push_back(x); // OK now return x * 2; } }; ```

**Explanation:**

- **Compilation error:**

```cpp
error: passing 'const std::vector<int>' as 'this' argument discards qualifiers
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
Convert this function pointer usage to a functor:
```cpp
bool isEven(int x) { return x % 2 == 0; }
std::vector<int> vec = {1, 2, 3, 4, 5};
vec.erase(std::remove_if(vec.begin(), vec.end(), isEven), vec.end());
```

**Answer:**

```cpp
class IsEven {
public:
    bool operator()(int x) const {
        return x % 2 == 0;
    }
};

std::vector<int> vec = {1, 2, 3, 4, 5};
vec.erase(std::remove_if(vec.begin(), vec.end(), IsEven()), vec.end());
// Result: vec = {1, 3, 5}
```

- cpp class IsEven { public: bool operator()(int x) const { return x % 2 == 0; } };
- std::vector<int> vec = {1, 2, 3, 4, 5}; vec.erase(std::remove_if(vec.begin(), vec.end(), IsEven()), vec.end()); // Result: vec = {1, 3, 5} ```

**Explanation:**

- **Functor advantages over function pointer:**
1. **State:** Can hold member variables
2. **Inline:** More likely to be inlined by compiler
3. **Type-specific:** Each functor is unique type

```cpp
// Function pointer
  bool isEven(int x) { return x % 2 == 0; }

  // Equivalent functor
  class IsEven {
  public:
      bool operator()(int x) const { return x % 2 == 0; }
  };
```

- cpp // Function pointer bool isEven(int x) { return x % 2 == 0; }
- // Equivalent functor class IsEven { public: bool operator()(int x) const { return x % 2 == 0; } }; ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
Identify and fix the issue with cache invalidation in this functor:
```cpp
class ScalingFunction {
    mutable std::unordered_map<int, int> cache;
    int scaleFactor;
public:
    ScalingFunction(int factor) : scaleFactor(factor) {}

    void setScaleFactor(int factor) {
        scaleFactor = factor;
    }

    int operator()(int x) const {
        auto it = cache.find(x);
        if (it != cache.end()) return it->second;
        int result = x * scaleFactor;
        cache[x] = result;
        return result;
    }
};
```

**Answer:**

```cpp
class ScalingFunction {
    mutable std::unordered_map<int, int> cache;
    int scaleFactor;
public:
    ScalingFunction(int factor) : scaleFactor(factor) {}

    void setScaleFactor(int factor) {
        scaleFactor = factor;
        cache.clear();  // Invalidate cache!
    }

    int operator()(int x) const {
    // ... (additional code omitted for brevity)
```

- cpp class ScalingFunction { mutable std::unordered_map<int, int> cache; int scaleFactor; public: ScalingFunction(int factor) : scaleFactor(factor) {}
- void setScaleFactor(int factor) { scaleFactor = factor; cache.clear(); // Invalidate cache

**Explanation:**

- **The bug: Stale cache**

```cpp
ScalingFunction f(2);
  f(10);  // Computes 10 * 2 = 20, caches {10: 20}

  f.setScaleFactor(3);  // Changes factor but cache still has {10: 20}!

  f(10);  // Returns cached 20, should be 30!
```

- cpp ScalingFunction f(2); f(10); // Computes 10 * 2 = 20, caches {10: 20}
- f.setScaleFactor(3); // Changes factor but cache still has {10: 20}
- f(10); // Returns cached 20, should be 30

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
Complete this variadic functor that counts how many times it's been called with different argument counts:
```cpp
class CallTracker {
    std::map<int, int> callsByArgCount;
public:
    template <typename... Args>
    void operator()(Args&&... args) {
        // Your code here
    }

    void printStats() const {
        // Your code here
    }
};
```

**Answer:**

- Args> void operator()(Args&&..
- args) { int argCount = sizeof...(Args); callsByArgCount[argCount]++; }

**Explanation:**

- **sizeof... operator:** Counts template parameter pack size at compile time
- **Variadic templates:** Accept any number of arguments of any types
- **Perfect forwarding:** `Args&&...` preserves value category (lvalue/rvalue)
- **How it works:**
- **sizeof... vs sizeof:**

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
Why might this functor be slower than expected? Optimize it.
```cpp
class StringConcatenator {
    std::string result;
public:
    void operator()(const std::string& s) {
        result = result + s;
    }
    std::string getResult() const { return result; }
};
```

**Answer:**

```cpp
Performance issue: result = result + s creates temporary string on each call
O(n²) complexity for n concatenations
Optimization: Use result += s for in-place modification (O(n))
```

- Performance issue: result = result + s creates temporary string on each call O(n²) complexity for n concatenations Optimization: Use result += s for in-place modification (O(n)) ```

**Explanation:**

- **The performance problem:**

```cpp
result = result + s;
  //       ^^^^^^^^^^
  //       Creates temporary string
```

- cpp result = result + s; // ^^^^^^^^^^ // Creates temporary string ``` - `result + s` creates

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
Implement a functor composition helper that chains two functors:
```cpp
template <typename F, typename G>
class ComposedFunctor {
    // Your implementation
};

template <typename F, typename G>
ComposedFunctor<F, G> compose(F f, G g) {
    // Your implementation
}
```

**Answer:**

```cpp
template <typename F, typename G>
class ComposedFunctor {
    F f;
    G g;
public:
    ComposedFunctor(F f_, G g_) : f(f_), g(g_) {}

    template <typename T>
    auto operator()(T&& x) const -> decltype(f(g(std::forward<T>(x)))) {
        return f(g(std::forward<T>(x)));  // f(g(x))
    }
};
    // ... (additional code omitted for brevity)
```

- cpp template <typename F, typename G> class ComposedFunctor { F f; G g; public: ComposedFunctor(F f_, G g_) : f(f_), g(g_) {}
- template <typename T> auto operator()(T&& x) const -> decltype(f(g(std::forward<T>(x)))) { return f(g(std::forward<T>(x))); // f(g(x)) } };
- template <typename F, typename G> ComposedFunctor<F, G> compose(F f, G g) { return ComposedFunctor<F, G>(f, g); }

**Explanation:**

- **Function composition:** Combines two functions into one
- Mathematical notation: `(f ∘ g)(x) = f(g(x))`
- Apply `g` first, then apply `f` to result
- Read right-to-left: `compose(f, g)` means `f(g(x))`

```cpp
template <typename F, typename G>
  class ComposedFunctor {
      F f;  // Outer function
      G g;  // Inner function (applied first)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
Fix the copy semantics issue in this code:
```cpp
class Aggregator {
    double sum;
    int count;
public:
    Aggregator() : sum(0), count(0) {}
    void operator()(double x) { sum += x; count++; }
    double average() const { return sum / count; }
};

std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
Aggregator agg;
std::for_each(data.begin(), data.end(), agg);
std::cout << "Average: " << agg.average();  // Prints wrong result!
```

**Answer:**

```cpp
// Fix 1: Use std::ref to pass by reference
std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
Aggregator agg;
std::for_each(data.begin(), data.end(), std::ref(agg));  // Pass by reference
std::cout << "Average: " << agg.average();  // Correct: 2.5

// Fix 2: Capture returned functor
std::vector<double> data = {1.0, 2.0, 3.0, 4.0};
Aggregator agg;
agg = std::for_each(data.begin(), data.end(), agg);  // Get modified copy
std::cout << "Average: " << agg.average();  // Correct: 2.5
```

**Explanation:**

- **The problem: STL algorithms pass by value**

```cpp
std::for_each(data.begin(), data.end(), agg);
  //                                       ^^^
  //                                       Copies agg!
```

- cpp std::for_each(data.begin(), data.end(), agg); // ^^^ // Copies agg

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
Implement a thread-safe logging functor with lock-free counters:
```cpp
class ThreadSafeLogger {
    std::atomic<int> messageCount;
    std::mutex logMutex;
    std::ofstream logFile;
public:
    // Your implementation
};
```

**Answer:**

```cpp
class ThreadSafeLogger {
    mutable std::atomic<int> messageCount{0};  // Lock-free counter
    mutable std::mutex logMutex;                // Protects file I/O
    mutable std::ofstream logFile;

public:
    ThreadSafeLogger(const std::string& filename)
        : logFile(filename, std::ios::app) {  // Append mode
        if (!logFile.is_open()) {
            throw std::runtime_error("Failed to open log file");
        }
    }
    // ... (additional code omitted for brevity)
```

- void operator()(const std::string& message) const { // Increment counter atomically (lock-free!) messageCount.fetch_add(1, std::memory_order_relaxed);
- // File I/O requires mutex (not thread-safe) std::lock_guard<std::mutex> lock(logMutex); logFile << "[" << messageCount.load() << "] " << message << std::endl; }
- int getMessageCount() const { return messageCount.load(std::memory_order_relaxed); } }; ```

**Explanation:**

- **Why atomic for counter:**

```cpp
mutable std::atomic<int> messageCount{0};
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
What's the difference in behavior between these two functors?
```cpp
class A {
public:
    int operator()(int x) const { return x * 2; }
};

class B {
public:
    int operator()(int x) { return x * 2; }
};

const A a;
const B b;
int r1 = a(5);  // Works
// int r2 = b(5);  // Error - explain why
```

**Answer:**

```cpp
A works: operator() is const, can be called on const object
B fails: operator() is non-const, cannot be called on const object
Compilation error: "discards qualifiers" or "cannot call non-const member function on const object"
```

**Explanation:**

- **The difference: const qualifier**

```cpp
class A {
      int operator()(int x) const { ... }  // CONST
  };

  class B {
      int operator()(int x) { ... }  // NON-CONST
  };
```

- cpp class A { int operator()(int x) const { ..
- class B { int operator()(int x) { ..
- } // NON-CONST }; ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
Implement a sensor filter functor for autonomous vehicles that maintains a moving window:
```cpp
class SensorFilter {
    // Your state variables
public:
    double operator()(double measurement) {
        // Implement moving average with window size 5
    }
};
```

**Answer:**

```cpp
class SensorFilter {
    std::deque<double> window;  // Efficient for front/back operations
    size_t windowSize;
    double sum;

public:
    SensorFilter(size_t size = 5)
        : windowSize(size), sum(0.0) {}

    double operator()(double measurement) {
        // Add new measurement
        window.push_back(measurement);
    // ... (additional code omitted for brevity)
```

- cpp class SensorFilter { std::deque<double> window; // Efficient for front/back operations size_t windowSize; double sum;
- public: SensorFilter(size_t size = 5) : windowSize(size), sum(0.0) {}
- double operator()(double measurement) { // Add new measurement window.push_back(measurement); sum += measurement;

**Explanation:**

- **Moving average: Smooths noisy sensor data**
- Averages last N measurements
- Reduces noise, shows trend
- Critical for autonomous vehicle sensors (LIDAR, cameras, IMU)

```cpp
std::deque<double> window;
```

- cpp std::deque<double> window; ``` - Efficient push_back() and pop_front() - Both O(1) operations - Perfect for sliding window pattern -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
Fix this lambda-to-functor conversion to preserve state correctly:
```cpp
// Lambda version
int multiplier = 3;
auto lambda = [multiplier](int x) { return x * multiplier; };

// Functor version - complete this
class Multiplier {
    // Your code
};
```

**Answer:**

```cpp
class Multiplier {
    int multiplier;  // Captured variable becomes member

public:
    // Constructor captures the value (like lambda capture)
    Multiplier(int m) : multiplier(m) {}

    // operator() uses the captured value
    int operator()(int x) const {
        return x * multiplier;
    }
};
    // ... (additional code omitted for brevity)
```

- cpp class Multiplier { int multiplier; // Captured variable becomes member
- public: // Constructor captures the value (like lambda capture) Multiplier(int m) : multiplier(m) {}
- // operator() uses the captured value int operator()(int x) const { return x * multiplier; } };

**Explanation:**

- **Lambda capture → Member variable**

```cpp
// Lambda captures multiplier by value
  auto lambda = [multiplier](int x) { return x * multiplier; };
  //             ^^^^^^^^^^
  //             Capture list

  // Functor stores multiplier as member
  class Multiplier {
      int multiplier;  // Captured variable
```

- cpp // Lambda captures multiplier by value auto lambda = [multiplier](int x) { return x * multiplier; }; // ^^^^^^^^^^ // Capture list

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
Implement a functor that can be used with `std::priority_queue` to sort by absolute distance from a target:
```cpp
class DistanceComparator {
    // Your implementation
};

std::priority_queue<int, std::vector<int>, DistanceComparator> pq(/* your constructor args */);
```

**Answer:**

```cpp
class DistanceComparator {
    int target;
public:
    DistanceComparator(int t) : target(t) {}

    // Comparison: Returns true if a is "less than" b
    // For max-heap (default priority_queue): return true if a should come AFTER b
    bool operator()(int a, int b) const {
        int distA = std::abs(a - target);
        int distB = std::abs(b - target);
        return distA > distB;  // Max-heap: larger distance = lower priority
        // Elements with smaller distance to target have higher priority (come out first)
    // ... (additional code omitted for brevity)
```

- cpp class DistanceComparator { int target; public: DistanceComparator(int t) : target(t) {}
- // Usage: int target = 50; std::priority_queue<int, std::vector<int>, DistanceComparator> pq(DistanceComparator(target));
- pq.push(45); // distance: 5 pq.push(60); // distance: 10 pq.push(48); // distance: 2 pq.push(55); // distance: 5

**Explanation:**

- **Priority queue comparison:**

```cpp
bool operator()(int a, int b) const {
      return distA > distB;  // "a has lower priority than b"
  }
```

- cpp bool operator()(int a, int b) const { return distA > distB; // "a has lower priority than b" } ``` - `operator()` returns true if `a` should come

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
Analyze this performance issue and propose an optimization:
```cpp
class ExpensiveFilter {
    std::vector<int> allowedValues;
public:
    ExpensiveFilter(std::vector<int> values) : allowedValues(values) {}

    bool operator()(int x) const {
        return std::find(allowedValues.begin(), allowedValues.end(), x)
               != allowedValues.end();
    }
};

std::vector<int> data = {/* 10,000 elements */};
ExpensiveFilter filter({1, 2, 3, 4, 5});
std::copy_if(data.begin(), data.end(), std::back_inserter(filtered), filter);
// Takes too long!
```

**Answer:**

```cpp
// Optimized version: Use unordered_set for O(1) lookup
class OptimizedFilter {
    std::unordered_set<int> allowedValues;  // Hash set instead of vector
public:
    OptimizedFilter(std::vector<int> values)
        : allowedValues(values.begin(), values.end()) {}  // Convert to set

    bool operator()(int x) const {
        return allowedValues.count(x) > 0;  // O(1) lookup
        // Or: return allowedValues.find(x) != allowedValues.end();
    }
};
    // ... (additional code omitted for brevity)
```

- bool operator()(int x) const { return allowedValues.count(x) > 0; // O(1) lookup // Or: return allowedValues.find(x) != allowedValues.end(); } };
- // Performance: // Original: O(n*m) where n=data size, m=allowedValues size // Optimized: O(n+m) → O(n) when m is small ```

**Explanation:**

- **Original performance problem:**

```cpp
std::find(allowedValues.begin(), allowedValues.end(), x)
  //        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //        Linear search: O(m) where m = allowedValues.size()
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
