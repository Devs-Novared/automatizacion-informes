from flask import Flask,request, jsonify, send_file, Response
from flask_cors import CORS
import requests as req
from xml.etree import ElementTree as ET
import logging
import json
import base64

from src.contratos_handler import getAllContratos, crear_informe
from src.graficos_handler import grafico_linea_HorasConsumidas, grafico_linea_TicketsConsumidos

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


@app.route('/getContratos', methods=['GET'])
def get_contratos():
    try:
        contratos = getAllContratos()
        
        return Response(
            response=json.dumps({
                "Status": 'Success',
                "Result": contratos
            }), status=200, mimetype="application/json")
    except Exception as e:
        logger.error(e)
        return Response(
            response=json.dumps({
                "Status": 'ERROR'
            }), status=400, mimetype="application/json")


@app.route('/selected-data', methods=['POST'])
def guardar_seleccion():
    data = request.json
    
    cliente = data.get('cliente')
    tecnologia = data.get('tecnologia')
    contrato = data.get('contrato')
    mes = data.get('selectedMonth')
    contentId = data.get('contentId')

    if not cliente or not tecnologia or not contrato or not mes:
        return jsonify({"error": "Faltan datos"}), 400
    

    data = {
        "cliente": cliente,
        "tecnologia": tecnologia,
        "contrato": contrato,
        "mes": mes,
        "contentId" : contentId, 
    }
    crear_informe(data)
    
    return jsonify(data), 200


@app.route('/informe', methods=['POST'])
def generar_informe():
    try:
        # Obtener datos de la solicitud
        data = request.get_json()

        mes = data.get('selectedMonth')
        contentId = data.get('contentId')

        if not mes or not contentId:
            return jsonify({"error": "Faltan datos"}), 400

        data = {
            "mes": mes,
            "contentId" : contentId, 
        }
        
        contratosInfo = getAllContratos()
        #logger.info(contratosInfo)

        contratosSeleccionado = next((contrato for contrato in contratosInfo if contrato['contentId'] == data.get('contentId')), None)
        #logger.info(contratosSeleccionado)
        
        resultado_mensual, resultado_mensual_tickets, mensual_tickets_Cerrados, mensual_Ult_Actualizacion, logoData, logoTecnologiaData, horasConsultoria = crear_informe(data)

        contratosSeleccionado['horasSoporte'] = horasConsultoria
        
        img_bytes_horas = grafico_linea_HorasConsumidas(resultado_mensual, meta_horas = horasConsultoria)
        #logger.info(img_bytes_horas)
        
        img_bytes_tickets = grafico_linea_TicketsConsumidos(resultado_mensual_tickets)
        #logger.info(img_bytes_tickets)

        image_horas_base64 = base64.b64encode(img_bytes_horas.read()).decode('utf-8')
        image_tickets_base64 = base64.b64encode(img_bytes_tickets.read()).decode('utf-8')

        # Retornar las imágenes en formato JSON
        return jsonify({
            "contratosSeleccionado": contratosSeleccionado,
            'image_horas': image_horas_base64,
            'image_tickets': image_tickets_base64,
            "tickets_mensual_Cerrados" : mensual_tickets_Cerrados,
            "tickets_ult_act":  mensual_Ult_Actualizacion,
            "logoCliente": logoData,
            "logoTecnologia": logoTecnologiaData
        }), 200
    except Exception as e:
        logger.error(f"Error al generar el informe: {e}")
        return jsonify({"error": "Error al generar el informe"}), 500

if __name__ == '__main__':
    app.run(debug=True)
