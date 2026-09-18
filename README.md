# Umoja Academic & Scientific Editing — Platform

Backend for Umoja Educational Tuition Centre's academic and scientific
editing service. Built in phases; this repo currently contains
**Phase 1: project architecture, custom User model, role system.**

## Local development setup

You'll need, installed on your machine:

- **Python 3.12+**
- **PostgreSQL 15+** running locally (or a connection string to one)
- **Redis** (used from a later phase onward, but installing it now
  saves a step later — `redis-server` on most package managers)
- **git**

Steps:

```bash
git clone <your-repo-url> umoja
cd umoja

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env: set SECRET_KEY to a long random string, and DATABASE_URL
# to point at your local Postgres, e.g.
# DATABASE_URL=postgres://umoja:umoja@localhost:5432/umoja

# Create the database and role in Postgres first, e.g.:
#   createuser -P umoja
#   createdb -O umoja umoja

python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/login/` to sign in, or
`http://127.0.0.1:8000/admin/` for the Django admin.

Run the tests with:

```bash
python manage.py test accounts
```

## Full intended project structure

This is where the project is headed across all 18 phases (see the
spec's phase order). Apps marked `← later` don't exist yet — they're
listed so the layout makes sense as it grows, and so you can see
where new code will land before it's written.

```
umoja/
├── config/                      Django settings, root URLs, WSGI/ASGI
│   ├── settings/
│   │   ├── base.py              Shared settings — no secrets, no env-specific values
│   │   ├── development.py       Local dev overrides
│   │   └── production.py        Production overrides — HTTPS, HSTS, S3 storage
│   ├── context_processors.py    Injects business name/brand into every template
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                    Phase 1 — DONE
│   ├── models.py                Custom User: email login, role field
│   ├── managers.py              UserManager — enforces safe role defaults
│   ├── admin.py                 Role field locked behind a dedicated permission
│   ├── forms.py                 Signup/profile forms with no role field
│   ├── views.py                 Login, signup, role-based dashboard redirect
│   ├── urls.py
│   ├── management/commands/setup_groups.py
│   ├── migrations/
│   └── tests/
│       ├── test_models.py
│       ├── test_forms.py
│       └── test_views.py
│
├── organizations/                ← later (Phase 2/14) — Organization, OrganizationMembership
├── website/                      ← later (Phase 3) — public marketing pages
├── assignments/                  ← later (Phase 4) — Assignment, Service, SubjectArea, Quote
├── documents/                    ← later (Phase 5) — AssignmentFile, private storage, versioning
├── payments/                     ← later (Phase 10) — PaymentProvider, PaymentTransaction, Pesapal
├── messaging/                    ← later (Phase 12) — assignment-scoped messages
│
├── templates/
│   ├── base.html                 HTMX wired in here; every page template extends this
│   └── accounts/
│       ├── login.html
│       ├── signup.html
│       └── dashboard_placeholder.html
│
├── static/                       CSS/JS/images (empty for now)
├── manage.py
├── requirements.txt
├── .env.example                  Copy to .env — never commit the real .env
├── .gitignore
└── README.md
```

## Role model (Phase 1)

Five roles: `CLIENT`, `EDITOR`, `SENIOR_EDITOR`, `ADMIN`, `SUPER_ADMIN`.
Stored as a plain field on `User` for cheap checks
(`request.user.role`, `request.user.is_editor`), backed by Django's
Group/Permission system for anything that needs to be independently
grantable. `is_superuser` remains Django's own override and is
separate from the `SUPER_ADMIN` role label.

Only staff with the `accounts.change_user_role` permission can edit a
user's role in the admin. No self-service form exposes the field.
Run `python manage.py setup_groups` after migrating to create the
`Editors`, `Senior Editors`, and `Administrators` groups referenced by
later phases.

## Tests

18 tests cover: role defaults, email normalization/uniqueness,
superuser creation, self-service forms excluding role/permission
fields, the login/signup/dashboard-redirect flow, and — directly —
that a staff user without `change_user_role` cannot edit role via
the admin while one with it can.

## What's not built yet

Public website, `organizations`, `assignments`, `documents`,
`payments`, `messaging` apps; real object storage (production.py is
wired for S3-compatible storage but untested until Phase 5); DRF API
layer; Celery workers.
