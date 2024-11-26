

```mermaid
flowchart TD
    subgraph "Client Side"
        CL([Client])
    end

    subgraph "Load Balancer"
        LB[NGINX]
    end

    subgraph "API Service"
        API[FastAPI]
    end

    subgraph "Cache & Queue"
        REDIS[Redis]
        RMQ[RabbitMQ]
    end

    subgraph "Storage"
        DB[(MongoDB)]
        OBJ[MinIO]
    end

    subgraph "ML Service"
        W1[ML Worker]
        W2[ML Worker]
    end

    %% Main Flow
    CL -->|1. Request| LB
    LB -->|2. Route Request| API
    API -->|3. Check Cache| REDIS
    API -->|4. Create Task| RMQ
    RMQ -->|5. Distribute Task| W1 & W2
    W1 & W2 -->|6. Load Model| OBJ
    W1 & W2 -->|7. Store Results| DB
    W1 & W2 -->|8. Cache Results| REDIS
    REDIS -->|9. Get Results| API
    API -->|10. Response| LB
    LB -->|11. Final Response| CL

    classDef client fill:#e1f5fe,stroke:#01579b
    classDef lb fill:#e8f5e9,stroke:#1b5e20
    classDef api fill:#fff3e0,stroke:#e65100
    classDef cache fill:#f3e5f5,stroke:#4a148c
    classDef storage fill:#c8e6c9,stroke:#388e3c
    classDef worker fill:#f8bbd0,stroke:#c2185b
    
    class CL client
    class LB lb
    class API api
    class REDIS,RMQ cache
    class DB,OBJ storage
    class W1,W2 worker

```

SIMPLIFIED COMPONENTS:

1. Core Services:
```
NGINX (Load Balancer):
- Route requests
- SSL termination
- Basic load balancing

FastAPI:
- Handle requests
- Task management
- Response handling

RabbitMQ:
- Task queue
- Message distribution
- Worker coordination

Redis:
- Results caching
- Session management
- Temporary storage
```

2. Storage:
```
MongoDB:
- Task results
- User data
- System logs

MinIO:
- ML model files
- Large datasets
- Binary data
```

3. Processing:
```
ML Workers:
- Model loading
- Inference
- Result generation
```

BASIC FLOW:

1. Request Handling:
```
Client → NGINX → FastAPI
- Request validation
- Authentication
- Task creation
```

2. Processing:
```
FastAPI → RabbitMQ → Workers
- Task distribution
- Model inference
- Result generation
```

3. Storage & Response:
```
Workers → MongoDB/Redis → FastAPI → Client
- Result storage
- Cache update
- Response delivery
```
