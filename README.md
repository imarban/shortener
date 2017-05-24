# shortener
Basic URL Shortener

This project is a very basic URL shortening service. It is able to handle up to 2,000,000 of short urls.

### Technology stack
- Python 3.6
- Django 1.11
- PostgreSQL for DB in prod environment
- SQLite for DB in dev environment
- Vue.JS 2.3.0

### How to run
1. Clone the project
2. Apply migrations with `python manage.py migrate`
3. Run application with `python manage.py runserver`
4. Open your browser at http://localhost:8000

### Run tests
1. Run `python manage.py test`

### How to create a short url
1. Type URL you want to short
2. Type a custom value (optional)
3. Click on shorten button
4. System will assign either a generated or custom short url
5. Copy generated url by clicking on Copy button

### How to visit a generated url
1. Just type at address bar the generated url

### List all saved urls
1. Navigate to /all to see a list of all the saved urls

