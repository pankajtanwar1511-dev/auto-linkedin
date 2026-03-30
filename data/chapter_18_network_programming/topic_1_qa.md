## TOPIC: TCP/IP Socket Fundamentals - Building Network Applications

### INTERVIEW_QA: Comprehensive Questions and Answers

#### Q1: What is the difference between TCP and UDP? When would you use each?

**Difficulty:** #beginner
**Category:** #fundamentals #protocols
**Concepts:** #tcp #udp #reliability

**Answer:** TCP is connection-oriented and reliable; UDP is connectionless and unreliable.

**Explanation:**

**TCP (Transmission Control Protocol)**:
- Connection-oriented: 3-way handshake establishes connection before data transfer
- Reliable: Guarantees delivery with acknowledgments and retransmissions
- Ordered: Data arrives in the order sent (sequence numbers)
- Flow control: Prevents sender from overwhelming receiver
- Overhead: Higher latency and bandwidth usage due to reliability mechanisms

**UDP (User Datagram Protocol)**:
- Connectionless: No handshake, just send packets
- Unreliable: No delivery guarantee, packets may be lost or arrive out of order
- No flow control: Sender can overwhelm receiver
- Low overhead: Minimal headers, lower latency

**When to use TCP**:
- File transfers (FTP, HTTP)
- Email (SMTP)
- Remote shell (SSH)
- Any application where reliability is critical

**When to use UDP**:
- Real-time video/audio streaming (acceptable to drop frames)
- Online gaming (position updates, occasional loss is fine)
- DNS queries (lightweight, retry if needed)
- Sensor data streaming where latest data matters more than old data

**Autonomous vehicle example**:
- TCP: Downloading HD maps, receiving navigation routes
- UDP: Streaming lidar point clouds, broadcasting vehicle position to nearby vehicles

#### Q2: Explain the server socket lifecycle. What does each system call do?

**Difficulty:** #beginner
**Category:** #fundamentals #api
**Concepts:** #socket #bind #listen #accept

**Answer:**



**Explanation:**

- AF_INET: IPv4 address family
- SOCK_STREAM: TCP socket (SOCK_DGRAM for UDP)
- Returns file descriptor or -1 on error
- Associates the socket with a specific network interface and port
- Server must bind to know which port to listen on

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q3: What is SIGPIPE and how do you handle it?

**Difficulty:** #intermediate
**Category:** #error_handling #signals
**Concepts:** #sigpipe #send #msg_nosignal

**Answer:** SIGPIPE is sent when writing to a closed socket; handle by ignoring the signal or using MSG_NOSIGNAL.

**Explanation:**

When you write to a TCP socket whose peer has already closed the connection:
1. First write: Returns -1 with errno = EPIPE (broken pipe)
2. Second write: Kernel sends SIGPIPE signal to your process
3. Default SIGPIPE handler: **Terminate the process**

This is a common production bug where a single client disconnect crashes your entire server!

**Solution 1: Ignore SIGPIPE globally**
```cpp
signal(SIGPIPE, SIG_IGN);  // At program startup
```
Now send() returns -1 with errno = EPIPE instead of crashing.

**Solution 2: Use MSG_NOSIGNAL flag**
```cpp
send(fd, data, size, MSG_NOSIGNAL);
```
Prevents SIGPIPE for this specific send() call.

**Why this happens**: TCP sends RST (reset) when you write to a closed connection. The kernel knows the connection is dead and signals your application. The default action is termination because writing to a closed connection often indicates a programming error.

**Production recommendation**: Always use MSG_NOSIGNAL or ignore SIGPIPE globally. Check return values and handle EPIPE errors gracefully.

#### Q4: Why must you convert port numbers to network byte order with htons()?

**Difficulty:** #intermediate
**Category:** #portability #byte_order
**Concepts:** #htons #endianness #network_order

**Answer:** Network protocols use big-endian byte order; htons() converts from host to network order.

**Explanation:**

Multi-byte integers can be stored two ways in memory:
- **Big-endian**: Most significant byte first (0x1234 → [0x12] [0x34])
- **Little-endian**: Least significant byte first (0x1234 → [0x34] [0x12])

x86/x64 processors use little-endian. ARM can be either (usually little). Network protocols mandate **big-endian**.

**Example bug**:
```cpp
server_addr.sin_port = 5000;  // ❌ WRONG
```

On x86 (little-endian):
- 5000 decimal = 0x1388 hex
- Stored as: [0x88] [0x13] (little-endian)
- Network interprets as: 0x8813 = 34835 decimal
- Your server binds to port 34835 instead of 5000!

**Correct approach**:
```cpp
server_addr.sin_port = htons(5000);  // ✅ CORRECT
```

**Conversion functions**:
- htons(): host to network short (16-bit port)
- htonl(): host to network long (32-bit IP address)
- ntohs(): network to host short
- ntohl(): network to host long

**Mnemonic**: "h" = host, "n" = network, "s" = short (16-bit), "l" = long (32-bit)

**Why it's easy to miss**: On big-endian machines, htons() is a no-op, code works without it. But on little-endian (most modern systems), it's required. Always use conversion functions for portable code.

#### Q5: What happens if send() returns a value less than the requested length?

**Difficulty:** #intermediate
**Category:** #edge_cases #io
**Concepts:** #partial_send #send_all

**Answer:** Partial send occurred; must loop to send remaining data.

**Explanation:**

send() does **not** guarantee to send all requested bytes in one call. It returns the number of bytes actually sent, which may be less due to:
- Network buffer space limitations
- TCP send buffer full
- Network congestion
- Slow receiver

**Example bug**:
```cpp
char data[10000];
send(fd, data, 10000, 0);  // ❌ Assumes all 10000 bytes sent
```

Actual behavior:
```cpp
ssize_t sent = send(fd, data, 10000, 0);
// sent might be 6144, not 10000!
// Remaining 3856 bytes were NOT sent
```

**Correct pattern**:
```cpp
size_t total_sent = 0;
while (total_sent < length) {
    ssize_t bytes = send(fd, data + total_sent, length - total_sent, MSG_NOSIGNAL);
    if (bytes < 0) {
        if (errno == EINTR) continue;  // Interrupted, retry
        return -1;  // Real error
    }
    if (bytes == 0) break;  // Connection closed
    total_sent += bytes;
}
```

**Same applies to recv()**: May return less than requested, must loop to receive exact amount.

**Why this happens**: TCP uses sliding window flow control. If the receiver's buffer is full, send() can only send what fits in available buffer space.

**Production tip**: Always wrap send()/recv() in send_all()/recv_all() helpers that loop until complete.

#### Q6: What is SO_REUSEADDR and why is it important for servers?

**Difficulty:** #intermediate
**Category:** #socket_options #production
**Concepts:** #so_reuseaddr #time_wait #port_reuse

**Answer:** Allows binding to a port in TIME_WAIT state; essential for quick server restarts.

**Explanation:**

After closing a TCP connection, the port enters **TIME_WAIT** state (typically 60 seconds on Linux). This prevents delayed packets from old connections from interfering with new connections using the same port.

**Problem**:
```cpp
// Server crashes or restarts
bind(fd, ...);  // ❌ Error: Address already in use (EADDRINUSE)
```

You must wait 60 seconds before restarting your server on the same port!

**Solution**:
```cpp
int opt = 1;
setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
bind(fd, ...);  // ✅ Now succeeds immediately
```

**What SO_REUSEADDR does**:
- Allows binding to a port in TIME_WAIT state
- Allows multiple sockets to bind to same port (with SO_REUSEPORT)
- Does **not** allow binding if an active connection exists on that port

**When to use**:
- Always set on server listening sockets before bind()
- Critical for development (fast restart cycles)
- Essential for production (automated restarts, deployments)

**Security consideration**: On some systems, SO_REUSEADDR allows port hijacking if not careful. Modern systems require same user ID for reuse.

**TIME_WAIT exists for good reason**: Ensures old duplicate packets don't corrupt new connections. SO_REUSEADDR carefully bypasses this only when safe.

#### Q7: How do you handle multiple clients with a single-threaded server?

**Difficulty:** #advanced
**Category:** #concurrency #io_multiplexing
**Concepts:** #select #poll #epoll

**Answer:**



**Explanation:**

- One thread/process per client
- Simple but doesn't scale (C10K problem - 10,000 connections = 10,000 threads)
- High memory usage, context switching overhead
- select: O(n) scan, FD_SETSIZE limit (1024), portable
- poll: O(n) scan, no limit, portable

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: What is the listen() backlog parameter and how does it affect connection handling?

**Difficulty:** #intermediate
**Category:** #fundamentals #performance
**Concepts:** #listen #backlog #connection_queue

**Answer:** Backlog sets the maximum number of pending connections in the SYN queue.

**Explanation:**

```cpp
listen(server_fd, backlog);
```

The backlog parameter controls the **completed connection queue** size—connections that have completed the 3-way handshake but haven't been accept()ed yet.

**Connection flow**:
1. Client sends SYN
2. Server sends SYN-ACK
3. Client sends ACK → connection moves to **completed queue**
4. accept() removes connection from queue

**If queue is full**: New connections are **refused** (client gets connection refused error).

**Typical values**:
- Small servers: 5-10
- Medium servers: 128
- High-traffic servers: 1024 or SOMAXCONN

**Real-world scenario**:
```cpp
listen(fd, 5);  // Backlog of 5

// 6 clients connect rapidly
// Clients 1-5: Queued, waiting for accept()
// Client 6: Connection refused (queue full)
```

**Tuning consideration**:
- Too small: Connection refused errors during traffic bursts
- Too large: Memory usage, longer SYN flood attack surface

**Production tip**: Set backlog to at least 128 for production servers. Use SOMAXCONN constant for system maximum:
```cpp
listen(fd, SOMAXCONN);
```

**Historical note**: Modern Linux interprets backlog as sum of SYN queue + completed queue. Actual behavior is system-dependent.

#### Q9: How would you implement a timeout for connect()?

**Difficulty:** #advanced
**Category:** #timeouts #non_blocking
**Concepts:** #connect #select #timeout

**Answer:**



**Explanation:**

- Problem: connect() can block for 75+ seconds if server is unreachable
- Solution: Non-blocking connect + select()
- // Attempt connection int result = connect(fd, (sockaddr*)addr, sizeof(*addr));
- if (result < 0) { if (errno != EINPROGRESS) { return false; // Real error }
- // Connection in progress, wait with timeout fd_set write_fds; FD_ZERO(&write_fds); FD_SET(fd, &write_fds);

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: Explain the difference between close() and shutdown(). When would you use each?

**Difficulty:** #intermediate
**Category:** #connection_management #api
**Concepts:** #close #shutdown #half_close

**Answer:**



**Explanation:**

- Decrements reference count on file descriptor
- If reference count reaches 0, sends FIN to peer
- Closes both sending and receiving
- File descriptor becomes invalid
- Closes one or both directions **without** releasing FD

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: What causes EINTR errors and how should you handle them?

**Difficulty:** #intermediate
**Category:** #error_handling #signals
**Concepts:** #eintr #signals #system_calls

**Answer:**



**Explanation:**

- recv(), send(), accept(), connect()
- read(), write()
- select(), poll(), epoll_wait()
- Any blocking system call

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12: How do you detect if a peer has closed the connection?

**Difficulty:** #beginner
**Category:** #connection_management #io
**Concepts:** #recv #eof #connection_close

**Answer:**



**Explanation:**

- **> 0**: Number of bytes received (success)
- **0**: Peer closed connection (EOF - End Of File)
- **< 0**: Error (check errno)
- TCP sends RST (reset) packet
- Server's recv() returns -1 with errno = ECONNRESET

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: What is the C10K problem and how is it solved?

**Difficulty:** #advanced
**Category:** #scalability #performance
**Concepts:** #c10k #epoll #io_multiplexing

**Answer:**



**Explanation:**

- O(n) complexity: Must scan all FDs on every call
- FD_SETSIZE limit: 1024 FDs maximum (select)
- Must rebuild FD set each call
- Performance degrades linearly with connection count
- O(1) complexity: Kernel maintains interest list

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: What is the purpose of inet_pton() and inet_ntop()? Why not use inet_addr()?

**Difficulty:** #intermediate
**Category:** #address_conversion #api
**Concepts:** #inet_pton #inet_ntop #ipv6

**Answer:**



**Explanation:**

- **p** = presentation (human-readable string)
- **n** = network (binary format)
- pton = "printable to network"
- ntop = "network to printable"

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: How would you implement a simple protocol for sending variable-length messages?


**Concepts:**



**Answer:**



**Explanation:**

**Problem**: TCP is a stream protocol—it doesn't preserve message boundaries.
**Example**:

```cpp
send(fd, "HELLO", 5);
send(fd, "WORLD", 5);

// Receiver might get:
recv() → "HELLO"    (lucky - message boundary preserved)
recv() → "WORLD"

// Or might get:
recv() → "HELLOW"   (messages merged - boundary lost!)
recv() → "ORLD"
```

- cpp send(fd, "HELLO", 5); send(fd, "WORLD", 5);
- // Receiver might get: recv() → "HELLO" (lucky - message boundary preserved) recv() → "WORLD"
- // Or might get: recv() → "HELLOW" (messages merged - boundary lost!) recv() → "ORLD" ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16: What are the advantages and disadvantages of non-blocking sockets?


**Concepts:**



**Answer:**



**Explanation:**

**Blocking sockets** (default):

```cpp
char buffer[1024];
recv(fd, buffer, sizeof(buffer), 0);  // ⏸️ Waits until data arrives
```

- cpp char buffer[1024]; recv(fd, buffer, sizeof(buffer), 0); // ⏸️ Waits until data arrives ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: Explain the TCP 3-way handshake. What happens during connect() and accept()?


**Concepts:**



**Answer:**



**Explanation:**

**3-Way Handshake** establishes TCP connection:

```cpp
Client                                  Server
  |                                       |
  | ─────── SYN (seq=X) ────────────────> |  connect() called
  |                                       |  (blocks here)
  | <────── SYN-ACK (seq=Y, ack=X+1) ──── |  listen() → accept() called
  |                                       |  (waiting)
  | ─────── ACK (ack=Y+1) ───────────────> |
  |                                       |  accept() returns
  | <═══ Connection Established ════════> |
  |                                       |
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: How do you implement keep-alive for long-lived connections?


**Concepts:**



**Answer:**



**Explanation:**

**Problem**: How to detect if peer has crashed or network is severed without sending data?
**Solution 1: TCP Keep-Alive** (OS-level):

```cpp
int enable = 1;
setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable));

// Fine-tune keep-alive parameters (Linux)
int idle = 60;        // Start probing after 60 seconds idle
int interval = 10;    // Send probe every 10 seconds
int count = 5;        // 5 failed probes = connection dead

setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle));
setsockopt(fd, IPPROTO_TCP, TCP_KEEPINTVL, &interval, sizeof(interval));
setsockopt(fd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count));
```

- cpp int enable = 1; setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enable, sizeof(enable));

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: What is the difference between recv() and recvfrom()? When do you use each?


**Concepts:**



**Answer:**



**Explanation:**

**recv()** - For connection-oriented protocols (TCP):

```cpp
ssize_t recv(int socket_fd, void* buffer, size_t length, int flags);
```

- cpp ssize_t recv(int socket_fd, void* buffer, size_t length, int flags); ``` - Used with connected sockets (TCP) - Source address is known (established connection) - Returns received data length

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: What is the file descriptor limit and how do you handle it in server applications?


**Concepts:**



**Answer:**



**Explanation:**

**The Problem**:
Each process has a **maximum number of file descriptors** (FDs) it can open. Sockets are file descriptors!

```cpp
$ ulimit -n
1024    # Default soft limit on many systems
```

- bash $ ulimit -n 1024 # Default soft limit on many systems ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
