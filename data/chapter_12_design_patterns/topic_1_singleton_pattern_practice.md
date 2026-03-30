## TOPIC: Thread-Safe Singleton Pattern

### PRACTICE_TASKS: Code Analysis and Implementation Challenges

#### Q1
```cpp
class Manager {
    static Manager* instance;
    Manager() {}
public:
    static Manager* getInstance() {
        if (!instance) instance = new Manager();
        return instance;
    }
};
Manager* Manager::instance = nullptr;

// Multiple threads call getInstance() simultaneously
// What can go wrong?
```

**Answer:**
```
Race condition: multiple threads may create multiple instances
Memory leak: lost pointers to earlier allocations
```

**Explanation:**
- **Thread interleaving scenario:**
  1. Thread A: checks `if (!instance)` → true (null)
  2. Thread B: checks `if (!instance)` → true (null, before A assigns)
  3. Thread A: executes `instance = new Manager()` → creates Manager #1
  4. Thread B: executes `instance = new Manager()` → creates Manager #2
  5. **Result: Manager #1 pointer lost, memory leaked**
  6. instance now points to Manager #2 only
- **Classic check-then-act race condition (TOCTOU)**
- **Multiple instance violation:** Singleton guarantee broken
- **Memory leak:** First allocated Manager never deleted
- **Possible outcomes:**
  - Different threads see different Manager instances
  - State inconsistency across threads
  - Resource waste (multiple database connections, etc.)
- **Why this happens:** Check and assignment are NOT atomic
- **Common fix 1:** Meyers Singleton (C++11 thread-safe)

```cpp
static Manager& getInstance() {
    static Manager instance;  // Thread-safe since C++11
    return instance;
}
```
- **Common fix 2:** Double-checked locking with mutex

```cpp
static mutex mtx;
if (!instance) {
    lock_guard lock(mtx);
    if (!instance) instance = new Manager();
}
```
- **Common fix 3:** std::call_once
- **Key Concept:** Lazy Singleton initialization without synchronization causes race conditions and violates single-instance guarantee

---

#### Q2
```cpp
class Service {
public:
    static Service& getInstance() {
        static Service instance;
        return instance;
    }
    ~Service() {
        Logger::getInstance().log("Service destroyed");
    }
};

// What happens if Logger is destroyed before Service?
```

**Answer:**
```
Undefined behavior: accessing destroyed Singleton
Possible crash or corruption during static destruction phase
```

**Explanation:**
- **Static destruction order problem:**
  1. Program ends, static destruction phase begins
  2. **Destruction order of static locals is REVERSE of initialization order**
  3. If Logger::getInstance() called before Service::getInstance(), Logger destroyed AFTER Service
  4. If Service::getInstance() called first, Service destroyed first
  5. **But destruction order is NOT deterministic across compilation units**
- **Problem scenario:**
  1. Logger static local destroyed first (memory freed)
  2. Service destructor runs
  3. Calls `Logger::getInstance().log(...)`
  4. **Access to destroyed object** → undefined behavior
- **Possible outcomes:**
  - Crash (segmentation fault)
  - Corrupted memory access
  - Silent failure (appears to work but UB)
  - Double destruction
- **Why this is common:** Singletons often depend on each other
- **Common fix 1:** Phoenix Singleton (never destroyed)

```cpp
static Logger& getInstance() {
    static Logger* instance = new Logger();  // Never deleted
    return *instance;
}
```
- **Common fix 2:** Dependency injection (avoid Singleton-to-Singleton calls)
- **Common fix 3:** Document initialization order dependencies
- **Common fix 4:** Use Nifty Counter idiom for guaranteed ordering
- **Design guideline:** Avoid Singleton dependencies between Singletons
- **Real-world issue:** Logger, Config, and Database Singletons commonly hit this
- **Key Concept:** Static destruction order fiasco causes UB when Singletons reference each other in destructors; use Phoenix pattern or avoid dependencies

---

#### Q3
```cpp
class Config {
    static unique_ptr<Config> instance;
    static mutex mtx;
public:
    static Config& getInstance() {
        lock_guard<mutex> lock(mtx);
        if (!instance) instance = make_unique<Config>();
        return *instance;
    }
};

// Is this implementation efficient? What's the performance impact?
```

**Answer:**



**Explanation:**

- **Performance problem: Lock on every call**
- **Mutex overhead costs:**
- Lock/unlock system calls
- Cache invalidation
- Thread serialization (only 1 thread in getInstance() at a time)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
template<typename T>
class Singleton {
public:
    static T& getInstance() {
        static T instance;
        return instance;
    }
};

class Logger : public Singleton<Logger> {};
class Config : public Singleton<Config> {};

// How many static instances exist in this program?
```

**Answer:**
```
Two separate instances: one for Logger, one for Config
Each template instantiation has its own static instance
```

**Explanation:**
- **Template instantiation creates separate classes:**
  1. `Singleton<Logger>` is ONE complete class
  2. `Singleton<Config>` is ANOTHER complete class
  3. These are as different as `vector<int>` and `vector<double>`
- **Static member per instantiation:**
  - `Singleton<Logger>::getInstance()` has its own `static T instance` (T=Logger)
  - `Singleton<Config>::getInstance()` has its own `static T instance` (T=Config)
  - **No sharing between template instantiations**
- **Memory layout:**

```
Address 0x1000: Logger instance (inside Singleton<Logger>::getInstance())
Address 0x2000: Config instance (inside Singleton<Config>::getInstance())
```
- **How to verify:**

```cpp
Logger& l1 = Logger::getInstance();
Logger& l2 = Singleton<Logger>::getInstance();  // Same instance
Config& c = Config::getInstance();  // Different instance
```
- **CRTP pattern (Curiously Recurring Template Pattern):**
  - Each derived class uses itself as template parameter
  - Base class provides common Singleton logic
  - Each derived class gets its own Singleton instance
- **Advantages:**
  - Reduces code duplication (don't rewrite getInstance() for each Singleton)
  - Type-safe (can't accidentally access wrong Singleton)
  - Zero runtime overhead (templates resolved at compile time)
- **Common pitfall:** Thinking template static members are shared across all instantiations
- **Use case:** When you have many Singletons and want DRY (Don't Repeat Yourself) code
- **Key Concept:** Template instantiations are separate types with separate static members; CRTP Singleton base provides Singleton behavior per derived class

---

#### Q5
```cpp
class Database {
public:
    static Database& getInstance() {
        static Database instance;
        return instance;
    }

    Database(const Database&) = default;
};

// What design flaw exists in this Singleton?
```

**Answer:**



**Explanation:**

- **Singleton contract violation:**
- **How to violate Singleton:**
- **Now have 3 Database instances:** Original static + db2 copy + db3 copy
- **Why this is dangerous:**
- Database connections duplicated

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
class Service {
    static shared_ptr<Service> instance;
public:
    static shared_ptr<Service> getInstance() {
        if (!instance) instance = make_shared<Service>();
        return instance;
    }
};

// Is this thread-safe? Why or why not?
```

**Answer:**



**Explanation:**

- **Thread interleaving race:**
- **shared_ptr is NOT thread-safe for concurrent writes**
- Reading shared_ptr is safe
- Modifying same shared_ptr from multiple threads is NOT safe
- Assignment involves multiple operations (not atomic)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
```cpp
class Manager {
public:
    static Manager& getInstance() {
        static Manager* instance = nullptr;
        if (!instance) instance = new Manager();
        return *instance;
    }
};

// What happens if getInstance() is called during static destruction?
```

**Answer:**



**Explanation:**

- **Phoenix Singleton pattern:**
- **Comparison with Meyers Singleton:**
- **Why Phoenix pattern exists:**
- Other static objects might call getInstance() during their destruction
- Meyers Singleton might already be destroyed → undefined behavior

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
class Logger {
    static once_flag flag;
    static unique_ptr<Logger> instance;
public:
    static Logger& getInstance() {
        call_once(flag, []() {
            instance.reset(new Logger());
        });
        return *instance;
    }
};

// What are the advantages of std::call_once over Meyers Singleton?
```

**Answer:**

```cpp
std::call_once allows complex initialization with parameters
Better control over exception handling and initialization timing
```

- std::call_once allows complex initialization with parameters Better control over exception handling and initialization timing ```

**Explanation:**

- **Advantages of std::call_once:**
1. **Parametrized initialization:**

```cpp
static Logger& getInstance(const string& filename) {
         call_once(flag, [&](){ instance = make_unique<Logger>(filename); });
         return *instance;
     }
```

- cpp static Logger& getInstance(const string& filename) { call_once(flag, [&](){ instance = make_unique<Logger>(filename); }); return *instance; } ``` 2.

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
class Config {
    int value;
public:
    static Config& getInstance() {
        static Config instance;
        return instance;
    }

    Config() : value(readFromFile()) {}

    int readFromFile() {
        // Opens file, reads value
        return 42;
    }
};

// What if readFromFile() throws an exception?
```

**Answer:**

```cpp
Exception propagates to caller
Initialization guard resets, allowing retry on next call
Instance construction retried until success
```

- Exception propagates to caller Initialization guard resets, allowing retry on next call Instance construction retried until success ```

**Explanation:**

- **C++11 magic static exception handling:**
1. First call to getInstance()
2. Compiler sets initialization guard (flag indicating "initializing")
3. Config constructor starts

```cpp
try {
      Config& c1 = Config::getInstance();  // Throws
  } catch(...) {
      // First attempt failed
  }

  try {
      Config& c2 = Config::getInstance();  // Retries construction
  } catch(...) {
      // Second attempt
  }
```

- cpp try { Config& c1 = Config::getInstance(); // Throws } catch(...) { // First attempt failed }
- try { Config& c2 = Config::getInstance(); // Retries construction } catch(...) { // Second attempt } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
class Service {
    static Service instance;
    Service() {}
public:
    static Service& getInstance() {
        return instance;
    }
};

Service Service::instance;

// What's the problem with this approach compared to Meyers Singleton?
```

**Answer:**



**Explanation:**

- **Eager vs Lazy initialization:**
- `Service::instance` constructed during static initialization phase
- Happens BEFORE main() runs
- **Initialized whether used or not**
- Constructed on first getInstance() call

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
class Manager {
    static atomic<Manager*> instance;
public:
    static Manager* getInstance() {
        Manager* tmp = instance.load(memory_order_acquire);
        if (!tmp) {
            tmp = new Manager();
            instance.store(tmp, memory_order_release);
        }
        return tmp;
    }
};

// Is this lock-free Singleton implementation correct?
```

**Answer:**

```cpp
Not correct: TOCTOU race between load and store
Multiple Manager instances created, memory leaked
Must use compare_exchange for atomic check-and-set
```

- Not correct: TOCTOU race between load and store Multiple Manager instances created, memory leaked Must use compare_exchange for atomic check-and-set ```

**Explanation:**

- **Race condition scenario:**
1. Thread A: loads instance → null
2. Thread B: loads instance → null (before A stores)
3. Thread A: creates Manager #1, stores to instance

```cpp
static Manager* getInstance() {
      Manager* tmp = instance.load(memory_order_acquire);
      if (!tmp) {
          Manager* new_instance = new Manager();
          if (!instance.compare_exchange_strong(tmp, new_instance,
                                                 memory_order_release,
                                                 memory_order_acquire)) {
              delete new_instance;  // Lost race, cleanup
          } else {
              tmp = new_instance;   // Won race
          }
      }
      return tmp;
  }
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
class Logger {
public:
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }

    void log(const string& msg) {
        file << msg << endl;
    }

    ~Logger() {
        file.close();
    }
private:
    ofstream file;
    Logger() : file("log.txt") {}
};

// Another static object logs during its destruction - is this safe?
```

**Answer:**

```cpp
Not safe: file might be closed before other destructors run
Accessing closed file causes failures or undefined behavior
```

- Not safe: file might be closed before other destructors run Accessing closed file causes failures or undefined behavior ```

**Explanation:**

- **Static destruction order problem:**
1. Program ends, static destruction begins
2. **Logger destructor runs** (closes file)
3. Another static object destructor runs

```cpp
file << msg << endl;  // file.close() already called!
```

- cpp file << msg << endl; // file.close() already called

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
// File1.cpp
class Service {
public:
    static Service& getInstance() {
        static Service instance;
        return instance;
    }
};

// File2.cpp (in a DLL/shared library)
void libraryFunction() {
    Service::getInstance().doWork();
}

// How many Service instances exist in this scenario?
```

**Answer:**

```cpp
Potentially TWO instances: one in main executable, one in DLL
Each module has its own copy of static local variable
```

- Potentially TWO instances: one in main executable, one in DLL Each module has its own copy of static local variable ```

**Explanation:**

- **DLL/Shared library boundary issue:**
1. Main executable compiles Service::getInstance() → static instance #1
2. DLL compiles Service::getInstance() → static instance #2
3. **Each module gets its own copy of template code**

```cpp
// Windows: Two instances (default hidden visibility)
  // Linux: Two instances unless -fvisibility=default

  // With explicit export:
  class __declspec(dllexport) Service {  // Windows
  class __attribute__((visibility("default"))) Service {  // Linux
```

- cpp // Windows: Two instances (default hidden visibility) // Linux: Two instances unless -fvisibility=default
- // With explicit export: class __declspec(dllexport) Service { // Windows class __attribute__((visibility("default"))) Service { // Linux ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
class Database {
    Database() {
        if (failedToConnect()) throw runtime_error("Connection failed");
    }
public:
    static Database& getInstance() {
        static Database instance;
        return instance;
    }
};

int main() {
    try {
        Database::getInstance();
    } catch(...) {
        // Can I retry?
    }
}
```

**Answer:**

```cpp
Yes, can retry!
C++11 guarantees initialization guard resets on exception
Each call retries construction until success
```

- C++11 guarantees initialization guard resets on exception Each call retries construction until success ```

**Explanation:**

- **Exception-safe initialization (C++11):**
1. First getInstance() call
2. Database constructor starts
3. failedToConnect() returns true

```cpp
bool initialized = false;
  try {
      Database::getInstance();  // First attempt
  } catch(...) {
      initialized = false;
  }

  if (!initialized) {
      try {
          Database::getInstance();  // Second attempt (retries)
      } catch(...) {
          // Still failing
      }
  }
```

- cpp bool initialized = false; try { Database::getInstance(); // First attempt } catch(...) { initialized = false; }
- if (!initialized) { try { Database::getInstance(); // Second attempt (retries) } catch(...) { // Still failing } } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
class Manager;
extern Manager& getManager();  // Declaration

// File1.cpp
Manager& getManager() {
    static Manager instance;
    return instance;
}

// File2.cpp
Manager& mgr = getManager();  // Global initialization

// What problem can occur here?
```

**Answer:**

```cpp
Static initialization order fiasco
mgr might be initialized before Manager instance exists
Undefined behavior if mgr used before first getManager() call
```

- Static initialization order fiasco mgr might be initialized before Manager instance exists Undefined behavior if mgr used before first getManager() call ```

**Explanation:**

- **The problem: Global variable initialization**

```cpp
// File2.cpp
  Manager& mgr = getManager();  // When does this run?
```

- cpp // File2.cpp Manager& mgr = getManager(); // When does this run

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
class IService {
public:
    virtual ~IService() = default;
    virtual void execute() = 0;
};

class ServiceFactory {
    static unique_ptr<IService> instance;
public:
    static IService& getInstance() {
        if (!instance) instance = createService();
        return *instance;
    }
    static void setTestInstance(unique_ptr<IService> svc) {
        instance = move(svc);
    }
};

// How does this design improve testability?
```

**Answer:**

```cpp
Allows dependency injection of mock implementations
Breaks Singleton coupling for unit testing
Test seam for replacing production code with test doubles
```

- Allows dependency injection of mock implementations Breaks Singleton coupling for unit testing Test seam for replacing production code with test doubles ```

**Explanation:**

- **Testability problem with traditional Singleton:**

```cpp
class Database {  // Traditional Singleton
      static Database& getInstance() { static Database db; return db; }
  };

  void processData() {
      Database::getInstance().query(...);  // Hard-coded dependency!
  }

  // Testing processData() requires real Database (slow, flaky)
```

- cpp class Database { // Traditional Singleton static Database& getInstance() { static Database db; return db; } };
- void processData() { Database::getInstance().query(...); // Hard-coded dependency
- // Testing processData() requires real Database (slow, flaky) ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
class Config {
public:
    static Config& getInstance() {
        static Config instance;
        return instance;
    }

    void reload() {
        // Re-read configuration
    }
};

// Multiple threads call reload() - what synchronization is needed?
```

**Answer:**

```cpp
reload() needs mutex protection for internal state modifications
getInstance() is thread-safe (C++11), but member functions are NOT
Data race on Config member variables
```

- reload() needs mutex protection for internal state modifications getInstance() is thread-safe (C++11), but member functions are NOT Data race on Config member variables ```

**Explanation:**

- **Common misconception:**
- "getInstance() is thread-safe, so Config is thread-safe" → **FALSE!**
- getInstance() only guarantees **construction** is thread-safe
- **Member function calls are NOT synchronized**

```cpp
class Config {
      map<string, string> settings;  // Mutable state

      void reload() {
          settings.clear();  // Modifies state
          readFromFile();    // Modifies state
      }
  };

  // Thread A calls reload()
  // Thread B calls reload()
  // Both modify settings concurrently → DATA RACE
```

- cpp class Config { map<string, string> settings; // Mutable state
- void reload() { settings.clear(); // Modifies state readFromFile(); // Modifies state } };
- // Thread A calls reload() // Thread B calls reload() // Both modify settings concurrently → DATA RACE ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
class ResourcePool {
    static ResourcePool* instance;
    vector<Resource> resources;

    ResourcePool() {
        for (int i = 0; i < 100; ++i) {
            resources.emplace_back();  // Allocate 100 resources
        }
    }
public:
    static ResourcePool& getInstance() {
        static ResourcePool instance;
        return instance;
    }
};

// What are the implications of this design for startup time?
```

**Answer:**

```cpp
Lazy initialization defers 100 resource allocations until first use
Improves startup time if pool rarely used
First access pays initialization cost (amortized)
```

- Lazy initialization defers 100 resource allocations until first use Improves startup time if pool rarely used First access pays initialization cost (amortized) ```

**Explanation:**

- **Lazy vs Eager initialization timing:**
1. **Eager (static member):**

```cpp
ResourcePool ResourcePool::instance;  // Before main()
     // 100 resources allocated during static init → 500ms startup
```

- cpp ResourcePool ResourcePool::instance; // Before main() // 100 resources allocated during static init → 500ms startup ``` 2.

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
class Singleton {
protected:
    Singleton() = default;
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
};

class MyClass : public Singleton {
    MyClass() = default;
public:
    static MyClass& getInstance() {
        static MyClass instance;
        return instance;
    }
};

// Can someone still create multiple instances of MyClass?
```

**Answer:**

```cpp
Yes! Protected constructor allows derived classes to construct
Friend classes can also construct
Need private constructor for strict enforcement
```

- Protected constructor allows derived classes to construct Friend classes can also construct Need private constructor for strict enforcement ```

**Explanation:**

- **Access control problem:**

```cpp
class Singleton {
  protected:  // ← DANGER!
      Singleton() = default;
  };

  class MyClass : public Singleton {
      MyClass() = default;  // Can call protected base constructor
  public:
      static MyClass& getInstance() { ... }
  };

  // Another derived class can violate Singleton!
    // ... (additional code omitted for brevity)
```

- cpp class Singleton { protected: // ← DANGER
- Singleton() = default; };
- class MyClass : public Singleton { MyClass() = default; // Can call protected base constructor public: static MyClass& getInstance() { ..

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
class Logger {
public:
    static Logger& getInstance() {
        static Logger instance;
        return instance;
    }

    Logger& operator=(const Logger&) = delete;
    Logger(const Logger&) = delete;
    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;
};

// Is this sufficient to prevent copying and moving?
```

**Answer:**

```cpp
Sufficient if constructor is private
Without private constructor, can create multiple instances directly
Need both: delete copy/move AND private constructor
```

- Sufficient if constructor is private Without private constructor, can create multiple instances directly Need both: delete copy/move AND private constructor ```

**Explanation:**

- **What's deleted:**

```cpp
Logger(const Logger&) = delete;      // Copy constructor
  Logger& operator=(const Logger&) = delete;  // Copy assignment
  Logger(Logger&&) = delete;           // Move constructor
  Logger& operator=(Logger&&) = delete;       // Move assignment
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
