import logging
from flask import Flask, jsonify
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

import plotly.io as pio      # Para guardar el gráfico como imagen
from io import BytesIO 

from src.shared import ARCHER_IDS, URL
#from src.archer_api_handler import archer_login, get_all_tree_sub_elements, get_tree_element, get_data_of_content_id

logger = logging.getLogger(__name__)


def formatear_meses(lista_fechas):
    """Convierte y formatea las fechas en 'MMM YYYY'."""
    return [pd.to_datetime(mes).strftime("%b %Y") for mes in lista_fechas]


def grafico_linea_HorasConsumidas(resultado_mensual,
                                  titulo="Horas Consumidas - Soporte Evolutivo",
                                  etiqueta_x="Fecha de carga de Horas",
                                  etiqueta_y="Horas Cargadas Normales"):
    # Extraemos los datos
    meses = [item['mes'] for item in resultado_mensual]
    totalHorasMensual = [item['totalHorasMensual'] for item in resultado_mensual]
    
    # Aplicamos el formato unificado
    meses_formateados = formatear_meses(meses)

    # Crear DataFrame
    data = pd.DataFrame({
        etiqueta_x: meses_formateados,
        etiqueta_y: totalHorasMensual
    })
    
    # Crear gráfico
    fig = px.line(data, x=etiqueta_x, y=etiqueta_y, title=titulo)

    # Aplicar etiquetas formateadas al eje X
    fig.update_xaxes(tickvals=meses_formateados)

    # Exportar imagen
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes


def grafico_linea_TicketsConsumidos(resultado_mensual_tickets,
                                    titulo="Tickets Consumidos - Soporte Evolutivo",
                                    etiqueta_x="Mes",
                                    etiqueta_y="Tickets Totales"):
    # Extraemos los datos
    meses = [item['mes'] for item in resultado_mensual_tickets]
    totalTicketsMensual = [item['totalTicketsMensual'] for item in resultado_mensual_tickets]
    
    # Aplicamos el formato unificado
    meses_formateados = formatear_meses(meses)

    # Crear DataFrame
    data = pd.DataFrame({
        etiqueta_x: meses_formateados,
        etiqueta_y: totalTicketsMensual
    })
    
    # Crear gráfico
    fig = px.line(data, x=etiqueta_x, y=etiqueta_y, title=titulo)

    # Aplicar etiquetas formateadas al eje X
    fig.update_xaxes(tickvals=meses_formateados)

    # Exportar imagen
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes


##def generar_tabla_tickets():
    """
    Función para generar una tabla interactiva a partir de los datos de los tickets y devolver la imagen como un objeto BytesIO.
    
    :param tickets: Lista de diccionarios con los datos de los tickets.
    :return: Imagen en formato PNG en memoria como un objeto BytesIO.
    """
    # Crear una lista de las columnas y los valores de la tabla
    columnas = ["FechaCreacionTicket", "TotalTicketsMensual", "CreadorTicket", 
                "PropietarioTicket", "FechaCierreTicket", "TipoTicket", 
                "TecnologiaTicket", "HorasConsumidasTicket", "EstadoTicket"]
    valores = [list(ticket.values()) for ticket in tickets]
    
    # Crear la tabla con Plotly
    fig = go.Figure(data=[go.Table(
        header=dict(values=columnas, fill_color='#f2f2f2', align='center'),
        cells=dict(values=zip(*valores), align='center', fill_color='white')
    )])

    # Ajustar el tamaño de la imagen
    fig.update_layout(
        width=800,
        height=400,
        title="Tabla de Tickets",
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # Crear un objeto BytesIO y guardar la imagen allí
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)  # Volver al principio del archivo en memoria
    
    return img_bytes
##