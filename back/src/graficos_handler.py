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

    # Agregar índices de valores en los puntos (sin flechas)
    for i, valor in enumerate(totalHorasMensual):
        fig.add_annotation(
            x=meses_formateados[i],
            y=valor,
            text=str(valor),  # Mostrar valor en español
            showarrow=False,  # Sin flechas
            font=dict(size=10, color="black"),
            align="center",
            yshift=10  # Desplazamiento vertical para no sobreponerse
        )

    # Hacer el fondo semi-transparente
    fig.update_layout(
        paper_bgcolor='rgba(200, 200, 200, 0.5)',  # Fondo de toda la figura semi-transparente
        plot_bgcolor='rgba(200, 200, 200, 0.5)'   # Fondo del área del gráfico semi-transparente
    )

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

    # Agregar índices de valores en los puntos (sin flechas)
    for i, valor in enumerate(totalTicketsMensual):
        fig.add_annotation(
            x=meses_formateados[i],
            y=valor,
            text=str(valor),  # Mostrar valor en español
            showarrow=False,  # Sin flechas
            font=dict(size=10, color="black"),
            align="center",
            yshift=10  # Desplazamiento vertical para no sobreponerse
        )

    # Hacer el fondo semi-transparente
    fig.update_layout(
        paper_bgcolor='rgba(200, 200, 200, 0.5)',  # Fondo de toda la figura semi-transparente
        plot_bgcolor='rgba(200, 200, 200, 0.5)'   # Fondo del área del gráfico semi-transparente
    )

    # Exportar imagen
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes
