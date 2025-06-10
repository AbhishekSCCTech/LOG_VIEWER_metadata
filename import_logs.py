import mysql.connector
import re
from datetime import datetime
import os

# Path to folder containing all log .txt files
LOG_FOLDER = r"F:\Log viwer Project\all_log - Copy"

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="268453",
    database="New_log_db"
)
cursor = conn.cursor()

# Regex to parse log lines
log_pattern = re.compile(r"\[(\d{2}-\d{2}-\d{4}) (\d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+)")

# Map log levels to database columns
level_map = {
    'Verbose': 'Verbose',
    'Debug': 'Debug',
    'Info': 'Information',
    'Information': 'Information',
    'Warning': 'Warning',
    'Error': 'Error',
    'Fatal': 'Fatal'
}

# Columns in DB table
columns = ["filename", "log_date", "log_time", "Verbose", "Debug", "Information", "Warning", "Error", "Fatal"]

# Iterate over all .txt files
for filename in os.listdir(LOG_FOLDER):
    if filename.endswith(".txt"):
        filepath = os.path.join(LOG_FOLDER, filename)
        with open(filepath, "r", encoding="utf-8") as file:
            for line in file:
                match = log_pattern.match(line)
                if match:
                    date_str, time_str, level, message = match.groups()
                    level = level_map.get(level)
                    if level:
                        date_obj = datetime.strptime(date_str, "%d-%m-%Y").date()
                        time_obj = datetime.strptime(time_str, "%H:%M:%S").time()

                        # Fill values: only current level gets message, rest are None
                        values = [filename, date_obj, time_obj]
                        for col in columns[3:]:
                            values.append(message if col == level else None)

                        sql = f"INSERT INTO logs_data ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
                        cursor.execute(sql, values)

conn.commit()
cursor.close()
conn.close()

print("✅ All log files imported successfully.")
