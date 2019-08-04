from os import environ

MONGO_URI = environ.get("MONGO_URI")
USER_COLLECTION = ("users", "accounts")

SECRET_KEY = environ.get("SECRET_KEY")

EMAIL_USER = environ.get("EMAIL_USER")
EMAIL_PASSWORD = environ.get("EMAIL_PASSWORD")