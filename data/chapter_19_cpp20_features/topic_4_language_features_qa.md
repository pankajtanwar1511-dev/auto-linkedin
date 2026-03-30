## TOPIC: C++20 Language Features - Three-Way Comparison and Modern Syntax

### INTERVIEW_QA: Common Questions

---

#### Q1: What is the three-way comparison operator and why was it introduced?

**Answer:**

The three-way comparison operator (`<=>`, "spaceship operator") performs a single comparison and returns a result indicating the relative order of two values.

**Before C++20:**
```cpp
struct Point {
    int x, y;

    // Need 6 operators
    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
    bool operator!=(const Point& o) const { return !(*this == o); }
    bool operator<(const Point& o) const { /* ... */ }
    bool operator<=(const Point& o) const { /* ... */ }
    bool operator>(const Point& o) const { /* ... */ }
    bool operator>=(const Point& o) const { /* ... */ }
};
```

**With C++20:**
```cpp
struct Point {
    int x, y;

    auto operator<=>(const Point&) const = default;  // 1 line!
    bool operator==(const Point&) const = default;
};
```

**Why introduce it?**
1. **Reduce boilerplate**: 1-2 lines instead of 6 functions
2. **Avoid errors**: Implementing 6 operators correctly is error-prone
3. **Better performance**: Single comparison for ordering operations
4. **Expressiveness**: Clearly shows type is comparable

---

#### Q2: Explain the three comparison categories.

**Answer:**

| Category | Meaning | Values | Example Types |
|----------|---------|--------|---------------|
| `std::strong_ordering` | Fully ordered, substitutable | `less`, `equal`, `greater` | `int`, `std::string` |
| `std::weak_ordering` | Fully ordered, not substitutable | `less`, `equivalent`, `greater` | Case-insensitive strings |
| `std::partial_ordering` | Some values unordered | `less`, `equivalent`, `greater`, `unordered` | `float`, `double` (NaN) |

**strong_ordering:** `a == b` means `a` and `b` are identical and interchangeable.

**weak_ordering:** `a == b` means they're equivalent for comparison purposes, but may differ in other ways.
```cpp
CaseInsensitiveString a{"Hello"}, b{"HELLO"};
// a == b (equivalent), but string contents differ
```

**partial_ordering:** Some values (like NaN) cannot be compared.
```cpp
double a = 1.0, b = NaN;
a <=> b;  // Returns std::partial_ordering::unordered
```

---

#### Q3: Why do we need both `operator<=>` and `operator==`?

**Answer:**

**Efficiency Reason:** Equality checks can be optimized differently than ordering.

```cpp
struct BigData {
    std::vector<int> data;

    // Fast equality: Check sizes first, short-circuit
    bool operator==(const BigData& other) const {
        return data.size() == other.size() &&  // O(1) check
               std::equal(data.begin(), data.end(), other.begin());
    }

    // Ordering: Must compare elements lexicographically
    auto operator<=>(const BigData& other) const {
        return data <=> other.data;  // Can't short-circuit as easily
    }
};
```

For simple types, you can default both:
```cpp
struct Point {
    int x, y;
    auto operator<=>(const Point&) const = default;
    bool operator==(const Point&) const = default;
};
```

**Why separate?** Compiler doesn't synthesize `operator==` from `operator<=>` to allow optimization opportunities.

---

#### Q4: What's the difference between `constexpr`, `consteval`, and `constinit`?

**Answer:**

| Feature | `constexpr` | `consteval` | `constinit` |
|---------|------------|-------------|-------------|
| **Purpose** | Can run at compile-time | **Must** run at compile-time | Ensures compile-time initialization |
| **Runtime execution** | ✅ Allowed | ❌ Never | N/A (for initialization only) |
| **Mutability** | Immutable if variable | Immutable if variable | ✅ Mutable after init |
| **Use on** | Functions, variables | Functions only | Variables only |

**Examples:**

```cpp
// constexpr: CAN be compile-time
constexpr int square(int x) { return x * x; }

constexpr int a = square(5);  // Compile-time
int b = square(10);           // Could be runtime

// consteval: MUST be compile-time
consteval int cube(int x) { return x * x * x; }

constexpr int c = cube(3);  // ✅ Compile-time
int n = 5;
int d = cube(n);            // ❌ Error: n is runtime

// constinit: Guarantees compile-time initialization, but mutable
constinit int global = 42;  // Initialized at compile-time
global = 100;               // ✅ OK: Can modify later
```

---

#### Q5: How do designated initializers work? What are the restrictions?


**Answer:**

Designated initializers let you initialize aggregate members by name:

```cpp
struct Point { int x, y, z; };

Point p {.x = 1, .y = 2, .z = 3};
```

- cpp struct Point { int x, y, z; };
- Point p {.x = 1, .y = 2, .z = 3}; ```

**Restrictions:**

1. **Must follow declaration order:**

```cpp
// ❌ Error: z before y
   Point p {.z = 3, .y = 2, .x = 1};

   // ✅ OK
   Point p {.x = 1, .y = 2, .z = 3};
```

- cpp // ❌ Error: z before y Point p {.z = 3, .y = 2, .x = 1};
- // ✅ OK Point p {.x = 1, .y = 2, .z = 3}; ```

**Benefits:**

- Self-documenting
- Less error-prone than positional
- Clear intent

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: How do `[[likely]]` and `[[unlikely]]` attributes improve performance?


**Answer:**
- These attributes help the compiler optimize branch prediction and instruction cache layout.
**How they work:**
```cpp
void process_request(Request req) {
    if (req.is_valid()) [[likely]] {
        // Most requests are valid - optimize for this path
        handle_request(req);
    } else [[unlikely]] {
        // Error path - less optimized, may be further away in code
        log_error(req);
    // ... (abbreviated)
```
**Performance Benefits:**
- Better Branch Prediction: CPU can prefetch instructions for likely path 2
- Code Layout: Compiler places `[[likely]]` blocks in hot path, `[[unlikely]]` blocks further away 3
- Instruction Cache: Keeps common paths in cache, reduces cache misses
**Benchmarks:**
- Can reduce branch mispredictions by 10-30% in hot loops
- Improves performance in error-handling heavy code
- Most effective when the likelihood is asymmetric (90%+ one way)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What are template lambdas and when should you use them?


**Answer:**
Template lambdas (C++20) allow lambdas to have explicit template parameters:
```cpp
// C++20: Template lambda
auto print = []<typename T>(T value) {
    std::cout << "Value: " << value << ", Type: " << typeid(T).name() << '\n';
};
print(42);      // T = int
print(3.14);    // T = double
print("text");  // T = const char*
```
- print(42); // T = int print(3.14); // T = double print("text"); // T = const char* ```
**When to use:**
1. **When you need the actual type:**
```cpp
// Can't do this with auto:
   auto get_size = []<typename T>(const T& container) {
       using value_type = typename T::value_type;  // Need actual type
       return container.size();
   };
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: Explain `using enum` and its benefits.


**Answer:**

- `using enum` brings enum values into current scope:

**Before C++20:**

- void paint(Color c) { switch (c) { case Color::Red: break; // Verbose case Color::Green: break; case Color::Blue: break; } } ```

**With C++20:**

- switch (c) { case Red: break; // Concise case Green: break; case Blue: break; } } ```

**Benefits:**

- Less Verbose: Eliminates repetitive `Color::` prefix 2
- Scoped: Only affects local scope, no global pollution 3
- Selective Import: Can import specific values: ```cpp using Color::Red; using Color::Blue; // Green still requires Color::Green ```
- Multiple Enums: ```cpp using enum Color; using enum Shape; // Both sets of enumerators available ```

**When NOT to use:**

- Avoid if names conflict with variables
- Don't use at global scope (defeats scoped enum purpose)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: What's the difference between `constexpr` and `consteval` in practice?


**Answer:**



**Example:**

```cpp
constexpr int square(int x) { return x * x; }
consteval int cube(int x) { return x * x * x; }

int main() {
    // constexpr: Can be compile-time OR runtime
    constexpr int a = square(5);  // Compile-time ✅
    int n = 10;
    // ... (abbreviated)
```

- cpp constexpr int square(int x) { return x * x; } consteval int cube(int x) { return x * x * x; }

**When to use `consteval`:**

1. **Enforce compile-time computation:**

```cpp
consteval size_t buffer_size(size_t n) {
       if (n > 1024) throw "Too large";
       return n * sizeof(int);
   }

   std::array<char, buffer_size(100)> buf;  // ✅ Validated at compile-time
```

- cpp consteval size_t buffer_size(size_t n) { if (n > 1024) throw "Too large"; return n * sizeof(int); }
- std::array<char, buffer_size(100)> buf; // ✅ Validated at compile-time ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: How does return type deduction work for `operator<=>`?


**Answer:**
Compiler chooses the **weakest** comparison category among all members:
```cpp
struct Example1 {
    int a;           // strong_ordering
    std::string b;   // strong_ordering
    auto operator<=>(const Example1&) const = default;
    // Deduced: strong_ordering (all members are strong)
};
    // ... (abbreviated)
```
- cpp struct Example1 { int a; // strong_ordering std::string b; // strong_ordering
- auto operator<=>(const Example1&) const = default; // Deduced: strong_ordering (all members are strong) };
**Category Hierarchy (weakest to strongest):**
```cpp
partial_ordering  (weakest)
    ↓
weak_ordering
    ↓
strong_ordering   (strongest)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: Can you mix designated and positional initializers?

**Answer:**

**No, you cannot mix them in C++20.**

```cpp
struct Point { int x, y, z; };

// ❌ Error: Can't mix positional and designated
Point p1{1, .y = 2, .z = 3};

// ✅ OK: All positional
Point p2{1, 2, 3};

// ✅ OK: All designated
Point p3{.x = 1, .y = 2, .z = 3};

// ✅ OK: Partial designated (others default-initialized)
Point p4{.x = 1};  // y=0, z=0
```

**Rationale:** Mixing would be ambiguous and error-prone.

**Nested Structures:**

```cpp
struct Line {
    Point start;
    Point end;
};

// ✅ OK: Each level uses one style
Line l1{
    .start = {1, 2, 3},           // Positional for Point
    .end = {.x=4, .y=5, .z=6}     // Designated for Point
};
```

---

#### Q12: What happens if you don't define `operator==` with `operator<=>`?


**Answer:**

**`operator==` is NOT automatically generated from `operator<=>`.**

```cpp
struct Point {
    int x, y;
    auto operator<=>(const Point&) const = default;
};

Point p1{1, 2}, p2{1, 2};

    // ... (abbreviated)
```

- cpp struct Point { int x, y; auto operator<=>(const Point&) const = default; };
- Point p1{1, 2}, p2{1, 2};

**Solution: Define both:**

```cpp
struct Point {
    int x, y;
    auto operator<=>(const Point&) const = default;
    bool operator==(const Point&) const = default;  // Add this
};
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: How do comparison categories convert?


**Answer:**
**Implicit Conversions (Weaker to Stronger):**
```cpp
std::strong_ordering s = std::strong_ordering::less;
// ✅ OK: strong → weak
std::weak_ordering w = s;
// ✅ OK: strong → partial
std::partial_ordering p1 = s;
    // ... (abbreviated)
```
- cpp std::strong_ordering s = std::strong_ordering::less;
- // ✅ OK: strong → weak std::weak_ordering w = s;
**Conversion Rules:**
```cpp
strong_ordering
    ↓ (implicit)
weak_ordering
    ↓ (implicit)
partial_ordering
```
- strong_ordering ↓ (implicit) weak_ordering ↓ (implicit) partial_ordering ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: What are the restrictions on designated initializers?


**Answer:**

- Must Match Declaration Order:**
- // ❌ Error: Wrong order Data d1{.c = 3, .b = 2, .a = 1};
- // ✅ OK: Correct order Data d2{.a = 1, .b = 2, .c = 3}; ```
- Can't Mix with Positional:**
- Only for Aggregates:**

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: When would you use conditionally explicit constructors?


**Answer:**

- Used when convertibility should depend on a compile-time condition:
- struct Base {}; struct Derived : Base {};
- int main() { Derived* d = new Derived;
- // ✅ Implicit conversion OK (Derived* → Base*) SmartPointer<Base> ptr1 = new Derived;
- // ✅ Explicit conversion required (unrelated types) SmartPointer<int> ptr2 = SmartPointer<int>(new int); } ```

**Use Cases:**



**Benefits:**

- Allows implicit conversion when safe
- Forces explicit conversion when potentially unsafe
- Single constructor instead of two overloads

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16: How does `constinit` differ from `constexpr` for global variables?


**Answer:**



**Examples:**

```cpp
// constexpr: Constant value
constexpr int MAX_SIZE = 100;
MAX_SIZE = 200;  // ❌ Error: Can't modify

// constinit: Initialized at compile-time, but mutable
constinit int current_size = 100;
current_size = 200;  // ✅ OK: Can modify
    // ... (abbreviated)
```

- cpp // constexpr: Constant value constexpr int MAX_SIZE = 100; MAX_SIZE = 200; // ❌ Error: Can't modify
- // constinit: Initialized at compile-time, but mutable constinit int current_size = 100; current_size = 200; // ✅ OK: Can modify

**When to use `constinit`:**

1. **Thread-local storage:**

```cpp
thread_local constinit int thread_counter = 0;  // Initialized at compile-time
```

- cpp thread_local constinit int thread_counter = 0; // Initialized at compile-time ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: Can you have a base class comparison with `operator<=>`?


**Answer:**



**Yes, defaulted `operator<=>` automatically includes base class comparison:**

```cpp
struct Base {
    int x;
    auto operator<=>(const Base&) const = default;
};

struct Derived : Base {
    int y;
    // ... (abbreviated)
```

- cpp struct Base { int x; auto operator<=>(const Base&) const = default; };
- struct Derived : Base { int y; auto operator<=>(const Derived&) const = default; // Compares Base::x first

**Custom Base Class Comparison:**

```cpp
struct Derived : Base {
    int y;

    // Custom: Compare y first, then base
    auto operator<=>(const Derived& other) const {
        if (auto cmp = y <=> other.y; cmp != 0)
            return cmp;
    // ... (abbreviated)
```

- cpp struct Derived : Base { int y;

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: What's the performance impact of branch prediction attributes?


**Answer:**



**Measurable Performance Gains in Specific Scenarios:**

**Scenario 1: Error Handling**

```cpp
// Without attribute
Result process(Data data) {
    if (data.is_corrupt()) {  // Happens <0.01% of the time
        return handle_error(data);
    }
    return fast_process(data);
}
    // ... (abbreviated)
```

- // Benchmark: 8-15% faster with [[unlikely]] (millions of iterations) ```

**When It Doesn't Help:**

- Balanced branches (50/50): No benefit 2
- Already-optimal CPU prediction: Minimal gain 3
- Cold code paths: Branch prediction not critical

**Best Practices:**

- Use when branch probability is >90% in one direction
- Profile first: Don't guess likelihood
- Most effective in hot loops and error handling

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: How do template lambdas help with perfect forwarding?


**Answer:**

- Template lambdas enable perfect forwarding in lambdas:

**Problem with Generic Lambdas (C++14):**



**Solution with Template Lambda (C++20):**

- // Variadic version auto wrapper3 = []<typename..
- args) { return func(std::forward<Args>(args)...); }; ```

**Practical Example:**

- void process(int& x) { std::cout << "lvalue: " << x << '\n'; } void process(int&& x) { std::cout << "rvalue: " << x << '\n'; }
- int main() { auto forwarder = []<typename T>(T&& arg) { process(std::forward<T>(arg)); };
- int a = 10; forwarder(a); // Calls lvalue version forwarder(20); // Calls rvalue version } ```

**Output:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: What are aggregate improvements in C++20?


**Answer:**



**C++20 Added Two Major Aggregate Enhancements:**

- Parenthesized Initialization:**
- // C++17: Only braces Point p1{1, 2};
- // ✅ C++20: Parentheses also work Point p2(1, 2); Point p3 = Point(3, 4); ```
- Aggregates with Base Classes:**
- // ✅ C++20: Can initialize base class members Derived d1{.id = 1, .name = "Alice"};

**What Qualifies as an Aggregate in C++20:**

- // ✅ Aggregate (with base) struct B : A { std::string s; };
- // ❌ Not Aggregate (has constructor) struct C { int x; C(int val) : x(val) {} };
- // ❌ Not Aggregate (has virtual function) struct D { virtual void foo(); }; ```

**Benefits:**

- More flexible initialization syntax
- Simpler inheritance initialization
- Better integration with designated initializers

**Note:** Full detailed explanation with additional examples available in source materials.

---
