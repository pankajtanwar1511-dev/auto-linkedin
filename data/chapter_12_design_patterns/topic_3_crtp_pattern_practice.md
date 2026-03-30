### PRACTICE_TASKS: Output Prediction and Code Analysis

#### Q1
Identify the issue with this CRTP implementation:
```cpp
template <typename T>
class Base {
public:
    void process() {
        static_cast<T*>(this)->process();
    }
};

class Derived : public Base<Derived> {
public:
    void process() {
        std::cout << "Processing\n";
    }
};
```

**Answer:**

```cpp
Infinite recursion: Base::process() calls Derived::process() which calls Base::process() again
Both have same name "process" - derived hides base method
Fix: Use different method names (e.g., processImpl in Derived)
```

**Explanation:**

- **The infinite recursion problem:**

```cpp
Derived d;
  d.process();  // Calls Base::process() (inherited)
  // Inside Base::process():
  static_cast<Derived*>(this)->process();  // Calls Derived::process()
  // Derived::process() prints, but then...
  // Name lookup finds Base::process() again!
  // INFINITE RECURSION!
```

- // Name lookup finds Base::process() again
- // INFINITE RECURSION

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
Fix the two-phase lookup error:
```cpp
template <typename T>
class Base {
public:
    void helper() { std::cout << "Helper\n"; }
};

template <typename T>
class Derived : public Base<T> {
public:
    void method() {
        helper();  // Error!
    }
};
```

**Answer:**

```cpp
// Fix 1: Use this->
void method() {
    this->helper();  // OK
}

// Fix 2: Use Base<T>::
void method() {
    Base<T>::helper();  // OK
}

// Fix 3: Using declaration
using Base<T>::helper;
void method() {
    helper();  // OK now
}
```

- cpp // Fix 1: Use this-> void method() { this->helper(); // OK }
- // Fix 2: Use Base<T>:: void method() { Base<T>::helper(); // OK }
- // Fix 3: Using declaration using Base<T>::helper; void method() { helper(); // OK now } ```

**Explanation:**

- **Two-phase name lookup problem:**

```cpp
void method() {
      helper();  // Error: "identifier not found"
  }
```

- cpp void method() { helper(); // Error: "identifier not found" } ``` - Template compilation has two phases: 1.

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
Complete this Shape hierarchy using CRTP:
```cpp
template <typename T>
class Shape {
public:
    double area() const {
        // Your code here
    }
};

class Circle : public Shape<Circle> {
    double radius;
public:
    Circle(double r) : radius(r) {}
    // Your code here
};
```

**Answer:**

```cpp
template <typename T>
class Shape {
public:
    double area() const {
        return static_cast<const T*>(this)->areaImpl();
    }
    
    void print() const {
        std::cout << "Area: " << area() << std::endl;
    }
};

    // ... (additional code omitted for brevity)
```

- class Circle : public Shape<Circle> { double radius; public: Circle(double r) : radius(r) {} double areaImpl() const { return 3.14159 * radius * radius; } };
- // Usage: Circle c(5.0); c.print(); // Area: 78.5398
- Rectangle r(4.0, 6.0); r.print(); // Area: 24 ```

**Explanation:**

- **CRTP pattern for shapes:**
- Base class `Shape<T>` provides interface (`area()`, `print()`)
- Derived classes provide implementation (`areaImpl()`)
- Each shape inherits from `Shape<Self>` (CRTP)

```cpp
template <typename T>
  double area() const {
      return static_cast<const T*>(this)->areaImpl();
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
What's wrong with this multiple CRTP inheritance?
```cpp
template <typename T>
class Logger {
public:
    void log() { /* ... */ }
};

template <typename T>
class Debugger {
public:
    void log() { /* ... */ }
};

class MyClass : public Logger<MyClass>, public Debugger<MyClass> {
public:
    void execute() {
        log();  // What happens?
    }
};
```

**Answer:**

```cpp
Ambiguous call: log() exists in both Logger<MyClass> and Debugger<MyClass>
Compiler error: "request for member 'log' is ambiguous"
Fix: Qualify which log() to call (Logger<MyClass>::log() or Debugger<MyClass>::log())
```

**Explanation:**

- **Multiple inheritance ambiguity:**

```cpp
void execute() {
      log();  // Error: Which log()? Logger::log or Debugger::log?
  }
```

- cpp void execute() { log(); // Error: Which log()
- Logger::log or Debugger::log
- } ``` - `MyClass` inherits `log()` from

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
Implement a caching policy using CRTP:
```cpp
template <typename T>
class Cacheable {
    // Your implementation
};

class ExpensiveCalculation : public Cacheable<ExpensiveCalculation> {
    double value;
public:
    double compute() const {
        // Your code to integrate caching
    }
};
```

**Answer:**

```cpp
template <typename T>
class Cacheable {
    mutable std::unordered_map<std::string, double> cache;
    mutable std::mutex cacheMutex;

protected:
    double cachedCompute(const std::string& key) const {
        std::lock_guard<std::mutex> lock(cacheMutex);
        
        auto it = cache.find(key);
        if (it != cache.end()) {
            return it->second;  // Cache hit
    // ... (additional code omitted for brevity)
```

- cpp template <typename T> class Cacheable { mutable std::unordered_map<std::string, double> cache; mutable std::mutex cacheMutex;
- class ExpensiveCalculation : public Cacheable<ExpensiveCalculation> { double value;
- public: ExpensiveCalculation(double v) : value(v) {}

**Explanation:**

- **CRTP caching pattern:**
- Base class `Cacheable<T>` manages cache
- Derived class provides `computeImpl()` (actual computation)
- Base provides `cachedCompute()` wrapper

```cpp
mutable std::unordered_map<std::string, double> cache;
  mutable std::mutex cacheMutex;
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
Add compile-time interface enforcement:
```cpp
template <typename T>
class Printable {
public:
    // Add static_assert to check T has printImpl()
    void print() const {
        static_cast<const T*>(this)->printImpl();
    }
};
```

**Answer:**

```cpp
// C++20 Concepts (best):
template <typename T>
concept HasPrintImpl = requires(const T t) {
    { t.printImpl() } -> std::same_as<void>;
};

template <typename T>
class Printable {
public:
    void print() const requires HasPrintImpl<T> {
        static_cast<const T*>(this)->printImpl();
    }
    // ... (additional code omitted for brevity)
```

- cpp // C++20 Concepts (best): template <typename T> concept HasPrintImpl = requires(const T t) { { t.printImpl() } -> std::same_as<void>; };
- template <typename T> class Printable { public: void print() const requires HasPrintImpl<T> { static_cast<const T*>(this)->printImpl(); } };
- // Usage: class Document : public Printable<Document> { public: void printImpl() const { std::cout << "Printing document "; } };

**Explanation:**

- **Problem: Missing implementation detected late:**

```cpp
class BrokenClass : public Printable<BrokenClass> {
      // Forgot to implement printImpl()
  };

  BrokenClass b;  // Compiles OK so far
  b.print();      // ERROR HERE - too late, cryptic message
```

- cpp class BrokenClass : public Printable<BrokenClass> { // Forgot to implement printImpl() };

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
Why won't this compile and how do you fix it?
```cpp
template <typename T>
class Base {
    char buffer[sizeof(T)];  // Error!
};

class Derived : public Base<Derived> {
    int data[100];
};
```

**Answer:**

```cpp
Incomplete type error: sizeof(T) evaluated before Derived is fully defined
When Base<Derived> is instantiated, Derived is still incomplete (only declared)
Cannot take sizeof incomplete type
Fix: Use std::aligned_storage, defer evaluation, or redesign
```

**Explanation:**

- **The incomplete type problem:**

```cpp
class Derived : public Base<Derived> {  // At this point:
      // 1. Derived is declared but not defined
      // 2. Compiler instantiates Base<Derived>
      // 3. Base tries to evaluate sizeof(Derived)
      // 4. ERROR: Derived is incomplete!
      int data[100];
  };
```

- cpp class Derived : public Base<Derived> { // At this point: // 1
- Derived is declared but not defined // 2
- Compiler instantiates Base<Derived> // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
Create a policy composition with logging and metrics:
```cpp
// Implement Logger<T> and Metricsable<T>
// then compose them in SmartClass
```

**Answer:**

```cpp
#include <iostream>
#include <chrono>
#include <string>
#include <map>

// Logger policy
template <typename T>
class Logger {
protected:
    void log(const std::string& message) const {
        auto now = std::chrono::system_clock::now();
        auto time = std::chrono::system_clock::to_time_t(now);
    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <chrono> #include <string> #include <map>
- void logError(const std::string& error) const { std::cerr << "[ERROR] " << error << std::endl; } };
- // Metrics policy template <typename T> class Metricsable { mutable std::map<std::string, int> counters; mutable std::map<std::string, long long> timings;

**Explanation:**

- **Policy-based design with CRTP:**

```cpp
class SmartClass : public Logger<SmartClass>, public Metricsable<SmartClass>
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
Detect and fix the CRTP template parameter error:
```cpp
class MyClass : public Base<SomeOtherClass> {  // Wrong!
    // How to detect this at compile-time?
};
```

**Answer:**

```cpp
// C++20 Solution with concepts:
template <typename T>
class Base {
    static_assert(std::is_same_v<T, decltype(*this)> ||
                  std::is_base_of_v<Base<T>, T>,
                  "CRTP: Template parameter must be the derived class itself");
public:
    void interface() {
        static_cast<T*>(this)->implementation();
    }
};

    // ... (additional code omitted for brevity)
```

- public: void interface() { // Verify at compile time that this is actually a T* T* derived = static_cast<T*>(this); (void)derived; // Suppress unused warning
- static_cast<T*>(this)->implementation(); } };
- // C++11 with friend trick: template <typename T> class Base { friend T; // Only T can inherit from Base<T>

**Explanation:**

- **The CRTP mistake:**

```cpp
class MyClass : public Base<SomeOtherClass> {  // BUG!
      // MyClass inherits from Base<SomeOtherClass>
      // But Base will static_cast to SomeOtherClass*
      // This is WRONG! Should be Base<MyClass>
  };
```

- cpp class MyClass : public Base<SomeOtherClass> { // BUG
- // MyClass inherits from Base<SomeOtherClass> // But Base will static_cast to SomeOtherClass* // This is WRONG
- Should be Base<MyClass> }; ``` - Derived class must pass

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
Implement a CRTP-based iterator:
```cpp
template <typename Derived, typename Value>
class IteratorBase {
    // Implement operator++, *, ->, ==, !=
};

class MyIterator : public IteratorBase<MyIterator, int> {
    // Your implementation
};
```

**Answer:**

```cpp
template <typename Derived, typename Value>
class IteratorBase {
public:
    using value_type = Value;
    using reference = Value&;
    using pointer = Value*;
    using difference_type = std::ptrdiff_t;
    using iterator_category = std::forward_iterator_tag;

    // Dereference - calls derived implementation
    reference operator*() {
        return derived().dereference();
    // ... (additional code omitted for brevity)
```

- // Dereference - calls derived implementation reference operator*() { return derived().dereference(); }
- pointer operator->() { return &(derived().dereference()); }
- // Pre-increment Derived& operator++() { derived().increment(); return derived(); }

**Explanation:**

- **CRTP iterator pattern:**
- Base class `IteratorBase<Derived, Value>` provides operators
- Derived class implements minimal interface:
- `dereference()` - returns reference to value

```cpp
using value_type = Value;
  using reference = Value&;
  using pointer = Value*;
  using difference_type = std::ptrdiff_t;
  using iterator_category = std::forward_iterator_tag;
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
Why is CRTP unsuitable here? What should you use instead?
```cpp
template <typename T>
class Animal {
public:
    void makeSound() {
        static_cast<T*>(this)->makeSoundImpl();
    }
};

// Want to store different animals in a vector
std::vector<???> animals;  // Problem!
```

**Answer:**

```cpp
CRTP unsuitable: Each Animal<T> is a DIFFERENT TYPE
Dog = Animal<Dog>, Cat = Animal<Cat> - no common base type
Cannot store in homogeneous container (std::vector requires single type)
Solution: Use runtime polymorphism (virtual functions) instead
```

**Explanation:**

- **The fundamental CRTP limitation:**

```cpp
class Dog : public Animal<Dog> {};
  class Cat : public Animal<Cat> {};

  // These are COMPLETELY DIFFERENT TYPES:
  // Animal<Dog> and Animal<Cat> have no relationship
  // They don't share a common base class

  std::vector<???> animals;  // What type goes here?
  // Can't use Animal<???> - each animal is different template instantiation
```

- cpp class Dog : public Animal<Dog> {}; class Cat : public Animal<Cat> {};
- // These are COMPLETELY DIFFERENT TYPES: // Animal<Dog> and Animal<Cat> have no relationship // They don't share a common base class
- std::vector<???> animals; // What type goes here

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
Add Empty Base Optimization awareness:
```cpp
// Measure sizeof() with and without EBO
class WithPolicies
    : public Logger<WithPolicies>,
      public Cacheable<WithPolicies> {
    int data;
};
```

**Answer:**

```cpp
#include <iostream>
#include <type_traits>

// Empty policy class (EBO candidate)
template <typename T>
class Logger {
protected:
    void log(const std::string& msg) const {
        std::cout << msg << "\n";
    }
};

    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <type_traits>
- // Empty policy class (EBO candidate) template <typename T> class Logger { protected: void log(const std::string& msg) const { std::cout << msg << "\n"; } };
- // Empty policy class template <typename T> class Cacheable { protected: void cache() {} };

**Explanation:**

- **Empty Base Optimization (EBO):**
- C++ standard allows empty base classes to occupy **zero bytes**
- Empty class normally has `sizeof` = 1 (for unique address)
- When used as **base class**, compiler can optimize away that 1 byte

```cpp
class Empty {};

  std::cout << sizeof(Empty);  // 1, not 0!
```

- cpp class Empty {};
- std::cout << sizeof(Empty); // 1, not 0

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
Implement sensor fusion using CRTP:
```cpp
template <typename T>
class SensorFusion {
    // Base functionality
};

class LidarFusion : public SensorFusion<LidarFusion> {
    // Sensor-specific implementation
};
```

#### Q14
Fix the infinite recursion:
```cpp
template <typename T>
class Base {
public:
    void interface() {
        // This causes infinite recursion - fix it
        static_cast<T*>(this)->interface();
    }
};
```

#### Q15
Use `std::enable_shared_from_this` pattern:
```cpp
class MyClass : public std::enable_shared_from_this<MyClass> {
public:
    std::shared_ptr<MyClass> getPtr() {
        // Implement using shared_from_this()
    }
};
```

#### Q16
Partially specialize CRTP for arithmetic types:
```cpp
template <typename T, typename Enable = void>
class Serializer {
    // Generic implementation
};

// Add specialization for arithmetic types
```

#### Q17
Create a mixin that tracks constructor/destructor calls:
```cpp
template <typename T>
class LifetimTracker {
    // Track construction/destruction
};

class MyClass : public LifetimeTracker<MyClass> {
    // Your code
};
```

#### Q18
Implement a CRTP base that prevents copying:
```cpp
template <typename T>
class NonCopyable {
    // Prevent copy, allow move
};

class Resource : public NonCopyable<Resource> {
    // Should not be copyable
};
```

#### Q19
Debug this CRTP error message:
```cpp
template <typename T>
class Base {
public:
    void method() {
        static_cast<T*>(this)->required();
    }
};

class Derived : public Base<Derived> {
    // Missing required() - what error message appears?
    // How to improve it?
};
```

#### Q20
Design a real-time control loop using CRTP:
```cpp
template <typename T>
class Controller {
    // Base control logic with CRTP hooks
};

class PIDController : public Controller<PIDController> {
    // Specific PID implementation
};
```

---
#### Q13
Implement sensor fusion using CRTP:
```cpp
template <typename T>
class SensorFusion {
    // Base functionality
};

class LidarFusion : public SensorFusion<LidarFusion> {
    // Sensor-specific implementation
};
```

**Answer:**

```cpp
#include <vector>
#include <chrono>
#include <iostream>

template <typename T>
class SensorFusion {
protected:
    std::vector<double> fusedData;
    std::chrono::time_point<std::chrono::high_resolution_clock> lastUpdate;

public:
    void updateData(const std::vector<double>& raw_data) {
    // ... (additional code omitted for brevity)
```

- cpp #include <vector> #include <chrono> #include <iostream>
- template <typename T> class SensorFusion { protected: std::vector<double> fusedData; std::chrono::time_point<std::chrono::high_resolution_clock> lastUpdate;
- const std::vector<double>& getFusedData() const { return fusedData; }

**Explanation:**

- **CRTP sensor fusion pattern:** Base class provides common sensor processing pipeline (pre-process, sensor-specific processing, post-process validation); derived classes implement sensor-specific processing via `processSensorDataImpl()`
- **Common infrastructure in base:** Timestamp tracking with `lastUpdate`, data validation removing NaN/inf values, data storage in `fusedData` vector - reused across all sensor types
- **CRTP dispatch:** `updateData()` calls `static_cast<T*>(this)->processSensorDataImpl()` for compile-time dispatch; zero overhead compared to virtual functions; inlined by compiler
- **Sensor-specific logic:** Lidar filters by distance range (min/max), Camera converts disparity to depth using focal length, Each sensor has unique parameters and processing
- **Type safety:** Each sensor type is distinct (LidarFusion ≠ CameraFusion); compile-time type checking; no runtime type errors
- **Performance critical:** Sensor fusion runs at high frequency (100+ Hz); CRTP provides zero-overhead abstraction; no vtable lookups per update

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
Fix the infinite recursion:
```cpp
template <typename T>
class Base {
public:
    void interface() {
        // This causes infinite recursion - fix it
        static_cast<T*>(this)->interface();
    }
};
```

**Answer:**

- class Derived : public Base<Derived> { public: void interfaceImpl() { // Implementation (different name!) std::cout << "Derived: Processing\n"; } };
- // Usage: Derived d; d.interface(); // Calls Base::interface() → Derived::interfaceImpl() → returns // Output: // Base: Starting..
- // Derived: Processing // Base: Complete
- // Alternative naming conventions: // 1
- Impl suffix: interface() → interfaceImpl() // 2

**Explanation:**

- **The infinite recursion bug:** `static_cast<T*>(this)->interface()` calls derived's `interface()` which **is** base's `interface()` (inherited); loops forever until stack overflow; **same method name** is the problem
- **Name hiding doesn't help:** Even if Derived defines `interface()`, it hides Base's version; but CRTP explicitly casts to T* to call Derived's method; if names match, calls inherited Base::interface() again; **infinite loop**
- **Fix: Different method names:** Base provides `interface()` (public API), Derived provides `interfaceImpl()` (implementation); CRTP calls `interfaceImpl()` from `interface()`; no recursion - different names
- **Pre/post processing pattern:** Base's `interface()` can add common logic before/after calling derived implementation; useful for logging, validation, error handling; all in one place (DRY principle)
- **Naming conventions:** Impl suffix (most common): `interface()` → `interfaceImpl()`; do prefix: `interface()` → `doInterface()`; Private internal: `interface()` → `interface_internal()` + friend

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
Use `std::enable_shared_from_this` pattern:
```cpp
class MyClass : public std::enable_shared_from_this<MyClass> {
public:
    std::shared_ptr<MyClass> getPtr() {
        // Implement using shared_from_this()
    }
};
```

**Answer:**

- class MyClass : public std::enable_shared_from_this<MyClass> { int data;
- public: MyClass(int d) : data(d) {}
- // Safely get shared_ptr to this object std::shared_ptr<MyClass> getPtr() { return shared_from_this(); // CRTP method
- void process() { std::cout << "Processing: " << data << std::endl; } };
- // Usage: int main() { // MUST create with std::make_shared or new + shared_ptr auto obj = std::make_shared<MyClass>(42);

**Explanation:**

- **std::enable_shared_from_this is CRTP:** Inherits from `enable_shared_from_this<MyClass>` - classic CRTP pattern; base class template parameterized on derived class; provides `shared_from_this()` method
- **Why it's needed:** Can't write `std::shared_ptr<MyClass>(this)` - creates second control block; leads to double-delete when both shared_ptrs go out of scope; `shared_from_this()` returns shared_ptr using **existing** control block; safe shared ownership
- **How it works internally:** `enable_shared_from_this` has weak_ptr to control block; when first shared_ptr to object created, weak_ptr initialized; `shared_from_this()` converts weak_ptr to shared_ptr; uses existing control block
- **Requirements:** Object MUST be managed by shared_ptr already; calling `shared_from_this()` on stack object is UB; calling before any shared_ptr exists is UB; always use `std::make_shared` or `new` + `shared_ptr` first
- **Common use cases:** Async operations need shared ownership (callbacks, threads, timers); registering object with manager that requires shared_ptr; passing "this" to functions expecting shared_ptr

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
Partially specialize CRTP for arithmetic types:
```cpp
template <typename T, typename Enable = void>
class Serializer {
    // Generic implementation
};

// Add specialization for arithmetic types
```

**Answer:**

```cpp
#include <type_traits>
#include <iostream>
#include <sstream>
#include <vector>

// Primary template (generic case)
template <typename T, typename Enable = void>
class Serializer {
public:
    std::string serialize(const T& obj) const {
        // Generic implementation - assume T has serialize() method
        return static_cast<const T&>(obj).serializeImpl();
    // ... (additional code omitted for brevity)
```

- cpp #include <type_traits> #include <iostream> #include <sstream> #include <vector>
- // Partial specialization for containers template <typename T> class Serializer<std::vector<T>> { Serializer<T> elementSerializer;
- class Point : public SerializableBase<Point> { double x, y;

**Explanation:**

- **Partial specialization with SFINAE:** Primary template for generic types; partial specialization with `std::enable_if_t<std::is_arithmetic_v<T>>` for arithmetic types (int, double, float, etc.); different implementations based on type traits
- **std::enable_if_t mechanics:** `std::enable_if_t<condition>` = `void` if condition is true; `std::enable_if_t<condition>` = substitution failure if false; SFINAE: Substitution Failure Is Not An Error; wrong specialization removed from overload set
- **Arithmetic types specialization:** `std::is_arithmetic_v<T>` matches int, long, float, double, char, bool; uses simple `std::to_string()` conversion; no need for custom serializeImpl()
- **Generic fallback:** Primary template requires T to have `serializeImpl()`; CRTP-style: `static_cast<const T&>(obj).serializeImpl()`; works for custom classes like Point
- **Container specialization:** `Serializer<std::vector<T>>` handles vectors of any type; recursively uses `Serializer<T>` for elements; composable: vector<int>, vector<double>, vector<Point> all work
- **Combining CRTP and specialization:** `SerializableBase<T>` is CRTP base providing `serialize()` method; derived classes (like Point) implement `serializeImpl()`; Serializer detects if T is arithmetic or custom, chooses correct specialization

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
Create a mixin that tracks constructor/destructor calls:
```cpp
template <typename T>
class LifetimeTracker {
    // Track construction/destruction
};

class MyClass : public LifetimeTracker<MyClass> {
    // Your code
};
```

**Answer:**

```cpp
#include <iostream>
#include <atomic>
#include <string>

template <typename T>
class LifetimeTracker {
    static std::atomic<int> constructCount;
    static std::atomic<int> destructCount;
    static std::atomic<int> liveCount;

protected:
    LifetimeTracker() {
    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <atomic> #include <string>
- template <typename T> class LifetimeTracker { static std::atomic<int> constructCount; static std::atomic<int> destructCount; static std::atomic<int> liveCount;
- protected: LifetimeTracker() { ++constructCount; ++liveCount; log("Constructor"); }

**Explanation:**

- **CRTP mixin pattern:** `LifetimeTracker<T>` is base class providing lifetime tracking; each derived class T gets **separate** static counters (LifetimeTracker<MyClass> ≠ LifetimeTracker<AnotherClass>); tracks construction, destruction, copy, move independently per type
- **Static counters per type:** `static std::atomic<int> constructCount` - one per template instantiation; MyClass has its own counters, AnotherClass has different counters; template magic: each T gets separate statics
- **Protected constructors:** Derived class must call base constructor; LifetimeTracker increments counters automatically; no manual tracking needed in derived class; **zero boilerplate** for user
- **Tracking all special members:** Default constructor, Copy constructor, Move constructor, Destructor - all tracked; distinguishes between construction types; useful for debugging copy/move efficiency
- **Atomic counters:** `std::atomic<int>` for thread safety; multiple threads can construct/destruct objects safely; no data races on counters
- **Live object count:** `liveCount = constructCount - destructCount`; shows current number of live objects; useful for detecting leaks (should be 0 at end)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
Implement a CRTP base that prevents copying:
```cpp
template <typename T>
class NonCopyable {
    // Prevent copy, allow move
};

class Resource : public NonCopyable<Resource> {
    // Should not be copyable
};
```

**Answer:**

```cpp
#include <iostream>
#include <memory>

template <typename T>
class NonCopyable {
protected:
    NonCopyable() = default;  // Allow construction
    ~NonCopyable() = default;  // Allow destruction

public:
    // Delete copy constructor and copy assignment
    NonCopyable(const NonCopyable&) = delete;
    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <memory>
- template <typename T> class NonCopyable { protected: NonCopyable() = default; // Allow construction ~NonCopyable() = default; // Allow destruction
- public: // Delete copy constructor and copy assignment NonCopyable(const NonCopyable&) = delete; NonCopyable& operator=(const NonCopyable&) = delete;

**Explanation:**

- **NonCopyable CRTP pattern:** Delete copy constructor and copy assignment in base class; derived class inherits deleted copy operations; **automatically non-copyable** - zero boilerplate; allows move operations (move constructor, move assignment)
- **Why delete in base class:** If deleted in derived class only, must remember to delete in **every** derived class; easy to forget; inheriting from NonCopyable guarantees non-copyability; **DRY principle** - define once, reuse everywhere
- **Protected constructors in base:** `protected:` constructor and destructor; derived class can construct/destruct; external code cannot instantiate NonCopyable directly; template parameter T unused but ensures separate base per type (good practice)
- **Move semantics still allowed:** `= default` for move operations in base; derived class can implement move if needed; common pattern: moveable but not copyable; e.g., unique_ptr, file handles, database connections
- **RAII resources typical use case:** File handles (can't copy file), Database connections (can't duplicate connection), Network sockets (can't share socket), Smart pointers like unique_ptr (exclusive ownership)
- **Alternative: Boost.Noncopyable:** Boost library has `boost::noncopyable` - same CRTP pattern; widely used in production code; validates this design

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
Debug this CRTP error message:
```cpp
template <typename T>
class Base {
public:
    void method() {
        static_cast<T*>(this)->required();
    }
};

class Derived : public Base<Derived> {
    // Missing required() - what error message appears?
    // How to improve it?
};
```

**Answer:**

```cpp
Without improvement:
error: 'class Derived' has no member named 'required'
  static_cast<T*>(this)->required();
                         ^~~~~~~~
note: in instantiation of member function 'Base<Derived>::method' requested here

This error is cryptic and appears only when method() is called, not when Derived is defined.

Improved with static_assert:
```

- This error is cryptic and appears only when method() is called, not when Derived is defined
- public: Base() { static_assert(decltype(test_required<T>(0))::value, "ERROR: Derived class must implement required() method"); }
- void method() { static_cast<T*>(this)->required(); } };

**Explanation:**

- **Default error message problems:** Error appears only when `method()` is **called**, not when Derived is defined; error mentions `static_cast` internals (confusing for users); long template instantiation stack trace; doesn't explain **what** Derived must implement
- **SFINAE-based check:** `test_required<T>(int)` tries to call `T::required()`; if `required()` exists → returns `std::true_type`; if missing → substitution failure, second overload returns `std::false_type`; `static_assert` checks result; **fails early** in constructor
- **Error message improvement:** `static_assert` shows **custom message**: "ERROR: Derived class must implement required()"; fails when Derived is **constructed**, not when method() called; user knows **exactly** what to implement
- **Where to put check:** In constructor: fails when object created (early); In method: fails when method called (late, but compile-time); Class-level static_assert: fails immediately when Derived defined (earliest)
- **C++20 concepts version:** `concept HasRequired` defines requirement clearly; `requires HasRequired<T>` constrains `method()`; error message: "Derived does not satisfy HasRequired"; clearest error of all; standard C++20 way
- **Trade-offs:** SFINAE: Works in C++11+, complex syntax; static_assert: Works in C++11+, clearer than SFINAE; Concepts: C++20 only, clearest errors, standard approach

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
Design a real-time control loop using CRTP:
```cpp
template <typename T>
class Controller {
    // Base control logic with CRTP hooks
};

class PIDController : public Controller<PIDController> {
    // Specific PID implementation
};
```

**Answer:**

```cpp
#include <iostream>
#include <chrono>
#include <thread>
#include <cmath>

template <typename T>
class Controller {
    double setpoint;
    double currentValue;
    std::chrono::microseconds loopPeriod;
    bool running;

    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <chrono> #include <thread> #include <cmath>
- template <typename T> class Controller { double setpoint; double currentValue; std::chrono::microseconds loopPeriod; bool running;
- public: Controller(double sp, std::chrono::microseconds period) : setpoint(sp), currentValue(0), loopPeriod(period), running(false) {}

**Explanation:**

- **CRTP control loop pattern:** Base class `Controller<T>` provides control loop infrastructure (timing, sensing, actuation, logging); derived classes implement controller-specific algorithms via `computeControlImpl()`; zero overhead dispatch - controller algorithm inlined
- **Real-time requirements:** Fixed loop period (e.g., 100 Hz = 10ms); timing measured and compensated (sleep for remaining time); deterministic execution critical for control stability; CRTP avoids virtual function overhead
- **Control loop phases:** Init → sense current value → calculate error (setpoint - current) → compute control output (controller-specific) → actuate → wait for next cycle → repeat → cleanup
- **CRTP hooks:** `initImpl()` - controller initialization; `computeControlImpl(error)` - calculate control output (PID, bang-bang, etc.); `cleanupImpl()` - controller cleanup; derived implements controller algorithm, base handles infrastructure
- **PID controller specifics:** Proportional (P): error * Kp; Integral (I): sum of errors over time * Ki; Derivative (D): rate of error change * Kd; maintains state (integral, previousError); classic control algorithm
- **Bang-bang controller:** Simple on-off control; output = +magnitude if error > 0, -magnitude otherwise; no state needed; demonstrates different controller types with same infrastructure

**Note:** Full detailed explanation with additional examples available in source materials.

---
