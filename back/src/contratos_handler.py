import logging
import requests as req
import traceback as tr
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
from typing import Union
from datetime import datetime
from collections import defaultdict

from src.shared import ARCHER_IDS, URL
from src.archer_api_handler import archer_login, get_data_of_content_id
from src.graficos_handler import grafico_linea_HorasConsumidas, grafico_linea_TicketsConsumidos

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


def mes_a_numero(mes):
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
        "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
        "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }
    return meses.get(mes.lower(), "Mes no válido")

# Ejemplo de uso
#mes_texto = "Marzo"
#numero_mes = mes_a_numero(mes_texto)




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
            #logger.info(tags_from)
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

    #logger.info("llegue")
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
    #logger.info(soporteCorrectivo)
    
    horasSoporte = record.find('./Field[@id="28013"]').text
    #logger.info(horasSoporte)

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



def crear_informe(data):

    contentId = data["contentId"]

    token = archer_login()

    response = get_data_of_content_id(contentId, token)

    cantidadHSSoporte = response[cantidadHSSoporte_id]["Value"]
    #logger.info(cantidadHSSoporte)
    HHSSExtras = response[HHSSExtras_id]["Value"]
    #logger.info(HHSSExtras)
    cantidadHSConsultoria = response[cantidadHSConsultoria_id]["Value"]
    #logger.info(cantidadHSConsultoria)
    HHSSTotales = response[HHSSTotales_id]["Value"]
    #logger.info(HHSSTotales)
    tecnologia = response[tecnologia_id]["Value"]
    #logger.info(tecnologia)

    detalleCargaHoras = response[detalleCargaHoras_id]["Value"]
    #logger.info(detalleCargaHoras)
    cargaHoras = []
    valores_mensuales = defaultdict(int)

    for contentIdHoras in detalleCargaHoras:
        infoHoras = get_data_of_content_id(contentIdHoras["ContentId"], token)
        cargaHorasNormales = infoHoras[cargaHorasNormales_id]["Value"]
        FechaCargaHora = infoHoras[FechaCargaHora_id]["Value"]
        shadow = infoHoras[shadow_id]["Value"]
        if (shadow != None):
            shadow = True
        else:
            shadow = False


        if FechaCargaHora:
            fecha_objeto = datetime.fromisoformat(FechaCargaHora)
            FechaCargaHora = fecha_objeto.strftime('%d/%m/%Y')

        # Extraer el mes y el año para agrupar
            mes_anio = fecha_objeto.strftime('%Y-%m')  # Formato: "YYYY-MM"
            valores_mensuales[mes_anio] += cargaHorasNormales 

        #logger.info(infoHoras)
        #logger.info(cargaHorasNormales)
        #logger.info(FechaCargaHora)
        #logger.info(shadow)
        jsonHoras = {
            "cargaHorasNormales": cargaHorasNormales,
            "FechaCargaHora": FechaCargaHora, 
            "shadow": shadow,
        }
        cargaHoras.append(jsonHoras)
    #logger.info(cargaHoras)
    #logger.info("Valores agrupados por mes:")
    #for mes, suma in valores_mensuales.items():
       #logger.info(f"{mes}: {suma}")


    resultado_mensual = [{"mes": mes, "totalHorasMensual":totalHorasMensual} for mes, totalHorasMensual in valores_mensuales.items()]
    #logger.info(resultado_mensual)


    TicketsAsociados = response[TicketsAsociados_id]["Value"]

    tickets_por_mes = defaultdict(int)

    tickets = []

    contadorTickets = 0

    for contentIdTickets in TicketsAsociados:
        infoTickets = get_data_of_content_id(contentIdTickets, token)
        FechaCreacionTicket = infoTickets[FechaCreacionTicket_id]["Value"]
        CreadorTicket = infoTickets[CreadorTicket_id]["Value"]
        PropietarioTicket = infoTickets[PropietarioTicket_id]["Value"]
        FechaCierreTicket = infoTickets[FechaCierreTicket_id]["Value"]
        TipoTicket = infoTickets[TipoTicket_id]["Value"]
        TecnologiaTicket = infoTickets[TecnologiaTicket_id]["Value"]
        HorasConsumidasTicket = infoTickets[HorasConsumidasTicket_id]["Value"]
        EstadoTicket = infoTickets[EstadoTicket_id]["Value"]

        if FechaCreacionTicket:
            fecha_objeto = datetime.fromisoformat(FechaCreacionTicket)
            FechaCreacionTicket = fecha_objeto.strftime('%Y-%m')
            tickets_por_mes[FechaCreacionTicket] += 1

        #logger.info(infoTickets)
        #logger.info(FechaCreacionTicket)
        jsonTickets = {
            "FechaCreacionTicket": FechaCreacionTicket,
            "TotalTicketsMensual": tickets_por_mes[FechaCreacionTicket],
            "CreadorTicket": CreadorTicket,
            "PropietarioTicket": PropietarioTicket,
            "FechaCierreTicket": FechaCierreTicket,
            "TipoTicket": TipoTicket,
            "TecnologiaTicket": TecnologiaTicket,
            "HorasConsumidasTicket": HorasConsumidasTicket,
            "EstadoTicket": EstadoTicket,

        }
        tickets.append(jsonTickets)
        #logger.info(jsonTickets)
    #logger.info(TicketsAsociados)
    #for mes, total in tickets_por_mes.items():
        #logger.info(f"Total de tickets en {mes}: {total}")

    resultado_mensual_tickets = [{"mes": mes, "totalTicketsMensual": total} for mes, total in tickets_por_mes.items()]

    #grafico_linea_HorasConsumidas(resultado_mensual)

    #grafico_linea_TicketsConsumidos(resultado_mensual_tickets)

    return resultado_mensual, resultado_mensual_tickets