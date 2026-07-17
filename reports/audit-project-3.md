# Architecture Audit Report

| Campo        | Detalhe                               |
|--------------|---------------------------------------|
| **Projeto**  | task-manager-api                      |
| **Stack**    | Python + Flask 3.0.0                  |
| **Arquivos** | 15 analisados · ~1161 linhas de código |
| **Data**     | 2026-06-27                            |

---

## Executive Summary

| Severidade   | Total |
|--------------|-------|
| 🔴 Critical  | 5     |
| 🟠 High      | 3     |
| 🟡 Medium    | 7     |
| 🔵 Low       | 2     |
| **Total**    | **17**|

---

## Findings

### 🔴 [CRITICAL] AP-01 — God Class / Monolith File

**Arquivo:** `routes/task_routes.py` · Linhas 1–300

```python
@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    for t in tasks:
        task_data = {}
        task_data['id'] = t.id
        # ... serialização inline de 10 campos
        if t.due_date:
            if t.due_date < datetime.utcnow():  # lógica de negócio
                if t.status != 'done' and t.status != 'cancelled':
```

**Problema:** O arquivo concentra 5 responsabilidades distintas no mesmo escopo: roteamento HTTP, acesso direto ao banco (`Task.query`, `User.query`, `db.session`), validação de entrada, lógica de negócio (cálculo de overdue) e serialização manual de objetos. Com 300 linhas, viola SRP e impossibilita testes isolados de qualquer camada.

**Ação:** Extrair a lógica de negócio para um `TaskController` (ou service), mover validação para schemas Marshmallow, e centralizar serialização no `to_dict()` existente no model.

---

### 🔴 [CRITICAL] AP-02a — Hardcoded Credentials / Secrets in Source

**Arquivo:** `app.py` · Linhas 11–13

```python
app.config['SQLALCHEMY_DATABASE_URI']    = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']                 = 'super-secret-key-123'
```

**Problema:** `SECRET_KEY` e `DATABASE_URI` estão escritos diretamente no código-fonte. Qualquer commit expõe essas chaves no histórico git. A `SECRET_KEY` é usada para assinar sessões e tokens — se vazada, permite forjar qualquer sessão da aplicação.

**Ação:** Mover para variáveis de ambiente lidas via `python-dotenv` (já é dependência do projeto). Criar `config.py` com `os.environ.get('SECRET_KEY')` e `os.environ.get('DATABASE_URI')`.

---

### 🔴 [CRITICAL] AP-02b — Hardcoded Credentials / SMTP Password

**Arquivo:** `services/notification_service.py` · Linhas 7–10

```python
self.email_host     = 'smtp.gmail.com'
self.email_port     = 587
self.email_user     = 'taskmanager@gmail.com'
self.email_password = 'senha123'
```

**Problema:** Credenciais de e-mail (usuário e senha SMTP) escritas como strings literais na classe de serviço. Qualquer pessoa com acesso ao repositório pode usar essas credenciais para enviar e-mail como a conta da aplicação.

**Ação:** Mover para variáveis de ambiente: `EMAIL_USER`, `EMAIL_PASSWORD`, `EMAIL_HOST`, `EMAIL_PORT`. Ler via `os.environ` no construtor ou injetar via parâmetro.

---


**Problema:** Token de autenticação fake e previsível gerado com prefixo literal + user ID. Além disso, `user.to_dict()` inclui o campo `password` (hash MD5) na resposta da API, expondo credenciais ao cliente. MD5 é inseguro para hash de senha.

**Ação:** Implementar autenticação real com `flask-jwt-extended` (já listado no README como pendente). Remover campo `password` do `to_dict()` público ou criar um método `to_public_dict()` sem o campo.

---

### 🟠 [HIGH] AP-04a — Fat Controller — Overdue e Serialização em `get_tasks`

**Arquivo:** `routes/task_routes.py` · Linhas 12–63

```python
def get_tasks():
    tasks = Task.query.all()
    for t in tasks:
        if t.due_date:
            if t.due_date < datetime.utcnow():
                if t.status != 'done' and t.status != 'cancelled':
                    task_data['overdue'] = True
        if t.user_id:
            user = User.query.get(t.user_id)
            task_data['user_name'] = user.name if user else None
```

**Problema:** Função de 51 linhas que concentra cálculo de overdue (regra de domínio), resolução de relacionamentos, serialização manual e lógica condicional aninhada de 3 níveis. O model `Task` já tem `is_overdue()` mas é ignorado. A regra "overdue" está duplicada em 6 pontos da codebase.

**Ação:** Delegar cálculo de overdue ao `Task.is_overdue()` existente. Delegar serialização ao `Task.to_dict()`. Extrair busca enriquecida para um `TaskService.get_all_tasks()` que retorne objetos já formatados.

---

### 🟠 [HIGH] AP-04b — Fat Controller — Lógica de Relatório no Handler HTTP

**Arquivo:** `routes/report_routes.py` · Linhas 12–101

```python
def summary_report():
    users = User.query.all()
    user_stats = []
    for u in users:
        user_tasks  = Task.query.filter_by(user_id=u.id).all()
        total       = len(user_tasks)
        completed   = sum(1 for t in user_tasks if t.status == 'done')
        user_stats.append({
            ...
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
        })
```

**Problema:** Função de 90 linhas que calcula produtividade por usuário, conta overdue, computa taxas de conclusão e agrega estatísticas — tudo dentro do handler HTTP. Regras de negócio idênticas à `task_stats()` em `task_routes.py`. Impossível testar sem simular uma request.

**Ação:** Extrair para `ReportService.generate_summary()` e `ReportService.generate_user_report()`. O handler deve apenas chamar o serviço e serializar a resposta.

---

### 🟠 [HIGH] AP-05 — Hard Coupling / No Dependency Injection

**Arquivo:** `services/notification_service.py` · Linhas 1–48

```python
class NotificationService:
    def __init__(self):
        self.notifications  = []
        self.email_host     = 'smtp.gmail.com'
        self.email_port     = 587
        self.email_user     = 'taskmanager@gmail.com'
        self.email_password = 'senha123'
```

**Problema:** `NotificationService` instancia toda a configuração SMTP internamente no `__init__`, sem receber dependências via injeção. Impossível substituir o transporte de e-mail por mock em testes, ou trocar o provedor SMTP sem editar a classe. Também acumula notificações em lista de instância (estado mutável acoplado ao serviço).

**Ação:** Receber `host`, `port`, `user` e `password` como parâmetros do construtor ou via objeto de configuração. Mover `self.notifications` para persistência real (banco ou cache). Definir protocolo `EmailTransport` abstrato.

---

### 🟡 [MEDIUM] AP-07a — N+1 Query Problem (`get_tasks`)

**Arquivo:** `routes/task_routes.py` · Linhas 41–57

```python
tasks = Task.query.all()
for t in tasks:
    if t.user_id:
        user = User.query.get(t.user_id)      # 1 query por task
    if t.category_id:
        cat = Category.query.get(t.category_id)  # +1 query por task
```

**Problema:** Para N tasks, são executadas até 2N queries adicionais para buscar `User` e `Category`. Com 100 tasks, são 201 queries. `Task` já tem relacionamentos ORM definidos (`task.user`, `task.category`) que poderiam ser carregados com eager loading.

**Ação:** Usar `joinedload`:

```python
Task.query.options(
    joinedload(Task.user),
    joinedload(Task.category)
).all()
```

Acessar `t.user` e `t.category` diretamente sem queries extras.

---

### 🟡 [MEDIUM] AP-07b — N+1 Query Problem (`summary_report`)

**Arquivo:** `routes/report_routes.py` · Linhas 53–68

```python
users = User.query.all()
for u in users:
    user_tasks = Task.query.filter_by(user_id=u.id).all()  # 1 query por usuário
    total      = len(user_tasks)
    completed  = sum(1 for t in user_tasks if t.status == 'done')
```

**Problema:** Para N usuários, são executadas N queries de tasks. Poderia ser resolvido com uma única query usando `GROUP BY` ou com eager loading do relacionamento `User.tasks` (já definido via backref).

**Ação:** Usar eager loading:

```python
User.query.options(joinedload(User.tasks)).all()
```

Ou agregar via:

```python
db.session.query(Task.user_id, func.count()).group_by(Task.user_id)
```

---

### 🟡 [MEDIUM] AP-08a — Missing Input Validation (`int(priority)` sem try/except)

**Arquivo:** `routes/task_routes.py` · Linhas 258–264

```python
def search_tasks():
    priority = request.args.get('priority', '')
    ...
    if priority:
        tasks = tasks.filter(Task.priority == int(priority))
```

**Problema:** Conversão `int(priority)` sem `try/except`. Se o cliente enviar `?priority=abc`, a aplicação lança `ValueError` não tratado, retornando 500 com stack trace exposto. A biblioteca `marshmallow` (já instalada) deveria ser usada para validar query params.

**Ação:** Envolver em `try/except` ou usar marshmallow Schema para validar e converter query params antes de usar.

---

### 🟡 [MEDIUM] AP-08b — Missing Input Validation (Body JSON Ausente)

**Arquivo:** `routes/report_routes.py` · Linhas 196–200

```python
def update_category(cat_id):
    ...
    data = request.get_json()
    if 'name' in data:   # TypeError se data for None
        cat.name = data['name']
```

**Problema:** `request.get_json()` retorna `None` se `Content-Type` não for `application/json` ou se o corpo for inválido. A verificação `if 'name' in data` sem checar se `data` é `None` causa `TypeError` 500. Padrão inconsistente com outros endpoints do projeto que verificam `if not data`.

**Ação:** Adicionar guard antes de acessar campos:

```python
if not data:
    return jsonify({'error': 'Dados inválidos'}), 400
```

---

### 🟡 [MEDIUM] AP-09a — Code Duplication (Lógica de Overdue em 6 Pontos)

**Arquivos:** `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`
**Linhas:** `task_routes.py:30–39` · `user_routes.py:171–180` · `report_routes.py:32–37`

```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            task_data['overdue'] = True
        else:
            task_data['overdue'] = False
    else:
        task_data['overdue'] = False
else:
    task_data['overdue'] = False
```

**Problema:** Bloco de lógica idêntico copiado em 6 pontos: `get_tasks()`, `get_task()`, `task_stats()`, `get_user_tasks()`, `summary_report()` e `user_report()`. O model `Task` já tem `is_overdue()` implementado corretamente (`models/task.py:38–60`) mas é ignorado em todos os pontos.

**Ação:** Substituir todos os blocos por `task.is_overdue()`. Adicionar campo `overdue` ao `Task.to_dict()` usando `is_overdue()` para evitar que routes precisem calcular.

---

### 🟡 [MEDIUM] AP-09b — Code Duplication (Serialização Manual de Task)

**Arquivos:** `routes/task_routes.py`, `routes/user_routes.py`
**Linhas:** `task_routes.py:17–28` · `user_routes.py:163–170`

```python
task_data = {}
task_data['id']          = t.id
task_data['title']       = t.title
task_data['description'] = t.description
task_data['status']      = t.status
task_data['priority']    = t.priority
task_data['created_at']  = str(t.created_at)
task_data['due_date']    = str(t.due_date) if t.due_date else None
```

**Problema:** Serialização manual de `Task` copiada em 3 locais, ignorando o `Task.to_dict()` já existente no model. Inconsistência: `get_tasks()` serializa manualmente mas `get_task()` usa `to_dict()`. Campos diferem entre as cópias.

**Ação:** Usar `Task.to_dict()` em todos os handlers. Se necessário subset de campos, criar `Task.to_summary_dict()`. Remover toda serialização manual inline.

---

### 🟡 [MEDIUM] AP-12 — Deprecated API Usage (SQLAlchemy 2.x)

**Arquivos:** `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`
**Linhas:** `task_routes.py:67, 117, 159` · `user_routes.py:29` · `report_routes.py:105`

```python
task = Task.query.get(task_id)
user = User.query.get(user_id)
cat  = Category.query.get(cat_id)
user = User.query.get(data['user_id'])
```

**Problema:** `Model.query.get()` é deprecated no SQLAlchemy 2.x (base do Flask-SQLAlchemy 3.x em uso). O método emite `LegacyAPIWarning` em runtime e será removido em versão futura. Aparece em 8 locais diferentes nos três arquivos de rota.

**Ação:** Substituir por `db.session.get(Model, pk)`:

```python
db.session.get(Task, task_id)
db.session.get(User, user_id)
db.session.get(Category, cat_id)
```

---

### 🔵 [LOW] AP-10 — Magic Numbers (Validações de Comprimento e Range)

**Arquivo:** `routes/task_routes.py` · Linhas 96–114

```python
if len(title) < 3:
    return jsonify({'error': 'Título muito curto'}), 400
if len(title) > 200:
    return jsonify({'error': 'Título muito longo'}), 400
if priority < 1 or priority > 5:
    return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
if len(password) < 4:
```

**Problema:** Literais `3`, `200`, `1`, `5` e `4` aparecem hardcoded em múltiplos handlers (`create_task` e `update_task` repetem as mesmas validações). O arquivo `utils/helpers.py` já define `MIN_TITLE_LENGTH = 3`, `MAX_TITLE_LENGTH = 200`, `MIN_PASSWORD_LENGTH = 4`, mas os arquivos de rota não os importam.

**Ação:** Importar e usar as constantes já definidas em `utils/helpers.py`. Centralizar `VALID_STATUSES` e `VALID_ROLES` também definidos em `helpers.py` mas ignorados nas rotas.

---

### 🔵 [LOW] AP-11 — Poor Naming (Variáveis de Prioridade e Loop Vars)

**Arquivo:** `routes/report_routes.py` · Linhas 24–28

```python
p1 = Task.query.filter_by(priority=1).count()
p2 = Task.query.filter_by(priority=2).count()
p3 = Task.query.filter_by(priority=3).count()
p4 = Task.query.filter_by(priority=4).count()
p5 = Task.query.filter_by(priority=5).count()
```

**Problema:** Variáveis `p1`–`p5` não comunicam seu significado. Loop variables `t` (Task), `u` (User), `c` (Category) e `cat` usadas em escopos amplos. Um leitor não sabe que `p1` significa "contagem de tasks com prioridade crítica" sem ler todo o contexto.

**Ação:** Renomear para `critical_count`, `high_count`, `medium_count`, `low_count`, `minimal_count`. Renomear loop vars para `task`, `user`, `category` nos `for` loops.

---

### 🔴 [CRITICAL] AP-13 — Weak / Reversible Password Hashing

```python
class User(db.Model):
 def to_dict(self):
        }
    def set_password(self, pwd):
        self.password = hashlib.md5(pwd.encode()).hexdigest()

    def check_password(self, pwd):
        return self.password == hashlib.md5(pwd.encode()).hexdigest()
```


### 🔴 [CRITICAL] AP-14 — Fake or Predictable Authentication Token

```python
class UserController:
 def login(email: str, password: str) -> dict:
            raise PermissionError('Credenciais inválidas')
        if not user.active:
            raise PermissionError('Usuário inativo')
        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': f'placeholder-{user.id}',
        }
```

*Total de findings: 17*
