from .celery import app as celery_app
import pymysql

# This allows Django to use pymysql seamlessly without needing the C++ build tools for mysqlclient on Windows!
pymysql.install_as_MySQLdb()

__all__ = ('celery_app',)
