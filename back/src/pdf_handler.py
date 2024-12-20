from flask import Flask, request, jsonify, send_file
import requests
import xml.etree.ElementTree as ET
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import time  # Import the time module for adding delay

app = Flask(__name__)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json :("}), 415
    try:
        
        data = request.json
        print("Received data:", data)  # Debug log
        # Rest of your code...

        data = request.json
        empresa = data.get('empresa', 'Sin_Empresa')
        mes = data.get('mes', 'Sin_Mes')
        nombre_archivo = data.get('nombre_archivo', 'reporte').replace(" ", "_")

        # Ensure the file name has a .pdf extension
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf'

        pdf_path = os.path.join("generated_reports", nombre_archivo)

        # Ensure the directory exists
        if not os.path.exists("generated_reports"):
            os.makedirs("generated_reports")

        # Define API URL and filters
        api_url = "https://help.archerirm.cloud/api_2024_06/es-mx/content/api/webapi/searchrecordsbyreport.htm"
        filters = {
            "empresa": empresa,
            "mes": mes
        }

        # Make the API call
        try:
            response = requests.post(api_url, json=filters, timeout=10)  # Replace POST/GET based on API specs
            if response.status_code == 200:
                data_from_api = response.json().get("data", [10, 20, 30, 40, 50])  # Example fallback
                print("Respuesta", data_from_api)
            else:
                return jsonify({"error": f"API request failed with status {response.status_code}"}), 500
        except requests.exceptions.Timeout:
            return jsonify({"error": "The API request timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {str(e)}"}), 500
        


if __name__ == '__main__':
    app.run(debug=True)
