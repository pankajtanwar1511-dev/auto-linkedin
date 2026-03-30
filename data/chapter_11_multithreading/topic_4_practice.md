## TOPIC: Condition Variables - Thread Synchronization and Event Notification

### PRACTICE_TASKS: Output Prediction and Code Analysis

#### Q1
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void worker() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock);  // No predicate
    std::cout << "Working\n";
}

void notifier() {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    cv.notify_one();
}
```

**Answer:**
```
May work or spurious wakeup may cause issues
```

**Explanation:**
- **cv.wait(lock) called WITHOUT predicate** - dangerous pattern
- **Spurious wakeup:** Thread can wake up even without notification
- **What happens:**
  1. Worker locks mutex and calls wait()
  2. wait() atomically unlocks mutex and blocks
  3. Notifier sleeps 100ms, then calls notify_one()
  4. Worker wakes up, reacquires lock, continues
- **Problem: Spurious wakeups are ALLOWED by the standard**
  - OS or implementation can wake thread without notify_one()
  - Thread wakes, ready still false, proceeds anyway
  - No way to distinguish spurious vs real wakeup
- **Possible outcomes:**
  - Usually works (notification received)
  - Sometimes fails (spurious wakeup before notification)
  - Undefined behavior (ready not checked)
- **Fix:** Always use predicate

```cpp
cv.wait(lock, []{ return ready; });
```
- **Predicate rechecked after wakeup** - handles spurious wakeups automatically
- **Why spurious wakeups exist:** Performance optimization in kernel scheduling
- **Rule:** NEVER use cv.wait() without predicate in production code
- **Key Concept:** Spurious wakeups require predicate; wait() without predicate is unreliable

---

#### Q2
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void producer() {
    ready = true;  // No lock
    cv.notify_one();
}

void consumer() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });
    std::cout << "Ready\n";
}
```

**Answer:**

```cpp
Race condition possible but predicate likely saves it
```

- Race condition possible but predicate likely saves it ```

**Explanation:**

- **ready modified without lock** - data race!
- **Consumer uses lock but producer doesn't** - inconsistent synchronization

```cpp
void producer() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true;
    }
    cv.notify_one();
}
```

- cpp void producer() { { std::lock_guard<std::mutex> lock(mtx); ready = true; } cv.notify_one(); } ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void notifier() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true;
    }
    cv.notify_one();
}

void waiter() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });
    std::cout << "Done\n";
}
```

**Answer:**
```
Output: "Done"
```

**Explanation:**
- **Early notification pattern** - notification BEFORE waiting
- **Execution scenario:**
  1. Waiter starts, sleeps 1 second
  2. Notifier runs immediately: locks, sets ready=true, unlocks
  3. Notifier calls notify_one() (no one waiting yet!)
  4. Waiter wakes from sleep after 1 second
  5. Waiter locks mutex, calls cv.wait()
  6. **Predicate checked BEFORE waiting:** ready=true
  7. wait() returns immediately without blocking
  8. Prints "Done"
- **Why it works:**
  - **Predicate prevents lost wakeup**
  - wait() checks condition first: if already true, doesn't wait
  - Notification was "lost" but doesn't matter
- **Without predicate:** Would wait forever (notification already sent)
- **Predicate equivalence:**

```cpp
// cv.wait(lock, pred) is equivalent to:
while (!pred()) {
    cv.wait(lock);
}
```
- **Pattern is CORRECT and safe** with predicate
- **Demonstrates:** Predicates make condition variables robust to timing
- **Key Concept:** Predicate prevents lost wakeups; checks condition before waiting regardless of notification timing

---

#### Q4
```cpp
std::mutex mtx;
std::condition_variable cv;
std::queue<int> q;

void producer() {
    for (int i = 0; i < 5; ++i) {
        std::lock_guard<std::mutex> lock(mtx);
        q.push(i);
        cv.notify_all();
    }
}

void consumer() {
    for (int i = 0; i < 5; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&]{ return !q.empty(); });
        std::cout << q.front() << " ";
        q.pop();
    }
}
```

**Answer:**
```
Output: "0 1 2 3 4" (order guaranteed within consumer)
```

**Explanation:**
- **notify_all() called on every push** - performance issue but works
- **Execution flow:**
  1. Producer locks, pushes 0, calls notify_all()
  2. Consumer locks, waits until !q.empty(), pops 0
  3. Producer locks, pushes 1, calls notify_all()
  4. This repeats for all 5 items
- **Why order is guaranteed:**
  - Single consumer processes in FIFO order
  - Queue maintains insertion order
  - Producer pushes 0,1,2,3,4 sequentially
- **Thundering herd problem:**
  - notify_all() wakes ALL waiting threads
  - With multiple consumers: all wake, recheck predicate
  - Only one can proceed (queue becomes empty again)
  - Others go back to sleep
  - **Wastes CPU cycles** on unnecessary wakeups
- **Better approach:** Use notify_one()

```cpp
cv.notify_one();  // Wake just one waiting thread
```
- **When to use notify_all():**
  - Multiple threads can proceed (e.g., broadcast "shutdown")
  - Different predicates for different threads
- **Performance impact:**
  - notify_one(): O(1) thread wakeup
  - notify_all(): O(N) wakeups, N-1 go back to sleep
- **Key Concept:** notify_all() causes thundering herd; use notify_one() for single-consumer patterns

---

#### Q5
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void worker() {
    std::unique_lock<std::mutex> lock(mtx);
    if (cv.wait_for(lock, std::chrono::milliseconds(100), []{ return ready; })) {
        std::cout << "Ready\n";
    } else {
        std::cout << "Timeout\n";
    }
}
```

**Answer:**

```cpp
Output: "Timeout" (no notifier)
```

- Output: "Timeout" (no notifier) ```

**Explanation:**

- **wait_for:** Waits with timeout (relative duration)
- **Execution:**
- **Return value of wait_for:**
- **true:** Predicate became true (condition met)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6
```cpp
std::mutex mtx;
std::condition_variable cv;
int counter = 0;

void waiter() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&]{ return counter > 0; });
    std::cout << counter << "\n";
}

void notifier() {
    cv.notify_one();  // Notify before setting counter
    {
        std::lock_guard<std::mutex> lock(mtx);
        counter = 10;
    }
}
```

**Answer:**



**Explanation:**

- **Lost wakeup problem** - classic mistake
- **Execution scenario:**
- **Race condition timeline:**
- **Why waiter blocks:**
- Notification sent before waiter calls wait()

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7
```cpp
std::mutex mtx;
std::condition_variable cv;
bool start = false;

void worker(int id) {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return start; });
    std::cout << id << " ";
}

int main() {
    std::vector<std::thread> threads;
    for (int i = 0; i < 3; ++i) {
        threads.emplace_back(worker, i);
    }

    {
        std::lock_guard<std::mutex> lock(mtx);
        start = true;
    }
    cv.notify_one();  // Only notify_one

    for (auto& t : threads) t.join();
}
```

**Answer:**

```cpp
Only one thread prints (0, 1, or 2), others wait forever
```

- Only one thread prints (0, 1, or 2), others wait forever ```

**Explanation:**

- **notify_one() limitation** - wakes only ONE thread
- **3 threads waiting, 1 notification** - 2 threads left waiting

```cpp
cv.notify_all();  // Wake ALL waiting threads
```

- cpp cv.notify_all(); // Wake ALL waiting threads ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8
```cpp
std::mutex mtx;
std::condition_variable cv;

void waiter() {
    std::lock_guard<std::mutex> lock(mtx);  // lock_guard
    cv.wait(lock, []{ return true; });
}
```

**Answer:**

```cpp
Compilation error
```

- Compilation error ```

**Explanation:**

- **Type mismatch:** cv.wait() requires unique_lock, not lock_guard
- **Compiler error:**

```cpp
no matching function for call to 'wait(std::lock_guard<std::mutex>&, ...)'
```

- no matching function for call to 'wait(std::lock_guard<std::mutex>&, ...)' ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9
```cpp
std::mutex mtx;
std::condition_variable cv;
std::queue<int> q;

void producer() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        q.push(42);
        cv.notify_one();  // Notify inside lock
    }
}

void consumer() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&]{ return !q.empty(); });
    std::cout << q.front() << "\n";
}
```

**Answer:**

```cpp
Output: "42"
```

- Output: "42" ```

**Explanation:**

- **Notify inside lock** - works but debated pattern
- **Execution flow:**

```cpp
{
    std::lock_guard<std::mutex> lock(mtx);
    q.push(42);
}  // Lock released here
cv.notify_one();  // Notify after unlock
```

- cpp { std::lock_guard<std::mutex> lock(mtx); q.push(42); } // Lock released here cv.notify_one(); // Notify after unlock ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void setup() {
    std::lock_guard<std::mutex> lock(mtx);
    ready = true;
    cv.notify_one();
}

void worker() {
    std::this_thread::sleep_for(std::chrono::seconds(2));
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });
    std::cout << "Working\n";
}

int main() {
    std::thread t1(setup);
    std::thread t2(worker);
    t1.join(); t2.join();
}
```

**Answer:**

```cpp
Output: "Working"
```

- Output: "Working" ```

**Explanation:**

- **Late wait pattern** - waiter starts waiting AFTER notification
- **Timeline:**

```cpp
cv.wait(lock);  // Would wait forever, missed notification
```

- cpp cv.wait(lock); // Would wait forever, missed notification ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11
```cpp
std::mutex mtx;
std::condition_variable cv;
int value = 0;

void waiter() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&]{ return value == 10; });
    std::cout << "Got 10\n";
}

void setter() {
    for (int i = 1; i <= 10; ++i) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            value = i;
        }
        cv.notify_one();
    }
}
```

**Answer:**

```cpp
Output: "Got 10"
```

- Output: "Got 10" ```

**Explanation:**

- **Multiple notifications** with predicate handling
- **Execution scenario:**

```cpp
value = 10;  // Set final value directly
    cv.notify_one();  // Single notification
```

- cpp value = 10; // Set final value directly cv.notify_one(); // Single notification ``` -

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12
```cpp
std::mutex m1;
std::condition_variable cv;

void thread1() {
    std::unique_lock<std::mutex> lock(m1);
    cv.wait(lock, []{ return false; });  // Predicate always false
}
```

**Answer:**



**Explanation:**

- **Predicate always returns false** - infinite wait
- **cv.wait() expansion:**
- **Execution:**
- **No notification exists:**
- Even worse, no other thread calls notify

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13
```cpp
std::mutex mtx;
std::condition_variable_any cv;
std::shared_lock<std::shared_mutex> smtx;

void worker() {
    cv.wait(smtx, []{ return true; });
}
```

**Answer:**

```cpp
Compilation error
```

- Compilation error ```

**Explanation:**

- **Multiple type errors** in this code
- **Error 1: shared_lock not constructed properly**

```cpp
std::shared_lock<std::shared_mutex> smtx;  // No mutex provided!
```

- cpp std::shared_lock<std::shared_mutex> smtx; // No mutex provided

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14
```cpp
std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void producer() {
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true;
    }
    cv.notify_all();
}

void consumer(int id) {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });
    std::cout << "Consumer " << id << " done\n";
}

int main() {
    std::thread p(producer);
    std::thread c1(consumer, 1);
    std::thread c2(consumer, 2);
    std::thread c3(consumer, 3);

    p.join(); c1.join(); c2.join(); c3.join();
}
```

**Answer:**

```cpp
All three consumers print "done"
```

- All three consumers print "done" ```

**Explanation:**

- **notify_all() broadcast** - wakes ALL waiting threads
- **Execution timeline:**
- **Order is non-deterministic:**
- Could be "1 2 3" or "3 1 2" or any permutation

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15
```cpp
std::mutex mtx;
std::condition_variable cv;
bool flag = false;

void waiter() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait_until(lock,
                  std::chrono::steady_clock::now() + std::chrono::seconds(1),
                  []{ return flag; });
    std::cout << (flag ? "Flag set" : "Timeout") << "\n";
}
```

**Answer:**

```cpp
Output: "Timeout" (if flag not set within 1 second)
```

- Output: "Timeout" (if flag not set within 1 second) ```

**Explanation:**

- **wait_until with absolute time point** - different from wait_for
- **wait_for vs wait_until:**

```cpp
// wait_for returns bool
if (cv.wait_for(lock, 1s, pred)) { /* success */ }

// wait_until returns cv_status but with predicate doesn't need checking
cv.wait_until(lock, timepoint, pred);
if (pred()) { /* success */ } else { /* timeout */ }
```

- cpp // wait_for returns bool if (cv.wait_for(lock, 1s, pred)) { /* success */ }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16
```cpp
std::mutex mtx;
std::condition_variable cv;
std::queue<int> q;

void producer() {
    for (int i = 0; i < 3; ++i) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            q.push(i);
        }
        cv.notify_one();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void consumer() {
    while (true) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&]{ return !q.empty(); });
        std::cout << q.front() << " ";
        q.pop();
    }
}
```

**Answer:**



**Explanation:**

- **Missing shutdown mechanism** - common producer-consumer bug
- **Execution timeline:**
- **Problem: Infinite loop in consumer**
- `while(true)` never terminates
- No way to signal "no more data"

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17
```cpp
std::mutex mtx;
std::condition_variable cv;
int counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);
    ++counter;
    if (counter == 5) {
        cv.notify_one();
    }
}

void waiter() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, [&]{ return counter >= 5; });
    std::cout << "Counter is " << counter << "\n";
}
```

**Answer:**

```cpp
Output: "Counter is 5" (or higher)
```

- Output: "Counter is 5" (or higher) ```

**Explanation:**

- **Conditional notification** - notify only when condition met
- **Typical scenario:**
- **Why "or higher":**
- If more increment() calls happen before waiter wakes

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18
```cpp
std::mutex mtx;
std::condition_variable cv;

void waiter() {
    std::unique_lock<std::mutex> lock(mtx);
    bool result = cv.wait_for(lock, std::chrono::seconds(0), []{ return false; });
    std::cout << std::boolalpha << result << "\n";
}
```

**Answer:**



**Explanation:**

- **Zero timeout** - wait_for with duration of 0
- **Execution:**
- **Essentially a non-blocking check:**
- Checks if condition currently true
- Doesn't wait if false

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19
```cpp
std::mutex mtx1, mtx2;
std::condition_variable cv;
bool ready = false;

void producer() {
    std::lock_guard<std::mutex> lock(mtx1);
    ready = true;
    cv.notify_one();
}

void consumer() {
    std::unique_lock<std::mutex> lock(mtx2);  // Different mutex!
    cv.wait(lock, []{ return ready; });
}
```

**Answer:**



**Explanation:**

- **Condition variable requires consistent mutex** - CRITICAL rule violated
- **Why this is wrong:**
- Producer uses mtx1 to protect ready
- Consumer uses mtx2 with condition variable
- cv.wait() expects same mutex that protects the condition

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20
```cpp
std::mutex mtx;
std::condition_variable cv;
bool done = false;

void worker() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return done; });
    std::cout << "Worker done\n";
}

void coordinator() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        done = true;
    }
    // Forgot to call cv.notify_one()
}
```

**Answer:**



**Explanation:**

- **Missing notification** - critical bug
- **Execution scenario:**
- **Why worker never wakes:**
- Waiting threads don't periodically check condition
- Must be explicitly woken by notification

**Note:** Full detailed explanation with additional examples available in source materials.

---
