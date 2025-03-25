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
                                  etiqueta_y="Horas Cargadas Normales",
                                  meta_horas=12):
    # Extraemos los datos
    meses = [item['mes'] for item in resultado_mensual]
    totalHorasMensual = [item['totalHorasMensual'] for item in resultado_mensual]
    
    meses_formateados = formatear_meses(meses)
    
    if(len(totalHorasMensual) == 1 and meta_horas):
        totalHorasMensual = [None] + totalHorasMensual + [None]
        meses_formateados = ["Inicio"] + meses_formateados + ["Fin"]
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses_formateados,
        y=totalHorasMensual,
        mode="lines+markers", 
        line=dict(color="blue", width=2),
        marker=dict(color="blue", size=8),
        name="Horas Cargadas"
    ))
    if (meta_horas):
        mes_inicio = meses_formateados[0]
        mes_fin = meses_formateados[-1]  
        fig.add_shape(
            type="line",
            x0=mes_inicio, x1=mes_fin, 
            y0=meta_horas, y1=meta_horas,  
            line=dict(color="red", width=2, dash="dash"), 
            name="Meta de Horas"
        )

    # Hacer el fondo semi-transparente
    fig.update_layout(
        paper_bgcolor='rgba(200, 200, 200, 0.5)',  # Fondo de toda la figura semi-transparente
        plot_bgcolor='rgba(200, 200, 200, 0.5)'   # Fondo del área del gráfico semi-transparente
    )
    
    fig.update_layout(
        title=titulo,
        xaxis_title=etiqueta_x,
        yaxis_title=etiqueta_y,
        xaxis=dict(categoryorder="array", categoryarray=meses)
    )
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
    
    meses_formateados = formatear_meses(meses)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses_formateados,
        y=totalTicketsMensual,
        mode="lines+markers",  
        line=dict(color="blue", width=2),
        marker=dict(color="blue", size=8),
        name="Horas Cargadas"
    ))
    fig.update_layout(
        title=titulo,
        xaxis_title=etiqueta_x,
        yaxis_title=etiqueta_y,
        xaxis=dict(categoryorder="array", categoryarray=meses),  
    )
    fig.update_layout(
        paper_bgcolor='rgba(200, 200, 200, 0.5)',  # Fondo de toda la figura semi-transparente
        plot_bgcolor='rgba(200, 200, 200, 0.5)'   # Fondo del área del gráfico semi-transparente
    )
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes
