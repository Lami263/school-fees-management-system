# School Fees & Payment Management System

**HSE412: Software Testing and Quality Assurance — Individual Practical Project**
University of Zimbabwe | Lecturer: Dr. Fine Masimba (PhD)

A full-stack fee management system built to demonstrate systematic
software testing and QA practice, not just working software. Backend:
Python (Flask). Frontend: React. See `docs/architecture.md` for the
full system design and database schema.

## Core business rule

```
Balance = Net Fees − Total Confirmed Payments
Net Fees = Total Fees − Total Discounts   (floored at 0)
```

All financial edge cases (full payment, partial payment, zero payment,
overpayment, negative payment, duplicate transaction, invalid student,
unauthorized edit) are implemented as explicit validation branches in
`backend/app/services/payment_service.py` and exercised by the
automated test suite in `backend/tests/`.

## Project structure

```
school-fees-system/
├── backend/                  Flask REST API
│   ├── app/
│   │   ├── models.py         SQLAlchemy models (see docs/architecture.md for ERD)
│   │   ├── services/         Business logic — the white-box testing target
│   │   │   ├── fee_service.py
│   │   │   └── payment_service.py
│   │   └── routes/           API endpoints (blueprints), one per module
│   ├── tests/                pytest suite: BVA / EP / decision-table cases
│   ├── seed.py                Demo data loader
│   └── requirements.txt
├── frontend/                 React (Vite) single-page app
│   └── src/
│       ├── pages/             One page per module
│       ├── components/
│       └── context/           Auth state
└── docs/
    └── architecture.md        Architecture, ERD, schema, business rules
```

## Modules implemented

| Module | Backend routes | Frontend page |
|---|---|---|
| Authentication (JWT, role-based) | `/api/auth/*` | `Login.jsx` |
| Student registration (CRUD) | `/api/students` | `Students.jsx` |
| Classes & Terms | `/api/classes`, `/api/terms` | (used across pages) |
| Fee structure | `/api/fee-structures` | `FeeStructures.jsx` |
| Discounts | `/api/discounts` | `Discounts.jsx` |
| Payment recording + validation | `/api/payments` | `Payments.jsx` |
| Balances / outstanding fees | `/api/reports/outstanding` | `OutstandingFees.jsx` |
| Receipts | `/api/receipts/<payment_id>` | (linked from Payments) |
| Search | `/api/search/students` | `Search.jsx` |
| Reports (statement, collections) | `/api/reports/*` | `Reports.jsx`, `Dashboard.jsx` |
| Audit log (admin only) | `/api/audit` | `AuditLog.jsx` |

## Getting started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
python seed.py                  # creates demo admin/bursar users + sample data
python run.py                   # runs on http://localhost:5000
```

Demo logins created by `seed.py`:
- `admin` / `Admin@123`
- `bursar` / `Bursar@123`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev                     # runs on http://localhost:5173
```

The Vite dev server proxies `/api` to `http://localhost:5000`, so run
the backend first.

## Running the automated test suite

```bash
cd backend
pytest
```

`tests/test_payment_service.py` implements the following test cases
directly (see file header comments for the mapping):

| ID | Case | Technique |
|---|---|---|
| TC01 | Full payment | Equivalence Partitioning |
| TC02 | Partial payment | Equivalence Partitioning |
| TC03 | Zero payment | Boundary Value Analysis |
| TC04 | Overpayment | Boundary Value Analysis |
| TC05 | Negative payment | Boundary Value Analysis |
| TC06 | Duplicate transaction | Equivalence Partitioning |
| TC07 | Invalid student | Equivalence Partitioning |
| TC08 | Unauthorized transaction editing | Decision Table (role × action) |

`tests/test_fee_service.py` covers the discount-exceeds-fees boundary
(net fees floored at 0) and the invalid-student/invalid-term paths.

`pytest.ini` is configured to run with `--cov=app`, so `pytest` alone
prints a statement coverage report — use this as evidence in your QA
documentation (Statement Coverage / Branch Coverage).

## Suggested next QA deliverables

This scaffold gives you working software with testable business logic
already wired up. Still to produce for the assignment:
1. **Test Plan** document (IEEE 829 style)
2. **Test case tables** (BVA / EP / Decision Table) written up formally, cross-referenced to the pytest file above
3. **UI/integration test automation** — e.g. Playwright or Selenium scripts against the React frontend
4. **Performance test** — e.g. Locust script hitting `/api/payments`
5. **Security test notes** — SQL injection attempts on `/api/search/students`, JWT tampering, role-bypass attempts on admin-only routes
6. **Defect log** — track bugs found during your own testing with severity/status
7. **Quality model mapping** — tie features to ISO/IEC 25010 characteristics (e.g. audit log → Integrity; input validation → Reliability)

## License

Educational project for HSE412 coursework.
