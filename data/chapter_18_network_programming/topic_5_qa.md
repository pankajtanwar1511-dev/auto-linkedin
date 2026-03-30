## TOPIC: epoll() - High-Performance I/O for Linux

### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: What is epoll() and how does it differ from select() and poll()?

**Answer:**

epoll() is a Linux-specific I/O event notification mechanism introduced in kernel 2.5.44 (2002) for scalable multiplexing of file descriptors.

**Key Differences:**

| Feature | select() | poll() | epoll() |
|---------|----------|--------|---------|
| **Max FDs** | 1024 (FD_SETSIZE) | Unlimited | Unlimited |
| **Add FD Cost** | O(1) | O(1) | O(log n) |
| **Wait Cost** | O(n) | O(n) | O(num_active) |
| **Kernel→User Data Copy** | All FDs | All FDs | Only active FDs |
| **Modify Interest** | Rebuild set | Rebuild array | O(log n) |
| **Portability** | POSIX, universal | POSIX, universal | Linux only |
| **Edge-Triggered** | No | No | Yes (optional) |

**Why epoll() Scales:**

1. **Interest list in kernel:** No need to pass all FDs on every wait
2. **Red-black tree:** Fast add/remove (O(log n))
3. **Ready list:** Only active FDs returned (O(num_active))
4. **Edge-triggered mode:** Reduces wake-ups for busy FDs

**When to Use:**
- epoll(): Linux server with >1000 connections
- poll(): Portable UNIX server with >64 FDs
- select(): Maximum portability, small FD count (<64)

---

#### Q2: Explain level-triggered vs edge-triggered modes in epoll. When would you use each?


**Answer:**



**Level-Triggered (default):**

- Behavior: `epoll_wait()` returns FD as long as data remains available
- You can read partial data, and epoll will notify again
- Easier to use, harder to get wrong
- Like poll() behavior

**Edge-Triggered:**

- Behavior: `epoll_wait()` returns FD only when state changes (new data arrives)
- You must read all available data (until EAGAIN)
- More efficient (fewer wake-ups), but harder to get right
- Requires non-blocking sockets

**When to Use:**



**Common Mistake:**

- // Event loop: int n = recv(fd, buf, 1024, 0); // ❌ Only reads 1024 bytes // If 2048 bytes arrived, 1024 bytes are LOST forever
- // epoll will NOT notify again until NEW data arrives ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3: What is EPOLLONESHOT and why is it critical for multi-threaded servers?


**Answer:**



**EPOLLONESHOT:**



**The Problem It Solves:**

- Without EPOLLONESHOT, multiple threads can process the same FD simultaneously, causing race conditions:
- | epoll_wait() → fd=5 | ❌ Both threads get fd=5
- | recv(fd=5) | ❌ RACE CONDITION ```

**With EPOLLONESHOT:**

- | epoll_wait() | B does NOT get fd=5 ✅ T4 | epoll_ctl(MOD) | - | A re-arms fd=5 T5 | done | Can now get fd=5 | Safe

**Implementation:**



**Why Critical:**

- Thread safety: Prevents concurrent access to same FD 2
- No locks needed: Kernel serializes events for you 3
- Common in thread pools: Each worker processes one FD at a time

**When NOT to Use EPOLLONESHOT:**

- Single-threaded servers (unnecessary overhead)
- Listen sockets (multiple threads can accept safely)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4: Explain the internal data structures of epoll. How does it achieve O(1) performance?


**Answer:**

- Stores all monitored FDs
- **Operations:** O(log n)
- `epoll_ctl(ADD)`: Insert into tree
- `epoll_ctl(DEL)`: Remove from tree
- `epoll_ctl(MOD)`: Update node

**How It Works:**

- Registration (`epoll_ctl(ADD)`): ``` 1
- Insert FD into red-black tree: O(log n) 2
- Register callback with kernel driver 3
- Driver calls callback when data arrives ```
- Event Arrival: ``` 1

**Why It's Fast:**



**Memory Usage:**

- Red-black tree node: ~64 bytes per FD
- 10,000 FDs: ~640 KB in kernel
- poll(): Must copy 10,000 × sizeof(pollfd) = 80 KB **every wait**
- epoll(): Copies only active events (~3.2 KB for 100 active)

**The O(1) Claim:**

- Add/remove: O(log n)
- Wait: O(num_active)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5: What happens if you close() a file descriptor without calling epoll_ctl(DEL) first?


**Answer:**



**Short answer:**



**What Happens:**

- Automatic Removal: ```cpp int fd = accept(...); epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev); close(fd); // Kernel removes fd from epoll automatically ✅ ```
- ❌ // Thread A's event loop epoll_wait(epfd, events, ...); // Gets event for fd=42, but it's a DIFFERENT connection now

**The Correct Pattern:**



**Why DEL Before Close:**

- Explicit tracking: You know exactly which FDs are monitored 2
- Avoid reuse bugs: FD is removed from epoll before kernel reuses it 3
- Multi-threaded safety: Prevents events for stale FDs

**Real-World Bug Example:**

- int new_fd = accept(...); // Kernel reuses fd=100
- // Event loop might deliver old buffered events for fd=100 // But fd=100 is now a DIFFERENT client

**Edge Case: dup() and dup2():**

- epoll_ctl(epfd, EPOLL_CTL_ADD, fd1, &ev); close(fd1); // epoll entry NOT removed
- // Event will still fire for the file description epoll_wait(epfd, ...); // ✅ Still works, but events point to fd1 (now invalid) ```

**Takeaway:**



**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: How do you handle partial sends with epoll? Explain the EPOLLOUT pattern.


**Answer:**
**Problem:**
```cpp
char msg[10000];
int n = send(fd, msg, 10000, 0);
// n might be 5000! ❌ 5000 bytes not sent
```
- cpp char msg[10000]; int n = send(fd, msg, 10000, 0); // n might be 5000
- ❌ 5000 bytes not sent ```
**Solution:**
**Pattern:**
```cpp
std::unordered_map<int, std::queue<std::string>> write_queues;
void send_message(int epfd, int fd, const std::string& msg) {
    // Try to send immediately
    int n = send(fd, msg.data(), msg.size(), 0);
    if (n < 0 && errno != EAGAIN) {
        // Error
        return;
    }
    if (n < msg.size()) {
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What is the thundering herd problem with epoll, and how does EPOLLEXCLUSIVE solve it?


**Answer:**
**Thundering Herd Problem:**
In multi-process/multi-threaded servers where each process/thread calls `epoll_wait()` on the same listen socket:
```cpp
[Listen Socket FD 3]
                            |
        +-------------------+-------------------+
        |                   |                   |
    Process A           Process B           Process C
    epoll_wait()        epoll_wait()        epoll_wait()
```
- When a new connection arrives: 1.
**Performance Impact:**
- 4 processes: 3 wasted wake-ups per connection
- 1000 connections/sec: 3000 wasted context switches/sec
- High CPU usage, cache pollution
**Solution: EPOLLEXCLUSIVE (Linux 4.5+):**
```cpp
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLEXCLUSIVE;  // ✅ Exclusive wake-up
ev.data.fd = listen_fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);
```
- cpp struct epoll_event ev; ev.events = EPOLLIN | EPOLLEXCLUSIVE; // ✅ Exclusive wake-up ev.data.fd = listen_fd; epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev); ```
**How EPOLLEXCLUSIVE Works:**
- Kernel wakes up **only one** waiter when event fires
- Other processes stay asleep
- Round-robin or random selection (kernel decides)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: How do you implement timeout handling with epoll (e.g., idle connection timeouts)?


**Answer:**
- epoll does NOT provide per-FD timeouts
- You must implement timeout tracking manually.
**Method 1: Timeouts in Event Loop (Simple):**
```cpp
#include <chrono>
#include <unordered_map>
using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::steady_clock::time_point;
std::unordered_map<int, TimePoint> last_activity;
const auto IDLE_TIMEOUT = std::chrono::seconds(30);
while (true) {
    // Set epoll_wait timeout to check timeouts periodically
    int timeout_ms = 1000;  // Check every second
    // ... (additional code omitted for brevity)
```
- cpp #include <chrono> #include <unordered_map>
- using Clock = std::chrono::steady_clock; using TimePoint = std::chrono::steady_clock::time_point;
- std::unordered_map<int, TimePoint> last_activity; const auto IDLE_TIMEOUT = std::chrono::seconds(30);
**Method 2: Timer Wheel (Efficient for Many Connections):**
```cpp
#include <list>
#include <vector>
struct TimerWheel {
    static const int SLOTS = 60;  // 60 seconds
    std::vector<std::list<int>> wheel;
    int current_slot = 0;
    TimerWheel() : wheel(SLOTS) {}
    void add(int fd, int timeout_seconds) {
        int slot = (current_slot + timeout_seconds) % SLOTS;
    // ... (additional code omitted for brevity)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: Can you use epoll with regular files? Why or why not?


**Answer:**
**Short Answer:**
**Technical Reason:**
epoll relies on kernel drivers providing event notifications. Regular files (on disk) don't have event-driven I/O:
```cpp
int fd = open("file.txt", O_RDONLY | O_NONBLOCK);
struct epoll_event ev;
ev.events = EPOLLIN;
ev.data.fd = fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);  // ✅ Succeeds
int n = epoll_wait(epfd, events, 1, -1);
// ❌ Returns immediately! File FD is always "ready"
```
- cpp int fd = open("file.txt", O_RDONLY | O_NONBLOCK);
- struct epoll_event ev; ev.events = EPOLLIN; ev.data.fd = fd; epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev); // ✅ Succeeds
- int n = epoll_wait(epfd, events, 1, -1); // ❌ Returns immediately
**Why Files Are Always Ready:**
- No blocking: Disk I/O might be slow, but it never blocks (from userspace perspective) 2
- No events: File system doesn't generate events like "data available" 3
- epoll can't help: Would need to poll disk controller (expensive)
**What Works with epoll:**
**Workaround for File I/O:**
**Option 1: Use io_uring (Linux 5.1+):**
```cpp
#include <liburing.h>
struct io_uring ring;
io_uring_queue_init(32, &ring, 0);
// Submit async read
struct io_uring_sqe *sqe = io_uring_get_sqe(&ring);
io_uring_prep_read(sqe, fd, buf, sizeof(buf), offset);
io_uring_submit(&ring);

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: What is the maxevents parameter in epoll_wait()? How do you choose the right value?


**Answer:**
**Definition:**
```cpp
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
                                                     ^^^^^^^^^^^^
```
- cpp int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout); ^^^^^^^^^^^^ ```
- `maxevents`: Maximum number of events to return in one call.
**What It Does:**
```cpp
struct epoll_event events[128];  // Array size
int n = epoll_wait(epfd, events, 128, -1);
                                ^^^^
                    "Return at most 128 events"
// n <= 128
for (int i = 0; i < n; i++) {
    handle_event(events[i]);
}
```
- cpp struct epoll_event events[128]; // Array size
- int n = epoll_wait(epfd, events, 128, -1); ^^^^ "Return at most 128 events"
- // n <= 128 for (int i = 0; i < n; i++) { handle_event(events[i]); } ```
**Impact on Performance:**
**Too Small (e.g., maxevents=1):**
```cpp
Ready FDs: 100
maxevents: 1
Iteration 1: epoll_wait() returns 1 event  (99 still pending)
Iteration 2: epoll_wait() returns 1 event  (98 still pending)
...

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: How does epoll handle EPOLLRDHUP, and why is it useful for detecting half-closed connections?


**Answer:**
**EPOLLRDHUP:**
**Without EPOLLRDHUP:**
```cpp
// Traditional detection
int n = recv(fd, buf, sizeof(buf), 0);
if (n == 0) {
    // Peer closed connection (or half-closed)
    close(fd);
}
```
- cpp // Traditional detection int n = recv(fd, buf, sizeof(buf), 0); if (n == 0) { // Peer closed connection (or half-closed) close(fd); } ```
- Problem: You only detect closure when you try to read.
**With EPOLLRDHUP:**
```cpp
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLRDHUP;  // ✅ Request EPOLLRDHUP events
ev.data.fd = fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
// Event loop
if (events[i].events & EPOLLRDHUP) {
    std::cout << "FD " << fd << " peer closed (FIN received)\n";
    // Can still send data if needed (half-close)
    const char *bye = "Goodbye\n";
    send(fd, bye, strlen(bye), 0);
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12: Explain how to safely transfer an epoll FD between threads or processes.


**Answer:**



**Short Answer:**



**epoll FD Characteristics:**

```cpp
int epfd = epoll_create1(0);
// epfd is a normal file descriptor
// Can be: dup()'d, sent via Unix socket, inherited by fork()
```

- cpp int epfd = epoll_create1(0); // epfd is a normal file descriptor // Can be: dup()'d, sent via Unix socket, inherited by fork() ```

**Important:**

```cpp
ev.events = EPOLLIN | EPOLLEXCLUSIVE;  // ✅ Only wake one process
```

- cpp ev.events = EPOLLIN | EPOLLEXCLUSIVE; // ✅ Only wake one process ```

**Thread Safety of epoll Operations:**

- | Operation | Thread-Safe

**Common Pitfalls:**

**1. Thundering Herd (Multi-process without EPOLLEXCLUSIVE):**

```cpp
// ❌ BAD: All processes wake up
for (int i = 0; i < 4; i++) {
    if (fork() == 0) {
        epoll_wait(epfd, ...);  // All 4 children wake for one event
    }
}

// ✅ GOOD: Use EPOLLEXCLUSIVE
ev.events = EPOLLIN | EPOLLEXCLUSIVE;
```

- cpp // ❌ BAD: All processes wake up for (int i = 0; i < 4; i++) { if (fork() == 0) { epoll_wait(epfd, ...); // All 4 children wake for one event } }
- // ✅ GOOD: Use EPOLLEXCLUSIVE ev.events = EPOLLIN | EPOLLEXCLUSIVE; ```

**Best Practices:**

- Multi-process: Use EPOLLEXCLUSIVE or SO_REUSEPORT 2
- Multi-threaded: Use EPOLLONESHOT to prevent races 3
- Ownership: Designate one thread/process as owner for cleanup 4
- Synchronization: Only needed for application-level data, not epoll calls

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: What happens when a monitored FD is closed while epoll_wait() is blocked?


**Answer:**
**Scenario:**
```cpp
Thread A: epoll_wait(epfd, ...) → BLOCKED
Thread B: close(monitored_fd) → ???
```
- Thread A: epoll_wait(epfd, ...) → BLOCKED Thread B: close(monitored_fd) → ??
**What Happens:**
- Kernel removes FD from epoll automatically ✅ 2
- epoll_wait() wakes up if that FD had pending events 3
- Events for that FD are still delivered (race)
**Timeline:**
```cpp
T1: Thread A calls epoll_wait(), blocks
T2: Thread B calls close(fd=42)
T3: Kernel removes fd=42 from epoll interest list ✅
T4: If fd=42 had pending events, epoll_wait() returns them ⚠️
T5: Thread A processes event for fd=42 (NOW INVALID!) ❌
```
**Kernel Behavior:**
The kernel tracks the **file description** (not FD number). When you `close()`:
1. **Decrement file description reference count**
2. **If ref count reaches 0**, remove from epoll
3. **If ref count > 0** (dup'd FDs), keep in epoll
```cpp
int fd1 = socket(...);
int fd2 = dup(fd1);  // Both point to same file description
epoll_ctl(epfd, EPOLL_CTL_ADD, fd1, &ev);
close(fd1);  // File description ref count: 2 → 1
// epoll entry NOT removed! fd2 still open ⚠️
epoll_wait(epfd, ...);  // Still returns events! (but for invalid fd1)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: Compare epoll() to alternatives like kqueue (BSD), IOCP (Windows), and io_uring (Linux).


**Answer:**
**Overview:**
| Mechanism | OS | API Style | Performance | Complexity |
|-----------|----|-----------| ------------|------------|
| **epoll** | Linux | Event notification | O(num_active) | Medium |
| **kqueue** | BSD/macOS | Event notification | O(num_active) | Medium |
```cpp
// Create
int epfd = epoll_create1(0);
// Register interest
struct epoll_event ev;
ev.events = EPOLLIN;
ev.data.fd = fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
// Wait for events (reactive)
int n = epoll_wait(epfd, events, maxevents, timeout);
// You call recv()
recv(fd, buf, sizeof(buf), 0);
```
- cpp // Create int epfd = epoll_create1(0);
- // Register interest struct epoll_event ev; ev.events = EPOLLIN; ev.data.fd = fd; epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
- // Wait for events (reactive) int n = epoll_wait(epfd, events, maxevents, timeout);
**Pros:**
- ✅ Fast for sockets (O(num_active))

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: How do you debug epoll applications? What tools and techniques are available?


**Answer:**

**1. strace: System Call Tracing**

```cpp
# Trace epoll-related syscalls
strace -e trace=epoll_create1,epoll_ctl,epoll_wait ./my_server

# Output:
epoll_create1(0) = 3
epoll_ctl(3, EPOLL_CTL_ADD, 4, {EPOLLIN, {u32=4, u64=4}}) = 0
epoll_ctl(3, EPOLL_CTL_ADD, 5, {EPOLLIN, {u32=5, u64=5}}) = 0
epoll_wait(3, [{EPOLLIN, {u32=4, u64=4}}], 128, -1) = 1
epoll_wait(3, [{EPOLLIN, {u32=5, u64=5}}], 128, -1) = 1

# Trace all syscalls with timestamps
strace -tt -T -e trace=all ./my_server
```

- bash # Trace epoll-related syscalls strace -e trace=epoll_create1,epoll_ctl,epoll_wait ./my_server
- # Trace all syscalls with timestamps strace -tt -T -e trace=all ./my_server ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16: Explain the relationship between epoll, non-blocking sockets, and edge-triggered mode.


**Answer:**
**Three Interconnected Concepts:**
- Non-blocking sockets: recv()/send() return immediately with EAGAIN instead of blocking 2
- Edge-triggered epoll: Notifies only on state change (not level) 3
- Mandatory combination: Edge-triggered REQUIRES non-blocking
**Why Edge-Triggered Requires Non-Blocking:**
**Scenario: Edge-triggered + Blocking Socket (❌ DEADLOCK):**
```cpp
// ❌ WRONG: Edge-triggered with BLOCKING socket
int fd = accept(...);
// fd is BLOCKING (default)
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLET;  // Edge-triggered
ev.data.fd = fd;
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
// Event loop
epoll_wait(epfd, events, 128, -1);  // Returns: fd has data
    // ... (additional code omitted for brevity)
```
- cpp // ❌ WRONG: Edge-triggered with BLOCKING socket int fd = accept(...); // fd is BLOCKING (default)
- struct epoll_event ev; ev.events = EPOLLIN | EPOLLET; // Edge-triggered ev.data.fd = fd; epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);
- // Event loop epoll_wait(epfd, events, 128, -1); // Returns: fd has data
**Correct: Edge-triggered + Non-blocking Socket:**
```cpp
// ✅ CORRECT: Edge-triggered with NON-BLOCKING socket
int fd = accept(...);
int flags = fcntl(fd, F_GETFL, 0);
fcntl(fd, F_SETFL, flags | O_NONBLOCK);  // ✅ Set non-blocking
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLET;
ev.data.fd = fd;

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: What are the security implications of epoll? How do you prevent epoll-based DoS attacks?


**Answer:**
**epoll-Specific Attack Vectors:**
- FD Exhaustion Attack**
**Attack:**
```cpp
Attacker: Open 100,000 connections
Server: epoll can't add new FDs (EMFILE error)
Result: Legitimate clients rejected ❌
```
- Attacker: Open 100,000 connections Server: epoll can't add new FDs (EMFILE error) Result: Legitimate clients rejected ❌ ```
**Mitigation:**
```cpp
// Set connection limit
const int MAX_CONNECTIONS = 10000;
std::atomic<int> active_connections{0};
// On new connection
if (active_connections >= MAX_CONNECTIONS) {
    std::cerr << "Connection limit reached, rejecting\n";
    close(client_fd);
    return;
}
active_connections++;
// On close
active_connections--;
```
- cpp // Set connection limit const int MAX_CONNECTIONS = 10000; std::atomic<int> active_connections{0};
- // On new connection if (active_connections >= MAX_CONNECTIONS) { std::cerr << "Connection limit reached, rejecting\n"; close(client_fd); return; }
- active_connections++;
**System-level mitigation:**
```cpp
# Increase FD limit (in /etc/security/limits.conf)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: How do you measure and optimize epoll performance? What metrics matter?


**Answer:**
**Key Performance Metrics:**
**1. Throughput (Events/Second)**
```cpp
auto start = std::chrono::steady_clock::now();
size_t events_processed = 0;
while (running) {
    int n = epoll_wait(epfd, events, 128, 1000);  // 1s timeout
    events_processed += n;
    // Print metrics every second
    auto now = std::chrono::steady_clock::now();
    if (std::chrono::duration_cast<std::chrono::seconds>(now - start).count() >= 1) {
        std::cout << "Events/sec: " << events_processed << "\n";
        events_processed = 0;
    // ... (additional code omitted for brevity)
```
- cpp auto start = std::chrono::steady_clock::now(); size_t events_processed = 0;
**Optimization Techniques:**
**1. Tune maxevents**
```cpp
// Start with 128, measure batch sizes
int maxevents = 128;
struct epoll_event *events = new epoll_event[maxevents];
// If consistently hitting limit, increase
// If rarely using more than 25%, decrease
```
- cpp // Start with 128, measure batch sizes int maxevents = 128; struct epoll_event *events = new epoll_event[maxevents];
- // If consistently hitting limit, increase // If rarely using more than 25%, decrease ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: Can multiple threads/processes call epoll_wait() on the same epoll FD simultaneously? What happens?


**Answer:**
**Short Answer:**
**What Happens:**
```cpp
// Thread A and Thread B both call:
int n = epoll_wait(epfd, events, 128, -1);
```
- cpp // Thread A and Thread B both call: int n = epoll_wait(epfd, events, 128, -1); ```
**Behavior:**
- Both threads block waiting for events 2
- When an event arrives, kernel wakes ALL threads (thundering herd) ❌ 3
- Each thread receives the same events (duplicate processing risk) 4
- Each thread must handle race conditions
**Example Timeline:**
```cpp
T1: Thread A calls epoll_wait() → blocks
T2: Thread B calls epoll_wait() → blocks
T3: FD 5 becomes ready (data arrives)
T4: Kernel wakes Thread A and Thread B ❌ (both wake up)
T5: Thread A: epoll_wait() returns {FD 5}
T6: Thread B: epoll_wait() returns {FD 5}  ← Duplicate!
T7: Thread A: recv(FD 5) → 1024 bytes
T8: Thread B: recv(FD 5) → EAGAIN (no more data) or partial read ❌
```
- T7: Thread A: recv(FD 5) → 1024 bytes T8: Thread B: recv(FD 5) → EAGAIN (no more data) or partial read ❌ ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: What are the differences between epoll_create() and epoll_create1()? Why should you use epoll_create1()?


**Answer:**
**epoll_create()** (Deprecated):
```cpp
int epoll_create(int size);
// Example:
int epfd = epoll_create(1024);  // "size" hint (ignored since Linux 2.6.8)
```
- cpp int epoll_create(int size);
- // Example: int epfd = epoll_create(1024); // "size" hint (ignored since Linux 2.6.8) ```
**Key Differences:**
**Why size is Meaningless in epoll_create():**
Originally (pre-2.6.8), `size` hinted how many FDs you'd monitor. Kernel pre-allocated hash table.
```cpp
// Old behavior (Linux < 2.6.8)
int epfd = epoll_create(1000);  // Pre-allocate for 1000 FDs
```
- cpp // Old behavior (Linux < 2.6.8) int epfd = epoll_create(1000); // Pre-allocate for 1000 FDs ```
- Since Linux 2.6.8, kernel uses dynamic red-black tree
**EPOLL_CLOEXEC Flag:**
Without EPOLL_CLOEXEC:
```cpp
int epfd = epoll_create(1);
if (fork() == 0) {
    // Child process inherits epfd ❌
    exec("./other_program");
    // other_program has epfd (file descriptor leak!)
}
```
- cpp int epfd = epoll_create(1);
- if (fork() == 0) { // Child process inherits epfd ❌ exec("./other_program"); // other_program has epfd (file descriptor leak!) } ```
- if (fork() == 0) { exec("./other_program"); // epfd automatically closed before exec() ✅ } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
