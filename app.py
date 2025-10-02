from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import matplotlib.pyplot as plt
import os
import csv
from datetime import datetime

app = Flask(__name__)

DB_NAME = "data/expenses.db"

def init_db():
    if not os.path.exists("data"):
        os.mkdir("data")
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS expenses
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         category TEXT,
                         amount REAL,
                         note TEXT,
                         date TEXT)''')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        category = request.form["category"]
        amount = float(request.form["amount"])
        note = request.form["note"]
        date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("INSERT INTO expenses (category, amount, note, date) VALUES (?, ?, ?, ?)",
                         (category, amount, note, date))
            conn.commit()
        return redirect("/")

    with sqlite3.connect(DB_NAME) as conn:
        expenses = conn.execute("SELECT * FROM expenses").fetchall()
    return render_template("index.html", expenses=expenses)

@app.route("/dashboard")
def dashboard():
    with sqlite3.connect(DB_NAME) as conn:
        data = conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category").fetchall()
        trend_data = conn.execute("SELECT date, SUM(amount) FROM expenses GROUP BY date").fetchall()

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    dates = [row[0] for row in trend_data]
    totals = [row[1] for row in trend_data]

    if categories:
        plt.figure(figsize=(6,6))
        plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90)
        if not os.path.exists("static"):
            os.mkdir("static")
        plt.savefig("static/pie_chart.png")
        plt.close()

    if dates:
        plt.figure(figsize=(8,4))
        plt.plot(dates, totals, marker='o', color='blue')
        plt.title("Daily Expense Trend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig("static/trend_chart.png")
        plt.close()

    total = sum(amounts) if amounts else 0
    return render_template("dashboard.html", total=total, categories=categories, amounts=amounts)

@app.route("/export")
def export():
    with sqlite3.connect(DB_NAME) as conn:
        expenses = conn.execute("SELECT * FROM expenses").fetchall()

    export_file = "expenses.csv"
    with open(export_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Category", "Amount", "Note", "Date"])
        writer.writerows(expenses)
    return send_file(export_file, as_attachment=True)

if __name__ == "__main__":
    init_db()
    print("✅ Expense Tracker Running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
