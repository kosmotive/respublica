# Backend management

Remember to activate the virtual environment, except for the *Prerequisites* section:
```bash
source venv/bin/activate
```

## Prerequisites

**This is required only once for inital setup.**

Create virtual environment:
```bash
python -m venv venv
```

Activate virtual environment:
```bash
source venv/bin/activate
```

Install dependencies into virtual environment:
```bash
pip install requirements.txt
```

## Reset the database

**This is only required when migrations cannot be performed.**

Reset database migrations:
```bash
rm db.sqlite3
rm -rf */migrations
```

## Initialize the database

**This is only required after initial setup or after resetting the database.**

Create migrations:

```bash
python manage.py makemigrations processes world game
```

Create database:

```bash
python manage.py migrate
```

## Day-to-day use

Run tests:

```bash
python manage.py test
```

Generate random world:
```bash
python manage.py shell -c "from world.generator import *; generate_world(10, 0.5, 0, exist_ok=True, tickrate=60)"
```
Use `generate_test_world` instead of `generate_world` to populate the world with some test data.
Tickrate is given in ticks per hour.
