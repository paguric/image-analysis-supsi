# image-analysis-supsi

## Tech Stack

| Componente        | Tecnologia                                                                      | Scopo                                                   |
| ----------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Backend           | [FastAPI](https://fastapi.tiangolo.com/)                                        | Framework sviluppo web Python                           |
| Validation        | [Pydantic](https://docs.pydantic.dev/)                                          | Validazione dati e serializzazione                      |
| Database          | [SQLite](https://sqlite.org/)                                                   | Database relazionale                                    |
| Web Frontend      | [React](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)     | Componenti UI                                           |
| Web Styling       | [Tailwind CSS](https://tailwindcss.com/) e  [MUI](https://mui.com/material-ui/) | Libreria CSS e componenti moderni                       |
| Web Build Tool    | [Vite](https://vitejs.dev/)                                                     | Server di sviluppo per frontend                         |
| Package Manager   | [uv](https://docs.astral.sh/uv/) (Python) / npm (Node)                          | Gestione dipendenze                                     |


## Requisiti

| Tool    | Versione | Installation                                                                 |
| ------- | -------- | -----------------------------------------------------------------------------|
| Python  | 3.11+    | [python.org](https://www.python.org/downloads/)                              |
| uv      | Latest   | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Node.js | 18+      | [nodejs.org](https://nodejs.org/)                                            |
| npm     | 9+       | Installato assieme a Node.js                                                 |


## Quick Start

### 1. Clona la repository

```bash
git clone 
cd
```

### 2. Avvia il backend

```bash
cd backend
uv sync                      # Installa dipendenze Python
uv run fastapi dev main.py   # Avvia server FastAPI
```

L'API sarà disponibile all'indirizzo **http://localhost:8000**
La documentazione generata automaticamente si trova all'indirizzo **http://localhost:8000/docs**

### 3. Avvia il frontend (da un altro terminale)

```bash
cd frontend
npm install                  # Installa dipendenze Node
npm run dev                  # Avvia server Vite
```

Potrai accedere all'app all'indirizzo  **http://localhost:5173**
