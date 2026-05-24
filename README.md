# Carbon Footprint Calculator



[![CI](https://github.com/ImpiusVenatus/carbon-footprint-calculator/actions/workflows/ci.yml/badge.svg)](https://github.com/ImpiusVenatus/carbon-footprint-calculator/actions/workflows/ci.yml)



A full-stack web app for organizations to record activity data (energy, travel, fuel, etc.), convert it into CO₂e emissions, and view results on an analytical dashboard with reduction targets and exportable reports.



**Live demo:** Deploy using the instructions below, then set `NEXT_PUBLIC_DEMO_URL` in this README.  

Suggested stack: frontend on [Vercel](https://vercel.com), API on [Render](https://render.com), database on [Neon](https://neon.tech).



---



## For reviewers



What to look at in ~30 seconds:



- **Tested calculation engine** — pure Python logic with unit tests (`backend/tests/test_calculator.py`) plus API integration tests (`backend/tests/test_api_integration.py`).

- **Audit-grade traceability** — every mutation writes to `audit_log`; admins can view it under **Audit log** in the sidebar.

- **Factor snapshotting** — each emission stores the factor value used at calculation time, so historical totals stay reproducible.

- **Multi-tenant RBAC** — JWT auth with admin / contributor / viewer roles; sidebar shows your role.

- **Full CRUD + dashboard** — create, edit, delete activities; overview charts with year-over-year delta.



**Quick walkthrough:** Log in with the [demo account](#try-the-demo) → open **Overview** (2026) → **Activities** (edit an entry) → **Audit log** (admin only) → **Reports** (CSV export).



---



## Try the demo



Seed a pre-populated organization (6 activities across scopes, one reduction target, 2025 + 2026 data for YoY):



```bash

cd backend

source .venv/Scripts/activate      # Windows Git Bash

alembic upgrade head

python -m app.seed.loader          # reference emission factors

python -m app.seed.demo            # demo org + activities

```



| Field | Value |

|-------|-------|

| Email | `demo@carbonfootprint.app` |

| Password | `Demo12345!` |



Then run the frontend and sign in at `/login`. The **Overview** dashboard for 2026 shows scope split, monthly trend, target progress, and year-over-year change vs 2025.



---



## What it does



1. **Register** an organization and admin account (or use the demo seed).

2. **Pick emission factors** from a seeded reference library (electricity, gas, diesel, travel, etc.).

3. **Log activities** — e.g. 1,000 kWh of electricity for January.

4. **Get automatic calculations** — `emissions = quantity × emission factor`.

5. **View the dashboard** — totals, scope split, monthly trends, categories, target progress, YoY delta.

6. **Import CSV** or **export reports** for audit and reporting.



Each calculated emission stores a **snapshot of the factor value used**, so historical results stay correct even if factors are updated later.



---



## Architecture



```

┌─────────────────────┐         ┌──────────────────────┐

│   Next.js Frontend  │  REST   │   FastAPI Backend    │

│   (React + TS)      │ ◄─────► │   (Python)           │

│                     │  JSON   │                      │

│  • Dashboard/charts │         │  • JWT auth          │

│  • Forms + dropdowns│         │  • Calculator engine │

│  • CSV import UI    │         │  • SQL aggregations  │

└─────────────────────┘         └──────────┬───────────┘

                                           │

                                           ▼

                                ┌──────────────────────┐

                                │  PostgreSQL (Neon)   │

                                │  or SQLite (local)   │

                                └──────────────────────┘

```



The frontend is presentation only. All business logic, validation, and calculations live in the FastAPI backend.



---



## How the calculation works



For every activity entry:



```

CO₂e (kg) = quantity × factor_value

```



Example: 1,000 kWh × 0.207 kg CO₂e/kWh = **207 kg CO₂e**



The backend validates:



- Quantity must be greater than zero

- Activity unit must match the factor's unit (no silent conversion)

- The factor must exist and be active

- `period_end` must not precede `period_start`



Results are stored in an `emissions` table (not computed on the fly) for fast dashboard queries and audit reproducibility.



### Emission scopes



| Scope | Meaning | Examples |

|-------|---------|----------|

| **1** | Direct emissions you control | Company vehicles, on-site fuel, gas heating |

| **2** | Indirect from purchased energy | Grid electricity, district heating |

| **3** | Other indirect value-chain | Business travel, commuting, purchased goods |



---



## User roles



| Role | Can do |

|------|--------|

| **Admin** | Everything + custom factors, targets, audit log |

| **Contributor** | Create/edit/delete activities, CSV import, view dashboards |

| **Viewer** | Read-only access to dashboards, entries, and reports |



---



## Project structure



```

Carbon-Footprint-Calculator/

├── backend/

│   ├── app/

│   │   ├── main.py              # FastAPI app, CORS

│   │   ├── config.py            # Environment settings

│   │   ├── database.py          # SQLAlchemy engine

│   │   ├── models/              # ORM models (7 entities)

│   │   ├── schemas/             # Pydantic request/response types

│   │   ├── api/                 # Route handlers (incl. audit-log)

│   │   ├── services/

│   │   │   ├── calculator.py    # Pure calculation engine

│   │   │   ├── aggregator.py    # Dashboard SQL rollups + YoY

│   │   │   └── importer.py      # CSV parse + validate

│   │   ├── core/security.py     # JWT, bcrypt, audit log

│   │   └── seed/                # Factor seed + demo org script

│   ├── alembic/                 # Database migrations

│   └── tests/                   # Calculator + API integration tests

├── frontend/

│   ├── src/app/                 # Next.js App Router pages

│   ├── src/components/

│   │   ├── ui/dropdown.tsx      # Custom dropdown component

│   │   └── charts/              # Recharts wrappers

│   └── src/lib/                 # API client, auth helpers

├── .github/workflows/ci.yml     # pytest + frontend build

├── render.yaml                  # Render deploy blueprint

├── docker-compose.yml           # Optional local PostgreSQL

└── README.md

```



---



## Setup



### Prerequisites



- Python 3.11+

- Node.js 18+

- PostgreSQL via [Neon](https://neon.tech) (recommended) or SQLite for local dev



### 1. Backend



```bash

cd backend

python -m venv .venv

source .venv/Scripts/activate      # Windows Git Bash

pip install -r requirements.txt

cp .env.example .env

```



Edit `backend/.env`:



```env

DATABASE_URL=postgresql://user:pass@host/db?sslmode=require   # Neon URL

JWT_SECRET=your-long-random-secret

CORS_ORIGINS=http://localhost:3000,http://localhost:3001

```



Run migrations and seed data:



```bash

alembic upgrade head

python -m app.seed.loader

python -m app.seed.demo            # optional demo account

```



Start the API:



```bash

uvicorn app.main:app --reload --port 8000

```



### 2. Frontend



```bash

cd frontend

npm install

cp .env.local.example .env.local

npm run dev

```



Open the URL shown in the terminal (usually `http://localhost:3000`).



`frontend/.env.local`:



```env

NEXT_PUBLIC_API_URL=http://localhost:8000

```



---



## Deploy (live demo)



### Backend — Render



1. Push this repo to GitHub and connect it in [Render](https://render.com).

2. Use the included [`render.yaml`](render.yaml) blueprint, or create a **Web Service** with root directory `backend`.

3. Set environment variables:

   - `DATABASE_URL` — Neon connection string (`?sslmode=require`)

   - `JWT_SECRET` — long random string

   - `CORS_ORIGINS` — your Vercel frontend URL (e.g. `https://your-app.vercel.app`)

   - `CORS_ORIGIN_REGEX` — leave empty in production

4. Build command: `pip install -r requirements.txt && alembic upgrade head && python -m app.seed.loader && python -m app.seed.demo`

5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`



### Frontend — Vercel



1. Import the repo in [Vercel](https://vercel.com); set **Root Directory** to `frontend`.

2. Environment variable: `NEXT_PUBLIC_API_URL=https://your-render-service.onrender.com`

3. Deploy. Update `CORS_ORIGINS` on the backend with the Vercel URL.



After deploy, add your live URLs at the top of this README and share the demo credentials from [Try the demo](#try-the-demo).



---



## Using the app



### First-time setup



1. Go to **Register** and create an organization + admin account, **or** run `python -m app.seed.demo` and sign in with the demo credentials.

2. Open **Emission Factors** to confirm seed data loaded (13 reference factors).

3. Go to **Activities** → pick a factor, enter quantity and date range → **Save**. Use **Edit** on any row to update and recalculate.

4. Open **Overview** to see charts update for the selected year (including YoY vs prior year when data exists).



### CSV import



Upload a CSV with columns:



```

category,quantity,unit,period_start,period_end

electricity,1000,kWh,2026-01-01,2026-01-31

```



The app previews each row (valid/invalid), then commits valid rows on confirm. Download the template from the Activities page when empty.



### Reduction targets



Admins can set targets under **Targets** (e.g. 30% reduction by 2030 vs 2024 base year). Progress appears on the Overview dashboard.



### Audit log



Admins see **Audit log** in the sidebar — a paginated trace of creates, updates, deletes, imports, and exports.



### Reports



**Reports** → pick a year → **Download** exports all emissions for that year as CSV.



---



## API reference



Base URL: `http://localhost:8000/api/v1`



| Method | Path | Description |

|--------|------|-------------|

| POST | `/auth/register` | Create org + admin user |

| POST | `/auth/login` | Get JWT tokens |

| POST | `/auth/refresh` | Refresh access token |

| GET | `/auth/me` | Current user |

| GET | `/factors` | List emission factors |

| POST | `/factors` | Add custom factor (admin) |

| GET | `/activities` | List activity entries |

| POST | `/activities` | Create entry + calculate emission |

| PUT | `/activities/{id}` | Update + recalculate |

| DELETE | `/activities/{id}` | Delete entry + emission |

| POST | `/activities/import/preview` | CSV preview |

| POST | `/activities/import/confirm` | Commit import |

| GET | `/emissions/summary?year=2026` | Dashboard data (incl. YoY) |

| GET | `/targets` | List targets |

| POST | `/targets` | Create target (admin) |

| GET | `/audit-log` | Audit trail (admin) |

| GET | `/reports/export?year=2026&format=csv` | Export CSV |



All routes except auth require `Authorization: Bearer <access_token>`.



---



## Database entities



| Table | Purpose |

|-------|---------|

| `organizations` | Tenant (company) |

| `users` | Login accounts with roles |

| `emission_factors` | Reference conversion rates |

| `activity_entries` | Raw input data |

| `emissions` | Computed results (1:1 with entries) |

| `reduction_targets` | Reduction goals |

| `audit_log` | Append-only action history |



Every business record is scoped to an `organization_id` for multi-tenancy.



---



## Running tests



```bash

cd backend

pytest

```



Tests cover the calculation engine (unit) and the register → create activity → summary flow (integration). CI runs the same suite on every push.



---



## Tech stack



| Layer | Technology |

|-------|------------|

| Frontend | Next.js 16, React, TypeScript, Tailwind CSS, Recharts |

| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |

| Database | PostgreSQL (Neon) or SQLite |

| Auth | JWT (access + refresh), bcrypt passwords |

| CI | GitHub Actions (pytest + `npm run build`) |



---



## Troubleshooting



**CORS errors on register/login**  

The frontend and backend must use compatible origins. Include your frontend port in `CORS_ORIGINS` (e.g. `http://localhost:3001`) and restart the backend.



**Empty dashboard**  

Add activity entries for the year selected on Overview. Emissions are grouped by `period_start` year. Or run `python -m app.seed.demo`.



**Database connection fails**  

Verify `DATABASE_URL` in `backend/.env`. For Neon, ensure `?sslmode=require` is in the connection string.



**Seed factors missing**  

Run `python -m app.seed.loader` from the `backend/` directory with venv activated.



---



## Future enhancements



- PDF report export

- Multi-year benchmarking and intensity metrics (CO₂e per employee/revenue)

- Factor versioning UI

- User invite flow for contributors/viewers

- GRI/CSRD disclosure mapping


