# hrh_invoicing
Run following commands

    brew install pango

    While making venv need to enable system site packages in pyenv.cfg or before

    source venv/bin/activate

    python manage.py makemigrations   

    python manage.py migrate_schemas --shared

    python manage.py crontab add

MUST HAVE ENV VARIABLES
   
  # Email Configuration
  EMAIL_USE_TLS=True
  EMAIL_HOST
  EMAIL_PORT
  EMAIL_HOST_USER
  EMAIL_HOST_PASSWORD
  DEFAULT_FROM_EMAIL // Normally it is EMAIL_HOST_USER
  
  # Database Configuration
  DB_NAME
  DB_USER
  DB_PASSWORD
  DB_HOST
  DB_PORT
  
  # Django Secret Key
  SECRET_KEY
