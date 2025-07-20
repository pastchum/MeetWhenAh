# Shared Business Logic

This folder contains the shared business logic that is used by both the Telegram bot and the Next.js webapp.

## Structure

```
shared/
├── business_logic/
│   └── services/             # Business logic services
│       ├── user_service.py   # User operations
│       ├── event_service.py  # Event operations
│       ├── availability_service.py  # Availability operations
│       └── scheduler.py      # Scheduling algorithm
├── utils/                    # Shared utilities
│   └── date_utils.py         # Date/time utilities
└── README.md                 # This file
```

## Architecture Decisions

### Why No Entities?
- **Performance**: Direct dictionary access is faster than object creation
- **Memory**: Less memory overhead without object instances
- **Simplicity**: Fewer files to maintain and understand
- **Type Safety**: Type hints provide sufficient validation

### Why No Repository Pattern?
- **Direct Access**: Services directly use database service methods
- **Security**: Database access is controlled at the service level
- **Simplicity**: Reduces abstraction layers while maintaining clean separation

## Usage

### For Bot
```python
from shared.business_logic.services.user_service import UserService
from bot.services.database_service import getEntry, setEntry, updateEntry

# Initialize with your database service
user_service = UserService(database_service)

# Use the service
user = user_service.get_user("telegram_id")
```

### For Webapp
```typescript
// Import the shared business logic
import { UserService } from '@/shared/business_logic/services/user_service';

// Initialize with your database service
const userService = new UserService(databaseService);

// Use the service
const user = await userService.getUser("telegram_id");
```

## Key Features

### Scheduler Algorithm
The `scheduler.py` contains the sophisticated optimization algorithm that:
- Creates availability maps from participant data
- Builds contiguous event blocks
- Validates blocks against sleep hours, participant thresholds
- Scores and finds optimal meeting times
- Handles complex time slot calculations

### Data Transformation
The `availability_service.py` transforms data between formats:
- Frontend format: `{date: "2023-11-15", time: "1430"}`
- Scheduler format: `{start_time: "2023-11-15 14:30:00", end_time: "2023-11-15 15:00:00"}`

## Architecture Principles

1. **Separation of Concerns**: Business logic is separated from data access
2. **Direct Database Access**: Services use database methods directly
3. **Type Safety**: Type hints provide validation without overhead
4. **Reusability**: Same business logic used by bot and webapp
5. **Algorithm Efficiency**: Sophisticated scheduling algorithm preserved

## Adding New Features

1. **Services**: Add business logic in `services/`
2. **Utils**: Add shared utilities in `utils/`
3. **Type Hints**: Use proper typing for data structures

## Migration Notes

- The bot currently uses direct database access in `bot/services/`
- The webapp currently uses direct database access in `webapp/lib/db.ts`
- Both should be migrated to use the shared business logic
- This will improve security and maintainability while preserving performance 