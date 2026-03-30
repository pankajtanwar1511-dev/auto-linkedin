### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1

**Goal**: Create User Service with hexagonal architecture.

**Requirements**:
1. Domain: `User` class with business logic
2. Port: `IUserRepository` interface
3. Core: `UserService` with business rules
4. Adapter: `InMemoryUserRepository`
5. Primary Adapter: `UserController` (simulated REST)

---

#### Q2

**Goal**: Implement 3 different repository adapters for same port.

**Requirements**:
1. `IOrderRepository` interface
2. `InMemoryOrderRepository`
3. `MySQLOrderRepository` (simulated with map)
4. `FileOrderRepository` (simulated with map)
5. Swap adapters at runtime

---

#### Q3

**Goal**: Write unit tests using mock adapters.

**Requirements**:
1. `MockUserRepository` that tracks method calls
2. Test `UserService.createUser()` without real database
3. Verify `save()` was called
4. Verify business rules (age validation, email format)

---

#### Q4

**Goal**: Move business logic from service to domain model.

**Requirements**:
1. Start with anemic `Order` (just data)
2. Move validation to `Order.validate()`
3. Move state transitions to `Order.confirm()`, `Order.cancel()`
4. Service becomes thin coordinator

---

#### Q5


**:**

- Goal: Implement multiple primary adapters for same core
- Core: `OrderService` 2
- Primary Adapter 1: `RESTController` (simulated HTTP) 3
- Primary Adapter 2: `CLIController` (command-line) 4
- Both use same `OrderService`

**Note:** Full detailed explanation with additional examples available in source materials.

---
