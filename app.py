from flask import Flask, request, jsonify, render_template
import csv
from datetime import datetime
import os

from modules.csv_manager import CachedCSVManager

app = Flask(__name__)

try:
    from config.settings import file_name as _applied_jobs_csv_path
except ImportError:
    _applied_jobs_csv_path = "all excels/all_applied_applications_history.csv"

# Thread-safe CSV manager with 30 second cache
_csv_manager = CachedCSVManager(_applied_jobs_csv_path, cache_ttl_seconds=30)

##> ------ Karthik Sarode : karthik.sarode23@gmail.com - UI for excel files ------
@app.route('/')
def home():
    """Displays the home page of the application."""
    return render_template('index.html')

@app.route('/applied-jobs', methods=['GET'])
def get_applied_jobs():
    '''
    Retrieves a list of applied jobs from the applications history CSV file.
    '''
    try:
        rows = _csv_manager.safe_read_dict_rows()
        jobs = []
        for row in rows:
            jobs.append({
                'Job_ID': row.get('Job ID', ''),
                'Title': row.get('Title', ''),
                'Company': row.get('Company', ''),
                'HR_Name': row.get('HR Name', ''),
                'HR_Link': row.get('HR Link', ''),
                'Job_Link': row.get('Job Link', ''),
                'External_Job_link': row.get('External Job link', ''),
                'Date_Applied': row.get('Date Applied', '')
            })
        return jsonify(jobs)
    except FileNotFoundError:
        return jsonify({"error": "No applications history found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/applied-jobs/<job_id>', methods=['PUT'])
def update_applied_date(job_id):
    """
    Updates the 'Date Applied' field of a job in the applications history CSV file.
    """
    try:
        csvPath = _applied_jobs_csv_path

        if not os.path.exists(csvPath):
            return jsonify({"error": f"CSV file not found at {csvPath}"}), 404

        # Read current CSV content
        data = []
        with open(csvPath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            fieldNames = reader.fieldnames
            found = False
            for row in reader:
                if row['Job ID'] == job_id:
                    row['Date Applied'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    found = True
                data.append(row)

        if not found:
            return jsonify({"error": f"Job ID {job_id} not found"}), 404

        with open(csvPath, 'w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            writer.writerows(data)

        # Invalidate cache after write
        _csv_manager.invalidate_cache()

        return jsonify({"message": "Date Applied updated successfully"}), 200
    except Exception as e:
        print(f"Error updating applied date: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Debug and port are controlled via environment variables.
    # Defaults are safe for local development and should not be used for public deployment.
    debug_flag = os.getenv("APP_DEBUG", "false").lower() == "true"
    port = int(os.getenv("APP_PORT", "5000"))
    app.run(debug=debug_flag, port=port)

##<
