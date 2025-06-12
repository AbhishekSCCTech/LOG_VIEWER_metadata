from flask import Flask, request, jsonify
import mysql.connector
from import_logs import start_watching
from log_parser import process_log_lines

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="log_db"
    )

@app.route("/details")
def details():
    filename = request.args.get("filename")
    level = request.args.get("level")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT log_date, log_time, message
        FROM log_Tekla_Table
        WHERE filename = %s AND log_level = %s
    """
    cursor.execute(query, (filename, level))
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(logs)

if __name__ == "__main__":
    LOG_FOLDER = r"F:\Log viwer Project\TeklaExternalLogFiles"
    start_watching(LOG_FOLDER, process_log_lines)
