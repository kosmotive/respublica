# Backend

Reset database migrations:
```
rm db.sqlite3
rm -rf */migrations
```

Create migrations:

```bash
python manage.py makemigrations processes world game
```

Create database:

```bash
python manage.py migrate
```

Run tests:

```bash
python manage.py test
```

Generate random world:
```bash
python manage.py shell -c "from world.generator import *; generate_world(10, 0.5, 0, exist_ok=True, tickrate=60)"
```
Use `generate_test_world` instead of `generate_world` to populate the world with some test data.
