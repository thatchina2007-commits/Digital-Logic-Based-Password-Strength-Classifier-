"""
app.py
Main Flask Application for EC2201 Digital Logic Based Password Strength Classifier.
Routes for all 9 web pages, REST API endpoints, database synchronization, and ZIP packaging.
"""

import os
import io
import zipfile
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import logic_engine
import test_cases
import database
import data_processor

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize database on startup
with app.app_context():
    database.init_db()


# ==========================================
# Web Page Routes
# ==========================================

@app.route("/")
def index():
    """1. Home Page"""
    return render_template("index.html")


@app.route("/about")
def about():
    """2. About Project Page"""
    return render_template("about.html")


@app.route("/classifier")
def classifier_page():
    """3. Password Classifier Module"""
    initial_pwd = request.args.get("pwd", "LogicPass#2026")
    return render_template("classifier.html", initial_pwd=initial_pwd)


@app.route("/logic-analysis")
def logic_analysis_page():
    """4. Digital Logic Analysis Page"""
    analysis_data = logic_engine.get_boolean_analysis()
    return render_template("logic_analysis.html", analysis=analysis_data)


@app.route("/test-cases")
def test_cases_page():
    """5. Test Case Module"""
    return render_template("test_cases.html")


@app.route("/dataset")
def dataset_page():
    """6. Dataset Management Page"""
    return render_template("dataset.html")


@app.route("/dashboard")
def dashboard_page():
    """7. Dashboard Page"""
    return render_template("dashboard.html")


@app.route("/report")
def report_page():
    """8. Report Page"""
    return render_template("report.html")


@app.route("/deliverables")
def deliverables_page():
    """9. Deliverables & Viva Hub"""
    readme_path = os.path.join(BASE_DIR, "README.md")
    readme_text = ""
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_text = f.read()
    return render_template("deliverables.html", readme_content=readme_text)


@app.route("/requirements.txt")
def serve_requirements():
    """Direct view of requirements.txt"""
    return send_from_directory(BASE_DIR, "requirements.txt", mimetype="text/plain")


# ==========================================
# REST API Endpoints
# ==========================================

@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    Evaluates raw password via Boolean logic engine, Full/Half adders, and Comparator.
    Stores evaluation in SQLite.
    """
    data = request.get_json() or {}
    password = data.get("password", "")
    eval_result = logic_engine.evaluate_password(password)
    
    # Persist in DB (skip completely empty to keep db clean, or record)
    try:
        database.save_evaluation(eval_result)
    except Exception as e:
        app.logger.warning(f"Failed to persist evaluation: {e}")

    return jsonify(eval_result)


@app.route("/api/truth-table", methods=["GET"])
def api_truth_table():
    """Returns all 32 truth table states (2^5)"""
    table = logic_engine.generate_truth_table()
    return jsonify(table)


@app.route("/api/test-cases/run", methods=["POST"])
def api_run_test_cases():
    """Executes all 10 normal and 5 edge test cases"""
    report = test_cases.run_all_test_cases()
    return jsonify(report)


@app.route("/api/dataset/generate", methods=["POST"])
def api_dataset_generate():
    """Generates synthetic password dataset"""
    data = request.get_json() or {}
    count = int(data.get("count", 50))
    count = max(10, min(count, 500))

    items = data_processor.generate_synthetic_passwords(total_count=count)
    dataset_id = database.save_dataset(f"Synthetic Dataset ({count} items)", items)

    return jsonify({
        "success": True,
        "dataset_id": dataset_id,
        "count": len(items),
        "items": items
    })


@app.route("/api/dataset/upload", methods=["POST"])
def api_dataset_upload():
    """Parses uploaded CSV file and classifies all entries"""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    try:
        content = file.read().decode("utf-8", errors="ignore")
        items = data_processor.parse_csv_dataset(content)
        if not items:
            return jsonify({"success": False, "error": "No valid passwords found in CSV"}), 400

        dataset_id = database.save_dataset(f"Uploaded: {file.filename}", items)
        return jsonify({
            "success": True,
            "dataset_id": dataset_id,
            "count": len(items),
            "items": items
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats():
    """Calculates aggregate metrics for Chart.js charts"""
    evaluations = database.get_recent_evaluations(limit=100)
    stats = data_processor.compute_analytics(evaluations)
    return jsonify(stats)


@app.route("/api/history", methods=["GET"])
def api_history():
    """Returns recent evaluation records"""
    history = database.get_recent_evaluations(limit=50)
    return jsonify(history)


@app.route("/api/download/sample-csv")
def download_sample_csv():
    """Downloads benchmark CSV sample dataset"""
    csv_path = os.path.join(BASE_DIR, "sample_data", "sample_passwords.csv")
    if not os.path.exists(csv_path):
        data_processor.seed_sample_dataset()
    return send_file(csv_path, as_attachment=True, download_name="sample_passwords_ec2201.csv", mimetype="text/csv")


@app.route("/api/download/report-pdf")
def download_report_pdf():
    """Downloads the official filled student mini project report PDF"""
    pdf_path = os.path.join(BASE_DIR, "A_Mohammed_Yasir_920425243054_Mini_Project_Report.pdf")
    if not os.path.exists(pdf_path):
        import build_project_report_pdf
        build_project_report_pdf.generate_report_pdf()
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="A_Mohammed_Yasir_920425243054_Mini_Project_Report.pdf",
        mimetype="application/pdf"
    )


@app.route("/api/download/project-zip")
def download_project_zip():
    """Dynamically packages project source code as a ZIP archive for deliverables"""
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Ignore cache, venv, and sqlite db files
            dirs[:] = [d for d in dirs if d not in ["__pycache__", ".git", ".idea", ".vscode", "venv"]]
            for file in files:
                if file.endswith((".pyc", ".db", ".log")):
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, BASE_DIR)
                zf.write(file_path, arcname=rel_path)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="digital_logic_password_classifier_EC2201.zip"
    )


if __name__ == "__main__":
    print("==================================================================")
    print(" EC2201 Digital Logic Based Password Strength Classifier Server")
    print(" Running locally at: http://127.0.0.1:5000")
    print("==================================================================")
    app.run(host="0.0.0.0", port=5000, debug=False)
