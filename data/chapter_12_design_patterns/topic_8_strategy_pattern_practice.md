## TOPIC: Strategy Pattern (Policy-Based Design)

### PRACTICE_TASKS: Code Analysis and Implementation Challenges

#### Q1
```cpp
class Calculator {
    int (*operation)(int, int);
public:
    void setOperation(int (*op)(int, int)) {
        operation = op;
    }

    int calculate(int a, int b) {
        return operation(a, b);  // What if operation is null?
    }
};

// What's the problem?
```

**Answer:**

- Null pointer dereference if `operation` not initialized
- Calling null function pointer causes undefined behavior (typically crashes).

**Explanation:**



**Why This is Dangerous:**

Function pointer initialized to garbage value by default. If `calculate()` called before `setOperation()`, dereferencing null/garbage pointer crashes program.

```cpp
Calculator calc;
// operation = <uninitialized garbage>

int result = calc.calculate(5, 3);  // ❌ CRASH
// Dereferencing uninitialized function pointer
```

- cpp Calculator calc; // operation = <uninitialized garbage>
- int result = calc.calculate(5, 3); // ❌ CRASH // Dereferencing uninitialized function pointer ```

**Concrete Failure:**

```cpp
void testCalculator() {
    Calculator calc;
    // Forgot to call setOperation()

    int result = calc.calculate(10, 5);
    // → operation() is null or garbage
    // → Segmentation fault or undefined behavior
}
```

- cpp void testCalculator() { Calculator calc; // Forgot to call setOperation()
- int result = calc.calculate(10, 5); // → operation() is null or garbage // → Segmentation fault or undefined behavior } ```

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
```cpp
class Sorter {
    bool (*compare)(int, int);
public:
    void sort(vector<int>& data) {
        std::sort(data.begin(), data.end(), compare);
    }
};

// Usage:
bool ascending(int a, int b) { return a < b; }
Sorter sorter;
sorter.setCompare(ascending);

// What are the limitations of function pointers for strategies?
```

**Answer:**

- Function pointers cannot capture state (no closures) and have limited type safety compared to functors or lambdas.

**Explanation:**

- Limitation #1: No State/Context
- Function pointers are just addresses - cannot carry additional data or configuration
- // Cannot do this with function pointers: sorter.setCompare(closeEnough_with_threshold_5); ```
- Limitation #2: Cannot Use Lambdas with Captures
- Sorter sorter; sorter.setCompare(compare); // ❌ Compile error // Lambda with capture cannot convert to function pointer ```

**Performance Comparison:**



**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
class FileCompressor {
    unique_ptr<CompressionStrategy> strategy;
public:
    void compress(const string& file) {
        auto data = readFile(file);
        auto compressed = strategy->compress(data);
        writeFile(file + ".compressed", compressed);
    }

    void setStrategy(unique_ptr<CompressionStrategy> s) {
        strategy = std::move(s);
    }
};

// Usage:
FileCompressor compressor;
compressor.setStrategy(make_unique<ZipStrategy>());
compressor.compress("data.txt");

compressor.setStrategy(make_unique<GzipStrategy>());
compressor.compress("data.txt");  // ❌ What's wrong?
```

**Answer:**

- First compression overwrites input file, making second compression attempt on corrupted/compressed data instead of original.

**Explanation:**



**Execution Flow:**

```cpp
// State: data.txt (original uncompressed)
compressor.setStrategy(make_unique<ZipStrategy>());
compressor.compress("data.txt");
// → Reads data.txt
// → Compresses with ZIP
// → Writes data.txt.compressed
// State: data.txt (still original), data.txt.compressed (ZIP)

compressor.setStrategy(make_unique<GzipStrategy>());
compressor.compress("data.txt");
// → Reads data.txt (ORIGINAL uncompressed)
// → Compresses with GZIP
// → Writes data.txt.compressed (OVERWRITES ZIP version!)
// State: data.txt (original), data.txt.compressed (GZIP, ZIP lost)
```

**Problem:**

**Fix #1: Strategy-Specific Extensions**

```cpp
class CompressionStrategy {
public:
    virtual string getExtension() const = 0;
    virtual vector<byte> compress(const vector<byte>&) = 0;
};

class ZipStrategy : public CompressionStrategy {
    string getExtension() const override { return ".zip"; }
};

class GzipStrategy : public CompressionStrategy {
    string getExtension() const override { return ".gz"; }
    // ... (additional code omitted for brevity)
```

- cpp class CompressionStrategy { public: virtual string getExtension() const = 0; virtual vector<byte> compress(const vector<byte>&) = 0; };
- class ZipStrategy : public CompressionStrategy { string getExtension() const override { return ".zip"; } };
- class GzipStrategy : public CompressionStrategy { string getExtension() const override { return ".gz"; } };

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
template<typename Strategy>
class Processor {
    Strategy strategy;
public:
    void process(Data& data) {
        strategy.execute(data);
    }
};

// Strategies:
struct FastStrategy {
    void execute(Data& d) { /* fast algorithm */ }
};

struct AccurateStrategy {
    void execute(Data& d) { /* accurate but slow */ }
};

// Usage:
Processor<FastStrategy> fastProcessor;
Processor<AccurateStrategy> accurateProcessor;

// What's the difference from runtime polymorphism?
```

**Answer:**
- Compile-time (template-based) strategy has zero runtime overhead but cannot switch strategies at runtime, unlike runtime polymorphism.
**Explanation:**
**Compile-Time Strategy (Templates):**
```cpp
template<typename Strategy>
class Processor {
    Strategy strategy;  // No virtual function, no pointer
public:
    void process(Data& data) {
        strategy.execute(data);  // Direct call, can be inlined
    }
};
// Compiler generates separate classes:
// Processor<FastStrategy> → separate type
// Processor<AccurateStrategy> → separate type
```
- // Compiler generates separate classes: // Processor<FastStrategy> → separate type // Processor<AccurateStrategy> → separate type ```
**Benefits:**
- **Zero overhead:** Direct function call, fully inlinable
- **Type safety:** Compile-time checks
- **Performance:** Same as hand-written specialized code
**Drawbacks:**
- **Cannot change at runtime:** Type fixed at compile time
```cpp
Processor<FastStrategy> proc;
  // ❌ Cannot switch to AccurateStrategy later
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
class Context {
    Strategy* strategy;
public:
    void executeStrategy(Data& data) {
        if (data.isLarge()) {
            strategy = &parallelStrategy;
        } else {
            strategy = &sequentialStrategy;
        }
        strategy->process(data);
    }

private:
    ParallelStrategy parallelStrategy;
    SequentialStrategy sequentialStrategy;
};

// Is it good practice to change strategy inside execution?
```

**Answer:**
- Generally not recommended - strategy selection should happen before execution, not during
- Mixing selection logic with execution violates separation of concerns.
**Explanation:**
**Why This is Problematic:**
**Problem #1: Mixed Responsibilities**
Context now has two jobs:
1. Choose appropriate strategy (selection logic)
2. Execute strategy (delegation)
```cpp
// Context knows too much about when to use each strategy
void executeStrategy(Data& data) {
    if (data.isLarge()) {  // ❌ Business logic in Context
        strategy = &parallelStrategy;
    } else if (data.isCritical()) {
        strategy = &accurateStrategy;
    } else {
        strategy = &fastStrategy;
    }
    strategy->process(data);
}
```
**When Internal Selection is Acceptable:**
Sometimes internal strategy switching is justified:
```cpp
class CacheStrategy : public Strategy {
    LRUCache cache;
public:

**Note:** Full detailed explanation with additional examples available in source materials.

---
