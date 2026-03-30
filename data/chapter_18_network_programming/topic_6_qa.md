### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: When should you use sendfile() vs traditional read()/write()? What are the performance implications?


**Answer:**
**When to use sendfile():**
- Serving static files (HTTP/FTP file servers)
- Proxying large binary data between sockets
- Any file-to-socket transfer where data doesn't need modification
- Requirements: Linux kernel 2.2+, file and socket must support sendfile
**When NOT to use sendfile():**
- Data transformation needed (compression, encryption)
- Cross-platform requirement (sendfile is Linux-specific)
- Small files (<4KB) where overhead dominates
- Non-file sources (memory buffers, pipes)
**Performance implications:**
```cpp
// Traditional approach: 2 copies + 2 context switches
char buffer[8192];
while ((n = read(file_fd, buffer, sizeof(buffer))) > 0) {
    write(socket_fd, buffer, n);
}
// Data path: Disk → Kernel → User space → Kernel → Network
// CPU copies: 2 (kernel→user, user→kernel)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q2: Explain the difference between Reactor and Proactor patterns. Which would you use for a high-traffic web server?


**Answer:**



**Reactor Pattern (Synchronous I/O):**

```cpp
Application registers interest → epoll_wait() returns → Application calls recv()
```

- Application registers interest → epoll_wait() returns → Application calls recv() ```

**Proactor Pattern (Asynchronous I/O):**

```cpp
Application submits read request → Kernel performs I/O → Kernel notifies completion
```

- Application submits read request → Kernel performs I/O → Kernel notifies completion ```

**Recommendation for high-traffic web server:**

- Linux-only deployment
- Network I/O is proven bottleneck (profiling shows recv/send dominating CPU)
- Team has expertise in async I/O debugging
- Willing to invest in cutting-edge tech (io_uring still evolving)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3: How do you detect and handle stale connections in a connection pool? What's the cost of not handling them?


**Answer:**
**Detection strategies:**
**1. Health check on acquire (Recommended):**
```cpp
int acquire() {
    while (!available.empty()) {
        int fd = available.front();
        available.pop();
        // Send 0 bytes with MSG_DONTWAIT (doesn't block)
        int err = send(fd, nullptr, 0, MSG_DONTWAIT | MSG_NOSIGNAL);
        if (err == 0) {
            return fd;  // Healthy
        } else if (errno == ENOTCONN || errno == EPIPE) {
            close(fd);  // Stale, discard
    // ... (additional code omitted for brevity)
```
**Cost:**
**2. TCP keepalive (Background probing):**
```cpp
int enable_keepalive(int fd) {
    int optval = 1;
    setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval));
    // Start probing after 60s idle
    optval = 60;
    setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &optval, sizeof(optval));
    // Probe every 10s
    optval = 10;
    setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &optval, sizeof(optval));
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4: Compare round-robin, least-connections, and consistent hashing load balancing. When would you use each?


**Answer:**
**1. Round-Robin:**
```cpp
int select_backend() {
    int backend = current_backend;
    current_backend = (current_backend + 1) % backends.size();
    return backend;
}
```
- cpp int select_backend() { int backend = current_backend; current_backend = (current_backend + 1) % backends.size(); return backend; } ```
**Pros:**
- Simple, fast (O(1))
- Fair distribution (each backend gets equal requests)
- Stateless (no memory overhead)
**Cons:**
- Ignores backend load (slow backend gets same traffic)
- Ignores request cost (heavy requests not distributed evenly)
**Use when:**
- All backends have equal capacity
- Requests have similar cost
- Backends are stateless (no session affinity needed)
- **Example:** Serving static files, stateless API endpoints
```cpp
int select_backend() {
    int min_conn = INT_MAX;
    int selected = 0;
    for (int i = 0; i < backends.size(); i++) {
        if (backends[i].active_connections < min_conn) {
            min_conn = backends[i].active_connections;
            selected = i;
        }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5: Explain the circuit breaker pattern. How does it prevent cascading failures?


**Answer:**
**Problem:**
```cpp
Client → Proxy → Backend (down)
```
- Client → Proxy → Backend (down) ```
- Without circuit breaker: 1
- Backend fails → Proxy retries → 10s timeout 2
**Three states:**
```cpp
CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing) → CLOSED
```
- CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing) → CLOSED ```
**State machine:**
```cpp
class CircuitBreaker {
    enum class State { CLOSED, OPEN, HALF_OPEN };
    State state = State::CLOSED;
    int failure_count = 0;
    std::chrono::steady_clock::time_point opened_at;
    const int FAILURE_THRESHOLD = 5;
    const std::chrono::seconds TIMEOUT{30};
    bool allow_request() {
        auto now = std::chrono::steady_clock::now();
    // ... (additional code omitted for brevity)
```
**How it prevents cascading failures:**
- Backend is known to be down
- Immediately return error (no 10s timeout)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: How do you implement application-level flow control to prevent overwhelming downstream services?


**Answer:**
**Problem:**
```cpp
Fast Producer (1000 req/s) → Network → Slow Consumer (100 req/s)
```
- Fast Producer (1000 req/s) → Network → Slow Consumer (100 req/s) ```
- Without flow control: - Producer sends 1000 req/s → Consumer's receive buffer fills → TCP window shrinks → Producer blocks on send() -
**Solution 1: Token Bucket (Rate Limiting):**
```cpp
class TokenBucket {
    const int capacity = 100;  // Max burst
    const int refill_rate = 10;  // Tokens per second
    int tokens = capacity;
    std::chrono::steady_clock::time_point last_refill;
    bool try_consume(int n = 1) {
        refill();
        if (tokens >= n) {
            tokens -= n;
    // ... (additional code omitted for brevity)
```
- // Usage if (bucket.try_consume()) { send_request(downstream); } else { // Back off: queue request or return 429 Too Many Requests queue.push(request); } ```
**Pros:**
- Allows bursts (up to capacity)
- Smooth rate limiting
- Simple to implement
**Cons:**
- Doesn't adapt to downstream capacity
- Fixed rate (may be too conservative or aggressive)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What's the difference between SIGPIPE and EPIPE? How do you handle each in production?


**Answer:**
**SIGPIPE (Signal):**
- **When it occurs:** write() or send() to a socket with peer's receive side closed
- **Default behavior:** Process terminates immediately
- **Problem:** Crashes entire server on single client disconnect
**Example:**
```cpp
// Client closes connection
close(client_fd);
// Server writes without checking
send(client_fd, data, size, 0);  // ← SIGPIPE kills server process!
```
- cpp // Client closes connection close(client_fd);
- // Server writes without checking send(client_fd, data, size, 0); // ← SIGPIPE kills server process
**EPIPE (Error Code):**
- **When it occurs:** Same as SIGPIPE, but when signal is blocked
- **Behavior:** send() returns -1, errno = EPIPE
- **Benefit:** Graceful error handling (no crash)
**Production handling:**
**Solution 1: Block SIGPIPE globally (Recommended):**
```cpp
// Block SIGPIPE for entire process
signal(SIGPIPE, SIG_IGN);
// Now send() returns EPIPE instead of killing process
ssize_t sent = send(fd, data, size, 0);
if (sent < 0 && errno == EPIPE) {
    std::cerr << "Client disconnected\n";
    close(fd);
}
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: How do you handle the EMFILE (too many open files) error in a high-traffic server?


**Answer:**
- EMFILE: Process file descriptor limit exceeded
**Typical limits:**
```cpp
$ ulimit -n
1024  # Default per-process limit
$ cat /proc/sys/fs/file-max
1000000  # System-wide limit
```
- bash $ ulimit -n 1024 # Default per-process limit
- $ cat /proc/sys/fs/file-max 1000000 # System-wide limit ```
**Problem:**
```cpp
int client_fd = accept(listen_fd, nullptr, nullptr);
if (client_fd < 0) {
    if (errno == EMFILE) {
        // ❌ Out of file descriptors!
        // Can't accept new connections
        // Existing connections still work
    }
}
```
- cpp int client_fd = accept(listen_fd, nullptr, nullptr); if (client_fd < 0) { if (errno == EMFILE) { // ❌ Out of file descriptors
- // Can't accept new connections // Existing connections still work } } ```
**Solution 1: Increase ulimit (Preventive):**
```cpp
# Temporary (current shell)
ulimit -n 100000
# Permanent (systemd service)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: Explain TCP keepalive vs application-level heartbeats. When do you need both?


**Answer:**
**TCP Keepalive (Transport Layer):**
```cpp
int enable_keepalive(int fd) {
    int optval = 1;
    setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &optval, sizeof(optval));
    // Start probing after 60 seconds of idle
    optval = 60;
    setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &optval, sizeof(optval));
    // Send probe every 10 seconds
    optval = 10;
    setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &optval, sizeof(optval));
    // ... (additional code omitted for brevity)
```
**How it works:**
- Connection idle for 60s → Send TCP keepalive probe (empty ACK) 2
- Peer responds → Connection alive 3
- No response after 10s → Send another probe 4
- After 3 failed probes (30s total) → Connection declared dead → recv() returns 0
**Pros:**
- Automatic (kernel handles it)
- No application code needed
- Detects network failures (cable unplugged, peer crashed)
**Cons:**
- Long detection time (60s + 30s = 90 seconds by default)
- Only detects TCP-level failures (not application hangs)
- OS-specific (Windows uses different defaults)
- Probe packets may be dropped by middleboxes (NAT, firewall)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: How do you implement zero-downtime configuration reload for a network server?


**Answer:**
**Approaches:**
**1. SIGHUP signal handler (Recommended):**
```cpp
#include <signal.h>
#include <atomic>
std::atomic<bool> reload_config{false};
void sighup_handler(int) {
    reload_config.store(true);
}
int main() {
    // Register signal handler
    signal(SIGHUP, sighup_handler);
    // ... (additional code omitted for brevity)
```
- cpp #include <signal.h> #include <atomic>
- std::atomic<bool> reload_config{false};
- void sighup_handler(int) { reload_config.store(true); }
**Usage:**
```cpp
# Send SIGHUP to reload
kill -HUP $(pidof myserver)
# Or with systemd
systemctl reload myserver
```
- bash # Send SIGHUP to reload kill -HUP $(pidof myserver)
- # Or with systemd systemctl reload myserver ```
**Pros:**
- Zero downtime (server keeps running)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: Compare epoll edge-triggered (EPOLLET) vs level-triggered mode. When is each appropriate?


**Answer:**
**Level-Triggered (Default):**
```cpp
Behavior: epoll_wait() returns as long as data is available
```
- Behavior: epoll_wait() returns as long as data is available ```
**Pros:**
- Forgiving (won't miss data even if you don't drain socket)
- Simple (can use blocking recv())
- Compatible with traditional I/O patterns
**Cons:**
- Performance: epoll_wait() returns repeatedly if socket not drained
- Must drain socket or remove from epoll
**Edge-Triggered (EPOLLET):**
```cpp
Behavior: epoll_wait() returns only on state change (new data arrived)
```
- Behavior: epoll_wait() returns only on state change (new data arrived) ```
- // ✅ MUST set non-blocking int flags = fcntl(fd, F_GETFL, 0); fcntl(fd, F_SETFL, flags | O_NONBLOCK);
**Pros:**
- High performance (fewer epoll_wait() returns)
- Scalability (won't thrash with many sockets)
- Precise control (know exactly when new data arrives)
**Cons:**
- Must drain socket completely (complex)
- Must use non-blocking I/O (otherwise recv() blocks)
- Easy to introduce bugs (missed data if not careful)
**Comparison:**
**When to use each:**
**Level-Triggered (Recommended for most cases):**
- Default choice (safer)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12: How do you design a wire protocol for a custom network service? What are the key considerations?


**Answer:**
**Key considerations:**
- Framing (How to delimit messages) 2
- Encoding (How to represent data) 3
- Versioning (How to evolve protocol) 4
- Error handling (How to signal failures) 5
- Performance (Latency, throughput, overhead)
- Framing Strategies:**
**a) Length-prefixed (Recommended):**
```cpp
Wire format: [4-byte length][payload]
Example:
[0x00 0x00 0x00 0x0A]"Hello World"
 ↑ Length = 10        ↑ 10 bytes
```
- Wire format: [4-byte length][payload]
- Example: [0x00 0x00 0x00 0x0A]"Hello World" ↑ Length = 10 ↑ 10 bytes ```
**Pros:**
- Binary-safe (can send any data)
- No escaping needed
- Efficient parsing (know exact length upfront)
**Cons:**
- Must buffer complete message before processing
- 4-byte overhead per message
**b) Delimiter-based (Text protocols):**
```cpp
Wire format: [payload]\n
Example: "GET /index.html HTTP/1.1\r\n"
```
- Wire format: [payload]\n
- Example: "GET /index.html HTTP/1.1\r\n" ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: Explain how to implement request timeouts in a non-blocking network server.


**Answer:**
**Problem:**
```cpp
Client sends request → Server waits for database → Database hangs → Request never completes
```
- Client sends request → Server waits for database → Database hangs → Request never completes ```
- Without timeout: Server thread/FD blocked forever
**Solution:**
**Implementation 1: Per-request timeout (Simple):**
```cpp
struct Request {
    int client_fd;
    std::string data;
    std::chrono::steady_clock::time_point start_time;
    std::chrono::seconds timeout{30};
};
std::unordered_map<int, Request> active_requests;
void handle_request(int client_fd, const std::string& data) {
    Request req;
    req.client_fd = client_fd;
    // ... (additional code omitted for brevity)
```
- cpp struct Request { int client_fd; std::string data; std::chrono::steady_clock::time_point start_time; std::chrono::seconds timeout{30}; };
- std::unordered_map<int, Request> active_requests;
**Pros:**
- Simple
- Works for any async operation
**Cons:**
- O(N) timeout checks (N = active requests)
- 1-second resolution (may timeout 0-1s late)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: How do you implement connection draining for graceful shutdown?


**Answer:**
**Problem:**
```cpp
Server receives SIGTERM → Immediately exits → In-flight requests lost
```
- Server receives SIGTERM → Immediately exits → In-flight requests lost ```
**Goal:**
- Stop accepting new connections 2
- Wait for in-flight requests to complete 3
- Close idle connections 4
**Implementation:**
```cpp
#include <signal.h>
#include <atomic>
std::atomic<bool> shutdown_requested{false};
void sigterm_handler(int) {
    shutdown_requested.store(true);
}
struct Connection {
    int fd;
    std::chrono::steady_clock::time_point last_activity;
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: Compare SO_REUSEADDR vs SO_REUSEPORT. When do you need each?


**Answer:**
**SO_REUSEADDR:**
```cpp
int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
int optval = 1;
setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));
bind(listen_fd, ...);  // Can bind even if previous socket in TIME_WAIT
```
- cpp int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
- int optval = 1; setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));
- bind(listen_fd, ...); // Can bind even if previous socket in TIME_WAIT ```
**What it does:**
- Allows binding to address in TIME_WAIT state
- TIME_WAIT: TCP state after close() (lasts 2*MSL = 60-120 seconds)
**Problem without SO_REUSEADDR:**
```cpp
$ ./server
Server listening on 0.0.0.0:8080
^C  # Ctrl-C (SIGINT)
Server exited
$ ./server
bind(): Address already in use  # ❌ Can't restart for 60s!
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16: How do you implement fair scheduling between connections to prevent starvation?


**Answer:**
**Problem:**
```cpp
1 client sends 1 GB file (100,000 packets)
99 clients send 1 KB requests each
Without fair scheduling:
- epoll_wait() returns for 1 GB client 100,000 times
- Other 99 clients starve (high latency)
```
- 1 client sends 1 GB file (100,000 packets) 99 clients send 1 KB requests each
- Without fair scheduling: - epoll_wait() returns for 1 GB client 100,000 times - Other 99 clients starve (high latency) ```
**Goal:**
**Solution 1: Round-robin with quota (Recommended):**
```cpp
struct Connection {
    int fd;
    std::deque<std::string> write_queue;
    int bytes_sent_this_round = 0;
};
const int MAX_BYTES_PER_ROUND = 64 * 1024;  // 64 KB quota
std::unordered_map<int, Connection> connections;
std::deque<int> ready_queue;  // Connections with data to send
void handle_write_ready(int fd) {
    // ... (additional code omitted for brevity)
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: Explain TCP_NODELAY and TCP_CORK. When should you use each?


**Answer:**
**Nagle's Algorithm (Default TCP Behavior):**
```cpp
Goal: Reduce small packet overhead
Rule: If unsent data < MSS (1460 bytes), wait for:
1. ACK for previous data, OR
2. Enough data to fill MSS
```
- Goal: Reduce small packet overhead
- Rule: If unsent data < MSS (1460 bytes), wait for: 1
- ACK for previous data, OR 2
**Example:**
```cpp
send(fd, "GET ", 4, 0);  // Sent immediately (first packet)
send(fd, "/index.html", 11, 0);  // Buffered (waiting for ACK or more data)
send(fd, " HTTP/1.1\r\n", 11, 0);  // Buffered
// ... 40ms delay waiting for ACK ...
// Finally sent when ACK arrives
```
- cpp send(fd, "GET ", 4, 0); // Sent immediately (first packet) send(fd, "/index.html", 11, 0); // Buffered (waiting for ACK or more data) send(fd, " HTTP/1.1\r\n", 11, 0); // Buffered // ..
- 40ms delay waiting for ACK ..
- // Finally sent when ACK arrives ```
**Result:**
---
**TCP_NODELAY: Disable Nagle's Algorithm**
```cpp
int optval = 1;
setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &optval, sizeof(optval));
send(fd, "GET ", 4, 0);  // Sent immediately ✅
send(fd, "/index.html", 11, 0);  // Sent immediately ✅
send(fd, " HTTP/1.1\r\n", 11, 0);  // Sent immediately ✅

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: How do you monitor and debug network performance issues in production?


**Answer:**
**Key metrics to monitor:**
1. **Throughput:** Bytes/sec, requests/sec
2. **Latency:** p50, p95, p99 response time
3. **Errors:** Connection failures, timeouts
4. **Resource usage:** CPU, memory, file descriptors
```cpp
struct ConnectionMetrics {
    std::atomic<uint64_t> bytes_sent{0};
    std::atomic<uint64_t> bytes_received{0};
    std::atomic<uint64_t> requests_handled{0};
    std::atomic<uint64_t> errors{0};
    std::deque<std::chrono::milliseconds> latencies;
    std::mutex latency_mutex;
};
ConnectionMetrics metrics;
    // ... (additional code omitted for brevity)
```
- ConnectionMetrics metrics;
**Key metrics:**
- **RTT (tcpi_rtt):** Round-trip time (network latency)
- **Retransmits:** Packet loss (network issues)
- **Congestion window:** TCP throughput capacity
- **Send queue (tcpi_notsent_bytes):** Application sending too fast
```cpp
# Monitor network interface
$ ifconfig eth0
RX bytes:1000000000 (1 GB)  TX bytes:500000000 (500 MB)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: What are the security implications of network programming? How do you mitigate common attacks?


**Answer:**
**Common attacks:**
- SYN flood (DoS) 2
- Slowloris (Slow HTTP) 3
- Buffer overflow 4
- Injection attacks 5
- Man-in-the-middle (MITM)
**Attack:**
```cpp
Attacker sends many SYN packets with spoofed source IP
Server responds with SYN-ACK (waits for ACK)
Attacker never sends ACK
→ Server's listen backlog fills → accept() fails → DoS
```
- Attacker sends many SYN packets with spoofed source IP Server responds with SYN-ACK (waits for ACK) Attacker never sends ACK → Server's listen backlog fills → accept() fails → DoS ```
**Mitigation:**
**a) SYN Cookies (Kernel-level):**
```cpp
# Enable SYN cookies
$ sudo sysctl -w net.ipv4.tcp_syncookies=1
```
- bash # Enable SYN cookies $ sudo sysctl -w net.ipv4.tcp_syncookies=1 ```
**How it works:**
- Don't allocate connection state for SYN
- Encode state in ISN (Initial Sequence Number)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: How do you optimize network code for modern multi-core CPUs?


**Answer:**
**Key principles:**
1. **Minimize lock contention**
2. **Maximize cache locality**
3. **Distribute work across cores**
4. **Avoid false sharing**
```cpp
for (int i = 0; i < NUM_CORES; i++) {
    std::thread([i]() {
        // Each thread creates own listen socket
        int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
        int optval = 1;
        setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval));
        bind(listen_fd, ...);  // All bind to same port
        listen(listen_fd, SOMAXCONN);
        // Each thread has own epoll (no shared state!)
    // ... (additional code omitted for brevity)
```
**Benefits:**
- ✅ No shared epoll (no lock contention)
- ✅ Each core handles own connections (cache locality)
- ✅ Kernel load-balances (same client → same core → better caching)
**Scalability:**
---
**2. Lock-free data structures:**
```cpp
// ❌ BAD: Shared queue with mutex
std::queue<int> work_queue;
std::mutex queue_mutex;
void producer() {
    std::lock_guard<std::mutex> lock(queue_mutex);  // Contention!

**Note:** Full detailed explanation with additional examples available in source materials.

---
