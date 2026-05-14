# EMSIBlogSpot

A Django blogging platform where users can publish articles, discover content, and interact through comments.

## Requirements

- Python 3.x
- Django 5.0.2
- MySQL database
- MySQL client libraries (mysqlclient)

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd EMSIBlogSpot
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install django==5.0.2 mysqlclient
   ```

5. Set up MySQL database:
   - Install and start MySQL server
   - Create a database named 'Blog'
   - Ensure the root user has access (or update settings accordingly)

6. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the required values (DJANGO_SECRET_KEY, DB_PASSWORD, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
   - DB_PASSWORD should match your MySQL root password

7. Run database migrations:
   ```
   python manage.py migrate
   ```

8. Start the development server:
   ```
   python manage.py runserver
   ```

The application will be available at http://127.0.0.1:8000/
