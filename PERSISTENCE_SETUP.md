# Stappenplan: Persistence Laag Opzetten met SQLModel

## Overzicht
Dit document beschrijft stap-voor-stap hoe je de persistence laag (database, ORM, repository pattern) opzet voor een FastAPI applicatie.

---

## Stap 1: Dependencies Installeren

### 1.1 Requirements.txt bijwerken
Voeg SQLModel toe aan `requirements.txt`:
```
sqlmodel==0.0.14
```

### 1.2 Packages installeren
```bash
pip install -r requirements.txt
```

**Wat gebeurt er?**
- SQLModel wordt geïnstalleerd (combineert SQLAlchemy + Pydantic)
- Dit geeft je type-safe database modellen die werken met FastAPI

---

## Stap 2: Database Configuratie

### 2.1 Database Type Kiezen

**Optie A: SQLite (Aanbevolen voor ontwikkeling)**
- ✅ Eenvoudigste setup
- ✅ Geen extra server nodig
- ✅ Bestand-gebaseerd (app.db)
- ✅ Perfect voor development/testing


**Optie B: PostgreSQL/MySQL (Voor productie)**
- ✅ Productie-ready
- ✅ Vereist database server
- ✅ Betere performance voor grote datasets

### 2.2 Database URL Configureren

In `main.py`:
```python
# SQLite (aanbevolen)
DATABASE_URL = "sqlite:///./app.db"

# PostgreSQL (voor productie)
# DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL (voor productie)
# DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

---

## Stap 3: Database Engine Opzetten

### 3.1 Engine Aanmaken
In `main.py`:
```python
from sqlmodel import create_engine

engine = create_engine(DATABASE_URL, echo=True)
```

**Parameters:**
- `DATABASE_URL`: Connection string naar database
- `echo=True`: Logt alle SQL queries (handig voor debugging)

### 3.2 Repository Engine Setup
In `main.py`:
```python
from repositories.user_repository import UserRepository

# Set engine voor repository (geen dependency injection nodig)
UserRepository.set_engine(engine)
```

**Waarom?**
- Repository beheert zijn eigen database sessies
- Geen dependency injection nodig - direct aanroepen mogelijk
- Automatische cleanup van sessies via `with` statements
- Simpelere code zonder sessie doorgeven
- **Belangrijk**: Roep dit aan VOORDAT je de repository gebruikt

---

## Stap 4: Database Modellen (Entities) Maken

### 4.1 Model Structuur
Maak `models/` directory aan:
```
models/
  __init__.py
  user_model.py
```

### 4.2 Model Definiëren
In `models/user_model.py`:
```python
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    """User entity voor database"""
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
```

**Belangrijke punten:**
- `SQLModel`: Base class (combineert Pydantic + SQLAlchemy)
- `table=True`: Maakt het een database tabel
- `Field()`: SQLModel field definitie
- `primary_key=True`: Primaire sleutel

### 4.3 Model Registreren
In `models/__init__.py`:

```python
from dbmodels.user_model import User

__all__ = ["User"]
```

---

## Stap 5: Database Tabellen Aanmaken

### 5.1 Lifespan Event Handler
In `main.py`:
```python
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from repositories.user_repository import UserRepository

# Database setup
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=True)

# Set engine voor repository (BELANGRIJK: voor lifespan)
UserRepository.set_engine(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events"""
    # Maak tabellen aan bij startup
    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup bij shutdown (optioneel)

app = FastAPI(lifespan=lifespan)
```

**Wat gebeurt er?**
- Bij applicatie start: alle tabellen worden aangemaakt
- Bij applicatie stop: cleanup (indien nodig)
- **Belangrijk**: `UserRepository.set_engine()` moet worden aangeroepen VOORDAT de app start

### 5.2 Alternatief: Migraties (Voor productie)
Voor productie gebruik je beter Alembic voor migrations:
```bash
pip install alembic
alembic init alembic
```

---

## Stap 6: Repository Laag Opzetten

### 6.1 Repository Structuur
Maak `repositories/` directory:
```
repositories/
  __init__.py
  user_repository.py
```

### 6.2 Repository Class Maken
In `repositories/user_repository.py`:

```python
from sqlmodel import Session, select, Engine
from dbmodels.user_model import User


class UserRepository:
    """Repository voor User data access"""

    _engine: Engine | None = None

    @classmethod
    def set_engine(cls, engine: Engine):
        """Set de database engine voor de repository"""
        cls._engine = engine

    @classmethod
    def _get_session(cls) -> Session:
        """Haal database sessie op"""
        if cls._engine is None:
            raise RuntimeError("Database engine niet ingesteld. Roep UserRepository.set_engine() eerst aan.")
        return Session(cls._engine)

    @classmethod
    def create(cls, user: User) -> User:
        """Maak nieuwe user aan"""
        with cls._get_session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @classmethod
    def find_by_id(cls, user_id: int) -> User | None:
        """Vind user op ID"""
        with cls._get_session() as session:
            statement = select(User).where(User.id == user_id)
            return session.exec(statement).first()

    @classmethod
    def find_by_email(cls, email: str) -> User | None:
        """Vind user op email"""
        with cls._get_session() as session:
            statement = select(User).where(User.email == email)
            return session.exec(statement).first()

    @classmethod
    def find_all(cls) -> list[User]:
        """Vind alle users"""
        with cls._get_session() as session:
            statement = select(User)
            return list(session.exec(statement).all())
```

**Repository Pattern Voordelen:**
- ✅ Scheiding van data access logica
- ✅ Geen dependency injection nodig - direct aanroepen mogelijk
- ✅ Automatische sessie management (geen sessie doorgeven)
- ✅ Makkelijk te testen (mock repository)
- ✅ Herbruikbaar voor verschillende data sources
- ✅ Centrale plek voor database queries

**Belangrijk:**
- Alle methoden zijn `@classmethod` - geen instantie nodig
- Je kunt direct `UserRepository.create(user)` aanroepen
- Sessies worden automatisch beheerd via `with` statements

---

## Stap 7: Mapper Laag Opzetten

### 7.1 Mapper Structuur
Maak `mappers/` directory:
```
mappers/
  __init__.py
  user_mapper.py
```

### 7.2 Mapper Class Maken
In `mappers/user_mapper.py`:

```python
from dbmodels.user_model import User
from dtos.user_dto import ApiUserCreate, ApiUser


class UserMapper:
    """Mapper voor DTO <-> Entity conversie"""

    @staticmethod
    def to_entity(dto: ApiUserCreate) -> User:
        """Converteer DTO naar Entity"""
        return User(
            name=dto.name,
            email=dto.email
        )

    @staticmethod
    def to_dto(entity: User) -> ApiUser:
        """Converteer Entity naar DTO"""
        return ApiUser(
            id=entity.id,
            name=entity.name,
            email=entity.email
        )
```

**Waarom Mappers?**
- ✅ Scheiding tussen API layer (DTOs) en database layer (Entities)
- ✅ Flexibiliteit om modellen onafhankelijk te wijzigen
- ✅ Veiligheid (geen database velden direct in API)

---

## Stap 8: Service Laag Opzetten

### 8.1 Service Structuur
Maak `services/` directory:
```
services/
  __init__.py
  user_service.py
```

### 8.2 Service Class Maken
In `services/user_service.py`:
```python
from repositories.user_repository import UserRepository
from mappers.user_mapper import UserMapper
from dtos.user_dto import ApiUserCreate, ApiUser

class UserService:
    """Service voor User business logica"""
    
    def __init__(self):
        self.mapper = UserMapper()
    
    def create_user(self, user_create: ApiUserCreate) -> ApiUser:
        """Maak nieuwe user aan met validatie"""
        # Check of user al bestaat
        existing_user = UserRepository.find_by_email(user_create.email)
        if existing_user:
            raise ValueError(f"User met email {user_create.email} bestaat al")
        
        # Converteer DTO naar Entity
        user_entity = self.mapper.to_entity(user_create)
        
        # Sla op in database (geen repository injectie nodig)
        created_user = UserRepository.create(user_entity)
        
        # Converteer Entity terug naar DTO
        return self.mapper.to_dto(created_user)
```

**Service Layer Voordelen:**
- ✅ Business logica gescheiden van data access
- ✅ Validatie en regels op één plek
- ✅ Geen dependency injection nodig - direct repository aanroepen
- ✅ Makkelijk te testen
- ✅ Herbruikbaar voor verschillende endpoints

---

## Stap 9: Router Integratie

### 9.1 Router Bijwerken
In `routers/user_router.py`:
```python
from fastapi import APIRouter, HTTPException, status
from services.user_service import UserService
from dtos.user_dto import ApiUserCreate, ApiUser

class UserRouter:
    router = APIRouter()

    def __init__(self):
        """Initialize router"""
        self.service = UserService()
        self._register_routes()

    def _register_routes(self):
        """Register routes"""
        @self.router.post("/users", response_model=ApiUser, status_code=status.HTTP_201_CREATED)
        def create_user(user_create: ApiUserCreate):
            """Maak nieuwe user aan"""
            try:
                return self.service.create_user(user_create)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
```

**Belangrijk:**
- Geen `Depends` of `Session` parameters nodig
- Service wordt direct geïnstantieerd in `__init__`
- Geen dependency injection - veel eenvoudiger!

### 9.2 Router Registreren
In `main.py`:
```python
from routers.user_router import UserRouter
from repositories.user_repository import UserRepository

# Set engine voor repository (moet voor router instantiatie)
UserRepository.set_engine(engine)

# Instantiate UserRouter (geen dependency injection nodig)
user_router_instance = UserRouter()
app.include_router(user_router_instance.router, prefix="", tags=["users"])
```

---

## Stap 10: Testen

### 10.1 Applicatie Starten
```bash
uvicorn main:app --reload
```

### 10.2 Database Controleren
- Check of `app.db` bestand is aangemaakt
- Check Swagger UI: http://localhost:8000/docs

### 10.3 Endpoint Testen
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'
```

### 10.4 Direct Repository Gebruik (Zonder Dependency Injection)
Je kunt de repository ook direct gebruiken zonder via de service/router:

```python
from repositories.user_repository import UserRepository
from dbmodels.user_model import User

# Direct gebruiken - geen sessie nodig!
user = User(name="John Doe", email="john@example.com")
saved_user = UserRepository.create(user)

# Of andere methoden:
found_user = UserRepository.find_by_email("john@example.com")
all_users = UserRepository.find_all()
```

**Voordelen:**
- ✅ Geen dependency injection nodig
- ✅ Simpelere code
- ✅ Direct aanroepen mogelijk
- ✅ Automatische sessie management

---

## Architectuur Overzicht

```
HTTP Request
    ↓
Router (user_router.py) - Geen dependency injection
    ↓
Service (user_service.py) - Business Logic
    ↓
Mapper (user_mapper.py) - DTO ↔ Entity
    ↓
Repository (user_repository.py) - Data Access (class methods)
    ↓ (beheert eigen sessies)
Model (user_model.py) - Database Entity
    ↓
Database (SQLite/PostgreSQL)
```

**Belangrijk verschil:**
- Geen dependency injection - repositories beheren hun eigen sessies
- Direct aanroepen: `UserRepository.create(user)` zonder sessie doorgeven
- Simpelere code zonder `Depends()` en sessie parameters

---

## Best Practices

### ✅ DO:
- Gebruik class methods voor repositories (geen dependency injection nodig)
- Roep `UserRepository.set_engine()` aan bij applicatie start
- Scheid lagen duidelijk (Router → Service → Repository)
- Gebruik DTOs voor API layer
- Valideer data in service layer
- Gebruik type hints overal
- Gebruik `with` statements voor automatische sessie cleanup

### ❌ DON'T:
- Database queries direct in routers
- Business logica in repositories
- Entities direct teruggeven aan API
- Sessies niet proper afsluiten (gebruik `with` statements)
- Hardcoded database credentials
- Dependency injection gebruiken voor repositories (niet nodig met deze aanpak)

---

## Volgende Stappen

1. **Migrations**: Setup Alembic voor database migrations
2. **Error Handling**: Verbeter error handling en logging
3. **Transactions**: Implementeer transaction management
4. **Testing**: Schrijf unit tests voor elke laag
5. **Relationships**: Voeg relaties tussen modellen toe
6. **Indexes**: Voeg database indexes toe voor performance

---

## Troubleshooting

### Probleem: "Table already exists"
**Oplossing**: Verwijder `app.db` bestand en herstart applicatie

### Probleem: "Import errors"
**Oplossing**: Check of alle `__init__.py` bestanden aanwezig zijn

### Probleem: "Database engine not set"
**Oplossing**: Zorg dat je `UserRepository.set_engine(engine)` aanroept in `main.py` voordat je de repository gebruikt

### Probleem: "Database locked"
**Oplossing**: Check of alle sessies correct worden afgesloten. In de repository worden `with` statements gebruikt voor automatische cleanup - dit zou niet moeten voorkomen.

### Probleem: "RuntimeError: Database engine not set"
**Oplossing**: Zorg dat `UserRepository.set_engine(engine)` wordt aangeroepen in `main.py` voordat de applicatie routes gebruikt

---
