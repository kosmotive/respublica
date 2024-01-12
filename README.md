<div align="center">
  <h1><a href="https://github.com/kostrykin/respublica">respublica</a><br>
  <a href="https://github.com/kostrykin/respublica/actions/workflows/backend-tests.yml"><img src="https://github.com/kostrykin/respublica/actions/workflows/backend-tests.yml/badge.svg"></a>
  <a href="https://github.com/kostrykin/respublica/actions/workflows/backend-tests.yml"><img src="https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/kostrykin/dad747c31377ea39fcd54bcd7d1702e2/raw/respublica.json" /></a>
  </h1>
</div>

The backend is a Django application, the frontend is written in pure HTML/JavaScript with JQuery.

Both can be served separately. To prevent corss-origin issues during development, the static frontend files will also be served by Django when running the backend:

```bash
cd backend
python manage.py runserver
```

See `backend/README.md` for details on backend management.
