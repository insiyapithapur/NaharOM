# Secondary Trading Backend

This is the backend part of Secondary Trading project. This part mainly contains the Database, django apps.

## Technology Used-

1. Backend
   a.Python/Django
   b.PostgreSQL Database from supabase.com

## Important Points

1. This project is under development.

## Setup

Initial requirements
a. Python
b. PostgreSQL

1. Clone the repository

```bash
git clone https://github.com/Nahar-OM/secondary-trading-backend.git
```

2. Set up a virtual environment:

To create a virtualenv on windows

```bash
python -m venv env
```
To create a virtualenv on UNIX (macOS/Linux)

```bash
python3 -m venv env
```

3. Activate virtual environment:

On windows

```bash
env\Scripts\activate
```

On UNIX (macOS/Linux)

```bash
source env/bin/activate
```

5. Install the required packages:

```bash
pip install -r requirements.txt

```

5. Before moving forward now setup database

In the .env file there is a live database already hooked up which you can use and requires no setup.
However, if you wanna create on own, you are welcome.
Head to,
```bash
SecondaryTradingPlatform -> .env
```
and update
```bash
DATABASE_URL =
```
with your URI.

DATABASE

6. Make django migrations:

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

7. Create a super user (if needed) or use provided super-users

```bash
python manage.py createsuperuser
```

8. Run the Django application:

```bash
python manage.py runserver
```

## Pages and links

```bash
http://127.0.0.1:8000/admin/
```



