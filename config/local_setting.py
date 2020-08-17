SERVER_PORT = 5000
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Zx1993624!@localhost/stock_ai'
SQLALCHEMY_TRACK_MODIFICATION = False
SQLALCHEMY_ENCODING = "utf-8"
AUTH_COOKIE_NAME = 'stock_ai'
REDIS_URL = "redis://:@:6379/0"

## filter url
IGNORE_URLS = [
    "^/user/login",
    "^/user/register",
    "^/jobs",
    "^/update",
    '^/predict'
]

IGNORE_CHECK_LOGIN_URLS = [
    "^/static",
    "^/.favicon.ico"
]

PAGE_SIZE=50
PAGE_DISPLAY=10