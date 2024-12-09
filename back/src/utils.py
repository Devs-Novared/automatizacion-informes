import json
import logging
import re
import traceback as tr
import socket

from typing import Union


logger = logging.getLogger(__name__)


def load_JSON_data(filename : str) -> dict:
    """Carga un archivo JSON y devuelve el contenido en formato de diccionario.

    Args:
        filename (str): Nombre del archivo JSON, de forma relativa o absoluta

    Returns:
        dict: Diccionario con los datos del JSON
    """
    with open(filename, 'r') as file:
        JSON_data = json.load(file)
    return JSON_data

def test_connection(url: str, timeout: int = 15, attempts: int = 3) -> bool:
    """Valida la conexion a una url con un timeout por defecto.

    Args:
        url (str): Url del host a probar la conexion
        timeout (int, optional): Timeout definido para probar la conexion. El valor por default es 15.
        attempts (int, optional): Intentos de conexion por realizar. Por defecto seran 3

    Returns:
        bool: True si la conexion fue exitosa, False en caso contrario
    """
    data_from_url = get_data_from_url(url)
    if data_from_url is None:
        return False
    
    protocol, host, port = data_from_url
    aux_port = int(port)
    valid_connection = False
    socket.setdefaulttimeout(timeout)
    for attempt_number in range(attempts):
        try:
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_connection.connect((host, aux_port))
            valid_connection = True
        except (OSError,socket.error,TimeoutError) as e:
            logger.warning(f'No se pudo validar la conexion en el intento {str(attempt_number+1)} con la siguiente URL: {url}')
            logger.error(f'Detalle del error que surgio: {e}')
            logger.error(f'Detalle del traceback: {tr.format_exc()}')
            socket_connection.close()
        else:
            logger.info(f'Se valido la conexion OK en el intento {str(attempt_number+1)} con la siguiente URL: {url}')
            socket_connection.close()
            return valid_connection
    return False


def get_data_from_url(url: str) -> tuple:
    """Obtiene los datos de una url fragmentandola

    Args:
        url (str): url del host a probar

    Returns:
        tuple(str,str,int): Tupla con formato `(protocolo,host,puerto)`
    """
    try:
        url_structure = re.findall(r'([^:\/\s]+)',url)
        protocol, url = url_structure[0], url_structure[1]
    except (IndexError, OSError) as e:
        logger.error('No se encontro una URL valida para obtener los datos de validacion')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None
    try:
        port = url_structure[2]
        if port.isdecimal():
            port = int(port)
        else:
            port = 80
    except IndexError:
        port = 80
    return (protocol,url,port)


def set_lang_color_name(umbral_color: str) -> Union[str, None]:
    """Cambio de idioma en el nombre del color

    Args:
        umbral_color (Union[str, None]): Nombre original del color

    Returns:
        Union[str, None]: Nombre de color cambiando de idioma o None en caso
        que el valor no este contemplado
    """
    if umbral_color is None:
        return None
    elif umbral_color == 'Verde':
        umbral_color = 'green'
    elif umbral_color == 'Rojo':
        umbral_color = 'red'
    elif umbral_color == 'Amarillo':
        umbral_color = 'yellow'
    else:
        logger.error('Ocurrio un error cuando se quizo cambiar el nombre del color')
    return umbral_color
    # from translate import Translator
    # colorUmbral = Translator(from_lang='es',to_lang='en').translate(colorUmbral).lower()


def is_integer(numero: Union[int, float]) -> bool:
    """Validacion de numero entero

    Args:
        numero (int): Numero por validar

    Returns:
        bool: Confirma si se trata de un numer entero o no
    """
    return numero % 1 == 0 if numero is not None else False


def assign_integer(number: Union[float, int]) -> int:
    """Reconvierte un numero coma flotante a un entero

    Args:
        number (float): Numero a validar, si es como flotante

    Returns:
        int: El mismo numero pero solo con la parte entera
    """

    try:
        number =float(number)

        if is_integer(number):
            number = int(number)
            # logger.info(number)
        # logger.info(number)
        # logger.info(type(number))
    except Exception as e:
        logger.error("No es un numero")
        logger.error(f"Error: {e}")
    return number


def set_periodic_number(number: float) -> Union[int, float]:
    """Dado un numero periodico, lo pasa a entero o con 
    coma flotante dependiendo el caso. Redondea a 4 decimales

    Args:
        number (float): Valor a verificar

    Returns:
        Union[int, float]: Numero entero o numero coma flotante cambiado
    """
    if number is None: return None
    if number == "None": return None
    try:
        if "%" in number: return number
        aux = number
        if isinstance(number,int):
            aux = int(number)
        else:
            if aux == "Sin datos": return 0
            aux = round(float(number),4)
        return aux
    except Exception as e:
        logger.error("Error en set periodic number")
        return None

def check_none_type(response_from_list_values: dict, value_list_id: str) -> Union[int, None]:
    """Valida el campo de la lista de valores de archer.

    Args:
        dataResponse (dict): Response del cual se quiere validar la existencia de un campo
        codigoId (str): Id que referencia la key del campo a validar

    Returns:
        Union[int, None]: Si el campo existe, devuelve su id, en caso de no haber valor en la lista
        de valores, devuelve None
    """
    try:
        if response_from_list_values[value_list_id]['Value'] is None:
            return None
        else:
            #logger.info(response_from_list_values[value_list_id]['Value'])
            return response_from_list_values[value_list_id]['Value']['ValuesListIds'][0]
    except (OSError,TypeError,ValueError,IndexError) as e:
        logger.error(f'Ocurrio un error al validar el campo de archer con el id {value_list_id}')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None


