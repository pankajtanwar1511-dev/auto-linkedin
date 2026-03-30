## TOPIC: Atomics and Memory Ordering - Lock-Free Programming Fundamentals

### PRACTICE_TASKS: Output Prediction and Code Analysis

#### Q1
```cpp
std::atomic<int> x(0);

void thread1() {
    x.store(1, std::memory_order_relaxed);
}

void thread2() {
    int val = x.load(std::memory_order_relaxed);
    if (val == 1) {
        std::cout << "Saw 1\n";
    }
}

// What is guaranteed about the output?
```

**Answer:**
```
Thread2 may or may not print "Saw 1"
```

**Explanation:**
- **memory_order_relaxed:** Weakest memory ordering
- **No inter-thread synchronization guarantees**
- **What relaxed provides:**
  - Atomicity of individual operation
  - Modification order consistency (all threads see same order of changes to x)
  - NO ordering with other operations
- **Possible scenarios:**
  1. Thread1 stores before thread2 loads: Sees 1 (prints)
  2. Thread2 loads before thread1 stores: Sees 0 (no print)
  3. Compiler/CPU may reorder: Load might never see store
- **No "happens-before" relationship**
- **Visibility not guaranteed:** Thread2 might cache old value indefinitely
- **Modification order:** If multiple stores, all threads see same final sequence
- **But timing:** When each thread observes changes is unspecified
- **Not a bug - by design:** Relaxed is for counters where order doesn't matter
- **Use case:** Performance-critical code where only atomicity needed, not ordering
- **Key Concept:** memory_order_relaxed provides atomicity but no inter-thread visibility or ordering guarantees

---

#### Q2
```cpp
std::atomic<bool> ready(false);
int data = 0;

void writer() {
    data = 42;
    ready.store(true, std::memory_order_relaxed);
}

void reader() {
    while (!ready.load(std::memory_order_relaxed)) {}
    assert(data == 42);
}

// Will the assertion always pass? Why or why not?
```

**Answer:**
```
No, assertion may fail
```

**Explanation:**
- **Classic data race pattern** with relaxed atomics
- **Problem: No synchronization between threads**
- **What can go wrong:**
  1. Writer sets data=42
  2. Writer sets ready=true (relaxed)
  3. Reader sees ready=true
  4. **But reader might still see data=0!**
- **Reordering issues:**
  - **Compiler reordering:** Compiler may reorder `data=42` after `ready.store(true)`
  - **CPU reordering:** CPU may execute/commit in different order
  - **Cache coherency delays:** data=42 write may not reach reader's cache
- **Relaxed stores don't synchronize non-atomic data**
- **Reader spin-waits on ready** but:
  - No guarantee data write visible when ready becomes true
  - ready=true only means ready itself changed
  - Doesn't establish happens-before relationship
- **Correct version: Use release-acquire**
  ```cpp
  void writer() {
      data = 42;
      ready.store(true, std::memory_order_release);  // Release
  }

  void reader() {
      while (!ready.load(std::memory_order_acquire)) {}  // Acquire
      assert(data == 42);  // Now guaranteed!
  }
  ```
- **Release-acquire creates synchronization:**
  - Release: All prior writes visible to acquirer
  - Acquire: All writes before release are visible
  - **Happens-before relationship established**
- **Rule:** Relaxed atomics don't synchronize non-atomic data
- **Key Concept:** memory_order_relaxed insufficient for synchronizing non-atomic data; need release-acquire

---

#### Q3
```cpp
std::atomic<int> counter(10);

void increment() {
    int expected = counter.load();
    counter.compare_exchange_strong(expected, expected + 1);
}

// If called by 100 threads once each, what is counter's final value?
```

**Answer:**



**Explanation:**

- **compare_exchange_strong without loop** - classic mistake
- **CAS (Compare-And-Swap) operation:**
- Checks if counter == expected
- If yes: Sets counter = expected+1, returns true
- If no: Updates expected to current value, returns false

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
std::atomic<int> val(0);

void thread1() {
    val.store(1, std::memory_order_release);
}

void thread2() {
    while (val.load(std::memory_order_acquire) == 0) {}
    std::cout << "Done\n";
}

// Is this correct for synchronization? Explain.
```

**Answer:**



**Explanation:**

- **Release-acquire synchronization** - the correct pattern
- **memory_order_release (thread1):**
- All memory writes before the release store are visible
- Creates a "release fence"
- Prevents reordering of prior writes past this point

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
std::atomic_flag flag = ATOMIC_FLAG_INIT;

void thread1() {
    bool was_set = flag.test_and_set();
    std::cout << was_set << "\n";
}

void thread2() {
    flag.clear();
}

// What are the possible outputs?
```

**Answer:**



**Explanation:**

- **atomic_flag:** Simplest atomic type
- **ATOMIC_FLAG_INIT:** Initializes flag to clear (false) state
- **test_and_set():**
- Atomically sets flag to true
- Returns previous value (before setting)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
std::atomic<int> x(0), y(0);

void thread1() {
    x.store(1, std::memory_order_seq_cst);
    y.store(1, std::memory_order_seq_cst);
}

void thread2() {
    while (y.load(std::memory_order_seq_cst) == 0) {}
    assert(x.load(std::memory_order_seq_cst) == 1);
}

// Will the assertion ever fail? Why or why not?
```

**Answer:**
```
Never fails
```

**Explanation:**
- **Sequential consistency (seq_cst):** Strongest memory ordering
- **Guarantees:**
  1. **Total global order:** All threads see all seq_cst operations in same order
  2. **Program order:** Operations within thread execute in code order
  3. **No reordering:** Compiler/CPU cannot reorder seq_cst operations
- **Thread1 execution order (guaranteed):**
  1. x.store(1) completes
  2. Then y.store(1) completes
  3. **Order preserved by seq_cst**
- **Thread2 observation:**
  1. Spins until y==1 (y.load returns 1)
  2. When y==1 is observed:
     - **By seq_cst guarantee:** x.store(1) already completed
     - **By program order:** x stored before y in thread1
     - **By total order:** All threads see same order
  3. assert(x==1) **MUST pass**
- **Why assertion can't fail:**
  - **Causality:** y=1 happens-after x=1 in thread1
  - **Seq_cst synchronization:** Thread2 sees consistent global view
  - **No way for y==1 to be visible before x==1**
- **With relaxed, assertion COULD fail:**

```cpp
// Relaxed version (WRONG)
x.store(1, std::memory_order_relaxed);
y.store(1, std::memory_order_relaxed);
// Thread2 might see y==1 but x==0 due to reordering
```
- **Seq_cst performance cost:**
  - Expensive: Full memory barriers
  - Prevents CPU/compiler optimizations
  - But provides strongest guarantees
- **Use when:**
  - Need total global order
  - Correctness more important than performance
- **Key Concept:** Sequential consistency provides total global order; if thread sees later operation, it must see all prior operations in program order

---

#### Q7
```cpp
std::atomic<int*> ptr(nullptr);
int data = 42;

void thread1() {
    ptr.store(&data);
}

void thread2() {
    int* p = ptr.load();
    if (p != nullptr) {
        std::cout << *p << "\n";
    }
}

// Is this code safe? What could go wrong?
```

**Answer:**



**Explanation:**

- **Multiple safety issues in this code**
- data is local variable (if in function scope)
- Storing &data in atomic ptr
- **If data goes out of scope:** ptr points to destroyed object
- **Dangling pointer** when thread2 dereferences

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
std::atomic<int> counter(0);

void worker() {
    for (int i = 0; i < 1000; ++i) {
        int expected = counter.load();
        while (!counter.compare_exchange_weak(expected, expected + 1));
    }
}

// Why is the loop necessary?
```

**Answer:**

```cpp
CAS may fail spuriously or due to contention
```

- CAS may fail spuriously or due to contention ```

**Explanation:**

- **compare_exchange_weak:** Weaker but faster than strong
- **Two reasons for CAS failure:**
**Reason 1: Contention (genuine failure)**
1. Thread A loads counter=0 into expected

```cpp
int expected = counter.load();  // Load once
  while (!counter.compare_exchange_weak(expected, expected + 1)) {
      // Retry until success
      // expected automatically updated on each failure
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
volatile int counter = 0;

void increment() {
    ++counter;  // 10 threads call this
}

// What is the problem with this code?
```

**Answer:**

```cpp
Race condition, not atomic
```

- Race condition, not atomic ```

**Explanation:**

- **volatile != atomic** - critical misconception
- **What volatile actually does:**
- Prevents compiler optimizations (caching in register)
- Forces read from memory on each access

```cpp
// ++counter decomposes to:
  temp = counter;  // Read
  temp = temp + 1;  // Modify
  counter = temp;  // Write
```

- cpp // ++counter decomposes to: temp = counter; // Read temp = temp + 1; // Modify counter = temp; // Write ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
std::atomic<bool> x(false), y(false);
int z = 0;

void thread1() {
    x.store(true, std::memory_order_relaxed);
}

void thread2() {
    y.store(true, std::memory_order_relaxed);
}

void thread3() {
    while (!x.load(std::memory_order_relaxed)) {}
    if (y.load(std::memory_order_relaxed)) ++z;
}

void thread4() {
    while (!y.load(std::memory_order_relaxed)) {}
    if (x.load(std::memory_order_relaxed)) ++z;
}

// Can z be 0, 1, or 2 at the end? Explain.
```

**Answer:**

```cpp
z can be 0, 1, or 2
```

- z can be 0, 1, or 2 ```

**Explanation:**

- **Relaxed ordering allows complete reordering** between threads
- **No happens-before relationships established**
**Scenario 1: z=2 (both threads increment)**

```cpp
Timeline:
  - Thread1 stores x=true
  - Thread2 stores y=true
  - Thread3: sees x=true, checks y → y=true → ++z (z=1)
  - Thread4: sees y=true, checks x → x=true → ++z (z=2)
  Result: z=2
```

- Timeline: - Thread1 stores x=true - Thread2 stores y=true - Thread3: sees x=true, checks y → y=true → ++z (z=1) - Thread4: sees y=true, checks x → x=true → ++z (z=2) Result: z=2 ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
std::atomic<int> val(100);
int old = val.exchange(200);

std::cout << "Old: " << old << ", New: " << val.load() << "\n";

// What is the output?
```

**Answer:**

```cpp
Old: 100, New: 200
```

- Old: 100, New: 200 ```

**Explanation:**

- **exchange():** Atomic swap operation
- **Operation:**

```cpp
int exchange(int new_value) {
      // Atomically:
      int old_value = current_value;
      current_value = new_value;
      return old_value;
  }
```

- cpp int exchange(int new_value) { // Atomically: int old_value = current_value; current_value = new_value; return old_value; } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
std::atomic<int> x(0);

void thread1() {
    x.fetch_add(5, std::memory_order_relaxed);
}

void thread2() {
    x.fetch_add(10, std::memory_order_relaxed);
}

// After both threads complete, what is x's value? Is it deterministic?
```

**Answer:**

```cpp
x = 15, deterministic
```

- x = 15, deterministic ```

**Explanation:**

- **fetch_add:** Atomic read-modify-write operation
- **Atomicity guarantees:**
- Each fetch_add is atomic
- x+=5 happens as single indivisible operation

```cpp
x=0 → fetch_add(5) → x=5 → fetch_add(10) → x=15
```

- x=0 → fetch_add(5) → x=5 → fetch_add(10) → x=15 ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
struct Node {
    int value;
    Node* next;
};

std::atomic<Node*> head(nullptr);

void push(int val) {
    Node* new_node = new Node{val, nullptr};
    new_node->next = head.load();
    head.store(new_node);  // ❌ What's wrong with this?
}
```

**Answer:**

```cpp
Race condition: no CAS
```

- Race condition: no CAS ```

**Explanation:**

- **Classic lock-free stack bug** - missing CAS
- **What goes wrong with multiple threads:**

**Race scenario:**

```cpp
Initial: head → A → nullptr
  Thread1 wants to push B
  Thread2 wants to push C

  Timeline:
  T1: Thread1: new_node B allocated
  T2: Thread1: B->next = head.load() → B->next = A
  T3: Thread2: new_node C allocated
  T4: Thread2: C->next = head.load() → C->next = A
  T5: Thread1: head.store(B) → head now points to B
  T6: Thread2: head.store(C) → head now points to C

  Result: head → C → A → nullptr
  LOST: Node B! Memory leak.
```

- Initial: head → A → nullptr Thread1 wants to push B Thread2 wants to push C
- Result: head → C → A → nullptr LOST: Node B

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
std::atomic<int> counter(0);
bool ready = false;

void thread1() {
    counter.fetch_add(1, std::memory_order_release);
    ready = true;
}

void thread2() {
    while (!ready) {}
    int val = counter.load(std::memory_order_acquire);
}

// What can go wrong here?
```

**Answer:**

```cpp
Race on ready
```

**Explanation:**

- **Mixed atomic/non-atomic synchronization** - dangerous pattern
- **Problems:**
**Problem 1: Data race on ready**
- **ready is non-atomic bool**

```cpp
// Compiler might transform thread2 to:
  bool cached_ready = ready;
  while (!cached_ready) {}  // Infinite loop!
```

- cpp // Compiler might transform thread2 to: bool cached_ready = ready; while (!cached_ready) {} // Infinite loop

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
std::atomic<int> val(0);

void thread1() {
    val.store(1);  // No explicit ordering
}

void thread2() {
    int x = val.load();  // No explicit ordering
}

// What memory ordering is used by default?
```

**Answer:**

```cpp
memory_order_seq_cst
```

- memory_order_seq_cst ```

**Explanation:**

- **Default memory ordering: Sequential consistency**
- **When not specified:**

```cpp
val.store(1);                          // Uses seq_cst
  val.store(1, std::memory_order_seq_cst);  // Explicit (same)
```

- cpp val.store(1); // Uses seq_cst val.store(1, std::memory_order_seq_cst); // Explicit (same) ```

**Relaxed (fastest, weakest):**

```cpp
counter.fetch_add(1, std::memory_order_relaxed);
  // For counters where order doesn't matter
```

- cpp counter.fetch_add(1, std::memory_order_relaxed); // For counters where order doesn't matter ```

**Release-acquire (common pattern):**

```cpp
data = 42;
  ready.store(true, std::memory_order_release);  // Publish

  while (!ready.load(std::memory_order_acquire)) {}  // Subscribe
  assert(data == 42);  // Guaranteed
```

- cpp data = 42; ready.store(true, std::memory_order_release); // Publish
- while (!ready.load(std::memory_order_acquire)) {} // Subscribe assert(data == 42); // Guaranteed ```

**Seq_cst (when total order needed):**

```cpp
x.store(1, std::memory_order_seq_cst);
  y.store(1, std::memory_order_seq_cst);
  // All threads see same order of x and y updates
```

- cpp x.store(1, std::memory_order_seq_cst); y.store(1, std::memory_order_seq_cst); // All threads see same order of x and y updates ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
std::atomic<std::string> str("hello");  // Compile error or not?

// Can you make an atomic of a large type? What happens?
```

**Answer:**

```cpp
Compiles but likely not lock-free
```

- Compiles but likely not lock-free ```

**Explanation:**

- **std::atomic works with any trivially copyable type**
- **Compilation:**
- std::string is NOT trivially copyable (has destructor, dynamic allocation)
- **Won't compile:** `std::atomic<std::string>` is ill-formed

```cpp
struct LargeStruct {
      int data[100];
  };

  std::atomic<LargeStruct> large;  // Compiles!
```

- cpp struct LargeStruct { int data[100]; };
- std::atomic<LargeStruct> large; // Compiles

**Small types (usually lock-free):**

```cpp
std::atomic<int> x;          // Lock-free on all platforms
  std::atomic<void*> p;        // Lock-free on all platforms
  std::atomic<uint64_t> v;     // Lock-free on 64-bit platforms
```

- cpp std::atomic<int> x; // Lock-free on all platforms std::atomic<void*> p; // Lock-free on all platforms std::atomic<uint64_t> v; // Lock-free on 64-bit platforms ```

**Large types (usually lock-based):**

```cpp
struct BigStruct { int arr[100]; };
  std::atomic<BigStruct> big;  // Likely uses internal mutex
```

- cpp struct BigStruct { int arr[100]; }; std::atomic<BigStruct> big; // Likely uses internal mutex ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
std::atomic<int> x(0);

void thread1() {
    x.store(1, std::memory_order_release);
}

void thread2() {
    x.store(2, std::memory_order_release);
}

void thread3() {
    while (x.load(std::memory_order_acquire) == 0) {}
    std::cout << x.load() << "\n";
}

// What values can thread3 print?
```

**Answer:**

```cpp
1 or 2
```

**Explanation:**

- **Concurrent stores to same atomic** - both valid
- **Race between thread1 and thread2:**
- Both store to x (1 and 2)
- **Both stores are atomic**

```cpp
T0: x = 0
  T1: Thread1 stores x=1 (release)
  T2: Thread2 stores x=2 (release)
  T3: Thread3 sees x!=0, loads → x=2
  Output: "2"
```

- T0: x = 0 T1: Thread1 stores x=1 (release) T2: Thread2 stores x=2 (release) T3: Thread3 sees x!=0, loads → x=2 Output: "2" ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
std::atomic<int> flag(0);
int data[10];

void writer() {
    for (int i = 0; i < 10; ++i) data[i] = i;
    std::atomic_thread_fence(std::memory_order_release);
    flag.store(1, std::memory_order_relaxed);
}

void reader() {
    while (flag.load(std::memory_order_relaxed) == 0) {}
    std::atomic_thread_fence(std::memory_order_acquire);
    for (int i = 0; i < 10; ++i) std::cout << data[i];
}

// Is this synchronization correct?
```

**Answer:**

```cpp
Yes, correct
```

**Explanation:**

- **Memory fences (barriers):** Alternative to atomic orderings
- **This pattern separates ordering from atomic variable**
- **How fences work:**

**Writer side:**

- All prior writes must complete before this fence
- Creates "release" point
- Flag is just signal, no ordering on flag itself

**Reader side:**

1. Relaxed load: `while (flag.load(relaxed) == 0)`
- Just waiting for signal
2. **Acquire fence:** `atomic_thread_fence(memory_order_acquire)`
- All subsequent reads must happen after this fence

```cpp
// Without fences (using atomic orderings directly)
  void writer() {
      for (int i = 0; i < 10; ++i) data[i] = i;
      flag.store(1, std::memory_order_release);  // Release
  }

  void reader() {
      while (flag.load(std::memory_order_acquire) == 0) {}  // Acquire
      for (int i = 0; i < 10; ++i) std::cout << data[i];
  }
```

- cpp // Without fences (using atomic orderings directly) void writer() { for (int i = 0; i < 10; ++i) data[i] = i; flag.store(1, std::memory_order_release); // Release }
- void reader() { while (flag.load(std::memory_order_acquire) == 0) {} // Acquire for (int i = 0; i < 10; ++i) std::cout << data[i]; } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
std::atomic<int> x(10);
int a = ++x;
int b = x++;

std::cout << "a: " << a << ", b: " << b << ", x: " << x.load() << "\n";

// What is the output?
```

**Answer:**

```cpp
a: 11, b: 11, x: 12
```

- a: 11, b: 11, x: 12 ```

**Explanation:**

- **Atomic pre/post-increment operators**
- **Step-by-step execution:**
- Pre-increment on atomic
- **Operation:**
- `a = 11`
- `x = 11` after this

**Output:**

```cpp
a: 11, b: 11, x: 12
```

- a: 11, b: 11, x: 12 ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
struct alignas(64) PaddedAtomic {
    std::atomic<int> val;
};

PaddedAtomic counters[4];

// Why use alignas(64)? What problem does this solve?
```

**Answer:**

```cpp
Prevents false sharing
```

- Prevents false sharing ```

**Explanation:**

- **False sharing:** Performance killer in concurrent code
- **Problem without alignment:**

**Cache line basics:**

- CPU caches data in **cache lines** (typically 64 bytes)
- When CPU accesses memory, entire cache line loaded
- Multiple variables can share same cache line

**False sharing scenario:**

```cpp
std::atomic<int> counters[4];  // No padding
  // Memory layout (assuming 4-byte ints):
  // [counter[0]][counter[1]][counter[2]][counter[3]][...] (16 bytes total)
  // All fit in single 64-byte cache line!
```

**What goes wrong:**

```cpp
Core 0: Increments counter[0]
    → Invalidates entire cache line in other cores
  Core 1: Wants to increment counter[1]
    → Must reload cache line (expensive!)
    → Even though counter[0] and counter[1] are independent!
  Core 2: Increments counter[2]
    → Invalidates cache line again
  Core 3: Increments counter[3]
    → Invalidates cache line again

  Result: Cache line bouncing between cores
          ("Ping-pong effect")
          Massive performance degradation
```

- Core 2: Increments counter[2] → Invalidates cache line again Core 3: Increments counter[3] → Invalidates cache line again
- Result: Cache line bouncing between cores ("Ping-pong effect") Massive performance degradation ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
