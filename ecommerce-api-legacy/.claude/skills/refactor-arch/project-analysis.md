# Project Analysis Reference — Phase 1

Este arquivo define as heurísticas que a skill `refactor-arch` utiliza na **Fase 1** para detectar
linguagem, framework, banco de dados, arquitetura atual e domínio de negócio de qualquer projeto,
independente da stack tecnológica.

Ao final da análise a skill imprime no terminal o **resumo estruturado** cujo formato está definido
na seção [Formato do Resumo](#formato-do-resumo-terminal).

---

## 1. Detecção de Linguagem

### Passo 1 — Identificar arquivos de manifesto (fonte primária)

| Arquivo encontrado        | Linguagem        |
|---------------------------|------------------|
| `requirements.txt`        | Python           |
| `pyproject.toml`          | Python           |
| `setup.py` / `setup.cfg`  | Python           |
| `Pipfile`                 | Python           |
| `package.json`            | JavaScript / TypeScript |
| `tsconfig.json`           | TypeScript       |
| `go.mod`                  | Go               |
| `Gemfile`                 | Ruby             |
| `pom.xml`                 | Java (Maven)     |
| `build.gradle`            | Java / Kotlin (Gradle) |
| `composer.json`           | PHP              |
| `Cargo.toml`              | Rust             |
| `*.csproj` / `*.sln`      | C#               |

### Passo 2 — Confirmar pela extensão predominante dos arquivos-fonte

| Extensão         | Linguagem        |
|------------------|------------------|
| `.py`            | Python           |
| `.js`            | JavaScript       |
| `.ts`            | TypeScript       |
| `.go`            | Go               |
| `.rb`            | Ruby             |
| `.java`          | Java             |
| `.php`           | PHP              |
| `.rs`            | Rust             |
| `.cs`            | C#               |

**Regra:** Se os dois passos concordam, a linguagem está confirmada. Se divergem, priorize o manifesto
e registre a divergência como observação.

---

## 2. Detecção de Framework e Versão

### Python

| Sinal de detecção                                               | Framework        | Como extrair versão               |
|------------------------------------------------------------------|------------------|-----------------------------------|
| `flask` em `requirements.txt` ou `pyproject.toml`               | Flask            | `flask==<versão>` no manifesto    |
| `from flask import` em qualquer `.py`                           | Flask            | —                                 |
| `django` no manifesto ou `manage.py` na raiz                    | Django           | `django==<versão>` no manifesto   |
| `fastapi` no manifesto ou `from fastapi import`                 | FastAPI          | `fastapi==<versão>` no manifesto  |
| `tornado` no manifesto                                          | Tornado          | idem                              |
| `aiohttp` no manifesto ou `from aiohttp import`                 | aiohttp          | idem                              |

### JavaScript / TypeScript (Node.js)

Ler `package.json` → campo `dependencies` (e `devDependencies`):

| Dependência encontrada                      | Framework        |
|---------------------------------------------|------------------|
| `"express"`                                 | Express          |
| `"@nestjs/core"`                            | NestJS           |
| `"fastify"`                                 | Fastify          |
| `"koa"`                                     | Koa              |
| `"hapi"` / `"@hapi/hapi"`                  | Hapi             |
| `"next"` (com pages/ ou app/)              | Next.js          |
| `"nuxt"`                                    | Nuxt.js          |

Versão: valor da chave em `dependencies` (ex: `"express": "^4.18.2"` → Express 4.18.2).

### Ruby

| Sinal                                        | Framework        |
|----------------------------------------------|------------------|
| `gem 'rails'` no `Gemfile`                  | Ruby on Rails    |
| `gem 'sinatra'`                              | Sinatra          |
| `gem 'hanami'`                               | Hanami           |

### Java

| Sinal                                        | Framework        |
|----------------------------------------------|------------------|
| `spring-boot-starter` em `pom.xml`          | Spring Boot      |
| `quarkus-core` em `pom.xml`                 | Quarkus          |
| `micronaut-core`                             | Micronaut        |

### PHP

| Sinal                                        | Framework        |
|----------------------------------------------|------------------|
| `laravel/framework` em `composer.json`      | Laravel          |
| `symfony/framework-bundle`                  | Symfony          |
| `slim/slim`                                 | Slim             |

---

## 3. Detecção de Dependências Relevantes

Após identificar o manifesto principal, listar **todas as dependências** e destacar as que têm
impacto arquitetural ou de segurança:

| Categoria              | Exemplos                                                              |
|------------------------|-----------------------------------------------------------------------|
| CORS                   | `flask-cors`, `cors` (npm), `rack-cors`                              |
| Autenticação / JWT     | `flask-jwt-extended`, `jsonwebtoken`, `passport`, `devise`           |
| ORM / Query Builder    | `sqlalchemy`, `sequelize`, `prisma`, `typeorm`, `activerecord`       |
| Validação              | `marshmallow`, `pydantic`, `joi`, `zod`, `cerberus`                  |
| Testes                 | `pytest`, `jest`, `rspec`, `junit`                                   |
| Migrations             | `alembic`, `flask-migrate`, `knex`, `flyway`, `liquibase`            |
| Caching                | `redis`, `flask-caching`, `ioredis`                                  |
| Task Queue             | `celery`, `bull`, `sidekiq`                                          |

---

## 4. Detecção de Banco de Dados

### 4.1 — Tipo de banco

| Sinal de detecção                                              | Banco de Dados    |
|----------------------------------------------------------------|-------------------|
| `import sqlite3` / `sqlite3` em qualquer `.py`                | SQLite            |
| Arquivo `.db` ou `.sqlite` na raiz ou em algum diretório      | SQLite            |
| `psycopg2` / `pg` / `DATABASE_URL` com `postgres://`         | PostgreSQL        |
| `pymysql` / `mysql-connector` / `mysql2` / `mysql://`        | MySQL / MariaDB   |
| `pymongo` / `mongoose` / `mongodb://`                         | MongoDB           |
| `redis` / `ioredis` / `redis://`                              | Redis             |
| `cx_Oracle` / `oracledb`                                      | Oracle            |
| `pyodbc` / `mssql://`                                         | SQL Server        |

### 4.2 — ORM ou acesso direto

| Sinal                                          | Tipo de acesso        |
|------------------------------------------------|-----------------------|
| `from sqlalchemy` / `import sqlalchemy`        | ORM (SQLAlchemy)      |
| `from flask_sqlalchemy import`                 | ORM (Flask-SQLAlchemy)|
| `sequelize.define(` / `Model.extend(`         | ORM (Sequelize)       |
| `prisma.schema` na raiz                        | ORM (Prisma)          |
| `cursor.execute(` / `db.query(`               | SQL direto (raw)      |
| `mongoose.model(`                              | ODM (Mongoose)        |

### 4.3 — Extração de tabelas / coleções (SQL direto)

Quando não há ORM, escanear todos os arquivos-fonte buscando:

```
CREATE TABLE\s+(\w+)
cursor\.execute\(.*?["']([A-Z]+ (?:INTO|FROM|UPDATE|JOIN) (\w+))
```

Listar as tabelas únicas encontradas. Exemplo de resultado:

```
DB tables: produtos, usuarios, pedidos, itens_pedido
```

### 4.4 — Extração de modelos (ORM)

Quando há ORM, escanear buscando definições de classe que estendam a classe base do ORM:

- SQLAlchemy: `class \w+\(db\.Model\)` ou `class \w+\(Base\)`
- Sequelize: `sequelize.define('(\w+)'`
- Mongoose: `new Schema\({`

---

## 5. Mapeamento de Arquitetura

### 5.1 — Inventário de arquivos-fonte

Listar todos os arquivos de código (excluindo `node_modules`, `.venv`, `__pycache__`, `.git`,
`dist`, `build`). Contar e registrar:

- Total de arquivos
- Total de linhas de código (aproximado)

### 5.2 — Padrões de nomenclatura e estrutura de diretórios

Identificar a presença (ou ausência) das camadas MVC pelos padrões abaixo:

| Sinal encontrado                                                   | Camada detectada         |
|--------------------------------------------------------------------|--------------------------|
| `models.py`, `model.py`, `models/`, `entities/`, `domain/`        | Model                    |
| `controllers.py`, `controller.py`, `controllers/`, `handlers/`    | Controller               |
| `views.py`, `views/`, `templates/`, `routes.py`, `routes/`        | View / Routes            |
| `services.py`, `services/`, `use_cases/`                          | Service Layer            |
| `repositories.py`, `repositories/`, `data/`                       | Repository Layer         |
| `middlewares/`, `middleware.py`                                    | Middleware               |
| `config.py`, `settings.py`, `config/`                             | Configuration            |
| `utils.py`, `helpers.py`, `utils/`                                 | Utilities                |
| `tests/`, `test_*.py`, `*.spec.js`, `*.test.ts`                   | Tests                    |

### 5.3 — Classificação da arquitetura atual

Com base no inventário, classificar em uma das categorias:

| Classificação                         | Critério                                                                                 |
|---------------------------------------|------------------------------------------------------------------------------------------|
| **Monolítica — arquivo único**        | Toda a lógica em 1 arquivo (rotas, banco, negócio, inicialização)                       |
| **Monolítica — múltiplos arquivos**   | Lógica dividida em poucos arquivos sem separação clara de responsabilidades              |
| **MVC Parcial**                       | Existe separação em camadas mas com violações (ex: lógica de negócio nos controllers)   |
| **MVC / Layered**                     | Separação clara entre Model, View/Routes e Controller; responsabilidades bem definidas   |
| **Hexagonal / Clean Architecture**    | Domínio isolado de infraestrutura; ports & adapters ou use cases explícitos             |

### 5.4 — Detecção de domínio de negócio

Inferir o domínio a partir de:

1. Nome do projeto / diretório raiz
2. Nomes de tabelas / modelos / entidades
3. Nomes de rotas e endpoints
4. `README.md` quando presente

Exemplos de domínios comuns:

| Sinais encontrados                                        | Domínio inferido                |
|-----------------------------------------------------------|---------------------------------|
| `produto`, `pedido`, `carrinho`, `checkout`, `estoque`   | E-commerce                      |
| `task`, `todo`, `tarefa`, `projeto`, `board`              | Task Manager                    |
| `curso`, `aula`, `aluno`, `matricula`, `lms`              | LMS / Educação                  |
| `usuario`, `login`, `auth`, `token`, `permissao`          | Autenticação / IAM              |
| `relatorio`, `dashboard`, `metricas`, `analytics`        | Analytics / BI                  |

---

## 7. Observações de Edge Cases

- **Múltiplos bancos de dados:** se houver mais de um banco (ex: PostgreSQL + Redis), listar todos
  separados por ` + ` no campo `DB Engine`.
- **Monorepo / múltiplos subprojetos:** analisar apenas o diretório raiz onde a skill foi invocada.
- **Arquivos de configuração com variáveis de ambiente:** quando a string de conexão está em `.env`,
  registrar o tipo de banco inferido pelo prefixo da URL (`postgres://`, `mongodb://`, etc.).
- **Projeto sem banco de dados:** preencher os campos DB com `N/A`.
- **Versão não detectável:** omitir o campo de versão em vez de exibir `None` ou `unknown`.
- **Projeto TypeScript transpilado:** contar os arquivos `.ts` como fonte primária;
  ignorar a pasta `dist/` ou `build/`.
