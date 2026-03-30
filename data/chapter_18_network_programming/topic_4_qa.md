## TOPIC: poll() - Scalable I/O Multiplexing Without FD Limits

### INTERVIEW_QA: Technical Questions for Mastery

#### Q1: What is poll() and why was it created? [BEGINNER]

**Answer**: poll() is a POSIX I/O multiplexing system call created to solve select()'s FD_SETSIZE limitation.

**The problem with select()**:
```cpp
// select() limited to 1024 FDs
#define FD_SETSIZE 1024

if (client_fd >= FD_SETSIZE) {
    // ❌ Cannot monitor this FD
    close(client_fd);
}
```

**poll() solution**:
```cpp
// ✅ No FD limit (only system resources)
std::vector<struct pollfd> fds;
fds.push_back({client_fd, POLLIN, 0});  // Works for any FD number
```

**Key improvements**:
1. **No FD limit**: Can monitor millions of FDs
2. **Cleaner API**: Array of structs instead of bitmasks
3. **Separate I/O**: events (input) vs revents (output)
4. **No max_fd tracking**: Just pass array size

**Created**: POSIX.1-2001 standard

**Use case**: Web servers handling thousands of connections.

---

#### Q2: Explain the pollfd structure and its three fields [BEGINNER]

**Answer**: pollfd is the data structure passed to poll() containing FD and event information.

**Structure definition**:
```cpp
struct pollfd {
    int fd;           // File descriptor to monitor
    short events;     // Events we want to monitor (INPUT)
    short revents;    // Events that occurred (OUTPUT)
};
```

**Field roles**:

1. **fd**: The file descriptor
   - Listening socket, client socket, pipe, etc.
   - Set to -1 to ignore this entry

2. **events**: What we want to monitor (set by user)
   ```cpp
   pfd.events = POLLIN;           // Want to read
   pfd.events = POLLOUT;          // Want to write
   pfd.events = POLLIN | POLLOUT; // Want both
   ```

3. **revents**: What actually happened (set by kernel)
   ```cpp
   if (pfd.revents & POLLIN)  { /* data available */ }
   if (pfd.revents & POLLOUT) { /* can write */ }
   if (pfd.revents & POLLHUP) { /* disconnected */ }
   ```

**Key insight**: events is INPUT (what you ask for), revents is OUTPUT (what you get).

**Example**:
```cpp
struct pollfd pfd;
pfd.fd = client_fd;
pfd.events = POLLIN;    // ← We set this
pfd.revents = 0;        // ← Kernel will set this

poll(&pfd, 1, -1);

// After poll():
if (pfd.revents & POLLIN) {
    // Kernel set POLLIN in revents
    recv(client_fd, buffer, size, 0);
}
```

---

#### Q3: What are the event flags in poll() and which are input vs output? [BEGINNER]

**Answer**: poll() has 6 main event flags, divided into input (user-set) and output (kernel-set).

**Input flags** (set in events field):

| Flag | Meaning | When to use |
|------|---------|-------------|
| `POLLIN` | Data available for reading | Always for sockets |
| `POLLOUT` | Can write without blocking | Handling partial sends |
| `POLLPRI` | High-priority data (OOB) | TCP urgent data (rare) |

**Output flags** (kernel sets in revents, automatically monitored):

| Flag | Meaning | Cause |
|------|---------|-------|
| `POLLERR` | Error condition | Socket error |
| `POLLHUP` | Peer disconnected | Connection closed |
| `POLLNVAL` | Invalid FD | FD not open (bug) |

**Example**:
```cpp
// Setup: Only ask for reads
pfd.events = POLLIN;  // ← We only set POLLIN

poll(&pfd, 1, -1);

// After poll(), revents might have:
if (pfd.revents & POLLIN)  { /* data ready */ }
if (pfd.revents & POLLHUP) { /* disconnected */ }  // ← Kernel added this!
if (pfd.revents & POLLERR) { /* error */ }         // ← And this!
```

**Key point**: POLLERR, POLLHUP, POLLNVAL are **always** monitored regardless of events field.

**Common mistake**:
```cpp
// ❌ Unnecessary
pfd.events = POLLIN | POLLHUP | POLLERR;

// ✅ Correct (POLLHUP/POLLERR implicit)
pfd.events = POLLIN;
```

---

#### Q4: What are poll()'s timeout modes? [BEGINNER]

**Answer**: poll() has three timeout modes, specified in milliseconds.

**Timeout parameter**:
```cpp
int poll(struct pollfd *fds, nfds_t nfds, int timeout);
//                                          ^^^^^^^ milliseconds
```

**Three modes**:

1. **Block forever** (timeout = -1)
```cpp
int ready = poll(fds, nfds, -1);  // Wait until activity
// Returns only when FD ready or signal
```

2. **Non-blocking poll** (timeout = 0)
```cpp
int ready = poll(fds, nfds, 0);  // Return immediately

if (ready == 0) {
    // No activity right now - do other work
    process_background_jobs();
}
```

3. **Timed wait** (timeout > 0)
```cpp
int ready = poll(fds, nfds, 5000);  // Wait max 5 seconds

if (ready == 0) {
    // Timeout expired - no activity in 5 seconds
    handle_timeout();
}
```

**Comparison with select()**:

| Timeout | select() | poll() |
|---------|----------|--------|
| **Block forever** | NULL | -1 |
| **Non-blocking** | {0, 0} | 0 |
| **5 seconds** | {5, 0} | 5000 |
| **500 ms** | {0, 500000} | 500 |

**Key difference**: poll() uses milliseconds, select() uses microseconds (more precise).

---

#### Q5: How does poll() compare to select()? [INTERMEDIATE]


**:**

- Answer: poll() improves on select() in several ways but has similar O(n) complexity
- Comparison table:
- while (true) { read_fds = master_fds; // Must copy every time select(max_fd + 1, &read_fds, NULL, NULL, NULL);
- for (int fd = 0; fd <= max_fd; fd++) { if (FD_ISSET(fd, &read_fds)) { // Handle fd } } }
- // poll(): Simpler std::vector<struct pollfd> fds = { {fd1, POLLIN, 0}, {fd2, POLLIN, 0} };

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: How do you safely remove FDs during iteration? [INTERMEDIATE]


**:**

- Answer: Use backward iteration or mark-and-remove pattern to avoid iterator invalidation
- Why it works: ```cpp // fds = [A, B, C, D, E] // Iteration: i=4, i=3, i=2, i=1, i=0
- i=3: erase D // fds = [A, B, C, E] // Next: i=2 processes C (correct)
- i=0: erase A // fds = [B, C, E] // Done (no more iterations) ```
- Solution 2: Mark and remove ```cpp std::vector<int> to_remove;

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What is the free slot reuse pattern and why use it? [INTERMEDIATE]


**:**

- Answer: Instead of erasing elements from the pollfd array, mark slots as free (fd = -1) and reuse them later
- Traditional approach (expensive): ```cpp // ❌ Vector erase is O(n) - shifts all elements fds.erase(fds.begin() + index); // Moves elements [index+1, end) ```
- Free slot pattern: ```cpp std::queue<int> free_slots;
- O(1) removal (vs O(n) erase) 2
- Stable array size (no reallocation) 3

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: Why must you check POLLHUP after POLLIN? [INTERMEDIATE]


**:**

- Answer: POLLHUP and POLLIN can both be set simultaneously when client sends final data before closing
- The problem: ```cpp // ❌ Wrong order - misses final data if (pfd.revents & POLLHUP) { close(pfd.fd); // Closed without reading final data
- if (pfd.revents & POLLIN) { recv(pfd.fd, buffer, size, 0); // Never reached } ```
- The scenario: ```cpp // Client sends "goodbye" and immediately closes
- // Server side after poll(): pfd.revents = POLLIN | POLLHUP; // Both set

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: Explain poll()'s O(n) complexity and when it matters [INTERMEDIATE]


**:**

- >1,000 connections: Consider epoll() (Linux) or kqueue() (BSD)
- epoll() is O(num_active) not O(num_total)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: When should you use poll() vs select()? [INTERMEDIATE]


**:**

- **Web proxy** (10,000 connections): epoll()
- **Game server** (1,000 players): poll()
- **IoT gateway** (500 sensors): poll()
- **Chat server** (100 users): poll() or select()
- **Shell script** (2-3 pipes): select()

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: Is poll() level-triggered or edge-triggered? [ADVANCED]


**:**

- Simpler programming model
- No data loss risk
- POSIX standard (edge-triggered not portable)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12: How do you monitor write readiness with POLLOUT? [ADVANCED]


**:**

- Answer: Monitor POLLOUT only when you have data to send and handle partial sends correctly
- The pattern: ```cpp std::map<int, std::queue<std::string>> write_queues;
- // When data needs to be sent void queue_data(int fd, const std::string& data) { write_queues[fd].push(data);
- // ✅ Enable POLLOUT monitoring update_events(fd, POLLIN | POLLOUT); }
- // In poll() loop if (pfd.revents & POLLOUT) { if (!write_queues[pfd.fd].empty()) { std::string& data = write_queues[pfd.fd].front();

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: How do you optimize poll() for large FD arrays? [ADVANCED]


**:**

**Answer**: Use early exit, free slot reuse, and process only ready FDs.
**Optimization 1: Early exit**

```cpp
int ready = poll(fds.data(), fds.size(), -1);
int processed = 0;

for (auto& pfd : fds) {
    if (pfd.revents != 0) {
        handle_events(pfd);
        processed++;

        if (processed >= ready) {
            break;  // ✅ Processed all ready FDs, stop iterating
        }
    }
    // ... (additional code omitted for brevity)
```

- cpp int ready = poll(fds.data(), fds.size(), -1); int processed = 0;
- for (auto& pfd : fds) { if (pfd.revents != 0) { handle_events(pfd); processed++;
- if (processed >= ready) { break; // ✅ Processed all ready FDs, stop iterating } } }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: What is ppoll() and when should you use it? [ADVANCED]


**:**

**Answer**: ppoll() is Linux/BSD extension providing nanosecond timeout precision and signal masking.
**Function signature**:

```cpp
#include <poll.h>

int ppoll(struct pollfd *fds, nfds_t nfds,
          const struct timespec *timeout,  // ← Nanosecond precision
          const sigset_t *sigmask);         // ← Signal mask
```

- cpp #include <poll.h>
- int ppoll(struct pollfd *fds, nfds_t nfds, const struct timespec *timeout, // ← Nanosecond precision const sigset_t *sigmask); // ← Signal mask ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: How portable is poll() compared to select()? [ADVANCED]

**Answer**: poll() is POSIX standard but less portable than select() on very old systems.

**Portability matrix**:

| System | select() | poll() | ppoll() | epoll() |
|--------|----------|--------|---------|---------|
| Linux | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| BSD (FreeBSD/OpenBSD) | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (use kqueue) |
| macOS | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (use kqueue) |
| Solaris | ✅ Yes | ✅ Yes | ❌ No | ❌ No (use /dev/poll) |
| Windows | ✅ Yes (Winsock) | ❌ No | ❌ No | ❌ No (use IOCP) |
| AIX | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| POSIX.1-2001 | ✅ Standard | ✅ Standard | ❌ Extension | ❌ Linux-only |

**Historical context**:
```cpp
// select(): BSD 4.2 (1983) - 40+ years old
// poll(): SVR4 (1988), POSIX.1-2001

// Very old systems (pre-2001) may lack poll()
```

**Portable abstraction**:
```cpp
class IOMultiplexer {
public:
    virtual void add_fd(int fd, int events) = 0;
    virtual int wait(int timeout_ms) = 0;
};

#ifdef __linux__
class EpollMultiplexer : public IOMultiplexer { ... };
#elif defined(__FreeBSD__)
class KqueueMultiplexer : public IOMultiplexer { ... };
#elif defined(_WIN32)
class IOCPMultiplexer : public IOMultiplexer { ... };
#else
class PollMultiplexer : public IOMultiplexer { ... };
#endif
```

**Recommendation**:
- **Cross-platform library**: Use libevent or Boost.Asio (abstracts platform differences)
- **Linux-only**: Use epoll() directly
- **BSD-only**: Use kqueue() directly
- **Maximum portability**: Use select() (but accept 1024 FD limit)
- **Modern POSIX**: Use poll() (works on 99% of systems)

---

#### Q16: How do you migrate existing select() code to poll()? [EXPERT]


**:**

**Answer**: Convert fd_set bitmasks to pollfd arrays and adjust event checking logic.
**Migration steps**:
**Step 1: Replace fd_set with std::vector<pollfd>**

```cpp
// Before (select)
fd_set master_fds, read_fds;
FD_ZERO(&master_fds);
int max_fd = -1;

// After (poll)
std::vector<struct pollfd> fds;
```

- cpp // Before (select) fd_set master_fds, read_fds; FD_ZERO(&master_fds); int max_fd = -1;
- // After (poll) std::vector<struct pollfd> fds; ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: How do you enforce connection limits with poll()? [EXPERT]


**:**

**Answer**: Check current connection count before accepting and reject with meaningful error message.
**Implementation**:

```cpp
const int MAX_CLIENTS = 1000;
std::vector<struct pollfd> fds;
int current_connections = 0;

// In poll loop, handle new connections
if (pfd.fd == server_fd && (pfd.revents & POLLIN)) {
    struct sockaddr_in client_addr;
    socklen_t addr_len = sizeof(client_addr);
    int new_client = accept(server_fd, (struct sockaddr*)&client_addr, &addr_len);

    if (new_client < 0) {
        perror("accept");
    // ... (additional code omitted for brevity)
```

- cpp const int MAX_CLIENTS = 1000; std::vector<struct pollfd> fds; int current_connections = 0;
- if (new_client < 0) { perror("accept"); continue; }
- send(new_client, msg, strlen(msg), 0); close(new_client);

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: How do you debug performance issues with poll()? [EXPERT]


**:**

**Answer**: Profile poll() call time, event processing time, and identify bottlenecks.
**Step 1: Measure poll() call duration**

```cpp
auto start = std::chrono::high_resolution_clock::now();
int ready = poll(fds.data(), fds.size(), timeout_ms);
auto end = std::chrono::high_resolution_clock::now();

auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

if (duration.count() > 1000) {  // > 1ms
    log_warning("Slow poll() call: " + std::to_string(duration.count()) + " μs");
}
```

- cpp auto start = std::chrono::high_resolution_clock::now(); int ready = poll(fds.data(), fds.size(), timeout_ms); auto end = std::chrono::high_resolution_clock::now();
- auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
- if (duration.count() > 1000) { // > 1ms log_warning("Slow poll() call: " + std::to_string(duration.count()) + " μs"); } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: What are the security considerations with poll()? [EXPERT]


**:**

**Answer**: poll() has several security implications: resource exhaustion, slowloris attacks, and FD exhaustion.
**Attack 1: Connection exhaustion**

```cpp
// Attacker opens MAX_CLIENTS connections and holds them open

// ✅ Mitigation: Connection limits + timeouts
const int MAX_CLIENTS = 1000;
const int MAX_PER_IP = 10;
const int IDLE_TIMEOUT = 60;

// Reject if over limit (see Q17)
if (current_connections >= MAX_CLIENTS) {
    reject_connection(new_client, "503 Server Full");
}

    // ... (additional code omitted for brevity)
```

- cpp // Attacker opens MAX_CLIENTS connections and holds them open
- // ✅ Mitigation: Connection limits + timeouts const int MAX_CLIENTS = 1000; const int MAX_PER_IP = 10; const int IDLE_TIMEOUT = 60;
- // Reject if over limit (see Q17) if (current_connections >= MAX_CLIENTS) { reject_connection(new_client, "503 Server Full"); }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: When should you migrate from poll() to epoll()? [EXPERT]


**:**

**Answer**: Migrate when you have >1000 connections or need maximum performance on Linux.
**Decision criteria**:
| Metric | poll() OK | Consider epoll() |
|--------|-----------|------------------|

```cpp
// poll(): O(n) every call
poll(fds, 10000, -1);  // Kernel checks all 10,000 FDs

// epoll(): O(num_active)
epoll_wait(epfd, events, 100, -1);  // Kernel returns only 100 active
```

- cpp // poll(): O(n) every call poll(fds, 10000, -1); // Kernel checks all 10,000 FDs
- // epoll(): O(num_active) epoll_wait(epfd, events, 100, -1); // Kernel returns only 100 active ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
