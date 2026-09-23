Markdown

## 📐 Arquitetura da Solução

O projeto adota uma arquitetura em camadas e microsserviços containerizados baseada no padrão **1.1 (API RESTful com Persistência e Consumo de API Externa)** da PUC-Rio.

```mermaid
graph TD
    %% Estilização de nós
    classDef client fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef api fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef db fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef ext fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff;
    classDef docker fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff;

    subgraph Docker_Environment [" 🐳 Ambiente Docker / Docker Compose "]
        
        subgraph Frontend_Container [" 🖥️ Container Front-End (flutuar-ui) "]
            UI[React.js App<br/>Porta :3001]:::client
        end

        subgraph Backend_Container [" ⚙️ Container Back-End (flutuar-api) "]
            API[Flask API REST<br/>Porta :5000]:::api
            CORS[Flask-CORS]:::api
            SWAGGER[Flasgger / Swagger UI<br/>/apidocs]:::api
            
            API --- CORS
            API --- SWAGGER
        end

        subgraph Database_Storage [" 💾 Camada de Persistência "]
            DB[(SQLite Database<br/>flutuar.db)]:::db
        end

    end

    subgraph External_Services [" 🌐 Serviços Externos "]
        EXT[API Meteorológica Externa<br/>Open-Meteo / wttr.in]:::ext
    end

    %% Fluxo de Comunicação
    UI -->|1. Requisições HTTP REST / JSON<br/>Fetch API| API
    API -->|2. Consultas e Persistência SQL| DB
    API -->|3. Consulta de Clima e Vento<br/>HTTP GET| EXT

    %% Estilização dos subgraphs
    style Docker_Environment fill:#f0f9ff,stroke:#0284c7,stroke-width:2px,stroke-dasharray: 5 5;
    style Frontend_Container fill:#eff6ff,stroke:#3b82f6,stroke-width:1px;
    style Backend_Container fill:#ecfdf5,stroke:#10b981,stroke-width:1px;
    style Database_Storage fill:#fffbeb,stroke:#f59e0b,stroke-width:1px;
    style External_Services fill:#f5f3ff,stroke:#8b5cf6,stroke-width:1px;

🔄 Fluxo de Comunicação do Sistema

    Interface do Usuario (Front-End): O painel em React (porta 3001) envia requisições assíncronas via Fetch API para o servidor backend na porta 5000.

    Processamento & Regras de Negócio (Back-End): A API Flask processa os endpoints (/clima, /cadastrar_aluno, /buscar_alunos, /atualizar_aluno).

    Persistência de Dados: O módulo CRUD comunica-se com o banco de dados SQLite (flutuar.db) para armazenamento de pilotos e alunos.

    Integração Externa: Ao consultar condições meteorológicas, a API conecta-se com serviços externos de clima para obter dados em tempo real sobre vento e voo.