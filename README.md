# Django LMS Project

A Learning Management System (LMS) built with Django and Django REST Framework.

## Features

- Course management
- User enrollment system
- Lesson tracking with progress
- RESTful API
- User authentication with django-allauth
- Swagger API documentation

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker and Docker Compose (optional)

### Setup with Docker

1. Clone the repository
2. Create a `.env` file:
   - Copy `.env.example` to `.env`
   - Update the values with your local configuration
3. Run with Docker Compose:
   ```bash
   docker compose up -d
   ```
4. Run migrations:
   ```bash
   docker compose exec web python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
6. Access the application at `http://localhost:8500`

### Setup without Docker

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` file with your local configuration

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment to Railway

### Prerequisites

- Railway account
- GitHub repository

### Important Notes

- **Dockerfile vs Dockerfile.railway**: 
  - `Dockerfile` is for local development (used by docker-compose)
  - `Dockerfile.railway` is for Railway deployment (includes tests and production optimizations)
  - Railway is configured to use `Dockerfile.railway` automatically via `railway.json`

- **Tests Before Deploy**: 
  - `Dockerfile.railway` runs pytest before building the image
  - If tests fail, the build is aborted and deployment is prevented
  - Tests use SQLite in-memory database (no external DB connection needed)

### Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Connect to Railway**
   - Go to [Railway](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add PostgreSQL Service**
   - In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

4. **Add Volume for Static and Media Files**
   - In Railway dashboard, click "New" → "Volume"
   - Name it (e.g., `staticfiles-volume`)
   - Mount it to your web service at path: `/staticfiles`
   - This volume will store both static files and media uploads

5. **Configure Environment Variables**
   In Railway dashboard, add these environment variables (see `.env.example` for reference):
   - `SECRET_KEY`: Django secret key (generate a new one for production)
   - `DEBUG`: Set to `False` for production
   - `ALLOWED_HOSTS`: Your Railway domain (e.g., `yourapp.railway.app`)
   - `VOLUME_PATH`: Set to `/staticfiles` (path where volume is mounted)
   - `DATABASE_URL`: Automatically provided by Railway PostgreSQL service (no need to set manually)
   - `PORT`: Automatically set by Railway (no need to set manually)
   
   **Note**: See `.env.example` file for detailed descriptions of all Railway environment variables.

6. **Deploy**
   - Railway will automatically detect `Dockerfile.railway` and deploy
   - Tests will run during build - if they fail, deployment is blocked
   - On startup, the app will:
     - Create necessary directories in the volume
     - Run `makemigrations` and `migrate`
     - Collect static files to the volume
     - Start Gunicorn server
   - The app will be available at your Railway domain

See `RAILWAY_VOLUME_SETUP.md` for detailed volume setup instructions.

### Generate Secret Key

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Management Commands

### Create Sample Courses
```bash
python manage.py create_sample_courses
```

### Create Sample Lessons
```bash
python manage.py create_sample_lessons
```

## Project Structure

```
djangop1/
├── lms/              # Main application
│   ├── models.py     # Database models
│   ├── views.py      # View functions and ViewSets
│   ├── urls.py       # URL routing
│   └── templates/    # HTML templates
├── project/          # Django project settings
│   ├── settings.py   # Django settings
│   └── urls.py       # Root URL configuration
├── Dockerfile        # Production Docker configuration
├── docker-compose.yaml  # Local development Docker setup
└── requirements.txt  # Python dependencies
```

## API Documentation

Once deployed, access the API documentation at:
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`


