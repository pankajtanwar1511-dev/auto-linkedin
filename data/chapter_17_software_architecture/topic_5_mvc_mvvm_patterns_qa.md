### INTERVIEW_QA: Comprehensive Questions and Answers
#### Q1: What is the main difference between MVC and MVVM?

**Answer**:

| Aspect | MVC | MVVM |
|--------|-----|------|
| **Communication** | View ↔ Controller (explicit) | View ↔ ViewModel (data binding) |
| **Update Mechanism** | Observer pattern (manual) | Two-way binding (automatic) |
| **View Intelligence** | Some logic allowed | Purely declarative |
| **Testability** | Good | Excellent (no UI dependency) |

**Key Difference**: **Data Binding**

**MVC**:
```cpp
// Manual update
controller.updateName("Alice");
view.updateNameLabel();  // Explicit call
```

**MVVM**:
```xml
<!-- Automatic update -->
<TextBox Text="{Binding UserName}" />
```

When user types, ViewModel updates automatically. When ViewModel changes, UI updates automatically.

---

#### Q2: When should you use MVP over MVC?

**Answer**:

**Use MVP when**:
1. **Maximum testability** needed (View is interface → easy to mock)
2. **No data binding framework** available
3. **Android development** (MVP common pattern)
4. **Legacy systems** without modern UI frameworks

**Example: Android**:
```kotlin
interface ILoginView {
    fun showError(message: String)
    fun navigateToHome()
}

class LoginPresenter(private val view: ILoginView) {
    fun onLoginClicked(username: String, password: String) {
        if (authenticate(username, password)) {
            view.navigateToHome()
        } else {
            view.showError("Invalid credentials")
        }
    }
}

// Easy to test!
class MockLoginView : ILoginView {
    var errorShown = false
    override fun showError(message: String) {
        errorShown = true
    }
}
```

---

#### Q3: How do you prevent "Fat Controllers"?


**:**

**Answer**:
**Fat Controller** = Controller with thousands of lines, handling everything.

```cpp
class UserController {
    UserService userService;  // Business logic here

    void handleLogin(const Credentials& creds) {
        bool success = userService.authenticate(creds);  // ✅ Thin controller
        if (success) view->navigateTo("home");
    }
};
```

- cpp class UserController { UserService userService; // Business logic here

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q4: How do you implement two-way data binding in C++?


**:**

- C++ doesn't have built-in data binding (unlike C#/WPF or JavaScript frameworks), but you can simulate it:
- ObservableProperty Pattern:
- public: void set(const T& newValue) { value = newValue; notify(); // Notify all listeners }
- T get() const { return value; }
- void onChange(std::function<void(const T&)> listener) { listeners.push_back(listener); }

**Note:** Full detailed explanation with additional examples available in source materials.

---
#### Q5: Where should validation logic go: View, Controller, or Model?


**:**

- Format checks (email has @, phone has digits)
- Required field checks
- **Where**: View or Controller
- Business rules (age must be 18+)
- Database constraints (email must be unique)

**Note:** Full detailed explanation with additional examples available in source materials.

---
