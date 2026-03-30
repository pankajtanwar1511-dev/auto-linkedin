### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: What are the benefits of using layered architecture?

**Answer**:

1. **Separation of Concerns**: Each layer has ONE responsibility
   - UI layer: Display
   - Business layer: Logic
   - Data layer: Storage

2. **Testability**: Can test layers independently
   - Test business logic without UI or database
   - Use mocks/stubs

3. **Maintainability**: Changes isolated to one layer
   - Change database (MySQL → PostgreSQL) → only Data layer changes
   - Change UI (Web → Mobile) → only Presentation layer changes

4. **Parallel Development**: Teams work on different layers
   - Frontend team works on UI
   - Backend team works on business logic
   - DBA team works on data layer

5. **Reusability**: Business logic shared across UIs
   - Same service used by Web app AND Mobile app

---

#### Q2: What is the "Golden Rule" of layered architecture?

**Answer**:

**Golden Rule**: **Upper layers depend on lower layers, NEVER the reverse.**

```
✅ CORRECT:
Presentation → Business → Data
(UI depends on services, services depend on data)

❌ WRONG:
Data → Business → Presentation
(Database depending on UI makes no sense!)
```

**Why?**
- **Avoids circular dependencies**
- **Keeps lower layers reusable** (data layer doesn't know about UI)
- **Allows layer replacement** (swap UI without changing business logic)

**Example Violation**:
```cpp
// ❌ WRONG: Data layer depends on UI
class UserRepository {
    void save(const User& user) {
        db.execute("INSERT ...");
        showSuccessMessage("User saved!");  // ← Data layer calling UI!
    }
};
```

---

#### Q3: How do you prevent layer violations?

**Answer**:

**Layer Violation**: Skipping intermediate layers (e.g., UI directly accessing Data layer).

**Prevention Methods**:

**1. Code Review**:
- Check that UI only calls Business layer
- Business layer only calls Data layer

**2. Dependency Analysis Tools**:
- Static analysis (NDepend, SonarQube)
- Detects incorrect dependencies

**3. Package Structure**:
```
src/
  presentation/    # Can import from business/
  business/        # Can import from data/
  data/            # Cannot import from business or presentation
```

**4. Compile-Time Enforcement**:
```cpp
// Data layer module doesn't link to business/presentation
// → Compile error if trying to use them!
```

**5. Architectural Tests**:
```cpp
void testNoDependencyViolations() {
    assert(!dataLayerDependsOn(presentationLayer));
    assert(!dataLayerDependsOn(businessLayer));
}
```

---

#### Q4: What is the Repository Pattern? Why use it in the Data layer?

**Answer**:

**Repository Pattern**: Abstract database operations behind an interface.

**Without Repository**:
```cpp
class UserService {
    void registerUser(const User& user) {
        // ❌ Business layer contains SQL!
        db.execute("INSERT INTO users (name, email) VALUES ('" + user.name + "', '" + user.email + "')");
    }
};
```

**With Repository**:
```cpp
class IUserRepository {
public:
    virtual void save(const User& user) = 0;
    virtual User getById(int id) = 0;
};

class UserService {
    IUserRepository* repo;

    void registerUser(const User& user) {
        repo->save(user);  // ✅ No SQL in business layer!
    }
};
```

**Benefits**:
1. **Abstraction**: Business logic doesn't know about SQL
2. **Testability**: Can use mock repository for testing
3. **Swappable**: Change database without changing business logic
4. **Reusability**: Multiple services use same repository

---

#### Q5: How do you handle cross-cutting concerns (logging, authentication) in layered architecture?


**:**

**Answer**:
**Cross-Cutting Concerns**: Features needed in multiple layers (logging, security, error handling).
**Problem**: Duplication

```cpp
void method1() {
    log("Starting...");
    // logic
    log("Done");
}

void method2() {
    log("Starting...");  // ← Duplicated!
    // logic
    log("Done");
}
```

- cpp void method1() { log("Starting..."); // logic log("Done"); }
- void method2() { log("Starting..."); // ← Duplicated
- // logic log("Done"); } ```

**Note:** Full detailed explanation with additional examples available in source materials.

---
