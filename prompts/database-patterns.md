# BluePrint: Database Patterns Reference

## Overview

This document provides comprehensive patterns for specifying database schemas, operations, and data flows within BluePrint. Use it when your project has significant data modeling requirements.

BluePrint takes a **declarative, intent-focused approach** to database design—specifying *what* the data layer should do rather than *how* it should be implemented in a specific database technology.

## 1. Schema Definition

### 1.1 Basic Table Structure

```blueprint
Database ProjectDB {
  Schema {
    Table Users {
      columns: {
        id: {type: UUID, primaryKey: true},
        username: {type: String, length: 50, unique: true, nullable: false},
        email: {type: String, nullable: false},
        passwordHash: {type: String, sensitive: true},
        status: {type: Enum, values: ["active", "suspended", "deleted"], default: "active"},
        created_at: {type: Timestamp, default: "CURRENT_TIMESTAMP"},
        updated_at: {type: Timestamp, onUpdate: "CURRENT_TIMESTAMP"}
      },
      
      indexes: [
        {name: "idx_username", columns: ["username"], unique: true},
        {name: "idx_email", columns: ["email"]},
        {name: "idx_status_created", columns: ["status", "created_at"]}
      ],
      
      constraints: [
        {type: "check", name: "email_format", condition: "email LIKE '%@%.%'"}
      ]
    }
  }
}
```

### 1.2 Column Types

| Type | Description | Options |
|------|-------------|---------|
| `UUID` | Universally unique identifier | `primaryKey`, `default: "gen_random_uuid()"` |
| `String` | Variable-length text | `length`, `nullable`, `unique`, `default` |
| `Text` | Unlimited text | `nullable` |
| `Int` | Integer | `nullable`, `default`, `autoIncrement` |
| `BigInt` | Large integer | Same as Int |
| `Float` | Floating point | `precision`, `nullable`, `default` |
| `Decimal` | Exact decimal | `precision`, `scale`, `nullable` |
| `Boolean` | True/false | `nullable`, `default` |
| `Timestamp` | Date and time | `nullable`, `default`, `onUpdate` |
| `Date` | Date only | `nullable`, `default` |
| `JSON` | Structured data | `nullable`, `default` |
| `Enum` | Constrained values | `values: [...]`, `default` |
| `Binary` | Binary data | `length`, `nullable` |

### 1.3 Column Modifiers

```blueprint
columns: {
  // Primary key with auto-generation
  id: {type: UUID, primaryKey: true, default: "gen_random_uuid()"},
  
  // Foreign key reference
  user_id: {type: UUID, references: "Users.id", onDelete: "CASCADE", onUpdate: "CASCADE"},
  
  // Composite unique constraint handled at table level
  
  // Sensitive data marker (affects logging, serialization)
  passwordHash: {type: String, sensitive: true},
  
  // Computed/derived column
  full_name: {type: String, computed: "first_name || ' ' || last_name"},
  
  // Nullable with explicit default
  deleted_at: {type: Timestamp, nullable: true, default: null}
}
```

### 1.4 Multi-Table Schema

```blueprint
Database EcommerceDB {
  Schema {
    Table Users {
      columns: {
        id: {type: UUID, primaryKey: true},
        email: {type: String, unique: true, nullable: false},
        created_at: {type: Timestamp, default: "CURRENT_TIMESTAMP"}
      }
    },
    
    Table Products {
      columns: {
        id: {type: UUID, primaryKey: true},
        sku: {type: String, length: 50, unique: true},
        name: {type: String, length: 200, nullable: false},
        price_cents: {type: Int, nullable: false},
        inventory_count: {type: Int, default: 0},
        active: {type: Boolean, default: true}
      },
      
      indexes: [
        {name: "idx_sku", columns: ["sku"]},
        {name: "idx_active_name", columns: ["active", "name"]}
      ]
    },
    
    Table Orders {
      columns: {
        id: {type: UUID, primaryKey: true},
        user_id: {type: UUID, references: "Users.id", onDelete: "RESTRICT"},
        status: {type: Enum, values: ["pending", "paid", "shipped", "delivered", "cancelled"]},
        total_cents: {type: Int, nullable: false},
        created_at: {type: Timestamp, default: "CURRENT_TIMESTAMP"}
      },
      
      indexes: [
        {name: "idx_user_orders", columns: ["user_id", "created_at"]}
      ]
    },
    
    Table OrderItems {
      columns: {
        id: {type: UUID, primaryKey: true},
        order_id: {type: UUID, references: "Orders.id", onDelete: "CASCADE"},
        product_id: {type: UUID, references: "Products.id", onDelete: "RESTRICT"},
        quantity: {type: Int, nullable: false},
        unit_price_cents: {type: Int, nullable: false}
      },
      
      indexes: [
        {name: "idx_order_items", columns: ["order_id"]}
      ],
      
      constraints: [
        {type: "check", name: "positive_quantity", condition: "quantity > 0"}
      ]
    }
  }
}
```

## 2. Relationships

### 2.1 Relationship Types

```blueprint
Database ProjectDB {
  Relationships {
    // One-to-Many: One user has many posts
    UserHasManyPosts {
      from: "Users.id",
      to: "Posts.user_id",
      type: "oneToMany",
      inverseOf: "PostBelongsToUser"
    },
    
    // Many-to-One: Many posts belong to one user
    PostBelongsToUser {
      from: "Posts.user_id",
      to: "Users.id",
      type: "manyToOne",
      inverseOf: "UserHasManyPosts"
    },
    
    // One-to-One: One user has one profile
    UserHasOneProfile {
      from: "Users.id",
      to: "UserProfiles.user_id",
      type: "oneToOne",
      required: true
    },
    
    // Many-to-Many: Users have many roles, roles have many users
    UserHasManyRoles {
      from: "Users.id",
      to: "Roles.id",
      type: "manyToMany",
      through: "UserRoles",  // Junction table
      throughKeys: {source: "user_id", target: "role_id"}
    },
    
    // Self-referential: Employee reports to manager
    EmployeeReportsTo {
      from: "Employees.id",
      to: "Employees.manager_id",
      type: "oneToMany",
      selfReferential: true
    }
  }
}
```

### 2.2 Cascade Behaviors

```blueprint
// On delete options
onDelete: "CASCADE"    // Delete related records
onDelete: "RESTRICT"   // Prevent deletion if related records exist
onDelete: "SET NULL"   // Set foreign key to null
onDelete: "SET DEFAULT" // Set foreign key to default value
onDelete: "NO ACTION"  // Database default (usually restrict)

// On update options
onUpdate: "CASCADE"    // Update foreign keys when primary key changes
onUpdate: "RESTRICT"   // Prevent update if related records exist
```

### 2.3 Junction Tables (Many-to-Many)

```blueprint
Table UserRoles {
  columns: {
    user_id: {type: UUID, references: "Users.id", onDelete: "CASCADE"},
    role_id: {type: UUID, references: "Roles.id", onDelete: "CASCADE"},
    granted_at: {type: Timestamp, default: "CURRENT_TIMESTAMP"},
    granted_by: {type: UUID, references: "Users.id", nullable: true}
  },
  
  primaryKey: ["user_id", "role_id"],  // Composite primary key
  
  indexes: [
    {name: "idx_role_users", columns: ["role_id"]}
  ]
}
```

## 3. Data Operations

### 3.1 Create Operations

```blueprint
// Simple create
Operation CreateUser {
  type: "create",
  table: "Users",
  data: {
    email: param.email,
    passwordHash: param.hashedPassword
  },
  returning: ["id", "email", "created_at"],
  
  preconditions: [
    email is valid format,
    email not already registered
  ],
  postconditions: [
    user record exists,
    id is generated
  ]
}

// Create with nested data
Operation CreateOrderWithItems {
  type: "create",
  table: "Orders",
  data: {
    user_id: param.userId,
    status: "pending",
    total_cents: param.totalCents
  },
  nested: {
    items: {
      table: "OrderItems",
      foreignKey: "order_id",
      data: param.items  // Array of {product_id, quantity, unit_price_cents}
    }
  },
  returning: ["id", "status", "items"]
}

// Upsert (insert or update)
Operation UpsertUserPreference {
  type: "upsert",
  table: "UserPreferences",
  conflictOn: ["user_id", "preference_key"],
  data: {
    user_id: param.userId,
    preference_key: param.key,
    preference_value: param.value
  },
  onConflict: {
    update: ["preference_value", "updated_at"]
  }
}
```

### 3.2 Read Operations

```blueprint
// Simple read with filters
Operation GetUserPosts {
  type: "read",
  table: "Posts",
  select: ["id", "title", "created_at", "published"],
  where: {
    user_id: param.userId,
    published: true
  },
  orderBy: ["created_at DESC"],
  limit: param.limit,
  offset: param.offset,
  
  preconditions: [user exists],
  postconditions: [returns array, may be empty]
}

// Read with joins
Operation GetOrderDetails {
  type: "read",
  table: "Orders",
  select: ["id", "status", "total_cents", "created_at"],
  include: {
    user: {
      table: "Users",
      select: ["id", "email"],
      on: "Orders.user_id = Users.id"
    },
    items: {
      table: "OrderItems",
      select: ["id", "quantity", "unit_price_cents"],
      on: "OrderItems.order_id = Orders.id",
      include: {
        product: {
          table: "Products",
          select: ["id", "name", "sku"],
          on: "OrderItems.product_id = Products.id"
        }
      }
    }
  },
  where: {id: param.orderId}
}

// Aggregation
Operation GetUserOrderStats {
  type: "read",
  table: "Orders",
  select: {
    total_orders: "COUNT(*)",
    total_spent: "SUM(total_cents)",
    avg_order_value: "AVG(total_cents)",
    first_order: "MIN(created_at)",
    last_order: "MAX(created_at)"
  },
  where: {user_id: param.userId},
  groupBy: ["user_id"]
}

// Complex filtering
Operation SearchProducts {
  type: "read",
  table: "Products",
  select: ["id", "name", "sku", "price_cents"],
  where: {
    active: true,
    price_cents: {between: [param.minPrice, param.maxPrice]},
    name: {ilike: param.searchTerm},  // Case-insensitive pattern match
    category_id: {in: param.categoryIds}
  },
  orderBy: [param.sortField, param.sortDirection],
  limit: 20
}
```

### 3.3 Update Operations

```blueprint
// Simple update
Operation UpdateUserEmail {
  type: "update",
  table: "Users",
  where: {id: param.userId},
  set: {
    email: param.newEmail,
    email_verified: false
  },
  returning: ["id", "email", "updated_at"],
  
  preconditions: [
    user exists,
    new email not already registered
  ],
  postconditions: [
    email is updated,
    email_verified is false
  ]
}

// Conditional update
Operation DecrementInventory {
  type: "update",
  table: "Products",
  where: {
    id: param.productId,
    inventory_count: {gte: param.quantity}  // Only if sufficient inventory
  },
  set: {
    inventory_count: {decrement: param.quantity}
  },
  returning: ["id", "inventory_count"],
  
  preconditions: [inventory_count >= quantity],
  postconditions: [inventory_count decreased by quantity],
  errorOnNoMatch: "InsufficientInventory"
}

// Bulk update
Operation MarkOrdersShipped {
  type: "update",
  table: "Orders",
  where: {
    id: {in: param.orderIds},
    status: "paid"  // Only paid orders can be shipped
  },
  set: {
    status: "shipped",
    shipped_at: "CURRENT_TIMESTAMP"
  },
  returning: ["id", "status"]
}
```

### 3.4 Delete Operations

```blueprint
// Simple delete
Operation DeletePost {
  type: "delete",
  table: "Posts",
  where: {
    id: param.postId,
    user_id: param.userId  // Ownership check
  },
  
  preconditions: [post exists, user owns post],
  postconditions: [post no longer exists]
}

// Soft delete
Operation SoftDeleteUser {
  type: "update",  // Not actually deleting
  table: "Users",
  where: {id: param.userId},
  set: {
    status: "deleted",
    deleted_at: "CURRENT_TIMESTAMP",
    email: {concat: ["deleted_", "id", "_", "email"]}  // Anonymize
  },
  
  postconditions: [
    user status is deleted,
    user cannot log in,
    email is anonymized
  ]
}

// Cascade-aware delete
Operation DeleteUserAccount {
  type: "delete",
  table: "Users",
  where: {id: param.userId},
  cascadePreview: true,  // Return what will be deleted
  
  // Explicit cascade handling (if not using FK cascades)
  priorOperations: [
    {type: "delete", table: "UserSessions", where: {user_id: param.userId}},
    {type: "delete", table: "UserPreferences", where: {user_id: param.userId}}
  ]
}

// Conditional bulk delete
Operation PurgeOldDrafts {
  type: "delete",
  table: "Posts",
  where: {
    published: false,
    updated_at: {before: param.cutoffDate}
  },
  limit: 1000,  // Batch size
  returning: ["id"]
}
```

## 4. Transactions

### 4.1 Basic Transaction

```blueprint
Transaction UserRegistration {
  description: "Create user and associated profile atomically",
  
  operations: [
    {
      name: "createUser",
      type: "create",
      table: "Users",
      data: {
        email: param.email,
        passwordHash: param.hashedPassword
      },
      returning: ["id"]
    },
    {
      name: "createProfile",
      type: "create",
      table: "UserProfiles",
      data: {
        user_id: "ref:createUser.id",  // Reference previous operation
        display_name: param.displayName,
        avatar_url: null
      }
    },
    {
      name: "assignDefaultRole",
      type: "create",
      table: "UserRoles",
      data: {
        user_id: "ref:createUser.id",
        role_id: "ROLE_USER_UUID"
      }
    }
  ],
  
  onError: "rollback",
  
  preconditions: [
    email not already registered
  ],
  postconditions: [
    user exists,
    profile exists,
    user has default role,
    OR none of the above (on failure)
  ]
}
```

### 4.2 Transaction with Compensation

```blueprint
Transaction ProcessPayment {
  description: "Charge payment and update order status",
  
  operations: [
    {
      name: "reserveInventory",
      type: "update",
      table: "Products",
      where: {id: {in: param.productIds}},
      set: {reserved_count: {increment: "quantities"}},
      compensation: {
        type: "update",
        set: {reserved_count: {decrement: "quantities"}}
      }
    },
    {
      name: "chargePayment",
      type: "external",
      service: "PaymentGateway",
      action: "charge",
      params: {amount: param.totalCents, method: param.paymentMethod},
      compensation: {
        action: "refund",
        params: {chargeId: "ref:chargePayment.chargeId"}
      }
    },
    {
      name: "updateOrder",
      type: "update",
      table: "Orders",
      where: {id: param.orderId},
      set: {status: "paid", paid_at: "CURRENT_TIMESTAMP"}
    },
    {
      name: "commitInventory",
      type: "update",
      table: "Products",
      set: {
        reserved_count: {decrement: "quantities"},
        inventory_count: {decrement: "quantities"}
      }
    }
  ],
  
  onError: "compensate",  // Run compensation actions in reverse order
  
  errorPaths: [
    payment declined -> release inventory, return payment error,
    insufficient inventory -> return inventory error before payment
  ]
}
```

### 4.3 Isolation Levels

```blueprint
Transaction ReadUserBalance {
  isolationLevel: "serializable",  // Strongest isolation
  
  operations: [
    {type: "read", table: "Accounts", where: {user_id: param.userId}, forUpdate: true},
    // ... other operations
  ]
}

// Isolation level options:
// - "readUncommitted": Dirty reads allowed (rarely used)
// - "readCommitted": Only see committed data (default in most DBs)
// - "repeatableRead": Consistent reads within transaction
// - "serializable": Full isolation, may require retries
```

## 5. Migrations

### 5.1 Add Column

```blueprint
Migration AddUserStatus {
  version: "20240115_001",
  description: "Add status column to users table",
  
  up: {
    addColumn: {
      table: "Users",
      column: {
        name: "status",
        type: "String",
        length: 20,
        default: "active",
        nullable: false
      }
    }
  },
  
  down: {
    dropColumn: {
      table: "Users",
      column: "status"
    }
  }
}
```

### 5.2 Create Table

```blueprint
Migration CreateAuditLog {
  version: "20240115_002",
  description: "Create audit log table for tracking changes",
  
  up: {
    createTable: {
      name: "AuditLogs",
      columns: {
        id: {type: UUID, primaryKey: true, default: "gen_random_uuid()"},
        table_name: {type: String, length: 100, nullable: false},
        record_id: {type: UUID, nullable: false},
        action: {type: Enum, values: ["create", "update", "delete"]},
        old_values: {type: JSON, nullable: true},
        new_values: {type: JSON, nullable: true},
        user_id: {type: UUID, references: "Users.id", nullable: true},
        created_at: {type: Timestamp, default: "CURRENT_TIMESTAMP"}
      },
      indexes: [
        {name: "idx_audit_table_record", columns: ["table_name", "record_id"]},
        {name: "idx_audit_created", columns: ["created_at"]}
      ]
    }
  },
  
  down: {
    dropTable: "AuditLogs"
  }
}
```

### 5.3 Modify Column

```blueprint
Migration ExpandUsernameLength {
  version: "20240116_001",
  description: "Increase username column length from 50 to 100",
  
  up: {
    alterColumn: {
      table: "Users",
      column: "username",
      changes: {
        length: 100
      }
    }
  },
  
  down: {
    alterColumn: {
      table: "Users",
      column: "username",
      changes: {
        length: 50
      }
    }
  },
  
  // Data considerations
  preConditions: [
    "No existing usernames exceed 100 characters"
  ],
  warnings: [
    "Down migration will fail if any username exceeds 50 characters"
  ]
}
```

### 5.4 Add Index

```blueprint
Migration AddOrderSearchIndexes {
  version: "20240116_002",
  description: "Add indexes to improve order search performance",
  
  up: {
    addIndexes: [
      {
        table: "Orders",
        name: "idx_orders_status_date",
        columns: ["status", "created_at"],
        where: "status != 'cancelled'"  // Partial index
      },
      {
        table: "Orders",
        name: "idx_orders_user_status",
        columns: ["user_id", "status"]
      }
    ]
  },
  
  down: {
    dropIndexes: [
      {table: "Orders", name: "idx_orders_status_date"},
      {table: "Orders", name: "idx_orders_user_status"}
    ]
  },
  
  // Index creation options
  concurrent: true,  // Don't lock table during creation
  ifNotExists: true
}
```

### 5.5 Data Migration

```blueprint
Migration BackfillUserDisplayNames {
  version: "20240117_001",
  description: "Populate display_name from email for existing users",
  
  up: {
    dataMigration: {
      table: "UserProfiles",
      batchSize: 1000,
      set: {
        display_name: {
          sql: "COALESCE(display_name, SPLIT_PART(u.email, '@', 1))",
          from: "Users u",
          where: "u.id = UserProfiles.user_id"
        }
      },
      where: {display_name: null}
    }
  },
  
  down: {
    // Data migrations are often not reversible
    note: "Cannot automatically reverse - display_name values will remain"
  },
  
  // Safety
  runInTransaction: true,
  timeout: "5 minutes"
}
```

### 5.6 Rename and Move

```blueprint
Migration RenamePostsToArticles {
  version: "20240118_001",
  description: "Rename posts table to articles",
  
  up: {
    renameTable: {
      from: "Posts",
      to: "Articles"
    },
    renameColumn: {
      table: "Articles",
      from: "post_type",
      to: "article_type"
    },
    // Update foreign keys in other tables
    alterColumn: {
      table: "Comments",
      column: "post_id",
      rename: "article_id"
    }
  },
  
  down: {
    renameColumn: {
      table: "Comments",
      from: "article_id",
      to: "post_id"
    },
    renameColumn: {
      table: "Articles",
      from: "article_type",
      to: "post_type"
    },
    renameTable: {
      from: "Articles",
      to: "Posts"
    }
  }
}
```

## 6. Query Patterns

### 6.1 Pagination

```blueprint
// Offset-based pagination (simple but slow for large offsets)
Operation ListUsersOffset {
  type: "read",
  table: "Users",
  select: ["id", "email", "created_at"],
  orderBy: ["created_at DESC"],
  limit: param.pageSize,
  offset: param.page * param.pageSize,
  
  returning: {
    data: "rows",
    meta: {
      page: param.page,
      pageSize: param.pageSize,
      totalCount: "SELECT COUNT(*) FROM Users"
    }
  }
}

// Cursor-based pagination (efficient for large datasets)
Operation ListUsersCursor {
  type: "read",
  table: "Users",
  select: ["id", "email", "created_at"],
  where: {
    created_at: {lt: param.cursor}  // Cursor is last item's created_at
  },
  orderBy: ["created_at DESC"],
  limit: param.pageSize + 1,  // Fetch one extra to detect hasMore
  
  returning: {
    data: "rows[0:pageSize]",
    meta: {
      nextCursor: "rows[pageSize-1].created_at",
      hasMore: "rows.length > pageSize"
    }
  }
}
```

### 6.2 Full-Text Search

```blueprint
Operation SearchArticles {
  type: "read",
  table: "Articles",
  select: ["id", "title", "excerpt", "created_at"],
  where: {
    searchVector: {matches: param.searchQuery},  // Full-text search
    published: true
  },
  orderBy: ["relevance DESC", "created_at DESC"],
  limit: 20,
  
  // Search configuration
  searchConfig: {
    columns: ["title", "content"],
    weights: {title: "A", content: "B"},
    language: "english"
  }
}
```

### 6.3 Recursive Queries

```blueprint
// Org chart / tree traversal
Operation GetEmployeeHierarchy {
  type: "read",
  table: "Employees",
  recursive: {
    anchor: {
      where: {id: param.rootEmployeeId}
    },
    recursiveStep: {
      join: "Employees.manager_id = recursive.id"
    },
    maxDepth: 10
  },
  select: ["id", "name", "manager_id", "depth"]
}

// Bill of materials / component tree
Operation GetProductComponents {
  type: "read",
  table: "Components",
  recursive: {
    anchor: {
      where: {product_id: param.productId, parent_id: null}
    },
    recursiveStep: {
      join: "Components.parent_id = recursive.id"
    }
  },
  select: ["id", "name", "quantity", "depth", "path"]
}
```

## 7. Design Principles

When specifying database operations in BluePrint:

### 7.1 Declarative Intent
Focus on *what* the operation should accomplish, not *how* to write the SQL:
- Describe the business operation
- Specify preconditions and postconditions
- Let the implementation choose optimal execution

### 7.2 Explicit Constraints
Make constraints visible in the specification:
- Uniqueness requirements
- Referential integrity rules
- Domain constraints (valid values, ranges)
- Business rules that affect data

### 7.3 Error Path Coverage
Define what happens when operations fail:
- Constraint violations
- Concurrent modification conflicts
- Missing referenced data
- Resource exhaustion

### 7.4 Transaction Boundaries
Be explicit about atomicity requirements:
- What operations must succeed or fail together?
- What compensating actions are needed on failure?
- What isolation level is required?

### 7.5 Performance Hints
Include information that affects implementation:
- Expected data volumes
- Query frequency patterns
- Acceptable latency bounds
- Index suggestions

## 8. Anti-Patterns to Avoid

### 8.1 N+1 Queries
```blueprint
// BAD: Fetching related data in a loop
Operation GetUsersWithPostsBad {
  for each user in Users {
    fetch Posts where user_id = user.id  // N additional queries!
  }
}

// GOOD: Use includes/joins
Operation GetUsersWithPostsGood {
  type: "read",
  table: "Users",
  include: {
    posts: {table: "Posts", on: "Posts.user_id = Users.id"}
  }
}
```

### 8.2 Implicit Cascades
```blueprint
// BAD: Relying on undocumented cascade behavior
Operation DeleteUser {
  type: "delete",
  table: "Users",
  where: {id: param.userId}
  // What happens to related data?
}

// GOOD: Explicit about cascades
Operation DeleteUser {
  type: "delete",
  table: "Users",
  where: {id: param.userId},
  cascades: ["UserProfiles", "UserSessions"],
  blockedBy: ["Orders"],  // Prevent deletion if orders exist
  postconditions: [
    user record deleted,
    profile deleted,
    sessions deleted,
    orders preserved with user_id intact
  ]
}
```

### 8.3 Missing Indexes
```blueprint
// Include index requirements with queries that need them
Operation FindOrdersByDateRange {
  type: "read",
  table: "Orders",
  where: {
    created_at: {between: [param.startDate, param.endDate]},
    status: param.status
  },
  
  requiredIndexes: [
    {columns: ["created_at", "status"]}
  ],
  
  performanceExpectation: {
    maxLatency: "100ms",
    expectedRows: "< 10000"
  }
}
```

## 9. Integration Notes

When compiling BluePrint database specifications to implementation:

1. **ORM vs. Raw SQL**: The specification is agnostic. Implementation may use either based on project conventions.

2. **Database-Specific Features**: BluePrint abstracts common patterns. Implementation should use native features (e.g., PostgreSQL's JSONB, MySQL's spatial indexes) where appropriate.

3. **Migration Tools**: BluePrint migrations map to tools like Flyway, Alembic, Knex, or ActiveRecord migrations.

4. **Connection Management**: Not specified in BluePrint. Implementation handles pooling, retries, and failover.

5. **Sensitive Data**: Columns marked `sensitive: true` should be excluded from logging and may require encryption at rest.
