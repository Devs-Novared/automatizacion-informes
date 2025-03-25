import logging
import requests as req
import traceback as tr
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
from typing import Union
from datetime import datetime
from collections import defaultdict

from src.shared import ARCHER_IDS, URL
from src.archer_api_handler import archer_login, get_data_of_content_id, get_data_of_attachment_id 

logger = logging.getLogger(__name__)

report_table_id = ARCHER_IDS['idInformeContrato']

cantidadHSSoporte_id = ARCHER_IDS['idsGraficos']['CantidadHSSoporte']
HHSSExtras_id = ARCHER_IDS['idsGraficos']['HHSSExtras']
cantidadHSConsultoria_id = ARCHER_IDS['idsGraficos']['CantidadHSConsultoria']
HHSSTotales_id = ARCHER_IDS['idsGraficos']['HHSSTotales']
detalleCargaHoras_id = ARCHER_IDS['idsGraficos']['detalleCargaHoras']
tecnologia_id = ARCHER_IDS['idsGraficos']['Tecnologia']
TicketsAsociados_id = ARCHER_IDS['idsGraficos']['TicketsAsociados']
cargaHorasNormales_id = ARCHER_IDS['idsGraficos']['cargaHorasNormales']
FechaCargaHora_id = ARCHER_IDS['idsGraficos']['FechaCargaHora']
shadow_id = ARCHER_IDS['idsGraficos']['shadow']

FechaCreacionTicket_id = ARCHER_IDS['idsGraficos']['FechaCreacionTicket']
CreadorTicket_id = ARCHER_IDS['idsGraficos']['CreadorTicket']
PropietarioTicket_id = ARCHER_IDS['idsGraficos']['PropietarioTicket']
FechaCierreTicket_id = ARCHER_IDS['idsGraficos']['FechaCierreTicket']
TipoTicket_id = ARCHER_IDS['idsGraficos']['TipoTicket']
TecnologiaTicket_id = ARCHER_IDS['idsGraficos']['TecnologiaTicket']
HorasConsumidasTicket_id = ARCHER_IDS['idsGraficos']['HorasConsumidasTicket']
EstadoTicket_id = ARCHER_IDS['idsGraficos']['EstadoTicket']

logo_id = ARCHER_IDS['idsGraficos']['Logo']
user_id = ARCHER_IDS['idsGraficos']['UserId']
userName_id = ARCHER_IDS['idsGraficos']['Username']
tecnologiaLogo_id = ARCHER_IDS['idsGraficos']['TecnologiaLogo']

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
            tags_from = tags_from.replace('<?xml version="1.0" encoding="utf-16"?>', '<?xml version="1.0" encoding="utf-8"?>').encode('utf-8', errors='ignore')
            tree = ET.fromstring(tags_from)
            records = tree.findall('Record')
            if not records or records is None:
                return contratos
            else:
                for record in records:
                    add_new_contrato(record, contratos)
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
    
def add_new_contrato(record: Element, contratos: list = []):
    """Agrega un nuevo contrato al listado global para la carga. En caso que falle ese contrato NO
    se cargara en el listado de contratos"""
    contrato = get_contrato_from_page(record)
    try:
        if contrato is not None: 
           contratos.append(contrato)
    except (OSError,ValueError) as e:
        logger.error('No se pudo agregar el contrato')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
    
def get_contrato_from_page(record: Element) -> Union[dict, None]:
    nroContrato = record.find('./Field[@id="15151"]').text.strip()
    cliente = record.find('./Field[@id="15132"]/Reference').text.strip()
    fechaInicio = record.find('./Field[@id="15140"]').text.strip()
    fechaFin = record.find('./Field[@id="15141"]').text.strip()
    tecnologia = record.find('./Field[@id="27430"]/ListValues/ListValue').text.strip()
    estadoContrato = record.find('./Field[@id="16921"]/ListValues/ListValue').text.strip()
    modulo = record.get("moduleId")
    contentId = record.get("contentId")
    soporteCorrectivo = None
    try:
        soporteCorrectivo = record.find('./Field[@id="27005"]/ListValues/ListValue').text.strip()
    except Exception as e:
        pass
    
    horasSoporte = record.find('./Field[@id="28013"]').text

    contrato = {
        "nroContrato": nroContrato,
        "cliente": cliente,
        "fechaInicio": fechaInicio,
        "fechaFin": fechaFin,
        "tecnologia": tecnologia,
        "estadoContrato": estadoContrato,
        "modulo": modulo,
        "contentId": contentId,
        "soporteCorrectivo": soporteCorrectivo,
        "horasSoporte": horasSoporte,
    }

    #logger.info(contrato)
    return contrato

def extraer_mes(fecha_str):
    """Convierte una fecha en formato ISO `YYYY-MM-DDTHH:MM:SS` a su número de mes."""
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S").month
    except ValueError:
        logger.error(f"Formato de fecha inválido: {fecha_str}")
        return None

def mes_a_numero(mes_nombre):
    """Convierte el nombre de un mes en español a su número correspondiente."""
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    return meses.get(mes_nombre.lower())

def crear_informe(data):
    #logger.info(f"Datos recibidos en crear_informe: {data}")

    mes_seleccionado = mes_a_numero(data["mes"])
    if mes_seleccionado is None:
        logger.error(f"El mes '{data['mes']}' no es válido.")
        return None, None

    token = archer_login()
    response = get_data_of_content_id(data["contentId"], token)
    #logger.info(response)
    
    logoId = response[logo_id]['Value']
    logoData = None
    if(logoId):
        logoData = get_data_of_attachment_id(logoId[0], token)
    
    logoTecnologiaId = response[tecnologiaLogo_id]['Value']
    logoTecnologiaData = None
    if(logoTecnologiaId):
        logoTecnologiaData = get_data_of_attachment_id(logoTecnologiaId[0], token)
    
    valores_mensuales = defaultdict(int)
    
    detalleCargaHoras = response[ARCHER_IDS['idsGraficos']['detalleCargaHoras']]['Value']
    #logger.info(detalleCargaHoras)
    
    for contentIdHoras in detalleCargaHoras:
        infoHoras = get_data_of_content_id(contentIdHoras["ContentId"], token)

        cargaHorasNormales = infoHoras[ARCHER_IDS['idsGraficos']['cargaHorasNormales']]['Value']

        FechaCargaHora = infoHoras[ARCHER_IDS['idsGraficos']['FechaCargaHora']]['Value']
        #shadow = bool(infoHoras[ARCHER_IDS['idsGraficos']['shadow']]['Value'])

        if FechaCargaHora:
            try:
                fecha_objeto = datetime.strptime(FechaCargaHora, "%Y-%m-%dT%H:%M:%S")
                
                if fecha_objeto.month <= mes_seleccionado:
                    mes_anio = fecha_objeto.strftime('%Y-%m')
                    valores_mensuales[mes_anio] += cargaHorasNormales
                   
            except ValueError:
                logger.error(f"Error procesando fecha de carga de horas: {FechaCargaHora}")
            
    resultado_mensual = [{"mes": mes, "totalHorasMensual": totalHorasMensual} for mes, totalHorasMensual in valores_mensuales.items()]
    
    tickets_por_mes = defaultdict(int)
    tickets = []
    ticketsUltimaActualizacion = []
    
    TicketsAsociados = response[ARCHER_IDS['idsGraficos']['TicketsAsociados']]['Value']
    
    for contentIdTickets in TicketsAsociados:
        infoTickets = get_data_of_content_id(contentIdTickets, token)
        FechaCreacionTicket = infoTickets[ARCHER_IDS['idsGraficos']['FechaCreacionTicket']]['Value']

        if FechaCreacionTicket:
            try:
                fecha_objeto = datetime.strptime(FechaCreacionTicket, "%Y-%m-%dT%H:%M:%S.%f")
                if fecha_objeto.month <= mes_seleccionado:
                    mes_anio = fecha_objeto.strftime('%Y-%m')
                    tickets_por_mes[mes_anio] += 1

            except ValueError:
                logger.error(f"Error procesando fecha de creación de ticket: {FechaCreacionTicket}")
    

        FechaCierreTicket = infoTickets[ARCHER_IDS['idsGraficos']['FechaCierreTicket']]['Value']
            
        propietarioTicketId = infoTickets[ARCHER_IDS['idsGraficos']['PropietarioTicket']]['Value'][0]['ContentId']
        
        userContent = get_data_of_content_id(propietarioTicketId, token)
        userName = userContent[userName_id]['Value']
            
        if FechaCierreTicket:
            try:
                fecha_objeto = datetime.strptime(FechaCierreTicket, "%Y-%m-%dT%H:%M:%S")
    
                if fecha_objeto.month == mes_seleccionado:
                    
                    jsonTickets = {
                        "Nro de Ticket":infoTickets[ARCHER_IDS['idsGraficos']['NroTicket']]['Value'],
                        "Fecha Cierre Ticket": FechaCierreTicket,
                        "Creador Ticket": infoTickets[ARCHER_IDS['idsGraficos']['CreadorTicket']]['Value'],
                        "Propietario Ticket": userName,
                        "Fecha Creacion Ticket": infoTickets[ARCHER_IDS['idsGraficos']['FechaCreacionTicket']]['Value'],
                        "Tipo Ticket": infoTickets[ARCHER_IDS['idsGraficos']['TipoTicket']]['Value'],
                        "Asunto": infoTickets[ARCHER_IDS['idsGraficos']['Asunto']]['Value'],
                    }
                    tickets.append(jsonTickets)
            except ValueError as e:
                logger.error(f"Error procesando fecha de cerrado de ticket: {e}")
    
        
        #FechaCreacionTicket = infoTickets[ARCHER_IDS['idsGraficos']['FechaCreacionTicket']]['Value']
        UltimaActualizacion = infoTickets[ARCHER_IDS['idsGraficos']['UltimaActualizacion']]['Value']

        if UltimaActualizacion:
            try:
                fecha_objeto = datetime.strptime(UltimaActualizacion, "%Y-%m-%dT%H:%M:%S.%f")
    
                if fecha_objeto.month == mes_seleccionado:
                    
                    jsonTicketsUlt = {
                        "Nro de Ticket":infoTickets[ARCHER_IDS['idsGraficos']['NroTicket']]['Value'],
                        "Fecha Ultima Actualizacion": UltimaActualizacion,
                        "Creador Ticket": infoTickets[ARCHER_IDS['idsGraficos']['CreadorTicket']]['Value'],
                        "Propietario Ticket": userName,
                        "Fecha Creacion Ticket": infoTickets[ARCHER_IDS['idsGraficos']['FechaCreacionTicket']]['Value'],
                        "Tipo Ticket": infoTickets[ARCHER_IDS['idsGraficos']['TipoTicket']]['Value'],
                        "Asunto": infoTickets[ARCHER_IDS['idsGraficos']['Asunto']]['Value']
                    }
                    ticketsUltimaActualizacion.append(jsonTicketsUlt)
            except ValueError as e:
                logger.error(f"Error procesando fecha de cerrado de ticket: {e}")
            
    resultado_mensual_tickets = [{"mes": mes, "totalTicketsMensual": total} for mes, total in tickets_por_mes.items()]
    mensual_tickets_Cerrados = tickets
    mensual_Ult_Actualizacion = ticketsUltimaActualizacion

    return resultado_mensual, resultado_mensual_tickets, mensual_tickets_Cerrados, mensual_Ult_Actualizacion, logoData, logoTecnologiaData


