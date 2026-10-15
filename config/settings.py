import os
import dj_database_url
from pathlib import Path
from urllib.parse import urlparse
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-this-key-before-production")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "flora-erp-omega.vercel.app",
]
INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "apps.core","apps.accounts","apps.catalog","apps.customers","apps.inventory",
    "apps.sales","apps.deliveries","apps.reports",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":[
"django.template.context_processors.request","django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=0,
        ssl_require=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
{"NAME":"django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},
{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},
{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE="pt-br"
TIME_ZONE="America/Sao_Paulo"
USE_I18N=True
USE_TZ=True
STATIC_URL="static/"
STATICFILES_DIRS=[BASE_DIR/"static"]
STATIC_ROOT=BASE_DIR/"staticfiles"
MEDIA_URL="media/"
MEDIA_ROOT=BASE_DIR/"media"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
LOGIN_URL="login"
LOGIN_REDIRECT_URL="dashboard"
LOGOUT_REDIRECT_URL="login"
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=False
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS="DENY"
if not DEBUG:
    SECURE_SSL_REDIRECT=True
    SESSION_COOKIE_SECURE=True
    CSRF_COOKIE_SECURE=True
