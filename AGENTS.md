# Repository Guidelines
 
## Project Structure & Module Organization
- `backend/`: FastAPI app (`app/{api,core,models,schemas,services,utils}`), entry `backend/main.py`, Alembic config, `requirements.txt`.
- `frontend/`: React + TypeScript app (`src/{components,pages,services,types,hooks}`), CRA scripts.
- `database/`: SQL init scripts; `sample_scans/`: example Nmap XML; `scripts/`: `setup.sh` for local Docker.
- Top-level `docker-compose.yml` runs backend, frontend, Postgres, Redis.
 
## Build, Test, and Development Commands
- Docker (recommended): `docker-compose up -d --build` — builds and starts all services.
- Backend dev: `pip install -r backend/requirements.txt && python backend/main.py` — run API locally on 8000.
- Frontend dev: `npm install --prefix frontend && npm start --prefix frontend` — run UI on 3000 (proxies to 8000).
- Migrations: `python backend/create_migration.py` — generate/apply DB changes during dev.
- Logs: `docker-compose logs -f backend frontend` — tail service logs.
 
## Coding Style & Naming Conventions
- Python: PEP8, 4-space indent, type hints preferred. Modules and functions `snake_case`, classes `PascalCase`. FastAPI routers live in `app/api`, Pydantic models in `app/schemas`, business logic in `app/services`.
- TypeScript/React: function components, `PascalCase` component files in `src/components`, pages in `src/pages`, hooks `useX` in `src/hooks`; variables `camelCase`. CRA ESLint defaults apply.
- Filenames: backend modules `snake_case.py`; frontend components `ComponentName.tsx`.
 
## Testing Guidelines
- Backend: `pytest` (async with `pytest-asyncio`). Place tests under `backend/tests/` as `test_*.py`. Example: `pytest -q`.
- Frontend: CRA tests via `npm test --prefix frontend`. Name files `*.test.tsx` near components or under `src/__tests__/`.
- Aim for meaningful coverage (≈70%+); include edge cases for parsing, API contracts, and UI state.
 
## Commit & Pull Request Guidelines
- Commit messages: adopt Conventional Commits for clarity (e.g., `feat(api): add scan upload`, `fix(ui): handle empty dataset`, `docs: update quick start`).
- PRs must include: concise description, linked issues, screenshots for UI changes, testing notes (commands + results), and any migration steps. Ensure `docker-compose up -d --build` succeeds and `README.md` stays accurate.
 
## Security & Configuration Tips
- Copy envs: `cp backend/.env.example backend/.env`; never commit secrets. Set `GEMINI_API_KEY`, DB, Redis, and `SECRET_KEY`.
- Use `sample_scans/` for safe demos. Validate uploads; avoid sensitive data in test artifacts.
