from flask import Flask, jsonify
from flask_cors import CORS  # Import Flask-CORS
import mysql.connector
import pymysql
import os
import subprocess
import json
import csv
import time
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# -----------------------------
# 🔹 Configure Logging (Docker Captures Logs)
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -----------------------------
# 🔹 Database Configuration
# -----------------------------

# Database connection
db_config = {
    "host": os.getenv("DB_HOST", "mysql"),
    "user": os.getenv("DB_USER", "myuser"),
    "password": os.getenv("DB_PASSWORD", "mypassword"),
    "database": os.getenv("DB_NAME", "mydatabase"),
}

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = mysql.connector.connect(**db_config)
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            retries -= 1
            time.sleep(5)  # Wait before retrying
    raise Exception("Could not connect to the database after multiple attempts")


conn = get_db_connection()

# -----------------------------
# ✅ Ensure Database Table Exists
# -----------------------------
def create_table():
    """Creates a table for storing live market data if it does not already exist."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            price DECIMAL(18,8) NOT NULL,
            uniswap_liquidity DECIMAL(30,8),
            curve_liquidity DECIMAL(30,8),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    logger.info("✅ Database table `market_data` checked/created.")

create_table()  # Ensure table is created on startup

def import_csv_to_db():
    """Imports CSV data into MySQL."""
    cur = conn.cursor()

    with open("historical_data.csv", "r") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Extract headers

        for row in reader:
            date = row[0]
            for i in range(1, len(headers)):  # Skip the date column
                symbol = headers[i]
                price = float(row[i]) if row[i] else 0  # Handle empty values
                cur.execute("""
                    INSERT INTO market_data (symbol, price, timestamp)
                    VALUES (%s, %s, %s)
                """, (symbol, price, date))

    conn.commit()
    cur.close()
    logger.info("✅ CSV data successfully imported into MySQL.")

#import_csv_to_db()  # Import CSV data on startup

# -----------------------------
# 🔹 Flask API Endpoints
# -----------------------------

@app.route("/")
def read_root():
    return jsonify({"message": "Hello, World!"})

@app.route("/users")
def get_users():
    """Fetches users from the database."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users;")
        users = cur.fetchall()
        cur.close()
        logger.info("✅ Users fetched successfully from database.")
        return jsonify({"users": users})
    except Exception as e:
        logger.error(f"❌ Error fetching users: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/live-data")
def fetch_and_store_live_data():
    """
    Calls an external Python script (`fetch_live_data.py`) to get:
    - Live price
    - Liquidity from Uniswap & Curve
    - Timestamp
    Stores data in MySQL & returns it to the frontend.
    """
    try:
        # ✅ Call the external script
        result = subprocess.run(["python", "fetch_live_data.py"], capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ Error in fetch_live_data.py: {result.stderr}")
            raise Exception(f"Error in fetch_live_data.py: {result.stderr}")

        # ✅ Parse JSON output from script
        live_data = json.loads(result.stdout)

        # ✅ Store the fetched data in the database
        cur = conn.cursor()

        for symbol, data in live_data.items():
            price = data["price"]
            uniswap_liquidity = data.get("uniswap_liquidity", None)
            curve_liquidity = data.get("curve_liquidity", None)
            timestamp = data["timestamp"]

            cur.execute("""
                INSERT INTO market_data (symbol, price, uniswap_liquidity, curve_liquidity, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """, (symbol, price, uniswap_liquidity, curve_liquidity, timestamp))

        conn.commit()
        cur.close()
        logger.info(f"✅ Live data stored successfully for {len(live_data)} symbols.")

        # ✅ Return live data to the frontend
        return jsonify({"status": "success", "live_data": live_data})

    except Exception as e:
        logger.error(f"❌ Error fetching live data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/historical-data")
def get_historical_data():
    """
    Fetches stored market data from MySQL.
    Returns the latest price, liquidity, and timestamp for each asset.
    """
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute("""
            SELECT symbol, price, uniswap_liquidity, curve_liquidity, timestamp
            FROM market_data
            ORDER BY timestamp DESC
        """)

        historical_data = cur.fetchall()
        cur.close()
        logger.info(f"✅ Retrieved {len(historical_data)} historical records.")
        logger.info(jsonify({"status": "success", "historical_data": historical_data}))
        return jsonify({"status": "success", "historical_data": historical_data})

    except Exception as e:
        logger.error(f"❌ Error fetching historical data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route("/history/<symbol>")
def get_full_history(symbol):
    """
    Fetches the full historical price data for a given trading pair.
    Returns all recorded prices and timestamps.
    """
    try:
        logger.info(f"Fetching historical data for {symbol}...")
        cur = conn.cursor(pymysql.cursors.DictCursor)

        cur.execute("""
            SELECT symbol, price, uniswap_liquidity, curve_liquidity, timestamp
            FROM market_data
            WHERE symbol = %s
            ORDER BY timestamp ASC
        """, (symbol,))

        history_data = cur.fetchall()
        cur.close()

        if not history_data:
            return jsonify({"status": "error", "message": f"No historical data found for {symbol}"}), 404

        logger.info(f"✅ Retrieved {len(history_data)} historical records for {symbol}.")
        return jsonify({"status": "success", "symbol": symbol, "history": history_data})

    except Exception as e:
        logger.error(f"❌ Error fetching history for {symbol}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
