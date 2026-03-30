### PRACTICE_TASKS: Output Prediction and Code Analysis
#### Q1

**Goal**: Create MVC pattern for a Counter application.

**Requirements**:
1. **Model**: `CounterModel` with `increment()`, `decrement()`, `getValue()`
2. **View**: `CounterView` displays count, has buttons
3. **Controller**: `CounterController` handles button clicks

**Test**:
- Click increment → count goes up
- Click decrement → count goes down
- View auto-updates via Observer pattern

---

#### Q2

**Goal**: Create MVVM pattern for a Login form.

**Requirements**:
1. **Model**: `AuthModel` with `authenticate(username, password)`
2. **ViewModel**: `LoginViewModel` with:
   - `ObservableProperty<string> username`
   - `ObservableProperty<string> password`
   - `ObservableProperty<bool> isLoginEnabled`
   - `loginCommand()`
3. **View**: Binds to ViewModel properties

**Test**:
- Username/password empty → login button disabled
- Fill both → login button enabled
- Click login → calls `AuthModel.authenticate()`

---

#### Q3

**Goal**: Create MVP pattern for same Login form.

**Requirements**:
1. **ILoginView** interface with:
   - `showError(message)`
   - `navigateToHome()`
2. **LoginPresenter** with all logic
3. **LoginView** implements interface (completely passive)

**Test**:
- Test Presenter with MockView
- Verify `showError()` called on invalid credentials

---

#### Q4

**Goal**: Take Task 1 (MVC Counter) and convert to MVVM.

**Requirements**:
- Remove Controller
- Create `CounterViewModel` with `ObservableProperty<int> count`
- View binds to ViewModel
- Implement `incrementCommand()`, `decrementCommand()`

---

#### Q5


**:**

**Goal**: Create generic `ObservableProperty<T>` class for data binding.
**Requirements**:
1. `set(value)` - sets value and notifies listeners
2. `get()` - returns current value

```cpp
ObservableProperty<int> count(0);
count.onChange([](int newValue) {
    std::cout << "Count changed to: " << newValue << "\n";
});
count.set(5);  // Prints: "Count changed to: 5"
```

- cpp ObservableProperty<int> count(0); count.onChange([](int newValue) { std::cout << "Count changed to: " << newValue << "\n"; }); count.set(5); // Prints: "Count changed to: 5" ```
- #### Task 6: Implement Navigation System

**Note:** Full detailed explanation with additional examples available in source materials.

---
