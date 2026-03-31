# Flutuar Parapente - API Backend

API REST para gerenciamente de alunos interessados em cursos de parapente.
Desenvolvida com Python, Flask, SQLite e documentada com Swagger.

## Descrição

Sistema de cadastro de alunos interessados nos cursos da escola Flutuar Parapente:

Curso ininciante
Cross
Voo duplo

## Rotas disponiveis

| Método | Rota | Descrição|
|--------|------|----------|
| POST | /cadastrar_aluno | Cadastra novo aluno |
| GET | /buscar_aluno/<id> | Busca aluno por ID |
| GET | /buscar_alunos | Lista todos alunos |
| GET | /busca_por_curso | Filtra alunos por curso |
| PUT | /Atualiza_aluno/<id> | Atualiza dados do aluno |
| DELETE | /deletar_aluno/<id> | Remove um aluno |

## Instalação

### Pré-requisitos

- Python 3.10 ou superior

### Passo a passo

1. Clone repositóio:
'''bash
git clone https://github.com/seu-usuario/flutuar-backend.git
cd flutuar-backend
'''

2. Crie e ative o ambiente Virtual:
'''bash
python3 -m venv venv
source venv/bin/activate
'''

3. Instale as dependenias:
'''bash
pip install -r requirements.txt
'''

4. Inicie a API:
'''bash
python app.py
'''
## Acesso

- API http://localhost:5000
- Documentação Swagger: http://localhost:5000/apidocs

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- Flasgger (Swagger)
- Flask-CORS
