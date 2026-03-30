### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1
Identify the bug in this object pool:
```cpp
template <typename T, size_t N>
class ObjectPool {
    T* storage;
    std::vector<T*> freeList;

public:
    ObjectPool() : storage(new T[N]) {
        for (size_t i = 0; i < N; ++i) {
            freeList.push_back(storage[i]);  // Bug!
        }
    }
};
```

#### Q2
What's wrong with this thread-safe pool?
```cpp
class ThreadSafePool {
    std::mutex mtx;
    std::vector<T*> freeList;

public:
    T* allocate() {
        std::lock_guard<std::mutex> lock(mtx);
        if (freeList.empty()) throw std::bad_alloc();
        T* obj = freeList.back();
        freeList.pop_back();
        return obj;
    }

    void deallocate(T* ptr) {
        freeList.push_back(ptr);  // Bug!
    }
};
```

#### Q3
Fix the double-free vulnerability:
```cpp
void deallocate(T* ptr) {
    freeList.push_back(ptr);
}

// User code
T* obj = pool.allocate();
pool.deallocate(obj);
pool.deallocate(obj);  // Corrupts pool!
```

#### Q4
Complete the index-based allocation:
```cpp
template <typename T, size_t N>
class IndexPool {
    T* storage;
    size_t freeList[N];
    size_t freeCount;

public:
    T* allocate() {
        // Your implementation
    }
};
```

#### Q5
Why does this pool leak memory?
```cpp
struct Resource {
    std::string data;
    std::vector<int> values;
};

class Pool {
    Resource* storage;

    void deallocate(Resource* obj) {
        freeList.push_back(obj);  // Leak!
    }
};
```

#### Q6
Implement chunk boundary checking:
```cpp
class ExpandablePool {
    std::vector<T*> chunks;
    static constexpr size_t CHUNK_SIZE = 100;

    void deallocate(T* ptr) {
        // Find owning chunk - implement this
    }
};
```

#### Q7
Add alignment validation:
```cpp
struct alignas(32) SIMDData {
    float values[8];
};

class Pool {
    SIMDData* allocate() {
        // Ensure returned pointer is 32-byte aligned
    }
};
```

#### Q8
What's the issue with this pool destructor?
```cpp
class Pool {
    T* storage;

public:
    ~Pool() {
        delete storage;  // Bug!
    }
};
```

#### Q9
Fix the race condition:
```cpp
class Pool {
    std::atomic<size_t> head{0};
    T* buffer[100];

    T* allocate() {
        size_t h = head.load();
        T* obj = buffer[h];
        head.store(h + 1);  // Race!
        return obj;
    }
};
```

#### Q10
Implement proper placement new lifecycle:
```cpp
class Pool {
    alignas(Resource) char storage[sizeof(Resource) * 100];

    Resource* allocate() {
        void* mem = getFreeSlot();
        // Construct Resource using placement new
    }

    void deallocate(Resource* obj) {
        // Properly destruct before returning to pool
    }
};
```

#### Q11
Calculate the correct global index:
```cpp
class ChunkedPool {
    std::vector<T*> chunks;
    static constexpr size_t CHUNK_SIZE = 100;

    size_t getGlobalIndex(T* ptr) {
        // Calculate global index from pointer
    }
};
```

#### Q12
Why doesn't this pool reuse memory?
```cpp
class Pool {
    T* storage;
    size_t nextIndex = 0;

    T* allocate() {
        return &storage[nextIndex++];  // Bug!
    }

    void deallocate(T* ptr) {
        // Nothing!
    }
};
```

#### Q13
Fix the false sharing issue:
```cpp
struct Counter {
    int value;  // 4 bytes
};

// Multiple threads allocate and modify Counters
// Performance degrades significantly - why?
```

#### Q14
Implement cache line alignment:
```cpp
template <typename T>
struct AlignedWrapper {
    // Ensure T is on its own cache line
};
```

#### Q15
Add statistics tracking:
```cpp
class MonitoredPool {
    // Track total allocations, deallocations, peak usage
    // Implement getStats() method
};
```

#### Q16
Fix the alignment bug:
```cpp
class Pool {
    char* storage = new char[sizeof(T) * 100];

    T* allocate() {
        return reinterpret_cast<T*>(storage);  // May be misaligned!
    }
};
```

#### Q17
Implement exhaustion handling:
```cpp
class Pool {
    T* allocate() {
        if (freeList.empty()) {
            // Implement 3 different strategies:
            // 1. Throw exception
            // 2. Return nullptr
            // 3. Allocate new chunk
        }
    }
};
```

#### Q18
Detect out-of-pool pointers:
```cpp
void deallocate(T* ptr) {
    // Validate ptr is from this pool before deallocating
}
```

#### Q19
Implement RAII pool handle:
```cpp
template <typename T>
class PoolHandle {
    // Automatically returns object to pool on destruction
};
```

#### Q20
Fix the memory leak on pool destruction:
```cpp
class Pool {
    T* storage;
    std::vector<T*> freeList;
    size_t capacity;

    ~Pool() {
        delete[] storage;
        // What if freeList.size() < capacity?
        // Some objects still allocated - leak!
    }
};
```

---
#### Q1
Identify the bug in this object pool:
```cpp
template <typename T, size_t N>
class ObjectPool {
    T* storage;
    std::vector<T*> freeList;

public:
    ObjectPool() : storage(new T[N]) {
        for (size_t i = 0; i < N; ++i) {
            freeList.push_back(storage[i]);  // Bug!
        }
    }
};
```

**Answer:**

```cpp
// Bug: storage[i] is a T&, but push_back expects T*
// Should be: freeList.push_back(&storage[i]);

template <typename T, size_t N>
class ObjectPool {
    T* storage;
    std::vector<T*> freeList;
    // ... (abbreviated)
```

- cpp // Bug: storage[i] is a T&, but push_back expects T* // Should be: freeList.push_back(&storage[i]);
- template <typename T, size_t N> class ObjectPool { T* storage; std::vector<T*> freeList;

**Explanation:**

- **The bug - missing address-of operator:** `storage[i]` returns `T&` (reference to T), but `freeList` holds `T*` (pointers); type mismatch causes compilation error; need `&storage[i]` to get pointer
- **Why this compiles in some cases:** If T is small (like int), compiler might try implicit conversion; creates dangling references; would compile but have undefined behavior
- **Correct pattern:** `storage` is `T*` (pointer to array), `storage[i]` is `T&` (reference to i-th element), `&storage[i]` is `T*` (pointer to i-th element)
- **Pointer arithmetic alternative:** `freeList.push_back(storage + i);` also works; `storage + i` = pointer to i-th element; equivalent to `&storage[i]`

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
What's wrong with this thread-safe pool?
```cpp
class ThreadSafePool {
    std::mutex mtx;
    std::vector<T*> freeList;

public:
    T* allocate() {
        std::lock_guard<std::mutex> lock(mtx);
        if (freeList.empty()) throw std::bad_alloc();
        T* obj = freeList.back();
        freeList.pop_back();
        return obj;
    }

    void deallocate(T* ptr) {
        freeList.push_back(ptr);  // Bug!
    }
};
```

**Answer:**

- class ThreadSafePool { std::mutex mtx; std::vector<T*> freeList;
- void deallocate(T* ptr) { std::lock_guard<std::mutex> lock(mtx); // Fixed: lock mutex freeList.push_back(ptr); } };
- // Even better: Use RAII lock guard to ensure unlock class ThreadSafePool { std::mutex mtx; std::vector<T*> freeList;
- private: bool isValidPointer(T* ptr) const { // Validation logic return ptr != nullptr; } }; ```

**Explanation:**

- **The data race:** `allocate()` locks mutex, but `deallocate()` does NOT; both functions access `freeList`; concurrent access to `std::vector` without synchronization = **undefined behavior**
- **What can go wrong - concurrent push_back:** Thread 1: `allocate()` reads `freeList.size()`, Thread 2: `deallocate()` calls `push_back()` (modifies size), Thread 1: continues with invalid size; **crash or corruption**
- **Vector internal state corruption:** `std::vector` has size, capacity, data pointer; unsynchronized modifications corrupt these; might grow during push_back while another thread reads; **dangling pointers, crashes**
- **Why allocate() is protected but deallocate() isn't:** Likely oversight/mistake; common pattern in single-threaded code; easy to forget when converting to thread-safe; **all shared state access must be synchronized**
- **Lock granularity:** Lock held only during vector operations (good); released before returning object to user; user code runs without holding lock; avoids deadlock if user code allocates again

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
Fix the double-free vulnerability:
```cpp
void deallocate(T* ptr) {
    freeList.push_back(ptr);
}

// User code
T* obj = pool.allocate();
pool.deallocate(obj);
pool.deallocate(obj);  // Corrupts pool!
```

**Answer:**

```cpp
#include <unordered_set>

class SafePool {
    std::vector<T*> freeList;
    std::unordered_set<T*> allocatedSet;  // Track allocated objects
    std::mutex mtx;

public:
    T* allocate() {
        std::lock_guard<std::mutex> lock(mtx);
        if (freeList.empty()) return nullptr;
        
    // ... (additional code omitted for brevity)
```

- cpp #include <unordered_set>
- class SafePool { std::vector<T*> freeList; std::unordered_set<T*> allocatedSet; // Track allocated objects std::mutex mtx;
- public: IndexBasedPool() { for (size_t i = 0; i < N; ++i) { freeIndices.push_back(i); } }

**Explanation:**

- **The double-free bug:** Calling `deallocate(ptr)` twice adds same pointer to freeList twice; next two `allocate()` calls return **same object** to two different users; both users modify same memory; **data corruption, unpredictable crashes**
- **Real-world impact:** Thread 1 allocates → gets object A, Thread 2 allocates → gets same object A (double-allocated), Both threads write to A's fields simultaneously; race conditions, memory corruption; extremely hard to debug
- **Solution 1: Track allocated pointers:** Use `std::unordered_set<T*>` to track allocated objects; `allocate()` inserts into set, `deallocate()` removes from set; if ptr not in set → double-free or invalid pointer; O(1) check with hash set
- **Solution 2: Index-based with flags:** Each slot has `allocated` boolean flag; `deallocate()` checks flag before returning to pool; if flag already false → double-free detected; simpler than hash set, faster for small pools
- **Pointer validation:** Calculate index: `idx = ptr - storage`; if idx >= N → pointer not from pool; catches invalid pointers (not from pool); prevents corruption from external pointers
- **Performance trade-off:** Tracking adds overhead (set operations, flag checks); worth it for safety in development; can be disabled in release builds with `#ifndef NDEBUG`; detect-and-throw vs. assert-and-crash trade-off

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
Complete the index-based allocation:
```cpp
template <typename T, size_t N>
class IndexPool {
    T* storage;
    size_t freeList[N];
    size_t freeCount;

public:
    T* allocate() {
        // Your implementation
    }
};
```

**Answer:**

```cpp
template <typename T, size_t N>
class IndexPool {
    T* storage;
    size_t freeList[N];  // Stack of free indices
    size_t freeCount;    // Number of free slots

public:
    IndexPool() : storage(new T[N]), freeCount(N) {
        // Initialize free list with all indices
        for (size_t i = 0; i < N; ++i) {
            freeList[i] = i;
        }
    // ... (additional code omitted for brevity)
```

- cpp template <typename T, size_t N> class IndexPool { T* storage; size_t freeList[N]; // Stack of free indices size_t freeCount; // Number of free slots
- public: IndexPool() : storage(new T[N]), freeCount(N) { // Initialize free list with all indices for (size_t i = 0; i < N; ++i) { freeList[i] = i; } }
- ~IndexPool() { delete[] storage; }

**Explanation:**

- **Index-based design:** Store indices in freeList, not pointers; `freeList[N]` is array of indices (0 to N-1); `freeCount` tracks how many slots are free; simpler than `std::vector<T*>`
- **Free list as stack:** freeList acts like stack; allocate() pops from top (--freeCount), deallocate() pushes to top (freeCount++); O(1) operations, very fast
- **Allocation algorithm:** Check if freeCount > 0 (pool not empty), Decrement freeCount (pop operation), Get index: `idx = freeList[freeCount]`, Return pointer: `&storage[idx]`
- **Deallocation algorithm:** Calculate index from pointer: `idx = ptr - storage`, Validate index: `if (idx >= N) throw`, Push index back: `freeList[freeCount] = idx`, Increment freeCount
- **Pointer arithmetic validation:** `ptr - storage` gives offset in array; if ptr from this pool → offset in [0, N); if ptr from elsewhere → offset can be huge (or negative); validates pool ownership
- **Cache efficiency:** freeList is array (contiguous memory); better cache locality than linked list or vector; freeCount keeps track without traversing; very fast in tight loops

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
Why does this pool leak memory?
```cpp
struct Resource {
    std::string data;
    std::vector<int> values;
};

class Pool {
    Resource* storage;

    void deallocate(Resource* obj) {
        freeList.push_back(obj);  // Leak!
    }
};
```

**Answer:**

```cpp
// Problem: Resource has dynamic members (string, vector)
// When returned to pool, data and values still hold allocated memory
// That memory is never freed until pool destroyed

// Fix 1: Explicitly reset/clear in deallocate
void deallocate(Resource* obj) {
    // Clear dynamic allocations
    obj->data.clear();
    obj->data.shrink_to_fit();  // Release capacity
    
    obj->values.clear();
    obj->values.shrink_to_fit();  // Release capacity
    // ... (additional code omitted for brevity)
```

- cpp // Problem: Resource has dynamic members (string, vector) // When returned to pool, data and values still hold allocated memory // That memory is never freed until pool destroyed
- // Fix 2: Destruct and reconstruct (placement new) template <typename T> class ProperPool { alignas(T) char storage[sizeof(T) * 100]; std::vector<void*> freeList;
- public: T* allocate() { void* mem = freeList.empty()

**Explanation:**

- **The memory leak:** Resource has `std::string data` and `std::vector<int> values`; these own heap-allocated memory; `deallocate()` returns pointer to pool but **doesn't free internal allocations**; memory stays allocated even though Resource is "free"
- **Why it's a leak:** User allocates Resource → fills data/values (allocates memory), User deallocates Resource → returns to pool, Resource stays allocated in pool with data/values still holding memory, Next user allocates same Resource → fills NEW data/values, **Old memory never freed** until pool destroyed
- **Accumulation over time:** Each allocate-use-deallocate cycle adds memory; pool thinks Resource is reused (good), but Resource's members keep growing (bad); can leak gigabytes in long-running program
- **Fix 1: Explicit clear + shrink_to_fit:** Call `clear()` to remove elements (size → 0), Call `shrink_to_fit()` to release capacity, **Warning:** shrink_to_fit is "request" not guarantee; may not actually free memory (implementation-defined)
- **Fix 2: Destruct and reconstruct (best):** Call destructor explicitly: `obj->~T()`; frees all internal allocations; use placement new on next allocation: `new (mem) T()`; constructs fresh object with empty members; **guaranteed** to free memory
- **Fix 3: Custom reset method:** Add `reset()` member function to Resource; reset() clears all internal state and frees memory; cleaner API, self-documenting; can be more efficient than destruct-reconstruct

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
Implement chunk boundary checking:
```cpp
class ExpandablePool {
    std::vector<T*> chunks;
    static constexpr size_t CHUNK_SIZE = 100;

    void deallocate(T* ptr) {
        // Find owning chunk - implement this
    }
};
```

**Answer:**

```cpp
template <typename T>
class ExpandablePool {
    std::vector<T*> chunks;          // Each chunk is array of T
    std::vector<T*> freeList;
    static constexpr size_t CHUNK_SIZE = 100;

public:
    ExpandablePool() {
        addChunk();  // Start with one chunk
    }

    ~ExpandablePool() {
    // ... (additional code omitted for brevity)
```

- cpp template <typename T> class ExpandablePool { std::vector<T*> chunks; // Each chunk is array of T std::vector<T*> freeList; static constexpr size_t CHUNK_SIZE = 100;
- public: ExpandablePool() { addChunk(); // Start with one chunk }
- ~ExpandablePool() { for (T* chunk : chunks) { delete[] chunk; } }

**Explanation:**

- **Expandable pool design:** Starts with one chunk (array of CHUNK_SIZE objects), When freeList empty → allocates new chunk, Grows automatically on demand; no fixed capacity limit
- **Chunk ownership problem:** Have multiple chunks (different memory ranges), Given pointer, must find which chunk owns it, Can't use simple `ptr - storage` (multiple arrays)
- **Linear search solution:** Iterate through all chunks, For each chunk, check if `ptr >= chunkStart && ptr < chunkEnd`, If in range → found owning chunk; O(num_chunks) time
- **Alignment verification:** `offset = ptr - chunk` gives offset in bytes, `offset % sizeof(T)` checks alignment, Must be zero (ptr points to valid element), Catches pointers to middle of objects (invalid)
- **Boundary conditions:** `ptr >= chunkStart` - inclusive start, `ptr < chunkEnd` - exclusive end, `chunkEnd = chunk + CHUNK_SIZE` - one past last element, Standard C++ pointer comparison rules
- **Map-based optimization:** Store `std::unordered_map<T*, T*>` mapping object ptr → chunk ptr, O(1) lookup instead of O(num_chunks), Trade-off: Extra memory (map overhead), Faster for large number of chunks

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
Add alignment validation:
```cpp
struct alignas(32) SIMDData {
    float values[8];
};

class Pool {
    SIMDData* allocate() {
        // Ensure returned pointer is 32-byte aligned
    }
};
```

**Answer:**

```cpp
#include <cstddef>
#include <cstdlib>
#include <new>

struct alignas(32) SIMDData {
    float values[8];
};

class Pool {
    static constexpr size_t ALIGNMENT = alignof(SIMDData);  // 32 bytes
    static constexpr size_t POOL_SIZE = 100;

    // ... (additional code omitted for brevity)
```

- cpp #include <cstddef> #include <cstdlib> #include <new>
- struct alignas(32) SIMDData { float values[8]; };
- class Pool { static constexpr size_t ALIGNMENT = alignof(SIMDData); // 32 bytes static constexpr size_t POOL_SIZE = 100;

**Explanation:**

- **Why alignment matters:** SIMD instructions (AVX, SSE) require aligned data; `_mm256_load_ps` requires 32-byte alignment; **crashes** (segfault) on misaligned access; or falls back to slow unaligned load
- **alignas specifier:** `alignas(32)` tells compiler to align to 32-byte boundary; works for types, variables, arrays; compiler ensures alignment; part of C++11 standard
- **Aligned allocation:** `std::aligned_alloc(alignment, size)` - C++17 function; allocates memory with specified alignment; returns `void*` aligned to boundary; must use `std::free()` (not delete) to deallocate
- **Alignment validation at runtime:** Convert pointer to integer: `uintptr_t addr = reinterpret_cast<uintptr_t>(ptr)`; Check alignment: `addr % ALIGNMENT == 0`; If not aligned → bug in allocator or corrupted pointer
- **Option 1: aligned_alloc:** Use `std::aligned_alloc` for dynamic allocation; guarantees alignment; portable (C++17); must use `free()` for deallocation; doesn't call constructors
- **Option 2: alignas buffer:** Use `alignas(32) char storage[...]`; aligned at compile time; no runtime allocation; can use placement new for construction; better for fixed-size pools

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
What's the issue with this pool destructor?
```cpp
class Pool {
    T* storage;

public:
    ~Pool() {
        delete storage;  // Bug!
    }
};
```

**Answer:**
```cpp
// Bug: storage was allocated with new T[N], must use delete[]

class Pool {
    T* storage;
    size_t capacity;

public:
    Pool(size_t n) : capacity(n) {
        storage = new T[n];  // Array allocation
    }

    ~Pool() {
        delete[] storage;  // Correct: delete[] for arrays
    }
};

// What happens with delete instead of delete[]:
// - Only first object's destructor is called
// - Memory for array header is incorrectly freed
// - Heap corruption
// - Undefined behavior (crash, leak, silent corruption)
```

**Explanation:**
- **The bug - delete vs delete[]:** `storage = new T[N]` allocates array (multiple objects); must use `delete[]` to deallocate; using `delete` (no brackets) is **undefined behavior**; common C++ mistake
- **What delete[] does:** Calls destructor for **each** array element (N times), Then frees entire array memory, Array header stores count (implementation detail)
- **What delete does (wrong):** Calls destructor only for **first** element, Tries to free memory assuming single object, **Heap corruption** - array header not handled correctly
- **Real-world consequences:** Non-POD types: Leaks memory (destructors not called for elements 1..N-1), POD types: May seem to work but still UB, Debug builds: Often crash immediately (good for debugging), Release builds: Silent corruption, crashes later
- **Example with std::string:** Array of 10 std::strings allocated, `delete storage` calls destructor only for `storage[0]`, `storage[1]` through `storage[9]` never destroyed, Memory for 9 strings leaked, Plus heap corruption from incorrect deallocation
- **How to detect:** Enable compiler warnings: `-Wall -Wextra`, Use sanitizers: `-fsanitize=address`, Valgrind: "Mismatched free() / delete / delete []", Static analysis: clang-tidy, cppcheck
- **Prevention with smart pointers:** Use `std::unique_ptr<T[]>` for arrays, Automatically uses `delete[]` in deleter, No manual delete needed, Array-aware smart pointer
- **Matching allocation/deallocation rules:** `new` → `delete`, `new[]` → `delete[]`, `malloc` → `free`, `aligned_alloc` → `free`, **Never mix** different allocation/deallocation pairs
- **Why compiler can't catch this:** `T*` is same type for single object and array, Type system doesn't distinguish, Impossible to enforce at compile time, Must remember allocation method
- **Modern C++ alternative:** Use `std::vector<T>` instead of `new T[]`, Automatic memory management, No manual delete needed, Exception-safe
- **Key Concept:** Array allocation (new[]) requires array deallocation (delete[]); single object delete causes UB; only first destructor called; heap corruption; use smart pointers or vector; compiler warnings help detect; matching new/delete pairs critical

---

#### Q9
Fix the race condition:
```cpp
class Pool {
    std::atomic<size_t> head{0};
    T* buffer[100];

    T* allocate() {
        size_t h = head.load();
        T* obj = buffer[h];
        head.store(h + 1);  // Race!
        return obj;
    }
};
```

**Answer:**

```cpp
// Bug: Load-modify-store is not atomic as a whole
// Two threads can read same h value before either increments

class Pool {
    std::atomic<size_t> head{0};
    T* buffer[100];
    static constexpr size_t CAPACITY = 100;

public:
    // Fix 1: Use compare_exchange (lock-free)
    T* allocate() {
        size_t h = head.load();
    // ... (additional code omitted for brevity)
```

- cpp // Bug: Load-modify-store is not atomic as a whole // Two threads can read same h value before either increments
- class Pool { std::atomic<size_t> head{0}; T* buffer[100]; static constexpr size_t CAPACITY = 100;
- // For deallocation, need different approach (stack-based) std::atomic<size_t> tail{0};

**Explanation:**

- **The race condition:** Thread 1: loads h = 5, Thread 2: loads h = 5 (same!), Thread 1: stores h = 6, Thread 2: stores h = 6 (overwrites!), **Both threads get buffer[5]** - same object allocated twice!
- **Why atomic doesn't help here:** `head.load()` is atomic, `head.store()` is atomic, But the **combination** "read-modify-write" is NOT atomic, Gap between load and store allows race
- **ABA problem:** Even worse: Thread 1 reads h=5, Thread 2 reads h=5, increments to 6, allocates buffer[5], Thread 3 deallocates buffer[5], head back to 5, Thread 1 thinks nothing changed, allocates same object!
- **Fix 1: compare_exchange_weak:** Atomically: "If head == expected, set head = desired, return true; else set expected = head, return false", Fails if another thread modified head, Loop retries until success, **Lock-free** but may spuriously fail (weak version)
- **Fix 2: fetch_add (simpler):** `fetch_add(1)` atomically increments AND returns old value, One atomic operation, no loop needed, Simpler than compare_exchange, **Best for monotonic counters**
- **Why fetch_add is better here:** Allocation is monotonic (always increasing), No need for complex CAS logic, Single atomic instruction, Hardware-optimized on most CPUs

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
Implement proper placement new lifecycle:
```cpp
class Pool {
    alignas(Resource) char storage[sizeof(Resource) * 100];

    Resource* allocate() {
        void* mem = getFreeSlot();
        // Construct Resource using placement new
    }

    void deallocate(Resource* obj) {
        // Properly destruct before returning to pool
    }
};
```

**Answer:**

```cpp
#include <new>
#include <vector>

struct Resource {
    std::string data;
    std::vector<int> values;
    
    Resource() {
        std::cout << "Resource constructed\n";
    }
    
    ~Resource() {
    // ... (additional code omitted for brevity)
```

- cpp #include <new> #include <vector>
- Resource* allocate() { if (freeList.empty()) { return nullptr; // Pool exhausted }
- void* mem = freeList.back(); freeList.pop_back();

**Explanation:**

- **Placement new:** `new (mem) T()` constructs object at address `mem`; doesn't allocate memory (memory already allocated); calls constructor on raw memory; returns pointer to constructed object
- **Why use placement new:** Pool pre-allocates memory (char buffer), Need to construct objects on demand, Separate allocation (done once) from construction (per object), Allows custom memory management
- **Explicit destructor call:** `obj->~Resource()` calls destructor without deallocating memory; destructor frees internal resources (string data, vector elements); memory remains allocated (returned to pool); rare case where explicit destructor call is correct
- **Lifecycle phases:** Memory allocation (once, in pool constructor), Object construction (placement new on allocate), Object destruction (explicit destructor on deallocate), Memory deallocation (once, in pool destructor)
- **Importance of destruction:** Resource has `std::string` and `std::vector` with dynamic allocations; if not destroyed, memory leaks; explicit destructor frees these; fresh construction on next allocation prevents stale data
- **Tracking construction status:** `initialized[]` array tracks which slots have constructed objects; prevents double-destruction (UB); prevents destroying unconstructed memory (UB); used in pool destructor to destroy only live objects

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
Calculate the correct global index:
```cpp
class ChunkedPool {
    std::vector<T*> chunks;
    static constexpr size_t CHUNK_SIZE = 100;

    size_t getGlobalIndex(T* ptr) {
        // Calculate global index from pointer
    }
};
```

**Answer:**

```cpp
template <typename T>
class ChunkedPool {
    std::vector<T*> chunks;
    static constexpr size_t CHUNK_SIZE = 100;

public:
    size_t getGlobalIndex(T* ptr) const {
        // Find which chunk contains this pointer
        for (size_t chunkIdx = 0; chunkIdx < chunks.size(); ++chunkIdx) {
            T* chunkStart = chunks[chunkIdx];
            T* chunkEnd = chunkStart + CHUNK_SIZE;

    // ... (additional code omitted for brevity)
```

- cpp template <typename T> class ChunkedPool { std::vector<T*> chunks; static constexpr size_t CHUNK_SIZE = 100;
- // Pointer not from this pool throw std::invalid_argument("Pointer not from pool"); }
- // Alternative: Store chunk index with each allocation std::unordered_map<T*, size_t> ptrToGlobalIndex;

**Explanation:**

- **Global index concept:** Each object has unique index across all chunks; Chunk 0: indices 0-99, Chunk 1: indices 100-199, Chunk 2: indices 200-299, etc.; allows flat indexing into chunked storage
- **Calculation formula:** `globalIndex = chunkIndex * CHUNK_SIZE + offsetInChunk`, `chunkIndex = globalIndex / CHUNK_SIZE`, `offsetInChunk = globalIndex % CHUNK_SIZE`; simple integer arithmetic
- **Finding chunk:** Linear search through chunks: `if (ptr >= chunkStart && ptr < chunkEnd)`, Once found, calculate offset: `ptr - chunkStart`, Combine with chunk index: `chunkIdx * CHUNK_SIZE + offset`
- **Reverse operation:** Given global index, find chunk: `chunkIdx = globalIndex / CHUNK_SIZE`, Find offset: `offsetInChunk = globalIndex % CHUNK_SIZE`, Get pointer: `&chunks[chunkIdx][offsetInChunk]`
- **Why this is useful:** Serialize pool state (save/load by indices), Implement handles instead of pointers (index-based), Iterate over all objects in order, Debug/logging (print object indices), External references (other systems use indices)
- **Performance consideration:** Linear search O(num_chunks) for getGlobalIndex, Use map for O(1) lookup if frequent, getPointerFromIndex is O(1) always (just division/modulo), Cache last chunk for locality of reference

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
Why doesn't this pool reuse memory?
```cpp
class Pool {
    T* storage;
    size_t nextIndex = 0;

    T* allocate() {
        return &storage[nextIndex++];  // Bug!
    }

    void deallocate(T* ptr) {
        // Nothing!
    }
};
```

**Answer:**

```cpp
// Problem: No free list - deallocate() does nothing
// Allocations are linear (nextIndex always increases)
// Never reuses deallocated objects - defeats purpose of pool

class BrokenPool {
    T* storage;
    size_t nextIndex = 0;
    size_t capacity;

public:
    BrokenPool(size_t n) : capacity(n) {
        storage = new T[n];
    // ... (additional code omitted for brevity)
```

- cpp // Problem: No free list - deallocate() does nothing // Allocations are linear (nextIndex always increases) // Never reuses deallocated objects - defeats purpose of pool
- class BrokenPool { T* storage; size_t nextIndex = 0; size_t capacity;
- public: BrokenPool(size_t n) : capacity(n) { storage = new T[n]; }

**Explanation:**

- **The fundamental flaw:** Pool allocator's purpose is **reuse** memory; this pool allocates linearly (nextIndex++); never returns memory to pool (deallocate does nothing); **defeats entire purpose** of object pool
- **What happens:** Allocate 10 objects → nextIndex = 10, Deallocate all → nextIndex still 10, Try to allocate → nextIndex >= capacity → nullptr, Pool appears "exhausted" even though all objects are "free"
- **Why deallocate is empty:** Likely incomplete implementation or misunderstanding; forgot to implement free list; or thought linear allocation was sufficient (wrong)
- **Free list necessity:** Track which objects are available for reuse, deallocate() adds to free list, allocate() checks free list first, Falls back to linear allocation if free list empty
- **Allocate strategy (fixed version):** 1. Check free list → if not empty, pop and return (reuse), 2. If free list empty → use nextIndex (fresh allocation), 3. If nextIndex >= capacity → nullptr (exhausted)
- **Memory usage pattern:** Without free list: Memory usage only grows (never shrinks), With free list: Memory usage grows to peak, then reuses (stays at peak)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
Fix the false sharing issue:
```cpp
struct Counter {
    int value;  // 4 bytes
};

// Multiple threads allocate and modify Counters
// Performance degrades significantly - why?
```

**Answer:**

```cpp
// Problem: False sharing - multiple Counters share cache line
// Cache line = 64 bytes on most CPUs
// Multiple 4-byte Counters fit in one cache line
// Different threads modify different Counters → cache line bounces between CPUs

// Without fix: False sharing
struct Counter {
    int value;  // 4 bytes
};

// Pool allocates Counters sequentially:
// [Counter0][Counter1][Counter2]...[Counter15] all in same 64-byte cache line
    // ... (additional code omitted for brevity)
```

- // Without fix: False sharing struct Counter { int value; // 4 bytes };
- // Fix 1: Pad to cache line size struct alignas(64) Counter { int value; char padding[60]; // Total 64 bytes = one cache line };
- // Now each Counter on its own cache line: // [Counter0 (64B)][Counter1 (64B)][Counter2 (64B)]..

**Explanation:**

- **False sharing definition:** Multiple threads access **different** variables on **same cache line**; CPU cache operates on cache line granularity (typically 64 bytes); modifying one variable invalidates entire cache line for other CPUs
- **Why it happens with Counters:** Counter is 4 bytes, cache line is 64 bytes; 16 Counters fit in one cache line; Thread 1 modifies Counter[0], Thread 2 modifies Counter[1]; **both modifications affect same cache line**
- **Cache coherency protocol (MESI):** Modified: CPU owns cache line exclusively, Exclusive: CPU has cache line, not modified, Shared: Multiple CPUs have copy (read-only), Invalid: Cache line invalidated; modification causes transition M→I on other CPUs
- **Performance impact:** Each modification triggers cache invalidation, Cache line bounces between CPUs ("ping-pong"), Memory bandwidth exhausted, **10x-100x slowdown** vs no false sharing
- **Fix 1: Explicit padding:** Pad Counter to 64 bytes (cache line size); each Counter gets own cache line; no sharing between adjacent Counters; wastes memory (60 bytes padding per Counter)
- **Fix 2: hardware_destructive_interference_size (C++17):** `std::hardware_destructive_interference_size` = cache line size (implementation-defined); `alignas(std::hardware_destructive_interference_size)` pads to cache line; portable across architectures

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
Implement cache line alignment:
```cpp
template <typename T>
struct AlignedWrapper {
    // Ensure T is on its own cache line
};
```

**Answer:**

```cpp
#include <new>  // For std::hardware_destructive_interference_size

// C++17 solution with std::hardware_destructive_interference_size
template <typename T>
struct alignas(std::hardware_destructive_interference_size) AlignedWrapper {
    T value;

    // Ensure total size is multiple of cache line
    char padding[std::hardware_destructive_interference_size - sizeof(T)];

    // Constructors
    AlignedWrapper() = default;
    // ... (additional code omitted for brevity)
```

- cpp #include <new> // For std::hardware_destructive_interference_size
- // C++17 solution with std::hardware_destructive_interference_size template <typename T> struct alignas(std::hardware_destructive_interference_size) AlignedWrapper { T value;
- // Ensure total size is multiple of cache line char padding[std::hardware_destructive_interference_size - sizeof(T)];

**Explanation:**

- **AlignedWrapper purpose:** Wraps type T to ensure it occupies entire cache line; prevents false sharing with adjacent objects; padding to cache line size (64 bytes); alignment to cache line boundary
- **C++17 std::hardware_destructive_interference_size:** Compile-time constant for cache line size; platform-specific (64 on x86, varies on others); portable way to avoid false sharing; guaranteed by compiler
- **Alignment vs size:** `alignas(64)` ensures **start** of wrapper on 64-byte boundary; padding ensures **entire** wrapper spans full cache line; both necessary for complete isolation
- **Padding calculation:** If `sizeof(T) < 64` → pad to 64 bytes, If `sizeof(T) >= 64` → no padding (already cache-line-sized or larger), Padding = CacheLineSize - sizeof(T)
- **Accessor methods:** `get()` returns reference to wrapped value; `operator*` for dereference-like syntax; `operator->` for member access; makes wrapper transparent
- **Perfect forwarding constructors:** `template <typename... Args> AlignedWrapper(Args&&... args)` forwards arguments to T's constructor; enables in-place construction; avoids copies

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
Add statistics tracking:
```cpp
class MonitoredPool {
    // Track total allocations, deallocations, peak usage
    // Implement getStats() method
};
```

**Answer:**

```cpp
#include <iostream>
#include <atomic>

template <typename T>
class MonitoredPool {
    static constexpr size_t POOL_SIZE = 100;
    T* storage;
    std::vector<T*> freeList;

    // Statistics (thread-safe with atomics)
    std::atomic<size_t> totalAllocations{0};
    std::atomic<size_t> totalDeallocations{0};
    // ... (additional code omitted for brevity)
```

- cpp #include <iostream> #include <atomic>
- template <typename T> class MonitoredPool { static constexpr size_t POOL_SIZE = 100; T* storage; std::vector<T*> freeList;
- public: MonitoredPool() { storage = new T[POOL_SIZE]; for (size_t i = 0; i < POOL_SIZE; ++i) { freeList.push_back(&storage[i]); } }

**Explanation:**

- **Why monitor pools:** Detect capacity issues (too small?), Track memory usage patterns, Identify leaks (deallocations < allocations), Performance tuning (failure rate), Production diagnostics
- **Atomic counters for thread safety:** `std::atomic<size_t>` for each statistic; thread-safe increment/decrement; no mutex needed for counters; lock-free performance
- **Statistics tracked:** `totalAllocations` - lifetime allocation count, `totalDeallocations` - lifetime deallocation count, `currentUsage` - currently allocated objects, `peakUsage` - maximum concurrent usage, `allocationFailures` - requests that returned nullptr
- **Peak usage update:** Read current usage; compare with stored peak; if current > peak, attempt CAS (compare_exchange_weak); retry if another thread updated peak; ensures accurate peak even under contention
- **Derived metrics:** Utilization: `peakUsage / capacity × 100%`, Failure rate: `failures / (allocations + failures) × 100%`, Leak indicator: `currentUsage - (totalAllocations - totalDeallocations)`
- **Stats struct:** Return snapshot of all statistics; immutable struct (all const values); thread-safe to read (atomics); user can store and compare snapshots

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
Fix the alignment bug:
```cpp
class Pool {
    char* storage = new char[sizeof(T) * 100];

    T* allocate() {
        return reinterpret_cast<T*>(storage);  // May be misaligned!
    }
};
```

**Answer:**

```cpp
// Problem: new char[] has no alignment guarantees beyond alignof(char) = 1
// If T requires 8, 16, or more byte alignment, storage may be misaligned

// Fix 1: Use alignas with array (C++11)
template <typename T>
class Pool {
    static constexpr size_t POOL_SIZE = 100;
    alignas(T) char storage[sizeof(T) * POOL_SIZE];  // Aligned to T's requirement
    
public:
    T* allocate() {
        // storage guaranteed aligned for T
    // ... (additional code omitted for brevity)
```

- cpp // Problem: new char[] has no alignment guarantees beyond alignof(char) = 1 // If T requires 8, 16, or more byte alignment, storage may be misaligned
- // Example demonstrating the bug: struct alignas(16) Vec4 { float x, y, z, w; };

**Explanation:**

- **The alignment bug:** `new char[]` allocates with `alignof(char)` = 1 byte alignment; no guarantee for larger alignments (8, 16, 32, 64 bytes); if T requires alignment > 1, storage may be misaligned; **undefined behavior** or crash
- **Why alignment matters:** CPU performance (aligned access faster), SIMD requirements (SSE, AVX require 16/32-byte alignment), Atomic operations (some architectures require natural alignment), Hardware restrictions (some types must be aligned)
- **Alignment requirements:** `alignof(T)` gives required alignment for type T; `int`: 4 bytes, `double`: 8 bytes, SIMD types (Vec4, __m128): 16 bytes, AVX (__m256): 32 bytes, Cache line: 64 bytes
- **Fix 1: alignas array (C++11):** `alignas(T) char storage[...]` aligns array to T's requirement; compiler guarantees proper alignment; works for stack/static arrays; simple and type-safe
- **Fix 2: std::aligned_alloc (C++17):** Allocates heap memory with specified alignment; `std::aligned_alloc(alignof(T), size)`; **must use std::free()**, not delete; portable across platforms
- **Fix 3: Runtime verification:** Check `addr % alignof(T) == 0` after allocation; throws if misaligned; catches bugs early; but better to fix at allocation

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
Implement exhaustion handling:
```cpp
class Pool {
    T* allocate() {
        if (freeList.empty()) {
            // Implement 3 different strategies:
            // 1. Throw exception
            // 2. Return nullptr
            // 3. Allocate new chunk
        }
    }
};
```

**Answer:**

```cpp
#include <stdexcept>

// Strategy 1: Throw exception
template <typename T>
class ThrowingPool {
    std::vector<T*> freeList;
    
public:
    T* allocate() {
        if (freeList.empty()) {
            throw std::bad_alloc();  // Or custom exception
        }
    // ... (additional code omitted for brevity)
```

- cpp #include <stdexcept>
- // Strategy comparison: void compare_strategies() { // Strategy 1: Throwing { ThrowingPool<int> pool; try { int* p = pool.allocate(); // Use p..

**Explanation:**

- **Strategy 1: Throw exception - Pros:** Forces error handling (can't ignore), Clean error propagation (exceptions), No null checks needed (strong guarantee); **Cons:** Exception overhead (stack unwinding, performance), Control flow complexity (harder to reason about), May terminate if uncaught
- **Strategy 1 - When to use:** Allocation failure is **exceptional** (rare), Prefer strong error guarantees, Not performance-critical path, Consistent with STL (std::vector throws)
- **Strategy 2: Return nullptr - Pros:** Zero overhead (no exception), Explicit check at call site, Works in no except code (`noexcept`); **Cons:** Easy to forget null check (UB if missed), Verbose (if (!p) everywhere), Error-prone (silent bugs)
- **Strategy 2 - When to use:** Performance-critical (hot path), Allocation failure common/expected, Embedded systems (no exceptions), Interfacing with C code
- **Strategy 3: Expandable pool - Pros:** Never fails (until OS OOM), No failure handling needed, Adapts to demand automatically; **Cons:** Unbounded memory growth, Can't predict memory usage, Fragmentation (many chunks), Slower deallocation (find owning chunk)
- **Strategy 3 - When to use:** Demand unpredictable, Memory plentiful, Development/testing (ease of use), Not real-time (growth has latency)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
Detect out-of-pool pointers:
```cpp
void deallocate(T* ptr) {
    // Validate ptr is from this pool before deallocating
}
```

**Answer:**

```cpp
template <typename T>
class ValidatingPool {
    static constexpr size_t POOL_SIZE = 100;
    T* storage;
    std::vector<T*> freeList;

public:
    ValidatingPool() {
        storage = new T[POOL_SIZE];
        
        for (size_t i = 0; i < POOL_SIZE; ++i) {
            freeList.push_back(&storage[i]);
    // ... (additional code omitted for brevity)
```

- cpp template <typename T> class ValidatingPool { static constexpr size_t POOL_SIZE = 100; T* storage; std::vector<T*> freeList;
- public: ValidatingPool() { storage = new T[POOL_SIZE]; for (size_t i = 0; i < POOL_SIZE; ++i) { freeList.push_back(&storage[i]); } }
- ~ValidatingPool() { delete[] storage; }

**Explanation:**

- **Validation necessity:** User may pass random pointer (not from pool), May pass pointer to middle of object (misaligned), May deallocate twice (double-free), May pass nullptr; **all cause corruption** - must detect
- **Validation 1: Nullptr check:** `if (ptr == nullptr) throw`; simplest check; prevents freeList from storing nullptr; catches common mistake
- **Validation 2: Range check:** `if (ptr < storage || ptr >= storage + POOL_SIZE) throw`; ensures pointer within pool's memory range; catches completely external pointers; O(1) check for single-chunk
- **Validation 3: Alignment check:** `offset = ptr - storage; if (offset % sizeof(T) != 0) throw`; ensures pointer aligned to object boundary; catches pointers to middle of objects (e.g., `&obj.member`); prevents corrupting pool structure
- **Validation 4: Double-free check:** Linear search O(n): iterate freeList, check if ptr already there; Set-based O(1): maintain `unordered_set<T*>` of free pointers, check membership; trade-off: memory for speed
- **Chunked pools - more complex:** Must check **all** chunks: linear search through chunks; for each chunk: `if (ptr >= start && ptr < end)`; can optimize: cache last chunk, store chunk ranges in vector

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
Implement RAII pool handle:
```cpp
template <typename T>
class PoolHandle {
    // Automatically returns object to pool on destruction
};
```

**Answer:**

```cpp
#include <memory>

template <typename T>
class Pool;  // Forward declaration

// RAII handle that auto-returns to pool
template <typename T>
class PoolHandle {
    T* ptr;
    Pool<T>* pool;

public:
    // ... (additional code omitted for brevity)
```

- cpp #include <memory>
- template <typename T> class Pool; // Forward declaration
- // RAII handle that auto-returns to pool template <typename T> class PoolHandle { T* ptr; Pool<T>* pool;

**Explanation:**

- **RAII principle:** Resource Acquisition Is Initialization; allocate in constructor, deallocate in destructor; automatic lifetime management; can't forget to deallocate
- **PoolHandle design:** Holds `T*` (the object) and `Pool<T>*` (owner pool); destructor calls `pool->deallocate(ptr)`; move-only (unique ownership); prevents double-free and leaks
- **Move semantics:** Move constructor transfers ownership; sets source `ptr` to nullptr (moved-from state); move assignment releases old object first; enables return by value, storage in containers
- **Deleted copy:** `PoolHandle(const PoolHandle&) = delete`; prevents copying (would cause double-free); ensures unique ownership; compile-time error if attempted
- **Access operators:** `operator->`, `operator*` for pointer-like syntax; `get()` for raw pointer access; `operator bool` to check if valid; transparent usage like raw pointer
- **Manual release:** `release()` returns object early; sets ptr/pool to nullptr; useful for early return; destructor safe (checks nullptr)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
Fix the memory leak on pool destruction:
```cpp
class Pool {
    T* storage;
    std::vector<T*> freeList;
    size_t capacity;

    ~Pool() {
        delete[] storage;
        // What if freeList.size() < capacity?
        // Some objects still allocated - leak!
    }
};
```

**Answer:**

```cpp
// Problem: User still holds pointers to allocated objects
// Pool destructor deletes storage but user has dangling pointers
// User dereferences → use-after-free (UB)

// Fix 1: Require all objects returned before destruction
template <typename T>
class StrictPool {
    static constexpr size_t POOL_SIZE = 100;
    T* storage;
    std::vector<T*> freeList;

public:
    // ... (additional code omitted for brevity)
```

- cpp // Problem: User still holds pointers to allocated objects // Pool destructor deletes storage but user has dangling pointers // User dereferences → use-after-free (UB)
- // Fix 1: Require all objects returned before destruction template <typename T> class StrictPool { static constexpr size_t POOL_SIZE = 100; T* storage; std::vector<T*> freeList;
- public: StrictPool() { storage = new T[POOL_SIZE]; for (size_t i = 0; i < POOL_SIZE; ++i) { freeList.push_back(&storage[i]); } }

**Explanation:**

- **The leak problem:** Pool destroyed while objects still allocated; `delete[] storage` frees memory; user still holds pointers → **dangling pointers**; dereferencing = use-after-free (UB); hard to debug (crashes later, not at destruction)
- **Why this happens:** User forgets to return objects, Exception thrown before deallocation, Complex control flow (early returns), Pool destroyed before objects; **common mistake** in manual memory management
- **Fix 1: Assert all returned:** Check `freeList.size() == POOL_SIZE` in destructor; if not → log error and `std::terminate()`; **detects** problem but doesn't fix; forces user to fix code; good for development/testing
- **Fix 2: Destroy allocated objects:** Track allocated objects in `std::unordered_set`; in destructor: iterate allocated objects, call destructors (`obj->~T()`), then delete storage; **prevents** use-after-free of storage; but user pointers still dangle (safer than crashing)
- **Fix 3: Shared ownership:** Pool data in `std::shared_ptr<PoolData>`; allocated objects hold weak_ptr to pool; custom deleter checks if pool alive; storage kept alive until last object destroyed; **solves** lifetime issue but complex and overhead
- **Fix 4: RAII handles (best):** Return handles, not raw pointers; handles auto-return on destruction; can't forget to deallocate; pool can safely destroy when all handles gone; **prevents** problem at design level

**Note:** Full detailed explanation with additional examples available in source materials.

---
