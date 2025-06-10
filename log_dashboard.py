from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="268453",
        database="New_log_db"
    )

@app.route("/")
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            filename,
            COUNT(Verbose) AS Verbose,
            COUNT(Debug) AS Debug,
            COUNT(Information) AS Information,
            COUNT(Warning) AS Warning,
            COUNT(Error) AS Error,
            COUNT(Fatal) AS Fatal
        FROM logs_data GROUP BY filename
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", summary=rows)

@app.route("/details")
def details():
    filename = request.args.get("filename")
    level = request.args.get("level")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT log_date, log_time, {level}
        FROM logs_data
        WHERE filename = %s AND {level} IS NOT NULL
    """, (filename,))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert to dict for cleaner frontend rendering
    results = [{"date": log[0], "time": log[1], "message": log[2]} for log in logs]
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True, port=5050)
