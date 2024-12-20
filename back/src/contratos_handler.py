import logging
import requests as req
import traceback as tr
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
from typing import Union

from src.shared import ARCHER_IDS, URL
from src.archer_api_handler import archer_login, get_all_tree_sub_elements, get_tree_element

logger = logging.getLogger(__name__)

report_table_id = ARCHER_IDS['idInformeContrato']

def getAllContratos ():
    token = archer_login()
    contratos = get_contratos_page(token, [])
    return contratos

def get_contratos_page(token: str, contratos: list = [], page: int = 1):
    id_report = report_table_id
    aux_page = page
    if token is None:
        logger.info('No se pudo obtener el token correctamente, validar usuario de servicio de archer')
        return

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
        response = req.post(f"{URL}/ws/search.asmx", verify=False, headers=headers, data=body)
    except (ConnectionError) as e:
        logger.error(f'Ocurrio un error a la hora de hacer la busqueda del reporte de archer. Pagina actual: {page}')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None
    
    if response.status_code != 500:
        try:
            tree = ET.fromstring(response.content)
            tags_from = tree.find('.//{http://archer-tech.com/webservices/}SearchRecordsByReportResult').text
            logger.info(tags_from)
            tags_from = tags_from.replace('<?xml version="1.0" encoding="utf-16"?>', '<?xml version="1.0" encoding="utf-8"?>').encode('utf-8', errors='ignore')
            tree = ET.fromstring(tags_from)
            records = tree.findall('Record')
            if not records or records is None:
                return contratos
            else:
                for record in records:
                    add_new_contrato(token, record, contratos)
                aux_page += 1
                get_contratos_page(token, contratos, aux_page)
        except (OSError,TypeError,ValueError) as e:
            logger.error('Ocurrio un error en el arbol XML del informe de archer. Revisar los contratos del informe')
            logger.error(f'Detalle del error: {e}')
            logger.error(f'Detalle del traceback: {tr.format_exc()}')
            return None
    else:
        logger.error('Ocurrio un error. No se obtuvo un response valido de la API de archer. Revisar y validar los datos del response')
        return None
    return contratos
    
def add_new_contrato( token: str, record: Element, contratos: list = []):
    """Agrega un nuevo contrato al listado global para la carga. En caso que falle ese contrato NO
    se cargara en el listado de contratos"""
    contrato = get_contrato_from_page(token, record)
    try:
        if contratos is not None: 
           contratos.append(contrato)
    except (OSError,ValueError) as e:
        logger.error('No se pudo agregar el contrato')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
    
def get_contrato_from_page(token: str, record: Element) -> Union[dict, None]:
    # Obtener los datos
    nroContrato = record.find('./Field[@id="15151"]').text.strip()
    print(nroContrato)
    cliente = record.find('./Field[@id="15132"]/Reference').text.strip()
    print(cliente)
    fechaInicio = record.find('./Field[@id="15140"]').text.strip()
    print(fechaInicio)
    fechaFin = record.find('./Field[@id="15141"]').text.strip()
    print(fechaInicio)
    tecnologia = record.find('./Field[@id="26996"]/ListValues/ListValue').text.strip()
    print(tecnologia)
    estadoContrato = record.find('./Field[@id="16921"]/ListValues/ListValue').text.strip()
    print(estadoContrato)
    modulo = record.get("moduleId")
    print(modulo)



# Crear el objeto Contrato
    contrato = {
        "nroContrato": nroContrato,
        "cliente": cliente,
        "fechaInicio": fechaInicio,
        "fechaFin": fechaFin,
        "tecnologia": tecnologia,
        "estadoContrato": estadoContrato,
        "modulo": modulo
    }
    

    return contrato

