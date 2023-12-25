# Backend

Reset migrations:
```
rm -rf */migrations
```

Create migrations:

```bash
python manage.py makemigrations world
python manage.py makemigrations processes
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
python manage.py shell -c "from world.generator import generate_world; generate_world(10, 0.5, 0, exist_ok=True)"
```
