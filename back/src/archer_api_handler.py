from flask import Flask, request, jsonify, send_file
import requests
import xml.etree.ElementTree as ET
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        empresa = data.get('empresa', 'Sin_Empresa')
        mes = data.get('mes', 'Sin_Mes')
        nombre_archivo = data.get('nombre_archivo', 'reporte.pdf').replace(" ", "_")

        # Asegúrate de que el nombre del archivo tenga extensión .pdf
        if not nombre_archivo.endswith('.pdf'):
            nombre_archivo += '.pdf'

        pdf_path = os.path.join("generated_reports", nombre_archivo)

        # Asegúrate de que el directorio exista
        if not os.path.exists("generated_reports"):
            os.makedirs("generated_reports")

        # Simular datos obtenidos de la API
        data_from_api = [10, 20, 30, 40, 50]  # Datos de ejemplo

        # Generar gráfico
        chart_path = "chart.png"
        try:
            plt.figure(figsize=(6, 4))
            plt.bar(range(len(data_from_api)), data_from_api, color='skyblue')
            plt.title(f"Datos extraídos para {empresa}")
            plt.xlabel("Índice")
            plt.ylabel("Valor")
            plt.savefig(chart_path)
            plt.close()
        except Exception as e:
            return jsonify({"error": f"No se pudo generar el gráfico: {str(e)}"}), 500

        # Crear PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, f"Reporte de {empresa} - {mes}", ln=True, align="C")
            if os.path.exists(chart_path):
                pdf.image(chart_path, x=30, y=80, w=150)
            pdf.output(pdf_path)
        except Exception as e:
            return jsonify({"error": f"No se pudo generar el PDF: {str(e)}"}), 500

        # Enviar PDF
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True)

        return jsonify({"error": "El archivo PDF no fue creado correctamente"}), 500

    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500

    finally:
        # Limpiar archivos temporales
        if os.path.exists("chart.png"):
            os.remove("chart.png")


if __name__ == '__main__':
    app.run(debug=True)
