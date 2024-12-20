from flask import Flask,request, jsonify, send_file, Response
from flask_cors import CORS
import requests
from xml.etree import ElementTree as ET
import logging
from src.archer_api_handler import archer_login
import json

from src.contratos_handler import getAllContratos
from src.shared import URL

logging.basicConfig(
    level=logging.INFO,
    filename="./logs/app-flask-log.log",
    format=f'[%(asctime)-5s] %(levelname)-8s %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S',
    filemode='w+'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"]) 


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    # Recibir los datos del formulario desde el frontend
    data = request.get_json()

    cliente = data.get('cliente')
    if not cliente:
        return jsonify ({"error": "La variable 'empresa' es obligatoria"}), 400
    
    selectedMonth = data.get('selectedMonth')
    mes = selectedMonth if selectedMonth else data.get('mes')
    if not mes:
        return jsonify ({"error": "El mes es obligatorio (selectedMonth o mes)"}), 400

    tecnologia = data.get('tecnologia')
    contrato = data.get('contrato')
    nombre_archivo = data.get('nombre_archivo')

    # Llamada a la API externa para obtener los datos
    token = archer_login()  # El token que usas para la autenticación en la API
    id_report = "E0099235-31F3-4BD5-ADCE-5F234317D686"  # El ID o GUID del reporte

    # Parámetros adicionales de la solicitud
    aux_page = 1  # Página por defecto, esto lo puedes ajustar según tus necesidades


    # Construir el cuerpo SOAP con los parámetros adicionales
    headers = {
        'Content-Type': 'text/xml;charset=utf-8',
        'SOAPAction': 'http://archer-tech.com/webservices/SearchRecordsByReport'
    }
    body = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <SearchRecordsByReport xmlns="http://archer-tech.com/webservices/">
                            <sessionToken>{token}</sessionToken>
                            <reportIdOrGuid>{id_report}</reportIdOrGuid>
                            <pageNumber>{aux_page}</pageNumber>
                        </SearchRecordsByReport>
                    </soap:Body>
                </soap:Envelope>"""
                
    try:
        response = requests.post(f"{URL}/ws/search.asmx", verify=False, headers=headers, data=body)
        print(response)
    except (ConnectionError) as e:
        logger.error(f'Ocurrio un error a la hora de hacer la busqueda del reporte de archer. Pagina actual: {aux_page}')
        logger.error(f'Detalle del error: {e}')
        return None
    
    if response.status_code != 200:
        return f"Error en la solicitud SOAP: {response.status_code}"

    if response.status_code != 500:
        try:
            tree = ET.fromstring(response.content)
            tags_from = tree.find('.//{http://archer-tech.com/webservices/}SearchRecordsByReportResult').text
            tags_from = tags_from.replace('<?xml version="1.0" encoding="utf-16"?>', '<?xml version="1.0" encoding="utf-8"?>').encode('utf-8', errors='ignore')
            tree = ET.fromstring(tags_from)
            records = tree.findall('Record')
            if not records or records is None:
                return None
            else:
                for record in records:
                    pass
                aux_page += 1
                
            
        except (OSError,TypeError,ValueError) as e:
            logger.error('Ocurrio un error en el arbol XML del informe de archer. Revisar los tickets del informe')
            logger.error(f'Detalle del error: {e}')
            return None
    else:
        logger.error('Ocurrio un error. No se obtuvo un response valido de la API de archer. Revisar y validar los datos del response')
        return None

@app.route('/getContratos', methods=['GET'])
def get_contratos():
    try:
        contratos = getAllContratos()
        logger.info(contratos)
        return Response(
            response=json.dumps({
                "Status": 'Success',
                "Result": contratos
            }), status=200, mimetype="application/json")
    except Exception as e:
        return Response(
            response=json.dumps({
                "Status": 'ERROR'
            }), status=400, mimetype="application/json")
    
if __name__ == '__main__':
    app.run(debug=True)
