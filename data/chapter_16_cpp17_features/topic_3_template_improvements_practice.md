### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1
**Difficulty:** Medium

Create a `Resource` class template that manages different types of autonomous vehicle resources (sensors, actuators, etc.). Implement proper CTAD so that `Resource r(sensor_ptr)` correctly deduces the template type from the smart pointer argument.

**Answer:**

- template<typename T> class Resource { std::shared_ptr<T> ptr; std::string name;
- public: // Constructor from shared_ptr Resource(std::shared_ptr<T> p, std::string n = "unnamed") : ptr(p), name(n) {}
- // Constructor from raw pointer (creates shared_ptr) Resource(T* p, std::string n = "unnamed") : ptr(p), name(n) {}
- void print() const { std::cout << "Resource: " << name << "\n"; }
- T* get() { return ptr.get(); } };

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
**Difficulty:** Medium

Write a variadic template function `validate_all` that takes multiple predicate functions and returns true only if all predicates return true. Use fold expressions.

**Answer:**
```cpp
#include <iostream>
#include <functional>

template<typename... Predicates>
bool validate_all(Predicates... preds) {
    return (... && preds());  // Left fold with &&
}

bool check_speed() {
    std::cout << "Checking speed... ";
    bool ok = true;
    std::cout << (ok ? "OK\n" : "FAIL\n");
    return ok;
}

bool check_sensors() {
    std::cout << "Checking sensors... ";
    bool ok = true;
    std::cout << (ok ? "OK\n" : "FAIL\n");
    return ok;
}

bool check_battery() {
    std::cout << "Checking battery... ";
    bool ok = false;
    std::cout << (ok ? "OK\n" : "FAIL\n");
    return ok;
}

int main() {
    bool all_ok = validate_all(check_speed, check_sensors, check_battery);

    std::cout << "System ready: " << std::boolalpha << all_ok << "\n";

    return 0;
}
```

**Explanation:** Fold expression `(... && preds())` short-circuits on first false, efficient validation.

---

#### Q3

**Difficulty:**

- Implement a parallel point cloud filter that removes outliers based on distance threshold
- Compare sequential vs parallel performance.

**Answer:**

```cpp
#include <vector>
#include <algorithm>
#include <execution>
#include <random>
#include <chrono>
#include <iostream>
#include <cmath>

struct Point3D {
    double x, y, z;

    double distance_from_origin() const {
    // ... (additional code omitted for brevity)
```

- cpp #include <vector> #include <algorithm> #include <execution> #include <random> #include <chrono> #include <iostream> #include <cmath>
- struct Point3D { double x, y, z;
- double distance_from_origin() const { return std::sqrt(x*x + y*y + z*z); } };

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4

**Difficulty:**

- Implement a resource manager that safely acquires multiple resources simultaneously using std::scoped_lock to prevent deadlock.

**Answer:**

```cpp
#include <mutex>
#include <thread>
#include <vector>
#include <iostream>
#include <chrono>

class Resource {
    std::mutex mtx;
    int value;
    std::string name;

public:
    // ... (additional code omitted for brevity)
```

- cpp #include <mutex> #include <thread> #include <vector> #include <iostream> #include <chrono>
- class Resource { std::mutex mtx; int value; std::string name;
- public: Resource(std::string n, int v) : name(n), value(v) {}

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
**Difficulty:** Medium

Create compile-time lookup tables for trigonometric functions used in autonomous vehicle trajectory planning using constexpr lambdas.

**Answer:**

- // constexpr pi constexpr double PI = 3.14159265358979323846;
- // Generate sine lookup table at compile time template<size_t N> constexpr auto generate_sin_table() { std::array<double, N> table{};
- for (int i = 1; i < 10; ++i) { term *= -x * x / ((2 * i) * (2 * i + 1)); result += term; }
- return result; };
- for (size_t i = 0; i < N; ++i) { double angle = (static_cast<double>(i) / N) * 2 * PI; table[i] = sine(angle); }

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6

**Difficulty:**

- Implement a fast logger using std::to_chars that formats sensor readings without allocations.

**Answer:**

```cpp
#include <charconv>
#include <string_view>
#include <iostream>
#include <chrono>
#include <vector>

class FastLogger {
    char buffer[1024];
    char* current;

public:
    FastLogger() : current(buffer) {}
    // ... (additional code omitted for brevity)
```

- cpp #include <charconv> #include <string_view> #include <iostream> #include <chrono> #include <vector>
- class FastLogger { char buffer[1024]; char* current;
- public: FastLogger() : current(buffer) {}

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
**Difficulty:** Hard

Implement a function composer using fold expressions that chains multiple transformation functions.

**Answer:**

- // Compose functions using fold expressions template<typename..
- Funcs> auto compose(Funcs..
- funcs) { return [=](auto x) { // Right fold: f(g(h(x))) return (..
- (funcs(x))); // Error: this doesn't work
- // Need to manually chain }; }

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
**Difficulty:** Medium

Create a type-safe message system using std::variant with CTAD for autonomous vehicle communication.

**Answer:**

- struct SpeedCommand { double speed; };
- struct StopCommand { std::string reason; };
- struct TurnCommand { double angle; std::string direction; };
- using Command = std::variant<SpeedCommand, StopCommand, TurnCommand>;
- class CommandHandler { public: void handle(const Command& cmd) { std::visit([](const auto& c) { using T = std::decay_t<decltype(c)>;

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
**Difficulty:** Hard

Implement sensor fusion that combines multiple sensor readings using parallel std::reduce.

**Answer:**

- struct SensorReading { double value; double confidence; // 0.0 to 1.0
- double fused_value = (value * confidence + other.value * other.confidence) / total_conf; double fused_conf = (confidence + other.confidence) / 2.0;
- return {fused_value, fused_conf}; } };
- for (int i = 0; i < 1000; ++i) { readings.push_back({val_dis(gen), conf_dis(gen)}); }

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10

**Difficulty:**

- Create a comprehensive example that uses multiple C++17 features together in a realistic autonomous vehicle scenario.

**Answer:**

```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <variant>
#include <string_view>
#include <filesystem>
#include <algorithm>
#include <execution>
#include <map>

namespace fs = std::filesystem;

    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <vector> #include <optional> #include <variant> #include <string_view> #include <filesystem> #include <algorithm> #include <execution> #include <map>
- namespace fs = std::filesystem;
- // Structured binding ready struct struct SensorData { std::string name; double value; int timestamp; };

**Explanation:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
