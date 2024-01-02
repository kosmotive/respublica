# respublica

The backend is a Django application, the frontend is written in pure HTML/JavaScript with JQuery.

Both can be served separately. To prevent corss-origin issues during development, the static frontend files will also be served by Django when running the backend:

```bash
cd backend
python manage.py runserver
```

See `backend/README.md` for details on handling the backend.
