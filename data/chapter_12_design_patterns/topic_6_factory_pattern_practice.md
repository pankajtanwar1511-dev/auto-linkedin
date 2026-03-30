## TOPIC: Factory Pattern (Factory Method and Abstract Factory)

### PRACTICE_TASKS: Code Analysis and Implementation Challenges

#### Q1
```cpp
class SensorFactory {
public:
    static Sensor* createSensor(Type type) {
        if (type == Type::LIDAR) {
            return new LidarSensor();
        }
        return new RadarSensor();
    }
};

// Used in a loop that processes thousands of sensor readings
for (int i = 0; i < 10000; ++i) {
    Sensor* s = SensorFactory::createSensor(Type::LIDAR);
    process(s);
    delete s;
}

// What's the problem and how do you fix it?
```

**Answer:**

```cpp
Severe performance problem: Memory fragmentation and allocation overhead from 10,000 allocations/deallocations
```

- Severe performance problem: Memory fragmentation and allocation overhead from 10,000 allocations/deallocations ```

**Explanation:**

- **Performance issues with repeated allocation:**
- Each new/delete pair: ~100-200ns overhead (system call to allocator)
- 10,000 iterations: ~1-2ms wasted on allocation alone
- Heap fragmentation from repeated alloc/free cycles

```cpp
// After many alloc/delete cycles:
  // Heap looks like Swiss cheese
  
  Memory layout:
  [Free][Used][Free][Used][Free][Free][Used]...
         └─ Small fragments, can't satisfy large allocations
  
  // Problems:
  // 1. Larger allocations may fail even with enough total free memory
  // 2. Allocator must search for suitable blocks
  // 3. Memory overhead from bookkeeping structures
```

- cpp // After many alloc/delete cycles: // Heap looks like Swiss cheese Memory layout: [Free][Used][Free][Used][Free][Free][Used]..
- └─ Small fragments, can't satisfy large allocations // Problems: // 1
- Larger allocations may fail even with enough total free memory // 2

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
```cpp
class Factory {
public:
    static Sensor createSensor() {  // Note: returns by value
        return LidarSensor();
    }
};

Sensor s = Factory::createSensor();
s.readValue();  // What happens here?
```

**Answer:**

```cpp
Object slicing - LidarSensor sliced to Sensor, polymorphism broken
```

- Object slicing - LidarSensor sliced to Sensor, polymorphism broken ```

**Explanation:**

- **Object slicing occurs when returning derived class by value:**
- LidarSensor has more data than base Sensor
- Returning by value copies only Sensor portion
- Derived class data discarded

```cpp
class Sensor {
      int baseData;
  public:
      virtual void readValue() { std::cout << "Sensor::readValue
"; }
  };
  
  class LidarSensor : public Sensor {
      int lidarSpecificData;  // Extra data
      std::vector<Point> pointCloud;  // Extra data
  public:
      void readValue() override { std::cout << "LidarSensor::readValue
    // ... (additional code omitted for brevity)
```

- LidarSensor temporary created (full object) // 2
- Copy to Sensor: only baseData copied // 3
- lidarSpecificData, pointCloud discarded

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
class SensorFactory {
    static map<string, unique_ptr<Sensor>> cache;

public:
    static Sensor* getSensor(const string& id) {
        if (cache.find(id) == cache.end()) {
            cache[id] = make_unique<Sensor>(id);
        }
        return cache[id].get();
    }
};

// Called from multiple threads simultaneously
// Is this thread-safe?
```

**Answer:**

```cpp
Not thread-safe - multiple race conditions
```

- Not thread-safe - multiple race conditions ```

**Explanation:**

- **Race condition 1: find() check and insert are not atomic:**

```cpp
// Thread 1:
  if (cache.find(id) == cache.end()) {  // Not found
      // Context switch to Thread 2...
  
  // Thread 2:
  if (cache.find(id) == cache.end()) {  // Also not found!
      cache[id] = make_unique<Sensor>(id);  // Insert
  
  // Back to Thread 1:
      cache[id] = make_unique<Sensor>(id);  // Insert again!
      // Previous unique_ptr destroyed, sensor leaked or double-free
  }
```

- cpp // Thread 1: if (cache.find(id) == cache.end()) { // Not found // Context switch to Thread 2..
- // Thread 2: if (cache.find(id) == cache.end()) { // Also not found
- cache[id] = make_unique<Sensor>(id); // Insert // Back to Thread 1: cache[id] = make_unique<Sensor>(id); // Insert again

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
class Factory {
public:
    virtual unique_ptr<Sensor> create() = 0;
};

class LidarFactory : public Factory {
public:
    unique_ptr<Sensor> create() override {
        return make_unique<LidarSensor>();
    }
};

// How does this differ from a static factory method?
```

**Answer:**

```cpp
Virtual factory enables runtime polymorphism of factories; static factory is compile-time fixed
```

- Virtual factory enables runtime polymorphism of factories; static factory is compile-time fixed ```

**Explanation:**

- **Virtual factory (Factory Method pattern):**

```cpp
// Factory itself is polymorphic
  void processWithFactory(Factory& factory) {
      auto sensor = factory.create();  // Virtual call
      // Don't know which factory at compile-time
      sensor->readValue();
  }
  
  LidarFactory lidarFactory;
  RadarFactory radarFactory;
  
  processWithFactory(lidarFactory);  // Creates LidarSensor
  processWithFactory(radarFactory);  // Creates RadarSensor
  
  // Factory chosen at runtime!
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
template<typename T>
class Factory {
public:
    static unique_ptr<Sensor> create() {
        return make_unique<T>();
    }
};

auto sensor = Factory<LidarSensor>::create();

// What are the advantages and limitations?
```

**Answer:**

```cpp
Advantages: Type-safe, zero overhead, inlined. Limitations: Type must be known at compile-time
```

- Advantages: Type-safe, zero overhead, inlined
- Limitations: Type must be known at compile-time ```

**Explanation:**

- **Compile-time polymorphism (templates):**

```cpp
// Each instantiation creates separate function
  auto lidar = Factory<LidarSensor>::create();
  // Compiler generates: Factory_LidarSensor::create()
  
  auto radar = Factory<RadarSensor>::create();
  // Compiler generates: Factory_RadarSensor::create()
  
  // No vtable, no indirection, fully inlined
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
class SensorFactory {
public:
    static unique_ptr<Sensor> create(Type type) {
        Sensor* s = nullptr;

        switch (type) {
            case Type::LIDAR:
                s = new LidarSensor();
                break;
            case Type::RADAR:
                s = new RadarSensor();
                break;
        }

        s->initialize();  // May throw exception
        return unique_ptr<Sensor>(s);
    }
};

// What's the problem if initialize() throws?
```

**Answer:**

```cpp
Memory leak if initialize() throws before unique_ptr construction
```

- Memory leak if initialize() throws before unique_ptr construction ```

**Explanation:**

- **Exception safety problem:**

```cpp
Sensor* s = new LidarSensor();  // 1. Allocate raw pointer
  s->initialize();                 // 2. May throw!
  return unique_ptr<Sensor>(s);    // 3. Never reached if throw
  
  // If initialize() throws:
  // - Exception propagates up the stack
  // - unique_ptr never constructed
  // - Raw pointer 's' lost
  // - Memory leaked!
```

- cpp Sensor* s = new LidarSensor(); // 1
- Allocate raw pointer s->initialize(); // 2
- return unique_ptr<Sensor>(s); // 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
```cpp
class Factory {
    map<string, function<unique_ptr<Sensor>()>> registry;

public:
    void registerType(const string& name, auto creator) {
        registry[name] = creator;
    }

    unique_ptr<Sensor> create(const string& name) {
        return registry[name]();  // What if name not found?
    }
};

auto sensor = factory.create("unknown_type");
```

**Answer:**

```cpp
Undefined behavior - accessing non-existent map key creates null function, calling it crashes
```

- Undefined behavior - accessing non-existent map key creates null function, calling it crashes ```

**Explanation:**

- **operator[] behavior on map:**

```cpp
map<string, function<unique_ptr<Sensor>()>> registry;
  
  // If key exists:
  auto& func = registry["lidar"];  // Returns reference to existing function
  
  // If key DOESN'T exist:
  auto& func = registry["unknown"];  // CREATES new entry!
  // - Inserts key "unknown"
  // - Value is default-constructed: function<...>()
  // - Default-constructed std::function is EMPTY (null)
```

- // - Inserts key "unknown" // - Value is default-constructed: function<...>() // - Default-constructed std::function is EMPTY (null) ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
enum class SensorType { LIDAR, RADAR, CAMERA };

unique_ptr<Sensor> createSensor(SensorType type) {
    switch (type) {
        case SensorType::LIDAR:
            return make_unique<LidarSensor>();
        case SensorType::RADAR:
            return make_unique<RadarSensor>();
    }
}

// What compile-time safety does this provide?
```

**Answer:**

```cpp
Compiler warns if not all enum cases handled (with -Wswitch or -Wswitch-enum enabled)
```

- Compiler warns if not all enum cases handled (with -Wswitch or -Wswitch-enum enabled) ```

**Explanation:**

- **Enum exhaustiveness checking:**

```cpp
enum class SensorType { LIDAR, RADAR, CAMERA };
  
  unique_ptr<Sensor> createSensor(SensorType type) {
      switch (type) {
          case SensorType::LIDAR:
              return make_unique<LidarSensor>();
          case SensorType::RADAR:
              return make_unique<RadarSensor>();
          // MISSING: SensorType::CAMERA
      }
  }
  
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
class Factory {
    static map<Type, function<unique_ptr<Sensor>()>> registry;

public:
    static void registerType(Type type, function<unique_ptr<Sensor>()> creator) {
        registry[type] = creator;
    }

    static unique_ptr<Sensor> create(Type type) {
        return registry[type]();
    }
};

// Auto-registration with static initializer
struct AutoRegister {
    AutoRegister(Type type, function<unique_ptr<Sensor>()> creator) {
        Factory::registerType(type, creator);
    }
};

static AutoRegister regLidar(Type::LIDAR, []() { return make_unique<LidarSensor>(); });
static AutoRegister regRadar(Type::RADAR, []() { return make_unique<RadarSensor>(); });

// What are the advantages of registry-based factories?
```

**Answer:**

```cpp
Registry-based factories enable Open/Closed Principle - add new types without modifying factory code
```

- Registry-based factories enable Open/Closed Principle - add new types without modifying factory code ```

**Explanation:**

- **Registry pattern eliminates switch statements:**

```cpp
// OLD: Must modify factory for each new type (violates OCP)
  unique_ptr<Sensor> create(Type type) {
      switch (type) {
          case Type::LIDAR: return make_unique<LidarSensor>();
          case Type::RADAR: return make_unique<RadarSensor>();
          // Add CAMERA: Must edit this function!
      }
  }

  // NEW: Registry-based (Open/Closed Principle)
  static map<Type, function<unique_ptr<Sensor>()>> registry;

    // ... (additional code omitted for brevity)
```

- // NEW: Registry-based (Open/Closed Principle) static map<Type, function<unique_ptr<Sensor>()>> registry;
- unique_ptr<Sensor> create(Type type) { return registry.at(type)(); // No modification needed
- // Add CAMERA: Just register it, no factory changes Factory::registerType(Type::CAMERA, []() { return make_unique<CameraSensor>(); }); ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
class SensorFactory {
public:
    static unique_ptr<Sensor> create(int type) {  // int instead of enum
        if (type == 1) return make_unique<LidarSensor>();
        if (type == 2) return make_unique<RadarSensor>();
        return nullptr;  // Invalid type
    }
};

auto sensor = SensorFactory::create(5);  // Typo or invalid

// What's wrong with this design?
```

**Answer:**

```cpp
No type safety - magic numbers allow invalid values, returning nullptr is error-prone
```

- No type safety - magic numbers allow invalid values, returning nullptr is error-prone ```

**Explanation:**

- **Magic numbers problem:**

```cpp
// BAD: Using int for sensor type
  auto sensor1 = SensorFactory::create(1);  // What is 1? LIDAR? RADAR?
  auto sensor2 = SensorFactory::create(2);  // What is 2?
  auto sensor3 = SensorFactory::create(5);  // Typo! Returns nullptr
  auto sensor4 = SensorFactory::create(-1);  // Invalid! Returns nullptr
  auto sensor5 = SensorFactory::create(99999);  // Also invalid!
  
  // No compile-time checking
  // No auto-completion in IDE
  // No documentation of valid values
```

- cpp // BAD: Using int for sensor type auto sensor1 = SensorFactory::create(1); // What is 1
- auto sensor2 = SensorFactory::create(2); // What is 2
- auto sensor3 = SensorFactory::create(5); // Typo

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
class Factory {
    template<typename T>
    static unique_ptr<Sensor> createHelper() {
        return make_unique<T>();
    }

public:
    static unique_ptr<Sensor> create(Type type) {
        static const map<Type, function<unique_ptr<Sensor>()>> creators = {
            {Type::LIDAR, createHelper<LidarSensor>},
            {Type::RADAR, createHelper<RadarSensor>},
            {Type::CAMERA, createHelper<CameraSensor>}
        };
        return creators.at(type)();
    }
};

// What's the advantage of static const map over regular static map?
```

**Answer:**

```cpp
Static const map is initialized once and immutable, avoiding repeated initialization overhead and preventing accidental modification
```

- Static const map is initialized once and immutable, avoiding repeated initialization overhead and preventing accidental modification ```

**Explanation:**

- **Initialization overhead comparison:**

```cpp
// NON-CONST: Map initialized every function call!
  static unique_ptr<Sensor> create(Type type) {
      static map<Type, function<unique_ptr<Sensor>()>> creators = {
          {Type::LIDAR, createHelper<LidarSensor>},
          {Type::RADAR, createHelper<RadarSensor>}
      };
      // Problem: Checking if already initialized adds overhead
      return creators.at(type)();
  }

  // CONST: Initialized once, truly immutable
  static unique_ptr<Sensor> create(Type type) {
    // ... (additional code omitted for brevity)
```

- cpp // NON-CONST: Map initialized every function call

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
class SensorFactory {
    static once_flag initFlag;
    static unique_ptr<HardwareInterface> hardware;

public:
    static unique_ptr<Sensor> create(Type type) {
        call_once(initFlag, []() {
            hardware = make_unique<HardwareInterface>();
            hardware->initialize();
        });

        return make_unique<Sensor>(hardware.get(), type);
    }
};

// What is the purpose of std::call_once here?
```

**Answer:**

```cpp
Ensures hardware interface is initialized exactly once in thread-safe manner (lazy initialization)
```

- Ensures hardware interface is initialized exactly once in thread-safe manner (lazy initialization) ```

**Explanation:**

- **Lazy initialization problem:**

```cpp
// PROBLEM: Initialize hardware on first use
  static unique_ptr<HardwareInterface> hardware;
  
  static unique_ptr<Sensor> create(Type type) {
      if (!hardware) {
          hardware = make_unique<HardwareInterface>();  // RACE CONDITION!
          hardware->initialize();
      }
      return make_unique<Sensor>(hardware.get(), type);
  }
  
  // Thread 1:                    // Thread 2:
    // ... (additional code omitted for brevity)
```

- } // First initialization leaks, second overwrites ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
class SensorFactory {
    static unique_ptr<Sensor> create(Type type, const json& config) {
        unique_ptr<Sensor> sensor;

        switch (type) {
            case Type::LIDAR:
                sensor = make_unique<LidarSensor>();
                break;
            case Type::RADAR:
                sensor = make_unique<RadarSensor>();
                break;
        }

        sensor->configure(config);  // What if sensor is nullptr?
        return sensor;
    }
};
```

**Answer:**

```cpp
Undefined behavior if type doesn't match any case - sensor stays nullptr, dereferencing crashes
```

- Undefined behavior if type doesn't match any case - sensor stays nullptr, dereferencing crashes ```

**Explanation:**

- **Missing default case problem:**

```cpp
unique_ptr<Sensor> sensor;  // Initialized to nullptr

  switch (type) {
      case Type::LIDAR:
          sensor = make_unique<LidarSensor>();
          break;
      case Type::RADAR:
          sensor = make_unique<RadarSensor>();
          break;
      // NO DEFAULT CASE!
  }

    // ... (additional code omitted for brevity)
```

- cpp unique_ptr<Sensor> sensor; // Initialized to nullptr
- // If type == Type::CAMERA (not handled): // - switch completes without executing any case // - sensor remains nullptr // - next line dereferences nullptr
- sensor->configure(config); // CRASH

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
class Factory {
public:
    template<typename T, typename... Args>
    static unique_ptr<Sensor> create(Args&&... args) {
        return make_unique<T>(std::forward<Args>(args)...);
    }
};

auto sensor = Factory::create<LidarSensor>("ID-001", 100, 200.0);

// What is std::forward doing here?
```

**Answer:**

```cpp
Perfect forwarding - preserves lvalue/rvalue-ness of arguments to avoid unnecessary copies
```

- Perfect forwarding - preserves lvalue/rvalue-ness of arguments to avoid unnecessary copies ```

**Explanation:**

- **Problem without perfect forwarding:**

```cpp
// BAD: Always takes by value (copies)
  template<typename T, typename... Args>
  static unique_ptr<Sensor> create(Args... args) {
      return make_unique<T>(args...);
  }
  
  string id = "sensor-001";
  auto sensor = Factory::create<LidarSensor>(id, 100);
  // id copied to args, then copied again to constructor
  // Total: 2 copies
  
  // BAD: Always takes by reference (can't accept rvalues efficiently)
    // ... (additional code omitted for brevity)
```

- cpp // BAD: Always takes by value (copies) template<typename T, typename..
- Args> static unique_ptr<Sensor> create(Args..
- Args> static unique_ptr<Sensor> create(Args&..

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
class AbstractFactory {
public:
    virtual unique_ptr<Sensor> createSensor() = 0;
    virtual unique_ptr<Display> createDisplay() = 0;
    virtual unique_ptr<Logger> createLogger() = 0;
};

class ProductionFactory : public AbstractFactory {
public:
    unique_ptr<Sensor> createSensor() override {
        return make_unique<HardwareSensor>();
    }
    unique_ptr<Display> createDisplay() override {
        return make_unique<HardwareDisplay>();
    }
    unique_ptr<Logger> createLogger() override {
        return make_unique<FileLogger>();
    }
};

class TestFactory : public AbstractFactory {
public:
    unique_ptr<Sensor> createSensor() override {
        return make_unique<MockSensor>();
    }
    unique_ptr<Display> createDisplay() override {
        return make_unique<MockDisplay>();
    }
    unique_ptr<Logger> createLogger() override {
        return make_unique<ConsoleLogger>();
    }
};

// When would you use Abstract Factory over simple Factory Method?
```

**Answer:**

```cpp
Abstract Factory creates families of related objects ensuring consistency; Factory Method creates single objects
```

- Abstract Factory creates families of related objects ensuring consistency; Factory Method creates single objects ```

**Explanation:**

- **Problem: Inconsistent object families:**

```cpp
// WITHOUT Abstract Factory: Can mix incompatible objects
  auto sensor = SensorFactory::create(Type::HARDWARE);
  auto display = DisplayFactory::create(Type::MOCK);  // Inconsistent!
  auto logger = LoggerFactory::create(Type::FILE);

  // Problem: Hardware sensor + Mock display
  // They may not be compatible:
  sensor->getData(display);  // Display expects mock format, but gets hardware data
  // Runtime errors, data corruption, crashes
```

- cpp // WITHOUT Abstract Factory: Can mix incompatible objects auto sensor = SensorFactory::create(Type::HARDWARE); auto display = DisplayFactory::create(Type::MOCK); // Inconsistent
- auto logger = LoggerFactory::create(Type::FILE);

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
class SensorFactory {
public:
    static unique_ptr<Sensor> create(Type type) {
        switch (type) {
            case Type::LIDAR:
                return make_unique<LidarSensor>();
            case Type::RADAR:
                return make_unique<RadarSensor>();
            case Type::CAMERA:
                return make_unique<CameraSensor>();
        }
    }
};

// What happens when you add a new sensor type?
```

**Answer:**

```cpp
Must modify factory code to add new case - violates Open/Closed Principle
```

- Must modify factory code to add new case - violates Open/Closed Principle ```

**Explanation:**

- **Open/Closed Principle (OCP) violation:**

```cpp
// PROBLEM: Adding new sensor type requires modifying factory

  // Original factory:
  switch (type) {
      case Type::LIDAR: return make_unique<LidarSensor>();
      case Type::RADAR: return make_unique<RadarSensor>();
      case Type::CAMERA: return make_unique<CameraSensor>();
  }

  // Need to add SONAR sensor:
  // 1. Modify enum
  enum class Type { LIDAR, RADAR, CAMERA, SONAR };  // CHANGE
    // ... (additional code omitted for brevity)
```

- cpp // PROBLEM: Adding new sensor type requires modifying factory
- // Need to add SONAR sensor: // 1
- Modify enum enum class Type { LIDAR, RADAR, CAMERA, SONAR }; // CHANGE

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
class Factory {
public:
    optional<unique_ptr<Sensor>> create(Type type) {
        if (type == Type::INVALID) {
            return nullopt;  // Error: invalid type
        }
        return make_unique<Sensor>(type);
    }
};

auto result = factory.create(type);
if (result) {
    auto sensor = std::move(*result);
    // use sensor
}

// Why use optional instead of exceptions?
```

**Answer:**

```cpp
optional avoids exception overhead and makes failure explicit in return type
```

- optional avoids exception overhead and makes failure explicit in return type ```

**Explanation:**

- **Exception overhead:**

```cpp
// Exceptions are expensive when thrown:
  // - Stack unwinding
  // - Destructor calls
  // - Exception object construction/copy
  // - ~1000-10000 CPU cycles per throw

  // Exception-based:
  unique_ptr<Sensor> create(Type type) {
      if (type == Type::INVALID) {
          throw std::invalid_argument("Invalid type");  // Expensive!
      }
      return make_unique<Sensor>(type);
    // ... (additional code omitted for brevity)
```

- cpp // Exceptions are expensive when thrown: // - Stack unwinding // - Destructor calls // - Exception object construction/copy // - ~1000-10000 CPU cycles per throw
- // Exception-based: unique_ptr<Sensor> create(Type type) { if (type == Type::INVALID) { throw std::invalid_argument("Invalid type"); // Expensive
- } return make_unique<Sensor>(type); }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
class SensorFactory {
    static atomic<int> instanceCount;

public:
    static unique_ptr<Sensor> create(Type type) {
        instanceCount++;
        auto sensor = make_unique<Sensor>(type);
        sensor->setID(instanceCount);
        return sensor;
    }
};

// Called from multiple threads - is this safe?
```

**Answer:**

```cpp
Mostly safe, but instanceCount++ and setID() are not atomic as a unit
```

- Mostly safe, but instanceCount++ and setID() are not atomic as a unit ```

**Explanation:**

- **Race condition: increment and use are separate:**

```cpp
// Thread 1:                          // Thread 2:
  instanceCount++;  // ID = 1           instanceCount++;  // ID = 2
  auto sensor = make_unique<Sensor>();
  sensor->setID(instanceCount);        auto sensor = make_unique<Sensor>();
  // sensor ID = ???                     sensor->setID(instanceCount);
                                         // sensor ID = ???

  // Possible outcomes:
  // Scenario 1:
  // T1: instanceCount++ (1)
  // T1: setID(1)  ✅
  // T2: instanceCount++ (2)
    // ... (additional code omitted for brevity)
```

- sensor->setID(instanceCount); // sensor ID = ??
- // Possible outcomes: // Scenario 1: // T1: instanceCount++ (1) // T1: setID(1) ✅ // T2: instanceCount++ (2) // T2: setID(2) ✅
- // Scenario 2: // T1: instanceCount++ (1) // T2: instanceCount++ (2) ← interleaved

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
class Factory {
    static shared_ptr<Sensor> cached;

public:
    static shared_ptr<Sensor> getInstance() {
        if (!cached) {
            cached = make_shared<Sensor>();
        }
        return cached;
    }
};

// Is this a Factory pattern or Singleton pattern?
```

**Answer:**

```cpp
Hybrid - Factory-like interface but Singleton-like behavior (single cached instance)
```

- Hybrid - Factory-like interface but Singleton-like behavior (single cached instance) ```

**Explanation:**

- **Singleton pattern characteristics:**

```cpp
// True Singleton:
  class Singleton {
      static unique_ptr<Singleton> instance;

      Singleton() = default;  // Private constructor

  public:
      static Singleton& getInstance() {
          if (!instance) {
              instance = make_unique<Singleton>();
          }
          return *instance;
    // ... (additional code omitted for brevity)
```

- cpp // True Singleton: class Singleton { static unique_ptr<Singleton> instance;
- Singleton() = default; // Private constructor
- public: static Singleton& getInstance() { if (!instance) { instance = make_unique<Singleton>(); } return *instance; }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
class Factory {
public:
    static unique_ptr<Sensor> create(const string& config) {
        json j = json::parse(config);
        Type type = j["type"];
        int rate = j["sampleRate"];

        auto sensor = make_unique<Sensor>(type);
        sensor->setSampleRate(rate);
        return sensor;
    }
};

// What happens if JSON parsing fails or fields are missing?
```

**Answer:**

```cpp
Exception thrown - need error handling and validation
```

- Exception thrown - need error handling and validation ```

**Explanation:**

- **Multiple exception points:**

```cpp
static unique_ptr<Sensor> create(const string& config) {
      json j = json::parse(config);  // May throw json::parse_error
      Type type = j["type"];  // May throw json::type_error or out_of_range
      int rate = j["sampleRate"];  // May throw json::type_error or out_of_range

      auto sensor = make_unique<Sensor>(type);  // May throw bad_alloc
      sensor->setSampleRate(rate);  // May throw if rate invalid
      return sensor;
  }

  // Possible exceptions:
  // 1. json::parse_error - invalid JSON syntax
    // ... (additional code omitted for brevity)
```

- auto sensor = make_unique<Sensor>(type); // May throw bad_alloc sensor->setSampleRate(rate); // May throw if rate invalid return sensor; }
- // Possible exceptions: // 1
- json::parse_error - invalid JSON syntax // 2

**Note:** Full detailed explanation with additional examples available in source materials.

---
