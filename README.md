# Flutuar Parapente - API Backend

API REST para gerenciamento de alunos interessados em cursos de parapente.
Desenvolvida com Python, Flask, SQLite e documentada com Swagger.

## 📝 Descrição

Sistema de cadastro de alunos interessados nos cursos da escola Flutuar Parapente:

* Curso Iniciante
* Cross
* Voo Duplo

## 🚀 Rotas Disponíveis

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/cadastrar_aluno` | Cadastra novo aluno |
| GET | `/buscar_aluno/<id>` | Busca aluno por ID |
| GET | `/buscar_alunos` | Lista todos os alunos |
| GET | `/busca_por_curso` | Filtra alunos por curso |
| PUT | `/atualiza_aluno/<id>` | Atualiza dados do aluno |
| DELETE | `/deletar_aluno/<id>` | Remove um aluno |

## 🛠️ Instalação

### Pré-requisitos

* Python 3.10 ou superior

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/cristianoricci/flutuar-backend.git](https://github.com/cristianoricci/flutuar-backend.git)
   cd flutuar-backend