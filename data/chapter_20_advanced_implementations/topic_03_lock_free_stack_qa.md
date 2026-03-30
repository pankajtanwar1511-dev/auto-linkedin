### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: What is the ABA problem? Provide a concrete example.
Implement this exercise.

**Answer:**

**ABA problem:** Value changes from A → B → A, making CAS succeed when it shouldn't.

**Concrete example:**

```cpp
// Stack: A → B → C
// Thread 1:
Node* old_head = head.load();  // Reads A

// Thread 1 pauses...

// Thread 2:
pop();  // Removes A, stack: B → C
pop();  // Removes B, stack: C
delete A;  // Free A's memory
Node* new_A = new Node();  // Reallocates at same address as A
push(new_A);  // Stack: A → C

// Thread 1 resumes:
head.compare_exchange(old_head, ...);  // Succeeds! (thinks A unchanged)
// But A->next now points to C, not B!
```

**Solution:** Tagged pointer with version counter:

```cpp
struct TaggedPointer {
    Node* ptr;
    uint64_t tag;  // Incremented on each change
};
```

Even if pointer is reused, tag will differ.

---
#### Q2: Explain `compare_exchange_weak()` vs `compare_exchange_strong()`.
Implement this exercise.

**Answer:**

**`compare_exchange_weak()`:**
- May **spuriously fail** (return false even if values match)
- Faster on some platforms (no loop inside)
- Use in loops:
  ```cpp
  do {
      // ...
  } while (!atomic.compare_exchange_weak(old, new));
  ```

**`compare_exchange_strong()`:**
- **Never** spuriously fails
- Only fails if values actually differ
- Slower (may loop internally)
- Use for single attempts:
  ```cpp
  if (atomic.compare_exchange_strong(old, new)) {
      // Success
  }
  ```

**When to use which:**
- **Weak:** In retry loops (performance)
- **Strong:** Single attempt, complex failure handling

---
#### Q3: What is the difference between lock-free and wait-free?
Implement this exercise.

**Answer:**

**Lock-Free:**
- **System-wide progress guarantee**
- At least one thread makes progress
- Individual threads may starve (retry forever)
- Example: CAS loop (one thread succeeds, others retry)

**Wait-Free:**
- **Per-thread progress guarantee**
- Every thread completes in bounded steps
- No starvation possible
- Stronger (and harder to implement)
- Example: `fetch_add()` (always succeeds in one step)

**Hierarchy:**
```
Wait-Free ⊂ Lock-Free ⊂ Obstruction-Free ⊂ Blocking
(strongest)                              (weakest)
```

---
#### Q4: How do memory orderings affect lock-free algorithms?
Implement this exercise.

**Answer:**

**Memory ordering controls visibility across threads:**

**`memory_order_relaxed`:**
- No synchronization
- Only atomicity guaranteed
- Use: Counters (where order doesn't matter)

**`memory_order_acquire` (load):**
- All writes before a `release` become visible
- Use: Reading shared data

**`memory_order_release` (store):**
- Makes all previous writes visible to `acquire`
- Use: Publishing shared data

**Example:**
```cpp
// Thread 1 (producer):
data.store(42, std::memory_order_relaxed);
ready.store(true, std::memory_order_release);  // Publish

// Thread 2 (consumer):
if (ready.load(std::memory_order_acquire)) {  // Synchronize
    assert(data.load(std::memory_order_relaxed) == 42);  // Guaranteed
}
```

**For lock-free stack:**
- Push: `release` on CAS (publish new node)
- Pop: `acquire` on load (see latest node)

---
#### Q5: Why is memory reclamation difficult in lock-free structures?
Implement this exercise.

**Answer:**

**Problem:** Can't immediately delete popped nodes:

```cpp
std::optional<T> try_pop() {
    Node* old_head = head.load();
    // ...
    delete old_head;  // ← DANGER!
}
```

**Why unsafe:**
1. Thread A loads `head` (node X)
2. Thread B pops X, tries to delete it
3. Thread A still reading X's `next` pointer → **use-after-free**

**Solutions:**

**1) Hazard Pointers:**
- Mark pointers as "in use"
- Defer deletion until no hazard pointers

**2) Reference Counting:**
- Track how many threads access node
- Delete when count reaches zero

**3) Epoch-Based Reclamation:**
- Group deletions by epoch
- Delete epoch when all threads exit it

**4) Garbage Collection:**
- Language-level GC (not available in C++)

**Trade-offs:**
- Hazard pointers: Low overhead, complex
- Ref counting: Simpler, atomic overhead
- Epochs: Good throughput, delayed reclamation

---
#### Q6: Can you implement a lock-free queue (not just stack)?
Implement this exercise.

**Answer:**

- Yes, but more complex (two pointers: head and tail).

**Simplified approach (Michael-Scott queue):**

```cpp
template<typename T>
class LockFreeQueue {
private:
    struct Node {
        std::shared_ptr<T> data;
        std::atomic<Node*> next;

        Node() : next(nullptr) {}
    };

    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
    // ... (additional code omitted for brevity)
```

- cpp template<typename T> class LockFreeQueue { private: struct Node { std::shared_ptr<T> data; std::atomic<Node*> next;
- Node() : next(nullptr) {} };
- std::atomic<Node*> head_; std::atomic<Node*> tail_;

**Key differences from stack:**

- Two CAS locations (head and tail)
- Dummy node to avoid special cases
- "Helping" mechanism (threads help complete others' operations)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What are the performance characteristics of lock-free vs mutex-based stacks?
Implement this exercise.

**Answer:**

**Lock-Free:**
- ✅ **Better under high contention** (no blocking)
- ✅ **Predictable latency** (no waiting)
- ✅ **Scalability** (more threads = more throughput)
- ❌ **Slower for single thread** (atomic overhead)
- ❌ **Cache ping-pong** (CAS invalidates other cores' caches)

**Mutex-Based:**
- ✅ **Simpler implementation**
- ✅ **Better single-threaded performance**
- ❌ **Blocking** (threads sleep when contention)
- ❌ **Scalability plateau** (lock becomes bottleneck)

**Benchmark (8 threads, 1M operations):**
```
Lock-Free: 340 ms
Mutex:     870 ms
```

**When to use:**
- **Lock-free:** High-performance servers, real-time systems, high contention
- **Mutex:** Low contention, simplicity preferred

---
#### Q8: How would you test a lock-free stack for correctness?
Implement this exercise.

**Answer:**

- Model checking (limited state space)
- Proof assistants (Coq, Isabelle)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: Explain the role of `std::atomic<T>` - what can T be?
Implement this exercise.

**Answer:**

**Requirements for `std::atomic<T>`:**

**1) Trivially Copyable:**
- No user-defined copy constructor
- No virtual functions

**2) Size Constraints:**
- Must fit in CPU word (typically ≤ 16 bytes)
- Larger types may use locks internally

**Valid:**
```cpp
std::atomic<int> a;          // ✓ Built-in type
std::atomic<int*> ptr;       // ✓ Pointer
std::atomic<bool> flag;      // ✓ Boolean

struct Point { int x, y; };
std::atomic<Point> p;        // ✓ Trivial struct
```

**Invalid:**
```cpp
std::atomic<std::string> s;  // ✗ Not trivially copyable
std::atomic<std::vector<int>> v;  // ✗ Not trivial
```

**Check if lock-free:**
```cpp
std::atomic<Point> p;
if (p.is_lock_free()) {
    std::cout << "True lock-free\n";
} else {
    std::cout << "Uses locks internally\n";
}
```

---
#### Q10: What is a "happens-before" relationship?
**Answer:**

**Happens-before:** Operation A's effects are visible to operation B.

**Established by:**

**1) Same thread (sequenced-before):**
```cpp
x = 1;  // Happens-before
y = 2;  // This sees x = 1
```

**2) Synchronization (release-acquire):**
```cpp
// Thread 1:
data = 42;
flag.store(true, std::memory_order_release);  // Release

// Thread 2:
if (flag.load(std::memory_order_acquire)) {  // Acquire
    assert(data == 42);  // Happens-after release
}
```

**3) Thread creation:**
```cpp
x = 1;
std::thread t([&]() {
    assert(x == 1);  // Sees parent's writes
});
```

**4) Thread join:**
```cpp
std::thread t([&]() { x = 1; });
t.join();
assert(x == 1);  // Sees thread's writes
```

**Transitivity:**
If A happens-before B, and B happens-before C, then A happens-before C.

**Used to reason about memory visibility in concurrent programs.**

---
