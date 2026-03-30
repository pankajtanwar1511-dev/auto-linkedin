## TOPIC: Multi-Client Server Patterns - Scaling Beyond One Connection

### INTERVIEW_QA: Comprehensive Questions and Answers

#### Q1: What are the main approaches to handle multiple clients? Compare them.

**Difficulty:** #beginner
**Category:** #concurrency #fundamentals
**Concepts:** #fork #threads #thread_pool #io_multiplexing

**Answer:** Fork (process per client), threads (thread per client), thread pool, and I/O multiplexing (select/poll/epoll).

**Explanation:**

**1. Fork-based (Process per client)**:
- Creates new process for each client using fork()
- Strong isolation (separate memory)
- Heavy resource usage, slower
- Best for < 100 clients

**2. Thread-based (Thread per client)**:
- Creates new thread for each client
- Shared memory, lighter than fork
- Faster creation, better scalability
- Best for 100-1000 clients

**3. Thread Pool**:
- Pre-creates fixed number of threads
- Threads reused for multiple clients
- No creation overhead, bounded resources
- Best for high-throughput servers

**4. I/O Multiplexing (select/poll/epoll)**:
- Single thread monitors multiple sockets
- Most scalable (10,000+ clients)
- Most complex to implement
- Best for massive scale

**Choosing strategy**:
- **Small scale (< 100)**: Fork or threads, simplicity matters
- **Medium scale (100-1000)**: Threads or thread pool
- **Large scale (1000+)**: Thread pool + epoll
- **Massive scale (10,000+)**: Pure event-driven (epoll/kqueue)

**Interview tip**: Explain trade-offs, mention you'd choose based on requirements (scale, complexity budget, performance needs).

#### Q2: What is a zombie process and how do you prevent it in fork-based servers?

**Difficulty:** #intermediate
**Category:** #fork #process_management
**Concepts:** #zombie #sigchld #waitpid

**Answer:** Zombie is a terminated child process whose exit status hasn't been reaped; prevent with SIGCHLD handler calling waitpid().

**Explanation:**

**What is a zombie**:
- Child process that finished execution (called exit())
- Still has entry in process table
- Parent hasn't called wait()/waitpid() to read exit status
- Shows as `<defunct>` in ps output

**Why zombies are bad**:
- Consume process table entries (finite resource)
- Eventually can't create new processes (fork() fails EAGAIN)
- Can't be killed (already dead, waiting for parent to reap)
- Only fix is reboot or parent process termination

**Solution 1: SIGCHLD handler**:
```cpp
void sigchld_handler(int sig) {
    int saved_errno = errno;
    while (waitpid(-1, NULL, WNOHANG) > 0);  // Reap all dead children
    errno = saved_errno;
}

signal(SIGCHLD, sigchld_handler);
```

**Solution 2: Double fork trick**:
```cpp
if (fork() == 0) {
    if (fork() == 0) {
        // Grandchild handles client
        handle_client();
        exit(0);
    }
    exit(0);  // Middle child exits immediately
}
wait(NULL);  // Parent reaps middle child
// Grandchild is orphaned, adopted by init (PID 1), which reaps it
```

**Key points**:
- waitpid() with WNOHANG flag (non-blocking)
- Loop to reap multiple zombies
- Save/restore errno (signal handler can interrupt syscalls)
- SA_RESTART flag to restart interrupted system calls

#### Q3: Why must you close file descriptors after fork() in both parent and child?

**Difficulty:** #intermediate
**Category:** #fork #file_descriptors
**Concepts:** #fd_leak #reference_counting

**Answer:** fork() duplicates file descriptors; both parent and child have references, causing FD leaks if not closed properly.

**Explanation:**

**How fork() handles FDs**:
- fork() duplicates all open file descriptors to child
- Both parent and child have separate FD numbers pointing to same underlying file
- Kernel maintains reference count for each file

**Example**:
```cpp
int client_fd = accept(server_fd, ...);  // ref count = 1
pid_t pid = fork();                      // ref count = 2 (parent + child)

if (pid == 0) {
    // Child
    close(server_fd);   // Child doesn't need listening socket
    handle_client(client_fd);
    close(client_fd);   // ref count = 1 (parent still has it)
    exit(0);
}

// Parent
close(client_fd);      // ✅ MUST close! ref count = 0, connection actually closes
```

**What happens if parent forgets to close client_fd**:
- Child closes its copy (ref count = 1)
- Connection stays open because parent still has reference
- Client doesn't receive FIN, connection hangs
- Parent accumulates FDs, eventually hits EMFILE

**General rule**:
- **Child closes**: FDs it doesn't need (typically server_fd)
- **Parent closes**: FDs it doesn't need (typically client_fd)

**Verification**:
```bash
# Check open FDs for process
ls /proc/<PID>/fd | wc -l
```

If count keeps growing, you have an FD leak.

#### Q4: What is a race condition? Give an example in multi-threaded server.


**Concepts:**



**Answer:**



**Explanation:**

**Example**: Client counter

```cpp
int client_count = 0;  // Shared by all threads

void handle_client() {
    client_count++;  // ❌ Race condition!
    // ...
    client_count--;
}
```

- cpp int client_count = 0; // Shared by all threads
- void handle_client() { client_count++; // ❌ Race condition
- client_count--; } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5: What is thread detachment? When should you detach vs join threads?

**Difficulty:** #intermediate
**Category:** #threads #lifecycle
**Concepts:** #detach #join #thread_lifecycle

**Answer:**



**Explanation:**

- **Joinable** (default): Parent can wait for completion with join()
- **Detached**: Runs independently, resources auto-cleaned on exit
- Blocks calling thread until t finishes
- Allows retrieving return value/exception
- Thread resources freed after join() returns

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q6: How does a thread pool work? What are its advantages over creating threads per client?

**Difficulty:** #intermediate
**Category:** #thread_pool #performance
**Concepts:** #thread_reuse #bounded_resources #condition_variable

**Answer:**



**Explanation:**

- Fixed memory usage (8 threads × 8MB = 64MB, regardless of client count)
- Predictable behavior under load
- Can't exhaust system resources
- Thread count matches CPU cores (no context switching overhead)
- 8 cores = 8 threads = maximum parallelism without contention

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q7: What is std::condition_variable and why is it used in thread pools?


**Concepts:**



**Answer:**



**Explanation:**

**Problem without condition_variable** (busy-waiting):

```cpp
std::mutex queue_mutex;
std::queue<int> client_queue;

void worker_thread() {
    while (true) {
        std::lock_guard<std::mutex> lock(queue_mutex);
        if (!client_queue.empty()) {
            int fd = client_queue.front();
            client_queue.pop();
            // Handle client
        }
        // ❌ Spin loop - wastes 100% CPU checking empty queue!
    }
}
```

- cpp std::mutex queue_mutex; std::queue<int> client_queue;

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q8: How would you implement graceful shutdown in a multi-threaded server?


**Concepts:**



**Answer:**



**Explanation:**

**Requirements**:
1. Stop accepting new connections
2. Finish serving existing clients
3. No abrupt termination (data loss)

```cpp
std::atomic<bool> shutdown_requested{false};

void signal_handler(int sig) {
    std::cout << "\nShutdown signal received\n";
    shutdown_requested = true;
}

void handle_client(int fd) {
    while (!shutdown_requested) {
        // Use timeout to check shutdown_requested periodically
        struct timeval timeout = {1, 0};  // 1 second
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    // ... (additional code omitted for brevity)
```

- cpp std::atomic<bool> shutdown_requested{false};
- void signal_handler(int sig) { std::cout << "\nShutdown signal received\n"; shutdown_requested = true; }
- // Send goodbye message const char* msg = "Server shutting down\n"; send(fd, msg, strlen(msg), MSG_NOSIGNAL); close(fd); }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q9: What happens if you forget to close() the listening socket in a forked child process?

**Difficulty:** #intermediate
**Category:** #fork #file_descriptors
**Concepts:** #fd_leak #server_fd

**Answer:**



**Explanation:**

- Each child has copy of server_fd
- Child doesn't need it (only handles one client)
- Wastes one FD per child process
- Compromised child process could accept new connections on server_fd
- Violates principle of least privilege

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q10: Explain the double fork trick for avoiding zombies. How does it work?


**Concepts:**



**Answer:**



**Explanation:**

**Traditional approach (requires SIGCHLD handler)**:

```cpp
pid_t pid = fork();
if (pid == 0) {
    handle_client();
    exit(0);  // Becomes zombie until parent calls wait()
}
// Parent must install SIGCHLD handler to reap
```

- cpp pid_t pid = fork(); if (pid == 0) { handle_client(); exit(0); // Becomes zombie until parent calls wait() } // Parent must install SIGCHLD handler to reap ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q11: What is the optimal number of threads for a thread pool? How do you determine it?


**Concepts:**



**Answer:**



**Explanation:**

**Rule of thumb**:
**CPU-bound work** (computation-heavy):

```cpp
size_t num_threads = std::thread::hardware_concurrency();  // CPU cores
```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q12: What are the pros and cons of using fork() vs threads for handling multiple clients?

**Difficulty:** #beginner
**Category:** #fork_vs_threads #design_choices
**Concepts:** #processes #threads #isolation

**Answer:**



**Explanation:**

- **Strong isolation**: Separate memory spaces, one client crash doesn't affect others
- **Security**: Compromised child can't read other clients' data
- **Simple**: Each process independent, no synchronization needed
- **Debugging**: Easier to debug (can attach to specific process)
- **Heavy**: Each process consumes significant memory (separate address space)

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q13: How do you prevent race conditions when multiple threads access shared data?


**Concepts:**



**Answer:**



**Explanation:**

**Problem**: Multiple threads accessing shared data without synchronization causes unpredictable results.
**Solution 1: Mutex (mutual exclusion)**

```cpp
std::mutex data_mutex;
int shared_counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(data_mutex);  // Acquire lock
    shared_counter++;
    // Lock automatically released when 'lock' goes out of scope
}
```

- cpp std::mutex data_mutex; int shared_counter = 0;
- void increment() { std::lock_guard<std::mutex> lock(data_mutex); // Acquire lock shared_counter++; // Lock automatically released when 'lock' goes out of scope } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q14: What is the difference between std::lock_guard and std::unique_lock?


**Concepts:**



**Answer:**



**Explanation:**

**std::lock_guard** (simple, most common):

```cpp
{
    std::lock_guard<std::mutex> lock(mutex);  // Locks immediately
    // Critical section
    counter++;
}  // Automatically unlocks when 'lock' destroyed
```

- cpp { std::lock_guard<std::mutex> lock(mutex); // Locks immediately // Critical section counter++; } // Automatically unlocks when 'lock' destroyed ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q15: How would you implement a server that broadcasts messages to all connected clients (chat server)?


**Concepts:**



**Answer:**



**Explanation:**

**Architecture**:

```cpp
std::mutex clients_mutex;
std::map<int, std::string> clients;  // fd -> username

void register_client(int fd, const std::string& username) {
    std::lock_guard<std::mutex> lock(clients_mutex);
    clients[fd] = username;
}

void unregister_client(int fd) {
    std::lock_guard<std::mutex> lock(clients_mutex);
    clients.erase(fd);
}
    // ... (additional code omitted for brevity)
```

- cpp std::mutex clients_mutex; std::map<int, std::string> clients; // fd -> username
- void register_client(int fd, const std::string& username) { std::lock_guard<std::mutex> lock(clients_mutex); clients[fd] = username; }
- void unregister_client(int fd) { std::lock_guard<std::mutex> lock(clients_mutex); clients.erase(fd); }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q16: What system call is used to reap zombie processes? Why is WNOHANG flag important?


**Concepts:**



**Answer:**



**Explanation:**

**Basic reaping**:

```cpp
pid_t pid = wait(NULL);  // Blocks until any child exits
```

- cpp pid_t pid = wait(NULL); // Blocks until any child exits ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q17: How do you handle a situation where the thread pool queue is full?


**Concepts:**



**Answer:**



**Explanation:**

**Problem**: Queue has maximum size (prevent memory exhaustion). What to do when full?
**Option 1: Reject with error** (common for HTTP servers):

```cpp
bool ThreadPool::add_client(int client_fd) {
    std::lock_guard<std::mutex> lock(queue_mutex);

    if (client_queue.size() >= MAX_QUEUE_SIZE) {
        // Send error response
        const char* error = "HTTP/1.1 503 Service Unavailable\r\n"
                           "Content-Length: 20\r\n\r\n"
                           "Server overloaded\r\n";
        send(client_fd, error, strlen(error), MSG_NOSIGNAL);
        close(client_fd);
        return false;  // Rejected
    }
    // ... (additional code omitted for brevity)
```

- cpp bool ThreadPool::add_client(int client_fd) { std::lock_guard<std::mutex> lock(queue_mutex);
- client_queue.push(client_fd); cv.notify_one(); return true; } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q18: What is the SA_RESTART flag in sigaction()? Why is it important for servers?


**Concepts:**



**Answer:**



**Explanation:**

**Problem without SA_RESTART**:

```cpp
signal(SIGCHLD, sigchld_handler);  // Old-style signal()

int client_fd = accept(server_fd, NULL, NULL);
// Signal arrives → accept() returns -1, errno = EINTR
if (client_fd < 0) {
    perror("accept");  // "accept: Interrupted system call"
    // Must check errno == EINTR and retry!
}
```

- cpp signal(SIGCHLD, sigchld_handler); // Old-style signal()

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q19: How would you implement connection limiting (max N clients) in a multi-threaded server?


**Concepts:**



**Answer:**



**Explanation:**

**Option 1: Atomic counter** (simple):

```cpp
std::atomic<int> active_connections{0};
const int MAX_CONNECTIONS = 1000;

void handle_client(int client_fd) {
    active_connections++;

    // Handle client...

    active_connections--;
}

int main() {
    // ... (additional code omitted for brevity)
```

- cpp std::atomic<int> active_connections{0}; const int MAX_CONNECTIONS = 1000;
- void handle_client(int client_fd) { active_connections++;
- active_connections--; }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q20: What happens if the main thread exits while detached threads are still running?


**Concepts:**



**Answer:**



**Explanation:**

**Problem code**:

```cpp
int main() {
    int server_fd = create_server();

    for (int i = 0; i < 10; i++) {
        int client_fd = accept(server_fd, NULL, NULL);
        std::thread t(handle_client, client_fd);
        t.detach();  // Detached
    }

    std::cout << "Main exiting\n";
    return 0;  // ❌ BUG: Main exits immediately!
}
// All detached threads killed abruptly
// No cleanup, connections closed without goodbye message
```

- cpp int main() { int server_fd = create_server();
- for (int i = 0; i < 10; i++) { int client_fd = accept(server_fd, NULL, NULL); std::thread t(handle_client, client_fd); t.detach(); // Detached }
- std::cout << "Main exiting\n"; return 0; // ❌ BUG: Main exits immediately

**Note:** Full detailed explanation with additional examples available in source materials.

---
