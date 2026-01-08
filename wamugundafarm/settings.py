from pathlib import Path
import os
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.templatetags.static import static

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = ['*']


# ==================== APPLICATION DEFINITION ====================
INSTALLED_APPS = [
    # --- UNFOLD (Must be BEFORE django.contrib.admin) ---
    "unfold",
    "unfold.contrib.filters",  # Optional: Adds nice sidebar filters
    "unfold.contrib.forms",    # Optional: Adds Tailwind forms
    "unfold.contrib.import_export", # Optional: If you use import/export
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'core',
    'shop',
    'cart',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'wamugundafarm.urls'

# ==================== TEMPLATES ====================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart',
            ],
        },
    },
]

# ==================== STATIC & MEDIA FILES ====================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================== CART SESSION ID ====================
CART_SESSION_ID = 'cart'

# ==================== WSGI ====================
WSGI_APPLICATION = 'wamugundafarm.wsgi.application'

# ==================== DATABASE ====================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==================== PASSWORD VALIDATION ====================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==================== INTERNATIONALIZATION ====================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Messages tags
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success',
    messages.ERROR: 'alert-danger',
    messages.WARNING: 'alert-warning',
    messages.INFO: 'alert-info',
}

# ==================== EMAIL SETTINGS ====================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.wamugundafarm.co.ke'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Wamugunda Farm <{EMAIL_HOST_USER}>'

# ==================== UNFOLD THEME SETTINGS ====================
UNFOLD = {
    "SITE_TITLE": "Wamugunda Farm Admin",
    "SITE_HEADER": "Wamugunda Farm",
    "SITE_URL": "/",
    "SITE_ICON": lambda request: static("assets/img/logo2.png"),
    # "SITE_SYMBOL": "agriculture",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,

    # 🟢 Custom Brown/Earth Color Palette
    "COLORS": {
        "primary": {
            "50": "251 246 243",
            "100": "245 235 229",
            "200": "234 213 202",
            "300": "222 191 176",
            "400": "207 160 141",
            "500": "160 82 45",    # Main Brand Brown
            "600": "133 66 35",
            "700": "104 50 26",
            "800": "77 36 18",
            "900": "53 24 12",
            "950": "31 12 5",
        },
    },

    # 🟢 Custom Sidebar Navigation
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False, # Set to False to strictly follow this layout
        "navigation": [
            {
                "title": "Store Management",
                "separator": True,
                "items": [
                    {
                        "title": "Products",
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:shop_product_changelist"),
                    },
                    {
                        "title": "Orders",
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:cart_order_changelist"),
                    },
                    {
                        "title": "Recipes",
                        "icon": "restaurant_menu",
                        "link": reverse_lazy("admin:shop_recipe_changelist"),
                    },
                    {
                        "title": "Categories",
                        "icon": "category",
                        "link": reverse_lazy("admin:shop_category_changelist"),
                    },
                    {
                        "title": "Reviews",
                        "icon": "star",
                        "link": reverse_lazy("admin:shop_review_changelist"),
                    },
                ],
            },
            {
                "title": "Website Content",
                "separator": True,
                "items": [
                    {
                        "title": "Testimonials",
                        "icon": "thumbs_up_down",
                        "link": reverse_lazy("admin:core_testimonial_changelist"),
                    },
                    {
                        "title": "Gallery",
                        "icon": "collections",
                        "link": reverse_lazy("admin:core_galleryitem_changelist"),
                    },
                    {
                        "title": "Gallery Categories",
                        "icon": "perm_media",  # <--- FIXED ICON
                        "link": reverse_lazy("admin:core_gallerycategory_changelist"),
                    },
                ],
            },
            {
                "title": "User Management",
                "separator": True,
                "items": [
                    {
                        "title": "Groups",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": "Users",
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
}