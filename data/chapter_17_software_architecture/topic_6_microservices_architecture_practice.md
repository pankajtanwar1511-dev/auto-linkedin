### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1

**Goal**: Implement a Product Service with CRUD operations.

**Requirements**:
1. `ProductRepository` (in-memory storage)
2. `ProductService` (business logic)
3. REST API endpoints:
   - GET /products → list all
   - GET /products/:id → get one
   - POST /products → create
   - PUT /products/:id → update
   - DELETE /products/:id → delete

---

#### Q2

**Goal**: Order Service calls User Service via HTTP.

**Requirements**:
1. User Service running on port 8001
2. Order Service running on port 8002
3. When creating order, Order Service queries User Service for user data
4. Handle errors if User Service is down

---

#### Q3

**Goal**: Single entry point for multiple services.

**Requirements**:
1. API Gateway on port 8000
2. Routes:
   - /api/users → User Service (8001)
   - /api/orders → Order Service (8002)
   - /api/products → Product Service (8003)
3. Gateway aggregates responses if needed

---

#### Q4

**Goal**: Protect against cascading failures.

**Requirements**:
1. `CircuitBreaker` class with states (CLOSED, OPEN, HALF_OPEN)
2. Failure threshold = 5
3. Timeout = 60 seconds
4. Test with simulated failing service

---

#### Q5


**:**

- Goal: Services register/discover each other
- `ServiceRegistry` (in-memory map) 2
- Services register on startup 3
- Services lookup other services by name 4
- Heartbeat mechanism (optional)

**Note:** Full detailed explanation with additional examples available in source materials.

---
