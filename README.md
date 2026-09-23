# Flutuar API - Escola de Parapente (Back-End)

A **Flutuar API** é o back-end do sistema de gestão da escola de parapente **Flutuar**, desenvolvido como parte do MVP de **Backend Avançado** da Pós-Graduação em Desenvolvimento Full Stack da PUC-Rio. A API é responsável pelo CRUD de alunos/pilotos, persistência em banco de dados SQLite e consulta de condições meteorológicas em tempo real via API externa, apoiando a decisão de voo dos instrutores.

## 🚀 Tecnologias Utilizadas

* **Python 3.10**
* **Flask** — framework web para construção da API REST
* **Flask-CORS** — liberação de acesso ao front-end (React)
* **Flasgger (Swagger UI)** — documentação interativa dos endpoints em `/apidocs`
* **SQLite** — persistência de dados
* **Requests** — consumo da API externa de clima
* **Docker** — containerização da aplicação

## 📐 Arquitetura da Solução

O projeto adota o **Cenário 1.1** proposto no MVP de Backend Avançado da PUC-Rio: uma Interface (Front-End) que se comunica via REST com uma API (Back-End) responsável pela persistência dos dados e pelo consumo de uma API externa.

```mermaid
graph TD
    %% Estilização de nós
    classDef client fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef api fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef db fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef ext fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff;
    classDef docker fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff;

    subgraph Frontend_Container [" 🐳 Container Front-End — repo flutuar-react (Dockerfile próprio) "]
        UI[React.js App<br/>Porta :3001]:::client
    end

    subgraph Backend_Container [" 🐳 Container Back-End — repo flutuar-backend (Dockerfile próprio) "]
        API[Flask API REST<br/>Porta :5000]:::api
        CORS[Flask-CORS]:::api
        SWAGGER[Flasgger / Swagger UI<br/>/apidocs]:::api
        DB[(SQLite Database<br/>flutuar.db)]:::db
        API --- CORS
        API --- SWAGGER
        API --- DB
    end

    subgraph External_Services [" 🌐 Serviços Externos "]
        EXT[API Meteorológica Externa<br/>Open-Meteo / wttr.in]:::ext
    end

    %% Fluxo de Comunicação
    UI -->|1. Requisições HTTP REST / JSON<br/>Fetch API| API
    API -->|2. Consultas e Persistência SQL| DB
    API -->|3. Consulta de Clima e Vento<br/>HTTP GET| EXT

    %% Estilização dos subgraphs
    style Frontend_Container fill:#eff6ff,stroke:#3b82f6,stroke-width:2px;
    style Backend_Container fill:#ecfdf5,stroke:#10b981,stroke-width:2px;
    style External_Services fill:#f5f3ff,stroke:#8b5cf6,stroke-width:1px;
```

### 🔄 Fluxo de Comunicação do Sistema

1. **Interface do Usuário (Front-End):** o painel em React envia requisições assíncronas via Fetch API para o servidor back-end.
2. **Processamento & Regras de Negócio (Back-End):** a API Flask processa os endpoints (`/clima`, `/cadastrar_aluno`, `/buscar_alunos`, `/atualizar_aluno`, `/deletar_aluno`).
3. **Persistência de Dados:** o módulo de acesso a dados comunica-se com o banco SQLite (`flutuar.db`) para armazenamento de pilotos e alunos.
4. **Integração Externa:** ao consultar condições meteorológicas, a API se conecta ao serviço externo **wttr.in** para obter dados em tempo real sobre vento e condição de voo.

## 🔧 Como Executar o Projeto Localmente

Certifique-se de ter o [Python 3.10+](https://www.python.org/) instalado.

1. Clone o repositório:
```bash
git clone https://github.com/cristianoricci/flutuar-backend.git
cd flutuar-backend
```

2. Crie e ative um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute a aplicação:
```bash
python app.py
```

5. A API estará disponível em `http://localhost:5000`, e a documentação Swagger em `http://localhost:5000/apidocs`.

## 🐳 Como Executar via Docker

1. Construa a imagem:
```bash
docker build -t flutuar-api .
```

2. Execute o container:
```bash
docker run -p 5000:5000 flutuar-api
```

3. Acesse `http://localhost:5000/apidocs` para testar os endpoints.

## 📌 Endpoints Disponíveis

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/cadastrar_aluno` | Cadastra um novo aluno/piloto |
| `GET` | `/buscar_alunos` | Lista todos os alunos cadastrados |
| `GET` | `/buscar_aluno/<id>` | Busca um aluno específico por ID |
| `GET` | `/buscar_por_curso?curso=` | Filtra alunos por curso |
| `PUT` | `/atualizar_aluno/<id>` | Atualiza os dados de um aluno |
| `DELETE` | `/deletar_aluno/<id>` | Remove um aluno |
| `GET` | `/clima?cidade=` | Consulta condição climática para voo |

Documentação completa e interativa de todos os endpoints disponível em **`/apidocs`** (Swagger UI).

## 🌐 API Externa Utilizada

* **Serviço:** [wttr.in](https://wttr.in) — serviço público e gratuito de consulta de condições climáticas.
* **Licença/Cadastro:** serviço aberto, sem necessidade de cadastro ou chave de API.
* **Rota consumida internamente:** `https://wttr.in/{cidade}?format=j1`
* **Rota exposta pela nossa API:** `GET /clima?cidade={nome_da_cidade}`
* Os dados retornados (temperatura, velocidade e direção do vento) são **tratados e reformatados** pela nossa API antes de serem entregues ao front-end — não há redirecionamento do usuário para o serviço externo.

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos, como parte do MVP de Backend Avançado da Pós-Graduação em Desenvolvimento Full Stack da PUC-Rio.
