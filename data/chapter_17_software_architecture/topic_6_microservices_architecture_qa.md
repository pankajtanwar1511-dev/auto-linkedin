### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: What is the main difference between monolithic and microservices architecture?

**Answer**:

| Aspect | Monolithic | Microservices |
|--------|-----------|---------------|
| **Structure** | One big application | Many small services |
| **Deployment** | Deploy entire app | Deploy each service independently |
| **Scaling** | Scale entire app | Scale individual services |
| **Database** | One shared database | Database per service |
| **Technology** | One tech stack | Different tech per service |
| **Fault Isolation** | One bug crashes all | One service failure isolated |

**Key Difference**: **Independent deployment and scaling.**

---

#### Q2: When should you NOT use microservices?

**Answer**:

**Don't use microservices when**:
1. **Small team** (< 5 people) - overhead too high
2. **Startup/early stage** - domain boundaries unclear
3. **Simple CRUD app** - unnecessary complexity
4. **Limited DevOps resources** - need infrastructure expertise
5. **Tight coupling** - features heavily interdependent

**Example**: Todo list app with 1 developer → Use monolith!

**Golden Rule**: Start with monolith, migrate to microservices when you NEED to.

---

#### Q3: How do you handle distributed transactions in microservices?

**Answer**:

**Problem**: Can't use traditional database transactions (each service has own DB).

**Solution: SAGA Pattern**

**Two approaches**:

**1. Choreography (Event-based)**:
```
Order Service → Publish "OrderCreated"
     ↓
Product Service → Subscribe, reserve inventory → Publish "InventoryReserved"
     ↓
Payment Service → Subscribe, charge card → Publish "PaymentSucceeded"
```

**2. Orchestration (Coordinator)**:
```
Saga Orchestrator:
  1. Call Product Service (reserve)
  2. Call Payment Service (charge)
  3. Call Order Service (create)

If any fails → compensate (rollback previous steps)
```

**Key**: Each step is **compensatable** (can be undone).

---

#### Q4: What is the Circuit Breaker pattern? Why use it?

**Answer**:

**Circuit Breaker** prevents cascading failures when a service is down.

**How it works**:
```
CLOSED (normal) → calls go through
    ↓ (failures exceed threshold)
OPEN (stop calling) → return error immediately, don't wait
    ↓ (wait timeout)
HALF_OPEN (try one request) → test if service recovered
    ↓ (success)
CLOSED (recovered)
```

**Why use it**:
- **Fast failure**: Don't wait for timeouts
- **Resource protection**: Don't exhaust threads
- **Cascading failure prevention**: Failure doesn't propagate

**Libraries**: Hystrix (Java), Polly (.NET), resilience4j

---

#### Q5: How do you ensure data consistency across microservices?


**:**

- Each service has own database
- Use events to propagate changes
- Accept temporary inconsistency
- Query master service for latest data
- No caching, always fresh

**Note:** Full detailed explanation with additional examples available in source materials.

---
