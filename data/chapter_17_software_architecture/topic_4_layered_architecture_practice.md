### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1

**Goal**: Create a complete 3-tier system for managing Products.

**Requirements**:
1. **Data Layer**: `ProductRepository` with save(), getById(), getAll(), update(), delete()
2. **Business Layer**: `ProductService` with business rules:
   - Price must be > 0
   - Stock must be >= 0
   - Name must not be empty
3. **Presentation Layer**: `ProductController` with UI methods

**Test Cases**:
- Add valid product
- Try to add product with negative price (should fail)
- Update product stock
- Display all products

---

#### Q2

**Goal**: Refactor Task 1 to use dependency injection.

**Requirements**:
1. Create `IProductRepository` interface
2. `ProductService` depends on `IProductRepository*` (constructor injection)
3. `ProductController` depends on `ProductService*`
4. Create a mock `MockProductRepository` for testing

---

#### Q3

**Goal**: Create generic repository base class.

**Requirements**:
1. `IRepository<T>` interface with:
   - `save(T entity)`
   - `getById(int id)`
   - `getAll()`
   - `update(T entity)`
   - `remove(int id)`
2. `ProductRepository` implements `IRepository<Product>`
3. `UserRepository` implements `IRepository<User>`

---

#### Q4

**Goal**: Implement logging decorator for all service methods.

**Requirements**:
1. `LoggingDecorator<T>` template class
2. Wraps any service
3. Logs method calls and results
4. Test with `ProductService`

**Expected Output**:
```
[LOG] ProductService.addProduct() called
[LOG] ProductService.addProduct() completed successfully
```

---

#### Q5


**:**

**Goal**: Add compile-time checks to prevent layer violations.
**Requirements**:
1. Organize code into separate namespaces/modules:
- `presentation::`

```cpp
Data layer: throw DataException("Database connection failed")
     ↓
Business layer: catch, wrap in BusinessException("Unable to save product")
     ↓
Presentation layer: catch, display "Error: Unable to save product. Try again later."
```

- Try again later." ```
- #### Task 9: Implement Caching in Service Layer

**Note:** Full detailed explanation with additional examples available in source materials.

---
