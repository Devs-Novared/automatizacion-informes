import json
import xml.etree.ElementTree as ET
import traceback as tr
import requests as req
import logging

from typing import Union
from xml.etree.ElementTree import Element
from urllib3.exceptions import InsecureRequestWarning

from src.shared import URL, REQUESTS_DATA, ARCHER_IDS
from src.utils import test_connection, check_none_type, set_periodic_number

req.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
logger = logging.getLogger(__name__)



def archer_login() -> Union[str, None]:
    """Realiza el login en la API de archer

    Raises:
        ConnectionError: Error de conexion con la API donde se debe loguear

    Returns:
        Union[str, None]: String con el token o None en caso que no se haya podido obtener el mismo
    """

    instance_name = REQUESTS_DATA[0]
    username = REQUESTS_DATA[1]
    password = REQUESTS_DATA[2]
   
    headers = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/json"
    }
    credentials = {
        "InstanceName": instance_name,
        "Username": username,
        "UserDomain":"",
        "Password": 'Novared#12345'
    }
    try:
        response = req.post(f"{URL}/api/core/security/login", data=json.dumps(credentials), headers=headers, verify=False)

    except (OSError,KeyError,ConnectionError) as e:
        logger.error(f'Hubo un error al iniciar sesión, comprueba el nombre de usuario y la contraseña')
        logger.error(f'Detalle del error {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None
    try:
        if response.status_code != 500:
            try:
                token = response.json()["RequestedObject"]["SessionToken"]
            except (TypeError,json.decoder.JSONDecodeError) as e:
                logger.error('Ocurrio un error al tratar de obtener el token de la solicitud')
                logger.error(f'Detalle del error: {e}')
                logger.error(f'Detalle del traceback: {tr.format_exc()}')
                return None
            else:
                logger.info('Se obtuvo el token de la solicitud correctamente')
                return token
        else:
            logger.error('Se obtuvo un status code 500 al obtener el response del login')
            return None
    except (OSError,KeyError,ConnectionError) as e:
        logger.error(f'Hubo un error interno a archer a la hora de tratar de iniciar la sesion en la api')
        logger.error(f'Detalle del error {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None
    


datos = list()

def get_gerencias_from_archer(aux_page=1):
    if(aux_page == 1):
        datos.clear()
    id_report="E0099235-31F3-4BD5-ADCE-5F234317D686"
    #INFORME GALICIA 
    token=archer_login()
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
    headers = {
        'Content-Type': 'text/xml;charset=utf-8',
        'SOAPAction': 'http://archer-tech.com/webservices/SearchRecordsByReport'
    }
    try:
        response = req.post(f"{URL}/ws/search.asmx", verify=False, headers=headers, data=body)
        tree = ET.fromstring(response.content)
        tags_from = tree.find('.//{http://archer-tech.com/webservices/}SearchRecordsByReportResult').text
        tags_from = tags_from.replace('<?xml version="1.0" encoding="utf-16"?>', '<?xml version="1.0" encoding="utf-8"?>').encode('utf-8', errors='ignore')
        tree = ET.fromstring(tags_from)
        records = tree.findall('Record')
        if not records or records is None:
            return
        else:
            for record in records:
                add_new_datos(record)
            aux_page+=1
            get_gerencias_from_archer(aux_page)
    except (ConnectionError) as e:
        logger.error('Ocurrio un error en el arbol XML del informe de archer. Revisar los indicadores del informe')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')	
    return(datos)
	