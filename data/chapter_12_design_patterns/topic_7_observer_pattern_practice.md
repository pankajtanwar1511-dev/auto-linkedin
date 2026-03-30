## TOPIC: Observer Pattern (Publish-Subscribe)

### PRACTICE_TASKS: Code Analysis and Implementation Challenges

#### Q1
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void attach(Observer* obs) {
        observers.push_back(obs);
    }

    void notify() {
        for (auto* obs : observers) {
            obs->update();  // Observer deletes itself here
        }
    }
};

class SelfDestructingObserver : public Observer {
    Subject* subject;
public:
    void update() override {
        subject->detach(this);
        delete this;  // ❌ Deletes itself
    }
};

// What's the problem?
```

**Problem: Use-After-Free During Notification Loop**

When an observer deletes itself during the notification loop, the iterator continues but the pointer becomes dangling, causing undefined behavior.

**Detailed Analysis:**
**Memory State Before `delete this`:**
```cpp
Heap:
┌─────────────────────────────────┐
│ SelfDestructingObserver object  │ ← Valid memory
│ - vtable ptr                    │
│ - subject ptr                   │
└─────────────────────────────────┘
        ↑
        │
observers[i] = 0x1000  (points here)
```
**After `delete this` Executes:**
```cpp
Heap:
┌─────────────────────────────────┐
│ ??????? FREED MEMORY ????????   │ ← Undefined
│ ??????? FREED MEMORY ????????   │
└─────────────────────────────────┘
        ↑
        │
observers[i] = 0x1000  (DANGLING!)
```
- Heap: ┌─────────────────────────────────┐ │ ??????
- │ ← Undefined │ ??????
- │ └─────────────────────────────────┘ ↑ │ observers[i] = 0x1000 (DANGLING!) ```
**Why This is Dangerous:**
- Segmentation fault (if memory unmapped)
- Corruption (if memory reused)
- Appears to work (worst case - latent bug)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void attach(Observer* obs) {
        observers.push_back(obs);
        observers.push_back(obs);  // ❌ Duplicate attachment
    }
};

// What happens during notify() with duplicate observers?
```

**Problem: Observer Receives Multiple Notifications**

Duplicate attachments cause the same observer to be notified multiple times per event, leading to redundant processing and incorrect behavior.

**Why This is Problematic:**

1. **Redundant Work:** Observer processes same event multiple times

```cpp
subject.attach(&logger);
   subject.attach(&logger);  // Duplicate

   subject.notify();
   // Output:
   // "Event logged"  (first notification)
   // "Event logged"  (second notification - redundant!)
```

- cpp subject.attach(&logger); subject.attach(&logger); // Duplicate
- subject.notify(); // Output: // "Event logged" (first notification) // "Event logged" (second notification - redundant!) ```

**Performance Comparison:**



**Real-World Example:**

```cpp
// GUI button with duplicate listeners
Button button;
button.onClick(saveAction);
button.onClick(saveAction);  // Accidentally added twice

// User clicks button:
// → saveAction() called twice
// → File saved twice
// → Corrupted data! ❌
```

- cpp // GUI button with duplicate listeners Button button; button.onClick(saveAction); button.onClick(saveAction); // Accidentally added twice
- // User clicks button: // → saveAction() called twice // → File saved twice // → Corrupted data

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
class Subject {
    vector<weak_ptr<Observer>> observers;
public:
    void notify() {
        for (auto& wp : observers) {
            if (auto obs = wp.lock()) {
                obs->update();
            }
        }
    }
};

// Two threads call notify() simultaneously - is this thread-safe?
```

**Problem: Data Race on Vector During Concurrent Notification**

Multiple threads calling `notify()` simultaneously causes data races because vector iteration is not thread-safe. Additionally, concurrent `attach()`/`detach()` operations can cause iterator invalidation.

**Detailed Analysis:**
**Race Condition #1: Concurrent Vector Iteration**
```cpp
// Thread 1 executes:
for (auto& wp : observers) {  // Reads vector internals
    if (auto obs = wp.lock()) {
        obs->update();
    }
}
// Thread 2 executes simultaneously:
for (auto& wp : observers) {  // Reads same vector internals
    if (auto obs = wp.lock()) {
        obs->update();
    }
}
```
- cpp // Thread 1 executes: for (auto& wp : observers) { // Reads vector internals if (auto obs = wp.lock()) { obs->update(); } }
- // Thread 2 executes simultaneously: for (auto& wp : observers) { // Reads same vector internals if (auto obs = wp.lock()) { obs->update(); } } ```
**Why This is Unsafe (Even for Reads):**
While reading the vector itself is technically safe if no writes occur, **the problem is with concurrent `attach()` or `detach()` operations:**
```cpp
// Thread 1:
subject.notify();  // Iterating observers
// Thread 2 (simultaneously):
subject.attach(newObserver);  // Modifies observers vector → REALLOCATION!
// Result: Thread 1's iterator invalidated → CRASH
```
- cpp // Thread 1: subject.notify(); // Iterating observers
- // Thread 2 (simultaneously): subject.attach(newObserver); // Modifies observers vector → REALLOCATION
- // Result: Thread 1's iterator invalidated → CRASH ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4
```cpp
class Observer {
    Subject* subject;
public:
    ~Observer() {
        // ❌ Forgot to detach
    }
};

// Subject holds raw Observer* pointers
// What happens when Observer is destroyed?
```

**Problem: Dangling Pointers After Observer Destruction**

When observer is destroyed without detaching, subject's vector still holds pointer to freed memory. Next notify() causes undefined behavior.

**Execution Flow:**

```cpp
Subject subject;
{
    Observer obs(&subject);
    subject.attach(&obs);

    // observers = [&obs (valid pointer)]
}  // obs destroyed here

// observers = [0x1234 (DANGLING - points to freed memory)]

subject.notify();
// for (auto* obs : observers) {
//     obs->update();  // ❌ Dereferences freed memory
// }
```

- cpp Subject subject; { Observer obs(&subject); subject.attach(&obs);
- // observers = [&obs (valid pointer)] } // obs destroyed here
- // observers = [0x1234 (DANGLING - points to freed memory)]

**Why This Causes Crashes:**

1. **Use-After-Free:** Pointer valid but memory freed → segfault or corruption
2. **Memory Reuse:** OS might reallocate freed memory, causing bizarre behavior
3. **Latent Bugs:** Might "work" temporarily if memory not reused yet (worst case)
**Fix #1: Manual Detach in Destructor**

```cpp
class Observer {
    Subject* subject;
public:
    Observer(Subject* s) : subject(s) {
        subject->attach(this);
    }

    ~Observer() {
        subject->detach(this);  // ✅ Clean detachment
    }
};
```

- cpp class Observer { Subject* subject; public: Observer(Subject* s) : subject(s) { subject->attach(this); }
- ~Observer() { subject->detach(this); // ✅ Clean detachment } }; ```

**Best Practice:**



**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void notify() {
        for (auto* obs : observers) {
            obs->update();  // What if this throws?
        }
    }
};

class ThrowingObserver : public Observer {
    void update() override {
        throw runtime_error("Failed!");
    }
};

// What happens to remaining observers?
```

**Problem: Exception Aborts Notification Loop**

When an observer's `update()` throws an exception, the exception propagates out of `notify()`, terminating the loop and preventing subsequent observers from receiving notifications.

**Detailed Analysis:**
**Execution Flow with Exception:**
```cpp
observers = [ObserverA, ThrowingObserver, ObserverB, ObserverC]
notify() called:
  for (auto* obs : observers) {  // Loop begins
      obs->update();
  }
Iteration 0: ObserverA->update()  ✅ Completes successfully
Iteration 1: ThrowingObserver->update()
  → throw runtime_error("Failed!")  ❌ EXCEPTION THROWN
  → Loop exits immediately
  → notify() returns via exception propagation
    // ... (additional code omitted for brevity)
```
- observers = [ObserverA, ThrowingObserver, ObserverB, ObserverC]
- notify() called: for (auto* obs : observers) { // Loop begins obs->update(); }
- Iteration 2: ObserverB->update() ❌ NEVER CALLED Iteration 3: ObserverC->update() ❌ NEVER CALLED
**Why This is Problematic:**
1. **Lost Notifications:** Critical observers (e.g., logging, monitoring) never execute
2. **State Inconsistency:** System state partially updated (only first N observers processed)
3. **Unpredictable Behavior:** Which observers execute depends on observer order
4. **Cascading Failures:** If first observer fails, ALL subsequent observers fail
```cpp
class SensorSubject {
    vector<Observer*> observers;  // [Validator, Processor, Logger, Alerter]
public:

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void notify(const string& message) {
        for (auto* obs : observers) {
            obs->update(message);  // ❌ Pass by value - copies string
        }
    }
};

// What's the performance issue with passing by value?
```

**Problem: Unnecessary String Copies**

Passing `message` by value creates a copy for each observer notification, wasting memory and CPU for large strings or frequent notifications.

**Cost Analysis:**

```cpp
string largeMessage(1'000'000, 'x');  // 1MB string

subject.notify(largeMessage);
// With 10 observers:
// - 10 string copies = 10 MB allocated
// - 10 allocations + 10 deallocations
// - ~1000x slower than passing by reference
```

**Benchmark:**

| Pass Type | 10 observers | 100 observers | 1000 observers |
|-----------|-------------|---------------|----------------|
| By value | 150 µs | 1.5 ms | 15 ms |
| By const ref | 1 µs | 1 µs | 1 µs |

**Fix: Pass by const Reference**

```cpp
void notify(const string& message) {  // ✅ No copies
    for (auto* obs : observers) {
        obs->update(message);
    }
}
```

**When to Use Each:**

- **const reference:** Default choice (zero copy, safe)
- **By value:** Only if observers need their own copy and might modify it
- **Move semantics:** If transferring ownership (uncommon for notifications)

**Key Takeaway:** Always pass large objects by const reference to avoid unnecessary copies, especially in loops.

---

---

---

---

---

#### Q7
```cpp
class Subject {
    vector<weak_ptr<Observer>> observers;
public:
    void attach(shared_ptr<Observer> obs) {
        observers.push_back(obs);
    }

    void notify() {
        for (auto& wp : observers) {
            if (auto obs = wp.lock()) {
                obs->update();
            }
        }
    }
};

// Does this automatically clean up expired observers?
```

**Answer:**
**Explanation:**
**Why Expired weak_ptrs Accumulate:**
```cpp
// Initially:
observers = []
// Attach 3 observers:
{
    auto obs1 = make_shared<Observer>();
    auto obs2 = make_shared<Observer>();
    auto obs3 = make_shared<Observer>();
    subject.attach(obs1);
    subject.attach(obs2);
    subject.attach(obs3);
    // ... (additional code omitted for brevity)
```
- cpp // Initially: observers = []
- // Attach 3 observers: { auto obs1 = make_shared<Observer>(); auto obs2 = make_shared<Observer>(); auto obs3 = make_shared<Observer>();
- subject.attach(obs1); subject.attach(obs2); subject.attach(obs3);
**Memory Growth Over Time:**
```cpp
// Simulation: attach 1000 observers, let them expire
for (int i = 0; i < 1000; ++i) {
    auto obs = make_shared<Observer>();
    subject.attach(obs);
}  // All observers destroyed immediately
cout << "observers.size() = " << observers.size() << "
";
// Output: 1000 (all expired!)
// Memory usage:

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void detach(Observer* obs) {
        auto it = find(observers.begin(), observers.end(), obs);
        if (it != observers.end()) {
            observers.erase(it);  // ❌ What if called during notify()?
        }
    }
};

// What happens if observer calls detach(this) during its update()?
```

**Problem: Iterator Invalidation During Notification Loop**

Modifying vector during iteration invalidates iterators, causing undefined behavior when loop continues.

**Execution Flow:**

```cpp
void notify() {
    for (auto* obs : observers) {  // Range-based loop → uses iterators
        obs->update();
        // If update() calls detach(this):
        // → observers.erase() invalidates loop iterator
        // → Continuing loop → undefined behavior
    }
}
```

**Concrete Failure Scenario:**

```cpp
observers = [obs1, obs2, obs3, obs4]
            ↑ iterator here

obs2->update() calls detach(obs2):
1. erase() removes obs2
2. Vector shifts: [obs1, obs3, obs4]
3. Iterator still points to old position
4. Next iteration: skips obs3 or accesses invalid memory
```

- observers = [obs1, obs2, obs3, obs4] ↑ iterator here
- obs2->update() calls detach(obs2): 1
- erase() removes obs2 2

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
class Subject {
    struct Entry {
        Observer* observer;
        int priority;
    };
    vector<Entry> observers;

public:
    void attach(Observer* obs, int priority) {
        observers.push_back({obs, priority});
        sort(observers.begin(), observers.end(), [](auto& a, auto& b) {
            return a.priority > b.priority;  // Higher first
        });
    }
};

// What does this implement?
```

**Answer:** Priority-based notification order - high priority observers notified first.

**Explanation:**

This implements a priority queue for observers, ensuring that observers with higher priority values are notified before those with lower priorities. This is useful when certain observers have dependencies or time-sensitive operations.

**Use Cases:**

1. **Validators Before Processors:** Validators (priority 100) run before data processors (priority 50), ensuring invalid data is rejected before expensive processing

2. **Critical Systems Before Logging:** Safety-critical observers (priority 90) execute before logging observers (priority 10), ensuring critical actions happen even if logging fails

3. **UI Updates Before Network:** UI observers (priority 80) notified before network sync observers (priority 40), ensuring responsive user experience

**Performance Consideration:** Sorting on every attach is O(n log n), inefficient for frequent attaches. Better to use `std::priority_queue` or sort once before notify.

**Key Takeaway:** Priority-based notification ensures execution order when observers have dependencies.

---

---

#### Q10
```cpp
class StockMarket : public Subject {
    double price;
public:
    void setPrice(double p) {
        price = p;
        notify();  // Notify on every change
    }
};

// Frequent price updates: 1000 updates/sec
// 100 observers
// What's the performance issue?
```

**Problem: Notification Storm with High-Frequency Updates**

Notifying on every update causes 1000 notifications/sec × 100 observers = 100,000 calls/sec, overwhelming system with redundant work.

**Performance Impact:**

```cpp
// Benchmark: 1000 price updates in 1 second
for (int i = 0; i < 1000; ++i) {
    subject.setPrice(100.0 + i * 0.01);  // Tiny changes
    // → 100 observers notified each time
    // → 100,000 total notifications
    // → CPU: 80% spent in notification overhead
}
```

**Performance Comparison:**



**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
class Subject {
    mutex mtx;
    vector<Observer*> observers;
public:
    void notify() {
        lock_guard lock(mtx);
        for (auto* obs : observers) {
            obs->update();  // ❌ Holding lock during callback
        }
    }
};

class Observer {
    Subject* subject;
public:
    void update() override {
        subject->attach(new AnotherObserver());  // ❌ Tries to acquire mtx
    }
};

// What problem occurs here?
```

**Problem: Deadlock from Reentrancy**

Subject holds mutex during `notify()` → calls `observer->update()` → observer tries to call `attach()` → `attach()` tries to acquire same mutex → **deadlock** (same thread can't acquire non-recursive mutex twice).

**Execution Flow:**

```cpp
Thread 1:
1. notify() acquires mtx (lock_guard)
2. Calls obs->update() (still holding mtx)
3. update() calls subject->attach(...)
4. attach() tries to acquire mtx
5. ❌ DEADLOCK - same thread waiting for itself
```

- notify() acquires mtx (lock_guard) 2
- Calls obs->update() (still holding mtx) 3
- update() calls subject->attach(...) 4

**Why This Happens:**

Standard `mutex` is non-recursive - same thread cannot lock it twice. Observer callback trying to modify subject creates a circular lock dependency.
**Fix #1: Release Lock Before Callbacks**

```cpp
void notify() {
    vector<Observer*> observersCopy;
    {
        lock_guard lock(mtx);
        observersCopy = observers;  // Copy under lock
    }  // Lock released

    // Notify without holding lock
    for (auto* obs : observersCopy) {
        obs->update();  // Safe: observers can attach/detach
    }
}
```

- cpp void notify() { vector<Observer*> observersCopy; { lock_guard lock(mtx); observersCopy = observers; // Copy under lock } // Lock released
- // Notify without holding lock for (auto* obs : observersCopy) { obs->update(); // Safe: observers can attach/detach } } ```

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
class AsyncSubject {
    queue<Event> eventQueue;
    thread workerThread;

public:
    void publish(Event event) {
        eventQueue.push(event);  // Queue event
    }

    void processEvents() {
        while (true) {
            if (!eventQueue.empty()) {
                Event e = eventQueue.front();
                eventQueue.pop();
                notify(e);
            }
        }
    }
};

// What are the benefits of asynchronous notification?
```

**Benefits: Non-Blocking Publish and Decoupled Processing**

Asynchronous notification separates event production (publish) from consumption (observer processing), improving responsiveness and throughput.

**Key Benefits:**

1. **Non-Blocking Publish:** Caller returns immediately without waiting for observers
   ```cpp
   subject.publish(event);  // Returns instantly
   // Event processed later by background thread
   ```

2. **Decoupled Timing:** Observer processing doesn't block event producer
   ```cpp
   // Slow observer (1 second to process):
   class SlowObserver {
       void update() { sleep(1s); }
   };

   // Without async: publish() blocks for 1 second
   // With async: publish() returns immediately, processing happens in background
   ```

3. **Load Smoothing:** Bursts of events queued and processed at steady rate
   ```cpp
   // 1000 events in 1 second:
   for (int i = 0; i < 1000; ++i) {
       subject.publish(event);  // Fast: just queue
   }
   // Worker processes at manageable rate (e.g., 100/sec)
   ```

4. **Thread Safety:** Single worker thread eliminates race conditions from concurrent processing

**Trade-offs:**

- ✅ **Pros:** Responsiveness, throughput, load isolation
- ❌ **Cons:** Complexity (threading, queues), latency (events processed later), requires synchronization

**Use Cases:**

- GUI event handling (keep UI responsive)
- High-frequency sensor data (batch processing)
- Logging systems (async writes)
- Network event dispatching

**Key Takeaway:** Async notification improves responsiveness by decoupling event generation from processing, at cost of added complexity and latency.

---

---

---

---

---

---

---

#### Q13
```cpp
class Observer {
public:
    virtual void update(const SensorData& data) = 0;
    virtual bool interestedIn(SensorType type) const = 0;
};

class Subject {
public:
    void notify(const SensorData& data) {
        for (auto& obs : observers) {
            if (obs->interestedIn(data.type)) {
                obs->update(data);
            }
        }
    }
};

// What optimization does interestedIn() provide?
```

**Optimization: Selective Notification via Event Filtering**

The `interestedIn()` method filters notifications, ensuring observers only receive events they care about, reducing unnecessary processing.

**How It Works:**

- void update(const SensorData& data) override { // Only called for temperature events } };

**Performance Benefit:**

- Alternative: Topic-Based Subscriptions
- // Even faster: no iteration over uninterested observers ```

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void notify() {
        for (size_t i = 0; i < observers.size(); ++i) {
            observers[i]->update();

            // ❌ Observer might remove itself, invalidating indices
        }
    }
};

// What's wrong with this notification approach?
```

**Problem: Index Skipping When Observer Removes Itself**

If observer at index `i` removes itself, all subsequent elements shift down. Loop increments `i`, skipping the element that moved into position `i`.

**Execution Flow:**

```cpp
observers = [obs0, obs1, obs2, obs3]

i=0: obs0->update()  ✅
i=1: obs1->update() → calls detach(obs1)
     → observers becomes [obs0, obs2, obs3]
     → obs2 shifts to index 1
i=2: observers[2]->update() → accesses obs3
     ❌ SKIPPED obs2!
```

- observers = [obs0, obs1, obs2, obs3]

**Concrete Example:**

```cpp
class SelfRemovingObserver : public Observer {
    void update() override {
        subject->detach(this);  // Remove self
    }
};

// observers = [normal, selfRemoving, important, normal]
// After notify():
// - normal (index 0): notified ✅
// - selfRemoving (index 1): notified, removes self ✅
// - important (was index 2, now index 1): SKIPPED ❌
// - normal (was index 3, now index 2): notified ✅
```

- cpp class SelfRemovingObserver : public Observer { void update() override { subject->detach(this); // Remove self } };

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
class Observer {
    unique_ptr<Connection> connection;
public:
    Observer(Subject& subject) {
        connection = make_unique<Connection>(subject, this);
    }

    ~Observer() {
        // Connection destructor auto-detaches
    }
};

class Connection {
    Subject& subject;
    Observer* observer;
public:
    ~Connection() {
        subject.detach(observer);
    }
};

// What pattern does Connection implement?
```

**Pattern: RAII Connection Handle for Automatic Detachment**

`Connection` uses RAII to manage observer lifetime - automatically detaches observer when Connection is destroyed, ensuring no dangling pointers.

**How It Works:**

- subject.notify(); // obs receives notification
- } // obs destroyed → Connection destroyed → auto-detach ```

**Benefits:**

- No Manual Cleanup: Forget about detach() calls ```cpp // Without RAII: Observer* obs = new Observer(); subject->attach(obs); // ..
- subject->detach(obs); // ❌ Easy to forget delete obs;
- // With RAII: auto obs = make_unique<Observer>(subject); // ..
- // ✅ Automatic cleanup ```
- Prevents Dangling Pointers: Impossible to destroy observer without detaching

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
class Subject {
public:
    Signal<double> temperatureChanged;
    Signal<double> pressureChanged;
    Signal<double> humidityChanged;

    void setTemperature(double t) {
        temperature = t;
        temperatureChanged(t);  // Emit specific signal
    }
};

// How is this different from single notify() method?
```

**Difference: Multiple Signals for Fine-Grained Subscription**

Instead of one generic `notify()` for all changes, separate signals allow observers to subscribe only to specific events they care about.

**Single notify() Approach:**
```cpp
class Subject {
public:
    void notify() {
        // All observers notified for any change
        for (auto* obs : observers) {
            obs->update();  // Which property changed?
        }
    }
};
// Observer must check what changed:
class Observer {
    // ... (additional code omitted for brevity)
```
- cpp class Subject { public: void notify() { // All observers notified for any change for (auto* obs : observers) { obs->update(); // Which property changed
**Multiple Signals Approach:**
```cpp
class Subject {
public:
    Signal<double> temperatureChanged;
    Signal<double> pressureChanged;
};
// Observer subscribes only to what it needs:
temperatureMonitor.connect(subject.temperatureChanged);
pressureMonitor.connect(subject.pressureChanged);
// Now:

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
class Subject {
    vector<weak_ptr<Observer>> observers;
    int notificationLevel = 0;  // Recursion depth

public:
    void notify() {
        if (notificationLevel > 3) {
            cerr << "Warning: Deep notification recursion!
";
            return;  // Prevent infinite loop
        }

        notificationLevel++;
        // ... notify observers ...
        notificationLevel--;
    }
};

// What does notificationLevel track?
```

**Purpose: Recursion Guard to Prevent Infinite Notification Loops**

`notificationLevel` tracks notification depth, detecting when observer callbacks trigger new notifications, preventing stack overflow from infinite recursion.

**How Recursion Happens:**
```cpp
class Subject {
    int value;
public:
    void setValue(int v) {
        value = v;
        notify();  // Notify observers
    }
};
class RecursiveObserver : public Observer {
    void update() override {
        // Modifies subject, triggering another notification
    // ... (additional code omitted for brevity)
```
- cpp class Subject { int value; public: void setValue(int v) { value = v; notify(); // Notify observers } };
**Execution Without Guard:**
```cpp
setValue(10)
  → notify() (level 1)
    → observer->update()
      → setValue(11)
        → notify() (level 2)
          → observer->update()
            → setValue(12)
              → notify() (level 3)
                ... infinite recursion ...
                → STACK OVERFLOW ❌
```
- infinite recursion ..
- → STACK OVERFLOW ❌ ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
class Subject {
public:
    void notify() {
        // Phase 1: Validators
        for (auto& obs : validatorObservers) {
            obs->update();
        }

        // Phase 2: Processors
        for (auto& obs : processorObservers) {
            obs->update();
        }

        // Phase 3: Loggers
        for (auto& obs : loggerObservers) {
            obs->update();
        }
    }
};

// What pattern does multi-phase notification implement?
```

**Pattern: Ordered Notification with Observer Dependencies**

Multi-phase notification ensures observers execute in specific order when some observers depend on others completing first (e.g., validators before processors).

**Why Order Matters:**

```cpp
// Without ordering:
subject.notify();
// Observers might execute in any order:
// 1. Processor (❌ processes invalid data)
// 2. Validator (rejects data, but too late!)
// 3. Logger (logs invalid processing)

// With multi-phase:
// Phase 1: Validator (✅ rejects invalid data first)
// → If validation fails, stop here
// Phase 2: Processor (only runs if validation passed)
// Phase 3: Logger (logs successful processing)
```

- cpp // Without ordering: subject.notify(); // Observers might execute in any order: // 1
- Processor (❌ processes invalid data) // 2
- Validator (rejects data, but too late!) // 3

**Benefits:**

- **Explicit Dependencies:** Clear which observers run first
- **Error Handling:** Can stop pipeline if early phase fails
- **Predictable Behavior:** Consistent execution order

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
class Observer {
    bool oneTime = false;
public:
    void update() override {
        processUpdate();

        if (oneTime) {
            requestRemoval();  // Mark for removal
        }
    }

    void setOneTime(bool ot) { oneTime = ot; }
};

// What is a one-time observer useful for?
```

**Use Case: Auto-Unsubscribe After First Notification**

One-time observers automatically detach after first notification, useful for completion handlers, async callbacks, and waiting for single events.

**Common Use Cases:**

- Promise/Future Completion: ```cpp class FutureObserver : public Observer { public: FutureObserver() { setOneTime(true); }
- void update() override { promise.set_value(subject->getValue()); // Auto-detached after this } };
- // Wait for next event: auto future = subject.waitForNext(); future.wait(); // Blocks until one notification ```

**Implementation:**

- if (obs->isOneTime()) { toRemove.push_back(obs); } }
- // Remove one-time observers after notification for (auto* obs : toRemove) { detach(obs); } toRemove.clear(); } }; ```

**Benefits:**

- **No Manual Cleanup:** Auto-detachment prevents memory leaks
- **Clear Intent:** Code explicitly shows one-time behavior
- **Useful for Async:** Bridges observer pattern with promise/future patterns

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
class Subject {
    vector<Observer*> observers;
public:
    void notify() {
        try {
            for (auto* obs : observers) {
                obs->update();
            }
        } catch (...) {
            // ❌ Catches all exceptions, logs nothing
        }
    }
};

// What's the problem with this exception handling?
```

**Problem: Outer Catch-All Silences First Exception and Stops Notification**

Placing catch-all outside loop causes first exception to terminate iteration, preventing remaining observers from being notified, and exception is silently swallowed.

**Execution Flow:**



**Two Problems:**

- Early Termination: Remaining observers not notified 2
- Silent Failure: No logging, debugging impossible
- Fix: Catch Inside Loop
- // Now all observers execute despite exceptions ```
- Advanced: Collect Exceptions

**Key Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
