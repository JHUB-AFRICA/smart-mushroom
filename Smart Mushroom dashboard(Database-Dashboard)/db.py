"""
db.py — MySQL connection for the Streamlit dashboard.
Put this file in the same folder as Home.py, data.py, and the Pages/ folder.

Requires: pip install mysql-connector-python

Set these before running the dashboard (same values used in ingest_api.py):
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
"""

import os
import mysql.connector

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "YOUR-USERNAME-HERE"),
    "password": os.environ.get("MYSQL_PASSWORD", "YOUR-PASSWORD-HERE"),
    "database": "mushroom_farm",
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
