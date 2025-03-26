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
        "Password": password
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
    
def get_tree_element(
        record: Element, 
        error_message: str = "Ocurrio un error al obtener el campo", *args: int
    ) -> Union[str, None]:
    """Obtiene los campos de un elemento del arbol XML en funcion de
    los indices *args pasados por parametro

    Args:
        record (Element): Registro del arbol XML
        error_message (str, optional): Mensaje en caso de no poder obtener el campo
        *args (int): Indices del array que devuelve un record del arbol XML

    Returns:
        Union[str,None]: Campo del arbol XML
    """
    try:
        tree_element = None
        for arg in args:
            tree_element = record[arg] if tree_element is None else tree_element[arg]
        return tree_element.text 
    except (IndexError, TypeError) as e:
        pass
        #logger.warning(error_message)
        #logger.error(f'Detalle del error: {e}')
        #logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None

def get_all_tree_sub_elements(
        record: Element, 
        error_message: str = "Ocurrio un error al obtener el campo",
        *args: int
    ) -> Union[str, None]:
    """Obtiene los campos de un elemento del arbol XML en funcion de
    los indices *args pasados por parametro

    Args:
        record (Element): Registro del arbol XML
        error_message (str, optional): Mensaje en caso de no poder obtener el campo
        args
    Returns:
        Union[str,None]: Campo del arbol XML
    """
    try:
        tree_element = None
        for arg in args:
            tree_element = record[arg] if tree_element is None else tree_element[arg]
    except (IndexError, TypeError) as e:
        pass
        logger.warning(error_message)
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None

    listOfValues=[]
    try:
        index=0
        listOfValues, value = add_tree_element_to_list(tree_element, error_message, listOfValues, index)
        while(value):
            index += 1
            listOfValues, value = add_tree_element_to_list(tree_element, error_message, listOfValues, index)
    except (IndexError, TypeError) as e:
        pass
        #logger.warning(error_message)
        #logger.error(f'Detalle del error: {e}')
        #logger.error(f'Detalle del traceback: {tr.format_exc()}')
    return listOfValues

def add_tree_element_to_list(
        record: Element, 
        error_message: str = "Ocurrio un error al obtener el campo",
        listOfValues: list = [],
        index: int = 0
    ) -> Union[str, None]:
    """Obtiene los campos de un elemento del arbol XML en funcion de
    los indices *args pasados por parametro

    Args:
        record (Element): Registro del arbol XML
        error_message (str, optional): Mensaje en caso de no poder obtener el campo
        *args (int): Indices del array que devuelve un record del arbol XML

    Returns:
        Union[str,None]: Campo del arbol XML
    """
    value = get_tree_element(
            record, error_message, index
        )
    if(value): listOfValues.append(value)
    return listOfValues, value

def get_data_of_content_id(contentId: str, token: str):
    """Obtencion del valor del content id de Archer.

    Args:
        contentId (str): Id de archer a buscar su contenido
        token (str): Token de usuario de archer de la sesion

    Returns:
        Any: Campos con la informacion de ese content id
    """

    headers = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
        "Authorization": f"Archer session-id={token}",
        "Content-Type": "application/json",
        "X-Http-Method-Override": "GET"
    }
    noPase = True
    while(noPase):
        try:
            response = req.post(f'{URL}/api/core/content/contentid?id={contentId}', headers=headers, verify=False, timeout=60)
            noPase = False
        except Exception as e:
            logger.warning(f"Error al buscar la data del content id {contentId}, se volvera a intentar")
    try:
        if not response: 
            logger.error(f'Se obtuvo un response None de un request data of content id')
        if response.status_code != 500:
            result = response.json()['RequestedObject']['FieldContents']
            return result
    except (OSError,KeyError,json.decoder.JSONDecodeError) as e:
        logger.error(f'Ocurrio un error al accceder al valor del content id {contentId} obtenido en el response')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        
def get_data_of_reference_field_id(referenceFieldId: str, token: str):
    """Obtencion del valor del content id de Archer.

    Args:
        contentId (str): Id de archer a buscar su contenido
        token (str): Token de usuario de archer de la sesion

    Returns:
        Any: Campos con la informacion de ese content id
    """

    headers = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
        "Authorization": f"Archer session-id={token}",
        "Content-Type": "application/json",
        "X-Http-Method-Override": "GET"
    }
    try:
        response = req.post(f'{URL}/api/core/content/referencefield/referencefieldid?id={referenceFieldId}', headers=headers, verify=False, timeout=30)
    except ConnectionError as e:
        logger.error('No se recibio respuesta de archer para el indicador solicitado')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
    try:
        if not response: 
            logger.error(f'Se obtuvo un response None de un request data of content id')
        if response.status_code != 500:
            return response.json()['RequestedObject']['FieldContents']
    except (OSError,KeyError,json.decoder.JSONDecodeError) as e:
        logger.error(f'Ocurrio un error al accceder al valor del field content id {referenceFieldId} obtenido en el response')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')        

def get_data_of_attachment_id(attachmentId: str, token: str):
    """Obtencion del valor del content id de Archer.

    Args:
        contentId (str): Id de archer a buscar su contenido
        token (str): Token de usuario de archer de la sesion

    Returns:
        Any: Campos con la informacion de ese content id
    """

    headers = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
        "Authorization": f"Archer session-id={token}",
        "Content-Type": "application/json",
        "X-Http-Method-Override": "GET"
    }
    try:
        response = req.post(f'{URL}/api/core/content/attachment/{attachmentId}', headers=headers, verify=False, timeout=30)
    except ConnectionError as e:
        logger.error('No se recibio respuesta de archer para el indicador solicitado')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
    try:
        if not response: 
            logger.error(f'Se obtuvo un response None de un request data of content id')
        if response.status_code != 500:
            return response.json()['RequestedObject']['AttachmentBytes']
    except (OSError,KeyError,json.decoder.JSONDecodeError) as e:
        logger.error(f'Ocurrio un error al accceder al valor del attachment id {attachmentId} obtenido en el response')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')        
        
def get_related_user(userId: str, token: str):
    """Obtencion del valor del user id de Archer.

    Args:
        userId (str): Id de archer a buscar su contenido
        token (str): Token de usuario de archer de la sesion

    Returns:
        Any: Campos con la informacion de ese user id
    """

    headers = {
        "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8",
        "Authorization": f"Archer session-id={token}",
        "Content-Type": "application/json",
        "X-Http-Method-Override": "GET"
    }
    try:
        response = req.post(f'{URL}/platformapi/core/system/user/{userId}', headers=headers, verify=False, timeout=30)
    except ConnectionError as e:
        logger.error('No se recibio respuesta de archer para el usuario solicitado')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
    try:
        if not response: 
            logger.error(f'Se obtuvo un response None de un request data of user id')
        if response.status_code != 500:
            userData = response.json()

            firstName = userData['FirstName']
            lastName = userData['LastName']
            userName = f"{firstName} {lastName}"

            return userName
    except (OSError,KeyError,json.decoder.JSONDecodeError) as e:
        logger.error(f'Ocurrio un error al accceder al valor del user id {userId} obtenido en el response')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')        
        
def get_value_list_value(valueId: str, token: str):
    """Obtencion del valor del valor de campo de lista global de Archer.

    Args:
        valueId (str): Id de archer a buscar su contenido
        token (str): Token de usuario de archer de la sesion

    Returns:
        Any: Campos con la informacion de ese user id
    """
                     
    headers = {
        'Content-Type': 'text/xml;charset=utf-8',
        'SOAPAction': "http://archer-tech.com/webservices/GetValuesListValue"
    }
    body = f"""<?xml version="1.0" encoding="utf-8"?>
                <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <GetValuesListValue xmlns="http://archer-tech.com/webservices/">
                            <sessionToken>{token}</sessionToken>
                            <valuesListValueId>{valueId}</valuesListValueId>
                        </GetValuesListValue>
                    </soap:Body>
                </soap:Envelope>"""
                    
    try:
        response = req.post(f'{URL}/ws/field.asmx', headers=headers, data=body, verify=False)
        if not response: 
            logger.error(f'Se obtuvo un response None de un request data of user id')
        if response.status_code != 500:
            ns = {
                    "soap": "http://schemas.xmlsoap.org/soap/envelope/", 
                    "ns1": "http://archer-tech.com/webservices/"
                }
            tree = ET.fromstring(response.content)
            valueData = tree.find(".//ns1:GetValuesListValueResult", ns)
            return valueData.text
    except (OSError,KeyError,json.decoder.JSONDecodeError) as e:
        logger.error(f'Ocurrio un error al accceder al valor del valueId {valueId} obtenido en el response')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')      