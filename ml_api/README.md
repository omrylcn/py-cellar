# ML API Template

## Docker Usage

**build the image**

<!-- ```bash
docker build -t spinal-cord-app -f docker/Dockerfile .  
``

``bash
docker run -d --name app -p 8000:8000 spinal-cord-app -v re
``  
# or with custom host and port
docker run -d --name face-analysis -p 9000:9000 -e HOST=0.0.0.0 -e PORT=9000 face-analysis-app
`` -->
<!-- 
```bash
#run with compose 
docker-compose  -f docker/docker-compose.yaml up
`` -->



#  ML API  System Architecture Diagram

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#f5f5f5', 'primaryTextColor': '#333', 'primaryBorderColor': '#a6a6a6', 'lineColor': '#a6a6a6', 'secondaryColor': '#f5f5f5', 'tertiaryColor': '#f5f5f5'}}}%%

graph TD
    User((User))
    Admin((Admin))
    
    subgraph "Docker Environment"
        QAS[QA Service]
        MDB[(MongoDB)]
        MIO[MinIO]
        PROM[Prometheus]
        NODE[Node Exporter]
        GF[Grafana]
        
        QAS -->|Stores Data| MDB
        QAS -->|Stores Files| MIO
        QAS -->|Exposes API Metrics| PROM
        NODE -->|Exposes Server Metrics| PROM
        PROM -->|Provides Log Data| GF
        GF -->|Reads Data| MDB
    end
    
    User -->|Queries| QAS
    Admin -->|Monitors| GF
    
    classDef default fill:#f5f5f5,stroke:#a6a6a6,stroke-width:1px;
    classDef database fill:#e6e6e6,stroke:#a6a6a6,stroke-width:1px;
    classDef storage fill:#f0f0f0,stroke:#a6a6a6,stroke-width:1px;
    classDef monitoring fill:#fafafa,stroke:#a6a6a6,stroke-width:1px;
    classDef metrics fill:#e6e6e6,stroke:#a6a6a6,stroke-width:1px;
    classDef visualization fill:#f0f0f0,stroke:#a6a6a6,stroke-width:1px;
    classDef user fill:#ffffff,stroke:#a6a6a6,stroke-width:1px,stroke-dasharray: 3 3;
    
    class QAS,PROM default;
    class MDB database;
    class MIO storage;
    class NODE metrics;
    class GF visualization;
    class User,Admin user;
    
    style Docker Environment fill:#ffffff,stroke:#d9d9d9,stroke-width:1px,stroke-dasharray: 3 3l:#1a1a1a,stroke:#F8B229,stroke-width:2px,stroke-dasharray: 5 5


```