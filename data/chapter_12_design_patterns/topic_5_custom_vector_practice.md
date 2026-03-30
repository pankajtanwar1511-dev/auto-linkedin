## TOPIC: STL-like Custom Vector Implementation

### PRACTICE_TASKS: Challenge Questions

#### Q1
```cpp
Vector<int> v;
v.reserve(10);
v[5] = 42;
std::cout << v[5];
```

**Answer:**

```cpp
Undefined behavior (most likely crashes or garbage output)
```

- Undefined behavior (most likely crashes or garbage output) ```

**Explanation:**

- **reserve(10) allocates capacity but does NOT construct elements**
- Allocates raw memory for 10 ints
- Does NOT call constructors or initialize elements
- size() remains 0 (no elements exist)

```cpp
// Option 1: Use resize
  Vector<int> v;
  v.resize(10);      // Creates 10 elements, default-initialized to 0
  v[5] = 42;         // Safe
  std::cout << v[5]; // Prints 42
  
  // Option 2: Use push_back
  Vector<int> v;
  v.reserve(10);     // Optimize capacity
  for (int i = 0; i < 10; ++i) {
      v.push_back(0); // Actually create elements
  }
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
```cpp
Vector<int> v = {1, 2, 3};
v.reserve(5);
auto it = v.begin();
v.push_back(4);
v.push_back(5);
std::cout << *it;
```

**Answer:**

```cpp
Safe, prints 1
```

**Explanation:**

- **Initial state:**
- v = {1, 2, 3}
- size = 3, capacity = 3 (implementation-dependent, could be larger)
- **v.reserve(5) ensures capacity ≥ 5:**

```cpp
// WITHOUT reserve:
  Vector<int> v = {1, 2, 3};  // capacity = 3
  auto it = v.begin();
  v.push_back(4);  // capacity 3→6, REALLOCATION!
  std::cout << *it; // UNDEFINED BEHAVIOR! Iterator invalidated
  
  // WITH reserve:
  Vector<int> v = {1, 2, 3};
  v.reserve(5);    // capacity = 5
  auto it = v.begin();
  v.push_back(4);  // No reallocation (4 ≤ 5)
  v.push_back(5);  // No reallocation (5 ≤ 5)
  std::cout << *it; // Safe, prints 1
```

- cpp // WITHOUT reserve: Vector<int> v = {1, 2, 3}; // capacity = 3 auto it = v.begin(); v.push_back(4); // capacity 3→6, REALLOCATION
- std::cout << *it; // UNDEFINED BEHAVIOR

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
Vector<int> v;
for (int i = 0; i < 8; ++i) {
    v.push_back(i);
}
std::cout << v.capacity();
```

**Answer:**

```cpp
8 (assuming doubling strategy)
```

- 8 (assuming doubling strategy) ```

**Explanation:**

- **Capacity doubling strategy:**
- Most vector implementations double capacity when full
- Amortized O(1) push_back performance
- Trade-off: memory overhead vs speed

```cpp
Initial: size=0, capacity=0
  
  i=0: push_back(0)
       - capacity=0, need space → allocate capacity=1
       - size=1, capacity=1
  
  i=1: push_back(1)
       - size=1, capacity=1 (full) → reallocate to capacity=2
       - size=2, capacity=2
  
  i=2: push_back(2)
       - size=2, capacity=2 (full) → reallocate to capacity=4
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
Vector<int> v1 = {1, 2, 3};
Vector<int> v2 = v1;
v2[0] = 99;
std::cout << v1[0];
```

**Answer:**

```cpp
1 (unaffected by v2 modification)
```

- 1 (unaffected by v2 modification) ```

**Explanation:**

- **Deep copy semantics:**
- Copy constructor creates independent copy
- v2 gets its own memory allocation
- v1 and v2 have separate data arrays

```cpp
Vector(const Vector& other) 
      : sz(other.sz), cap(other.cap) {
      
      // Allocate new memory
      data = static_cast<T*>(::operator new(cap * sizeof(T)));
      
      // Copy construct each element
      for (size_t i = 0; i < sz; ++i) {
          new (&data[i]) T(other.data[i]);
      }
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
Vector<int> v1 = {1, 2, 3};
Vector<int> v2 = std::move(v1);
std::cout << v1.size();
```

**Answer:**

```cpp
0 (safe to access size)
```

- 0 (safe to access size) ```

**Explanation:**

- **Move semantics:**
- Transfers ownership of resources
- v2 "steals" v1's data pointer
- v1 left in valid moved-from state

```cpp
Vector(Vector&& other) noexcept 
      : data(other.data), sz(other.sz), cap(other.cap) {
      
      // Steal resources from other
      // Leave other in valid state
      other.data = nullptr;
      other.sz = 0;
      other.cap = 0;
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
Vector<int> v;
v.resize(5);
std::cout << v[3];
```

**Answer:**

```cpp
0 (default-constructed value for int)
```

- 0 (default-constructed value for int) ```

**Explanation:**

- **resize(5) creates 5 elements:**
- Allocates memory for at least 5 ints
- Calls default constructor for each element
- For int: default constructor initializes to 0

```cpp
void resize(size_t new_size) {
      if (new_size < sz) {
          // Shrink: destroy extra elements
          for (size_t i = new_size; i < sz; ++i) {
              data[i].~T();
          }
          sz = new_size;
      } else if (new_size > sz) {
          // Grow: ensure capacity, construct new elements
          if (new_size > cap) {
              reserve(new_size);
          }
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
```cpp
Vector<int> v = {1, 2, 3};
v.resize(10);
std::cout << v.size() << ", " << v.capacity();
```

**Answer:**

```cpp
10, ≥10 (capacity at least 10, possibly more)
```

- 10, ≥10 (capacity at least 10, possibly more) ```

**Explanation:**

- **resize(10) grows from 3 to 10 elements:**
- Current: size=3, capacity=3 (or more)
- After: size=10, capacity≥10
- **Step-by-step execution:**

```cpp
// Initial: v = {1, 2, 3}
  // size=3, capacity=3 (assuming tight fit)
  
  v.resize(10);
  // 1. Check: new_size (10) > sz (3) → need to grow
  // 2. Check: new_size (10) > cap (3) → need reallocation
  // 3. reserve(10) → allocates capacity for 10 elements
  // 4. Construct 7 new elements (indices 3-9) with default values (0)
  // 5. sz = 10
  
  // Result: v = {1, 2, 3, 0, 0, 0, 0, 0, 0, 0}
  // size=10, capacity≥10
```

- cpp // Initial: v = {1, 2, 3} // size=3, capacity=3 (assuming tight fit) v.resize(10); // 1
- Check: new_size (10) > sz (3) → need to grow // 2
- Check: new_size (10) > cap (3) → need reallocation // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
Vector<int> v = {1, 2, 3, 4};
v.pop_back();
v.pop_back();
std::cout << v.capacity();
```

**Answer:**

```cpp
4 (unchanged - capacity not reduced)
```

- 4 (unchanged - capacity not reduced) ```

**Explanation:**

- **pop_back() only reduces size, not capacity:**
- Destroys the last element
- Decrements size counter
- Does NOT deallocate memory

```cpp
Vector<int> v = {1, 2, 3, 4};
  // size=4, capacity=4
  
  v.pop_back();  // Removes 4
  // Destroys element at index 3
  // size=3, capacity=4 (unchanged!)
  
  v.pop_back();  // Removes 3
  // Destroys element at index 2
  // size=2, capacity=4 (still unchanged!)
  
  std::cout << v.capacity();  // Prints 4
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
Vector<int> v;
v.reserve(100);
v.resize(50);
std::cout << v.size() << ", " << v.capacity();
```

**Answer:**

```cpp
50, 100
```

**Explanation:**

- **reserve(100) sets capacity to at least 100:**
- Allocates memory for 100 ints
- size remains 0 (no elements constructed)
- capacity becomes 100

```cpp
Vector<int> v;
  // size=0, capacity=0
  
  v.reserve(100);
  // Allocates space for 100 ints
  // size=0 (no elements yet)
  // capacity=100
  
  v.resize(50);
  // Constructs 50 elements (indices 0-49) with value 0
  // size=50
  // capacity=100 (no reallocation, 50 < 100)
  
  std::cout << v.size() << ", " << v.capacity();
  // Prints: 50, 100
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
Vector<std::string> v;
v.push_back("hello");
v.push_back("world");
v.clear();
std::cout << v.capacity();
```

**Answer:**

```cpp
≥2 (capacity unchanged by clear)
```

- ≥2 (capacity unchanged by clear) ```

**Explanation:**

- **clear() destroys all elements but doesn't free memory:**
- Calls destructor for each element
- Sets size to 0
- Capacity remains unchanged

```cpp
Vector<std::string> v;
  // size=0, capacity=0
  
  v.push_back("hello");
  // size=1, capacity=1 (or more, implementation-dependent)
  
  v.push_back("world");
  // size=2, capacity≥2 (possibly doubled to 2 or 4)
  
  v.clear();
  // Destroys "hello" and "world" strings
  // size=0
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
Vector<int> v = {1, 2, 3};
Vector<int>& ref = v;
ref.push_back(4);
std::cout << v.size();
```

**Answer:**

```cpp
4 (reference modifies original)
```

- 4 (reference modifies original) ```

**Explanation:**

- **References are aliases, not copies:**
- `ref` is a reference to `v`
- `ref` and `v` refer to the same object
- Modifying through reference modifies original

```cpp
Vector<int> v = {1, 2, 3};
  // v: size=3, data={1,2,3}
  
  Vector<int>& ref = v;
  // ref is an alias for v
  // No copy, ref and v are the same object
  
  ref.push_back(4);
  // Modifies the object (v)
  // v: size=4, data={1,2,3,4}
  
  std::cout << v.size();
  // Prints 4 (v was modified)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
Vector<int> v1 = {1, 2, 3};
Vector<int> v2;
v2 = v1;
v2 = v1;  // Assign again
std::cout << v2.size();
```

**Answer:**

```cpp
3 (safe, self-assignment check prevents issues)
```

- 3 (safe, self-assignment check prevents issues) ```

**Explanation:**

- **Second assignment is NOT self-assignment:**
- v1 and v2 are different objects
- v2 = v1 assigns v1 to v2 (twice)
- Both assignments are valid

```cpp
Vector<int> v1 = {1, 2, 3};
  // v1: size=3, data={1,2,3}
  
  Vector<int> v2;
  // v2: size=0, data=nullptr, capacity=0
  
  v2 = v1;  // First assignment
  // Copies v1 to v2
  // v2: size=3, data={1,2,3} (independent copy)
  
  v2 = v1;  // Second assignment
  // Copies v1 to v2 again
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
struct NonCopyable {
    NonCopyable() = default;
    NonCopyable(const NonCopyable&) = delete;
    NonCopyable(NonCopyable&&) = default;
};

Vector<NonCopyable> v;
NonCopyable obj;
v.push_back(obj);
```

**Answer:**

```cpp
Compilation error: Cannot copy
```

- Compilation error: Cannot copy ```

**Explanation:**

- **push_back(lvalue) requires copy constructor:**
- obj is lvalue (has a name)
- push_back(const T&) tries to copy-construct
- NonCopyable has deleted copy constructor

```cpp
NonCopyable obj;  // OK: Default constructor
  
  v.push_back(obj);
  // Calls: push_back(const NonCopyable& value)
  // Implementation: new (&data[sz]) NonCopyable(value);
  //                                  ^^^^^^^^^^^^^^^^^^
  //                                  Copy constructor call
  // ERROR: Copy constructor deleted!
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
Vector<int> v = {1, 2, 3};
auto it = v.begin();
v.reserve(100);
std::cout << *it;
```

**Answer:**

```cpp
Undefined behavior (iterator invalidated)
```

- Undefined behavior (iterator invalidated) ```

**Explanation:**

- **reserve(100) reallocates and invalidates iterators:**
- Current capacity = 3
- reserve(100) allocates new memory
- Moves elements to new location

```cpp
Vector<int> v = {1, 2, 3};
  // v.data → [1,2,3] at address 0x1000
  // size=3, capacity=3
  
  auto it = v.begin();
  // it points to 0x1000 (first element)
  
  v.reserve(100);
  // 1. Allocate new memory at 0x2000 (capacity 100)
  // 2. Move elements: [1,2,3] from 0x1000 to 0x2000
  // 3. Free old memory at 0x1000
  // v.data → [1,2,3,...] at 0x2000
    // ... (additional code omitted for brevity)
```

- cpp Vector<int> v = {1, 2, 3}; // v.data → [1,2,3] at address 0x1000 // size=3, capacity=3 auto it = v.begin(); // it points to 0x1000 (first element) v.reserve(100); // 1
- Allocate new memory at 0x2000 (capacity 100) // 2
- Move elements: [1,2,3] from 0x1000 to 0x2000 // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
Vector<int> createVector() {
    Vector<int> v = {1, 2, 3};
    return v;
}

Vector<int> result = createVector();
std::cout << result.size();
```

**Answer:**

```cpp
3 (RVO/NRVO eliminates copy/move)
```

- 3 (RVO/NRVO eliminates copy/move) ```

**Explanation:**

- **Return Value Optimization (RVO) / Named Return Value Optimization (NRVO):**
- Compiler optimization that elides copy/move operations
- Constructs return value directly in caller's memory
- Zero overhead for returning by value

```cpp
Vector<int> createVector() {
      Vector<int> v = {1, 2, 3};  // 1. Construct v
      return v;                    // 2. Move v to temporary
  }                                // 3. Destroy v
  
  Vector<int> result = createVector();  // 4. Move temporary to result
  // 5. Destroy temporary
  // Total: 1 construction, 2 moves, 2 destructions
```

- cpp Vector<int> createVector() { Vector<int> v = {1, 2, 3}; // 1
- Construct v return v; // 2
- Move v to temporary } // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
Vector<int> v;
v.resize(5, 10);
std::cout << v[0] << ", " << v[4];
```

**Answer:**

```cpp
10, 10 (all elements initialized to custom value)
```

- 10, 10 (all elements initialized to custom value) ```

**Explanation:**

- **resize(n, value) creates n elements initialized to value:**
- First parameter: new size
- Second parameter: value for new elements
- All new elements get this custom value

```cpp
Vector<int> v;
  // size=0, capacity=0
  
  v.resize(5, 10);
  // 1. new_size=5 > current size (0)
  // 2. Allocate capacity for at least 5 elements
  // 3. Construct 5 elements, each with value 10
  // v = {10, 10, 10, 10, 10}
  // size=5, capacity≥5
  
  std::cout << v[0] << ", " << v[4];
  // Prints: 10, 10
```

- cpp Vector<int> v; // size=0, capacity=0 v.resize(5, 10); // 1
- new_size=5 > current size (0) // 2
- Allocate capacity for at least 5 elements // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
Vector<int> v = {1, 2, 3, 4, 5};
v.shrink_to_fit();
std::cout << v.capacity();
```

**Answer:**

```cpp
5 (capacity reduced to match size)
```

- 5 (capacity reduced to match size) ```

**Explanation:**

- **shrink_to_fit() requests capacity reduction to match size:**
- Non-binding request (implementation may ignore)
- Typically reallocates to tight-fit capacity
- Frees excess memory

```cpp
Vector<int> v = {1, 2, 3, 4, 5};
  // size=5, capacity≥5 (possibly larger from growth)
  
  v.shrink_to_fit();
  // 1. Check if capacity > size
  // 2. If yes, reallocate to capacity=size (5)
  // 3. Move elements to new memory
  // 4. Free old memory
  // size=5, capacity=5 (typically)
  
  std::cout << v.capacity();
  // Prints: 5 (most implementations)
```

- cpp Vector<int> v = {1, 2, 3, 4, 5}; // size=5, capacity≥5 (possibly larger from growth) v.shrink_to_fit(); // 1
- Check if capacity > size // 2
- If yes, reallocate to capacity=size (5) // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
Vector<int> v;
try {
    v.reserve(SIZE_MAX);
} catch (const std::bad_alloc& e) {
    std::cout << "Allocation failed";
}
std::cout << v.size();
```

**Answer:**

```cpp
Allocation failed0
```

- Allocation failed0 ```

**Explanation:**

- **reserve(SIZE_MAX) throws std::bad_alloc:**
- SIZE_MAX is maximum size_t value (~18 exabytes on 64-bit)
- Allocation fails (not enough memory)
- reserve() throws std::bad_alloc

```cpp
Vector<int> v;
  // size=0, capacity=0, data=nullptr
  
  try {
      v.reserve(SIZE_MAX);
      // 1. Tries to allocate SIZE_MAX * sizeof(int) bytes
      // 2. Allocation fails (impossible to satisfy)
      // 3. ::operator new throws std::bad_alloc
      // 4. reserve() doesn't catch, propagates exception
      // Vector state unchanged!
  } catch (const std::bad_alloc& e) {
      std::cout << "Allocation failed";
    // ... (additional code omitted for brevity)
```

- cpp Vector<int> v; // size=0, capacity=0, data=nullptr try { v.reserve(SIZE_MAX); // 1
- Tries to allocate SIZE_MAX * sizeof(int) bytes // 2
- Allocation fails (impossible to satisfy) // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
Vector<int> v = {1, 2, 3};
for (auto& elem : v) {
    elem *= 2;
}
std::cout << v[1];
```

**Answer:**

```cpp
4 (elements modified via reference)
```

- 4 (elements modified via reference) ```

**Explanation:**

- **Range-for with reference allows modification:**
- `auto& elem` creates reference to each element
- Modifying `elem` modifies the vector element
- Non-const reference allows writes

```cpp
Vector<int> v = {1, 2, 3};
  
  for (auto& elem : v) {
      elem *= 2;
  }
  // Iteration 1: elem refers to v[0], elem *= 2 → v[0] = 1*2 = 2
  // Iteration 2: elem refers to v[1], elem *= 2 → v[1] = 2*2 = 4
  // Iteration 3: elem refers to v[2], elem *= 2 → v[2] = 3*2 = 6
  // v = {2, 4, 6}
  
  std::cout << v[1];
  // Prints: 4
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
Vector<int> v1 = {1, 2, 3};
Vector<int> v2 = {4, 5};
std::swap(v1, v2);
std::cout << v1.size() << ", " << v2.size();
```

**Answer:**

```cpp
2, 3 (contents swapped)
```

- 2, 3 (contents swapped) ```

**Explanation:**

- **std::swap exchanges contents of two vectors:**
- Swaps internal pointers, sizes, and capacities
- O(1) operation (constant time)
- No element copies

```cpp
Vector<int> v1 = {1, 2, 3};
  // v1: data → [1,2,3], size=3, capacity=3
  
  Vector<int> v2 = {4, 5};
  // v2: data → [4,5], size=2, capacity=2
  
  std::swap(v1, v2);
  // Swaps: v1.data ↔ v2.data
  //        v1.size ↔ v2.size
  //        v1.capacity ↔ v2.capacity
  
  // After swap:
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
