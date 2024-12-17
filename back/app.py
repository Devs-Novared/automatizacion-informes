from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import requests
import matplotlib.pyplot as plt
import io
from fpdf import FPDF
from xml.etree import ElementTree as ET

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"]) 

# Endpoint para manejar la solicitud de descarga del PDF
@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    # Recibir los datos del formulario desde el frontend
    data = request.get_json()

    app.logger.info(f"Datos recibidos: {data}")

    cliente = data.get('cliente')
    if not cliente:
        return jsonify ({"error": "La variable 'empresa' es obligatoria"}), 400
    
    selectedMonth = data.get('selectedMonth')
    mes = selectedMonth if selectedMonth else data.get('mes')
    if not mes:
        return jsonify ({"error": "El mes es obligatorio (selectedMonth o mes)"}), 400

    app.logger.info(f"cliente: {cliente}, Mes: {mes}")

    tecnologia = data.get('tecnologia')
    contrato = data.get('contrato')
    nombre_archivo = data.get('nombre_archivo')

    # Llamada a la API externa para obtener los datos
    token = "tu_token_aqui"  # El token que usas para la autenticación en la API
    id_report = "tu_report_id_aqui"  # El ID o GUID del reporte

    # Parámetros adicionales de la solicitud
    aux_page = 1  # Página por defecto, esto lo puedes ajustar según tus necesidades

    # Construir el cuerpo SOAP con los parámetros adicionales
    body = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <SearchRecordsByReport xmlns="http://archer-tech.com/webservices/">
                            <sessionToken>{token}</sessionToken>
                            <reportIdOrGuid>{id_report}</reportIdOrGuid>
                            <pageNumber>{aux_page}</pageNumber>
                            <cliente>{cliente}</cliente>
                            <mes>{mes}</mes>
                            <tecnologia>{tecnologia}</tecnologia>
                            <contrato>{contrato}</contrato>
                            <selectedMonth>{selectedMonth}</selectedMonth>
                        </SearchRecordsByReport>
                    </soap:Body>
                </soap:Envelope>"""

    headers = {
        'Content-Type': 'text/xml;charset=utf-8',
        'SOAPAction': 'http://archer-tech.com/webservices/SearchRecordsByReport'
    }

    # Realizar la solicitud SOAP
    url = "http://archer-tech.com/webservices/your_soap_service"  # URL del servicio SOAP
    response = requests.post(url, data=body, headers=headers)

    if response.status_code != 200:
        return f"Error en la solicitud SOAP: {response.status_code}"

    # Procesar la respuesta XML de la API
    try:
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        # Aquí debes ajustar según la estructura de la respuesta que recibes de la API
        # Por ejemplo, extraer los datos del XML (ajustar según la respuesta de la API)
        data_from_api = []  # Listado de datos obtenidos de la API

        # Este es solo un ejemplo de cómo extraer datos
        for record in root.iter('Record'):
            campo_x = record.find('CampoX').text  # Ajusta según el nombre de los campos en el XML
            campo_y = record.find('CampoY').text  # Ajusta según el nombre de los campos en el XML
            data_from_api.append({'campo_x': campo_x, 'campo_y': campo_y})

    except ET.ParseError as e:
        return f"Error al procesar el XML: {e}"

    # Procesa los datos de la API para crear el gráfico
    x_data = [item['campo_x'] for item in data_from_api]
    y_data = [item['campo_y'] for item in data_from_api]

    # Crear el gráfico usando Matplotlib
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data, label='Datos')

    ax.set(xlabel='Campo X', ylabel='Campo Y', title='Gráfico de Datos')
    ax.grid()

    # Guardar el gráfico en un buffer de memoria
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='PNG')
    img_stream.seek(0)
    plt.close(fig)

    # Crear el PDF usando FPDF
    pdf = FPDF()
    pdf.add_page()

    # Establecer título en el PDF
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Informe para {cliente} - {mes}", ln=True, align='C')
    pdf.ln(10)  # Espacio entre el título y la imagen

    # Agregar el gráfico al PDF
    img_path = '/tmp/graph.png'  # Guardar temporalmente la imagen en el sistema de archivos
    with open(img_path, 'wb') as img_file:
        img_file.write(img_stream.read())  # Escribir los datos de la imagen en un archivo
    pdf.image(img_path, x=10, y=40, w=190)  # Ajusta la posición y tamaño de la imagen

    # Guardar el archivo PDF en un buffer
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    # Enviar el archivo PDF como respuesta
    return send_file(pdf_output,
                    as_attachment=True,
                    download_name=nombre_archivo,
                    mimetype='application/pdf')


if __name__ == '__main__':
    app.run(debug=True)
