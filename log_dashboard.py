from flask import Flask, render_template, request, jsonify
import mysql.connector
from app import get_db_connection
from import_logs import start_watching
import os

app = Flask(__name__)

import re
from datetime import datetime
import mysql.connector

log_pattern = re.compile(r"\[(\d{2}-\d{2}-\d{4}) (\d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+)")
level_map = {
    'Verbose': 'Verbose',
    'Debug': 'Debug',
    'Info': 'Information',
    'Information': 'Information',
    'Warning': 'Warning',
    'Error': 'Error',
    'Fatal': 'Fatal'
}

#columns = ["filename", "log_date", "log_time", "Verbose", "Debug", "Information", "Warning", "Error", "Fatal"]
columns = ["filename", "log_date", "log_time", "log_level", "message"]

sql = f"INSERT INTO log_New_Table ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"


#def process_log_lines(filepath, lines):
#    conn = mysql.connector.connect(host="localhost", user="root", password="268453", database="log_db")
#    cursor = conn.cursor()
#    sql = f"INSERT INTO log_table ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

#    filename = os.path.basename(filepath)
#   for line in lines:
#        match = log_pattern.match(line)
#        if match:
#            date_str, time_str, level_raw, message = match.groups()
#            level = level_map.get(level_raw)
#            if level:
#                date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
#                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
#                values = [filename, date_obj, time_obj]
#                for col in columns[3:]:
#                    values.append(message if col == level else None)
#                try:
#                    cursor.execute(sql, values)
#                except Exception as e:
#                   print(f"DB insert error: {e}")

#    conn.commit()
#   cursor.close()
#    conn.close()


"""def process_log_lines(filepath, lines):
    conn = mysql.connector.connect(host="localhost", user="root", password="268453", database="log_db")
    cursor = conn.cursor()
    
    columns = ["filename", "log_date", "log_time", "log_level", "message"]
    sql = f"INSERT INTO log_New_Table ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
    
    filename = os.path.basename(filepath)
    for line in lines:
        match = log_pattern.match(line)
        if match:
            date_str, time_str, level_raw, message = match.groups()
            level_raw = level_raw.lower()
            level = level_map.get(level_raw)
            if level:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                values = [filename, date_obj, time_obj, level, message]
                try:
                    cursor.execute(sql, values)
                except Exception as e:
                    print(f"DB insert error: {e}")

    conn.commit()
    cursor.close()
    conn.close()
"""

def process_log_lines(filepath, lines):
    conn = mysql.connector.connect(host="localhost", user="root", password="268453", database="log_db")
    cursor = conn.cursor()

    log_pattern = re.compile(r"\[(\d{2}-\d{2}-\d{4}) (\d{2}:\d{2}:\d{2})\] \[(\w+)\]\s*(.+)")

    level_map = {
        'verbose': 'Verbose',
        'debug': 'Debug',
        'info': 'Information',
        'information': 'Information',
        'warning': 'Warning',
        'error': 'Error',
        'fatal': 'Fatal'
    }

    sql = """
    INSERT INTO log_New_Table (filename, log_date, log_time, log_level, message)
    VALUES (%s, %s, %s, %s, %s)
    """

    filename = os.path.basename(filepath)

    for line in lines:
        line = line.strip()
        if not line:
            continue
        print(f"Line: {line}")
        match = log_pattern.match(line)
        if match:
            date_str, time_str, level_raw, message = match.groups()
            level_raw = level_raw.lower()
            level = level_map.get(level_raw)
            print(f"Parsed: {date_str} {time_str} {level} {message}")
            if level:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
                time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
                values = [filename, date_obj, time_obj, level, message]
                try:
                    cursor.execute(sql, values)
                except Exception as e:
                    print(f"DB insert error: {e}")
            else:
                print(f"Unrecognized level: {level_raw}")
        else:
            print("Regex didn't match line")

    conn.commit()
    cursor.close()
    conn.close()


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password_here",  # Replace with your actual password
        database="log_db"
    )


#@app.route("/details")
#def details():
#    filename = request.args.get("filename")
#    level = request.args.get("level")
#    conn = get_db_connection()
#    cursor = conn.cursor(dictionary=True)
#    cursor.execute(f"""
#        SELECT log_date, log_time, {level}
#        FROM log_table
#        WHERE filename = %s AND {level} IS NOT NULL
#    """, (filename,))
#    logs = cursor.fetchall()
#    cursor.close()
#    conn.close()
#    return jsonify(logs)

@app.route("/details")
def details():
    filename = request.args.get("filename")
    level = request.args.get("level")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT log_date, log_time, message
        FROM log_New_Table
        WHERE filename = %s AND log_level = %s
    """
    cursor.execute(query, (filename, level))
    logs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(logs)


if __name__ == "__main__":
    LOG_FOLDER = r"F:\Log viwer Project\all_log"
    start_watching(LOG_FOLDER, process_log_lines)
    

