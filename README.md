# Umoja Academic & Scientific Editing — Platform

Backend for Umoja Educational Tuition Centre's academic and scientific
editing service. Built in phases; this repo currently contains
**Phase 1 (accounts/roles), Phase 2 (client/editor profiles,
organizations), and Phase 3 (public website) — all DONE.**

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
python manage.py test accounts profiles organizations website
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
├── profiles/                     Phase 2 — DONE
│   ├── models.py                ClientProfile, EditorProfile (1:1 with User)
│   ├── forms.py                 Self-service edit forms — no `user` field
│   ├── admin.py
│   ├── views.py                 edit_client_profile / edit_editor_profile
│   ├── urls.py
│   ├── migrations/
│   └── tests/
│       ├── test_models.py
│       ├── test_forms.py
│       └── test_views.py
│
├── organizations/                 Phase 2 — DONE
│   ├── models.py                Organization, OrganizationMembership
│   ├── admin.py                 membership.role gated like accounts.change_user_role
│   ├── migrations/
│   └── tests/
│       ├── test_models.py
│       └── test_admin.py
│
├── website/                       Phase 3 — DONE
│   ├── models.py                 Service, SubjectArea (admin-editable, spec 8/9)
│   ├── forms.py                  QuoteInquiryForm — plain Form, nothing persisted
│   ├── admin.py
│   ├── views.py                  Thin views; services_list does the category filter
│   ├── urls.py                   Home, About, Services, legal pages, etc.
│   ├── migrations/
│   └── tests/
│       ├── test_models.py
│       └── test_views.py
│
├── assignments/                  ← later (Phase 4) — Assignment, Quote
├── documents/                    ← later (Phase 5) — AssignmentFile, private storage, versioning
├── payments/                     ← later (Phase 10) — PaymentProvider, PaymentTransaction, Pesapal
├── messaging/                    ← later (Phase 12) — assignment-scoped messages
│
├── templates/
│   ├── base.html                 HTMX wired in here; every page template extends this
│   ├── accounts/
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── dashboard_placeholder.html
│   ├── profiles/
│   │   ├── edit_client_profile.html
│   │   └── edit_editor_profile.html
│   └── website/
│       ├── home.html, about.html, how_it_works.html
│       ├── for_researchers.html, for_universities.html, for_students.html
│       ├── services_list.html, subject_areas_list.html
│       ├── pricing.html, request_a_quote.html, faq.html, contact.html
│       └── legal/
│           ├── privacy_policy.html, terms_of_service.html
│           └── confidentiality_policy.html, refund_cancellation_policy.html
│
├── static/
│   └── css/style.css             Shared stylesheet — nav, forms, messages
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

## Profiles & organizations (Phase 2)

`ClientProfile` and `EditorProfile` are 1:1 with `User`, created on
first visit to `/profiles/client/` or `/profiles/editor/` (whichever
matches the user's role — the other returns 403). Self-service forms
never expose `user`; `EditorProfile.is_active` is deliberately left
out of the self-service form too, since it controls whether an editor
is excluded from assignment matching entirely (an admin call, not a
self-service toggle) — `availability_status` IS self-service, since
that's day-to-day editor-managed per spec section 25.

`EditorProfile.internal_rate` was deliberately deferred to Phase 9,
once the pricing/service model exists to give it real scope (editor
default vs service-specific vs org-specific vs historical-on-assignment).

`Organization` / `OrganizationMembership` model institutional clients.
`OrganizationMembership.role` (`MEMBER` / `ORG_ADMIN`) is intentionally
separate from the platform-wide `User.role` — a platform `CLIENT` can
be an `ORG_ADMIN` within their organization without any change to
their platform permissions. Membership role changes are gated behind
`organizations.change_membership_role`, the same pattern as
`accounts.change_user_role`. No self-service organization views exist
yet — membership is admin-managed via `/admin/` for now.

Editor profile photos need `MEDIA_URL`/`MEDIA_ROOT` (already set in
`development.py`) and `Pillow` (in `requirements.txt`).

## Public website (Phase 3)

`Service` and `SubjectArea` are admin-editable content models (spec
sections 8/9/32) — new services or subject areas don't need a code
deploy. "Academic Editing" and "Scientific Editing" are not separate
pages: `/services/` filters one listing by `Service.category` via
`?category=academic` / `?category=scientific`, so there's one template
and one source of truth rather than duplicated markup.

`/request-a-quote/` is a lightweight public inquiry form
(`QuoteInquiryForm`, a plain `Form`, not a `ModelForm`). Submitting it
only sends an email to `SUPPORT_EMAIL` — it deliberately does **not**
create an `Assignment` or `Quote` record, since those models don't
exist until Phase 4. The real flow (inquiry → assignment → documents →
quote → payment) replaces this in later phases; for now it's
`Inquiry → Email notification` only.

Legal pages (privacy, terms, confidentiality, refund/cancellation) are
plain templates with real starter content — written to avoid
overclaiming (no "100% secure", no claimed university partnerships,
per spec section 5/35) but they are placeholder text a business would
still want reviewed by a lawyer before relying on them, not a
substitute for that review.

No FAQ/testimonial/homepage-content CMS yet — those stay as plain
templates until there's a demonstrated operational need for admins to
edit that copy without a deploy.

## Tests

51 tests total: Phase 1's 18, Phase 2's 19, and Phase 3 adds 14 more —
`Service`/`SubjectArea` slug generation and ordering, the
`/services/` category filter (including an invalid category falling
back to "all active"), a smoke test that every static page returns
200, and the quote inquiry form: a valid submission sends exactly one
email and an invalid one sends none.

## What's not built yet

`assignments`, `documents`, `payments`, `messaging` apps; self-service
organization views (membership is admin-managed via `/admin/` for
now); real object storage (production.py is wired for S3-compatible
storage but untested until Phase 5); DRF API layer; Celery workers;
FAQ/testimonial CMS.