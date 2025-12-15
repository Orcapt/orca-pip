# Quick Reference - Lexia SDK Architecture

## 📁 File Organization (Clean & Minimal)

### Core Files (User-Facing)

```
unified_handler.py   170 lines  → Main orchestrator
session.py          259 lines  → Session operations
button_helper.py    115 lines  → Button management
button_utils.py      46 lines  → Standalone utilities
```

### Service Layer (Business Logic)

```
services/
├── buffer_manager.py          → Thread-safe buffering
├── button_renderer.py         → Button formatting
├── loading_marker_provider.py → Loading indicators
├── usage_tracker.py           → Token tracking
├── tracing_service.py         → Debug tracing
├── error_handler.py           → Error formatting
└── response_builder.py        → Response payloads
```

### Infrastructure Layer

```
factories/
└── stream_client_factory.py   → Client creation

interfaces.py                  → All abstractions
api_client.py                  → HTTP client
centrifugo_client.py          → Production streaming
dev_stream_client.py          → Dev mode streaming
```

## 🎯 Quick Navigation

### "Where do I find...?"

| What                                   | File                                 | Lines |
| -------------------------------------- | ------------------------------------ | ----- |
| Main handler initialization            | `unified_handler.py`                 | 170   |
| Session methods (stream, close, error) | `session.py`                         | 259   |
| Button operations                      | `button_helper.py`                   | 115   |
| Standalone button functions            | `button_utils.py`                    | 46    |
| Buffer management                      | `services/buffer_manager.py`         | ~100  |
| Error handling                         | `services/error_handler.py`          | ~100  |
| Stream client creation                 | `factories/stream_client_factory.py` | ~150  |

## 🔍 Code Reading Order

### For New Developers

1. Start with `unified_handler.py` (170 lines) - understand the main flow
2. Read `session.py` (259 lines) - see user-facing API
3. Browse `services/` - understand business logic
4. Check `interfaces.py` - see contracts

### For Contributors

1. `interfaces.py` - understand abstractions
2. `unified_handler.py` - see orchestration
3. Specific service you're modifying
4. Related tests

## 📊 Complexity Metrics

| File               | Lines | Complexity  | Maintainability |
| ------------------ | ----- | ----------- | --------------- |
| unified_handler.py | 170   | Low ✅      | High ✅         |
| session.py         | 259   | Medium ✅   | High ✅         |
| button_helper.py   | 115   | Low ✅      | High ✅         |
| button_utils.py    | 46    | Very Low ✅ | Very High ✅    |

## 🚀 Common Tasks

### Add New Feature

1. Create interface in `interfaces.py`
2. Implement service in `services/`
3. Inject into `LexiaHandler.__init__`
4. Use in `Session` or handler methods

### Fix Bug

1. Identify affected module (small files = easy to find!)
2. Check service layer first
3. Verify interface contracts
4. Update tests

### Add New Stream Client

1. Implement `IStreamClient` interface
2. Register in `StreamClientFactory`
3. No changes to handler needed!

## 💡 Design Patterns Used

| Pattern              | Where                           | Purpose             |
| -------------------- | ------------------------------- | ------------------- |
| Dependency Injection | `LexiaHandler.__init__`         | Loose coupling      |
| Factory              | `StreamClientFactory`           | Object creation     |
| Strategy             | `IStreamClient` implementations | Algorithm selection |
| Facade               | `LexiaHandler`                  | Simple interface    |
| Service Layer        | `services/`                     | Business logic      |

## 🎨 SOLID Principles Map

| Principle | Implementation                   |
| --------- | -------------------------------- |
| **S**RP   | Each file has one responsibility |
| **O**CP   | Factory pattern for extension    |
| **L**SP   | Interface-based substitution     |
| **I**SP   | Small, focused interfaces        |
| **D**IP   | Dependency injection everywhere  |

## 📝 Naming Conventions

### Files

- `*_handler.py` → Orchestration
- `*_service.py` → Business logic
- `*_helper.py` → Helper classes
- `*_utils.py` → Standalone functions
- `*_client.py` → External communication
- `*_factory.py` → Object creation

### Classes

- `LexiaHandler` → Main orchestrator
- `Session` → User session
- `*Service` → Business logic services
- `*Helper` → Helper classes
- `*Factory` → Factories
- `I*` → Interfaces (Abstract Base Classes)

## 🧪 Testing Strategy

### Unit Tests

- Mock all dependencies via DI
- Test services in isolation
- Fast and focused

### Integration Tests

- Use real services
- Test handler + services
- Verify interactions

### Example

```python
# Unit test with mocks
handler = LexiaHandler(
    stream_client=Mock(),
    api_client=Mock()
)

# Integration test with real services
handler = LexiaHandler(dev_mode=True)
```

## 📈 Metrics

### Before Refactoring

- Main file: **748 lines** ❌
- Complexity: **High** ❌
- Testability: **Difficult** ❌
- Maintainability: **Low** ❌

### After Refactoring

- Main file: **170 lines** ✅ (77% reduction!)
- Complexity: **Low** ✅
- Testability: **Easy** ✅
- Maintainability: **High** ✅

## 🎯 Key Takeaways

1. **Small files** = Easy to understand
2. **Clear names** = Easy to navigate
3. **Single responsibility** = Easy to modify
4. **Dependency injection** = Easy to test
5. **Interface-based** = Easy to extend

## 🔗 Related Documentation

- `ARCHITECTURE.md` - Detailed architecture explanation
- `REFACTORING_SUMMARY.md` - Refactoring details
- `README.md` - Usage guide
- `test_refactored.py` - Test examples

---

**Remember:** The goal is **clean, maintainable, professional code** that any senior developer would be proud of! 🚀
