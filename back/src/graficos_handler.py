import logging
from flask import Flask, jsonify
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import traceback as tr
import plotly as po

from datetime import datetime
from dateutil.relativedelta import relativedelta
from decimal import DivisionByZero
from numpy import radians, cos, sin, linspace

import plotly.io as pio      # Para guardar el gráfico como imagen
from io import BytesIO 

from src.shared import ARCHER_IDS, URL
from src.utils import set_lang_color_name
#from src.archer_api_handler import archer_login, get_all_tree_sub_elements, get_tree_element, get_data_of_content_id

logger = logging.getLogger(__name__)


def formatear_meses(lista_fechas):
    """Convierte y formatea las fechas en 'MMM YYYY'."""
    return [pd.to_datetime(mes).strftime("%b %Y") for mes in lista_fechas]


def grafico_linea_HorasConsumidas(resultado_mensual, meta_horas):    
    titulo="Horas Consumidas"
    etiqueta_x="Fecha de carga de Horas"
    etiqueta_y="Horas Cargadas Normales"
    
    # Extraemos los datos
    meses = [item['mes'] for item in resultado_mensual]
    totalHorasMensual = [item['totalHorasMensual'] for item in resultado_mensual]
    
    meses_formateados = formatear_meses(meses)
    
    if(len(totalHorasMensual) == 1 and meta_horas):
        totalHorasMensual = [None] + totalHorasMensual + [None]
        meses_formateados = ["Inicio"] + meses_formateados + ["Fin"]
        
    fig = go.Figure()
    # Línea suavizada y relleno hasta el eje x
    fig.add_trace(go.Scatter(
        x=meses_formateados,
        y=totalHorasMensual,
        text=[str(val) if val is not None else "" for val in totalHorasMensual], 
        textposition="top center",
        cliponaxis=False,
        textfont=dict(color="black", size=14), 
        fill='tozeroy',
        fillcolor='rgba(173, 216, 230, 0.5)',
        mode="lines+markers+text",
        line=dict(color="blue", width=2, shape='spline'),
        marker=dict(color="blue", size=8),
        name="Horas Cargadas"
    ))
    # Línea de meta en rojo punteado
    if meta_horas:
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
        paper_bgcolor='rgba(200, 200, 200, 0.5)',  
        plot_bgcolor='rgba(200, 200, 200, 0.5)',  
        title=dict(text=titulo, font=dict(color="black", size=18)),
        xaxis=dict(
            title=dict(text=etiqueta_x, font=dict(color="black", size=14)),
            tickfont=dict(color="black", size=12) 
        ),
        yaxis=dict(
            title=dict(text=etiqueta_y, font=dict(color="black", size=14)), 
            tickfont=dict(color="black", size=12) 
        )
    )
    
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)
    return img_bytes


def grafico_linea_TicketsConsumidos(resultado_mensual_tickets):
    titulo="Tickets Consumidos"
    etiqueta_x="Fecha de creación de Ticket"
    etiqueta_y="Tickets Totales"
                                    
    # Extraemos los datos
    meses = [item['mes'] for item in resultado_mensual_tickets]
    totalTicketsMensual = [item['totalTicketsMensual'] for item in resultado_mensual_tickets]
    
    meses_formateados = formatear_meses(meses)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses_formateados,
        y=totalTicketsMensual,
        text=[str(val) if val is not None else "" for val in totalTicketsMensual], 
        textposition="top center",
        cliponaxis=False,
        textfont=dict(color="black", size=14), 
        fill='tozeroy',
        fillcolor='rgba(173, 216, 230, 0.5)',
        mode="lines+markers+text",
        line=dict(color="blue", width=2, shape='spline'),
        marker=dict(color="blue", size=8),
        name="Horas Cargadas"
    ))
    fig.update_layout(
        paper_bgcolor='rgba(200, 200, 200, 0.5)', 
        plot_bgcolor='rgba(200, 200, 200, 0.5)',   
        title=dict(text=titulo, font=dict(color="black", size=18)),
        xaxis=dict(
            title=dict(text=etiqueta_x, font=dict(color="black", size=14)),
            tickfont=dict(color="black", size=12) 
        ),
        yaxis=dict(
            title=dict(text=etiqueta_y, font=dict(color="black", size=14)), 
            tickfont=dict(color="black", size=12) 
        )
    )
    
    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)

    return img_bytes

def grafico_velocimetro_HorasConsumidas(fechasContrato, cantidadHSConsultoria, resultado_mensual):
    
    """Armado del velocimetro con los datos propios del contrato

    Args:
        fechasContrato (dict): Diccionario con los datos del indicador
        que necesita actualmente el velocimetro
            {
                'fechaInicioContrato': '2024-05-17T00:00:00',
                'fechaFinContrato': '2025-05-17T00:00:00',
                'mesInforme': 'Febrero'
            }
        cantidadHSConsultoria (int): horas de consultoria
        resultado_mensual (dict):

    Returns:
        Union[str, None]: String base64 del grafico o None en caso de que exista algun error
    """
    
    title = "Horas consumidas - Soporte Evolutivo"
    if(not fechasContrato["horasPorMes"]): return None
    
    result_value = cantidadHSConsultoria #Aguja velocimetro
    
    delta = relativedelta(datetime.strptime(fechasContrato["fechaFinContrato"], "%Y-%m-%dT%H:%M:%S"), datetime.strptime(fechasContrato["fechaInicioContrato"], "%Y-%m-%dT%H:%M:%S"))
    diferenciaMesesContrato =  delta.years * 12 + delta.months
    horasMaximasContrato = int(diferenciaMesesContrato) * int(fechasContrato["horasPorMes"]) #Rojo / Limite amarillo
    
    delta = relativedelta(datetime.today(), datetime.strptime(fechasContrato["fechaInicioContrato"], "%Y-%m-%dT%H:%M:%S"))
    diferenciaMesesRelativa =  delta.years * 12 + delta.months
    horasMaximasRelativas = int(diferenciaMesesRelativa) * int(fechasContrato["horasPorMes"]) #Amarillo/Limite verde
    
    horasMaximasExceso = int(horasMaximasRelativas*1.2) #/Limite amarillo

    umbrals_from_values = [0, horasMaximasRelativas, min(horasMaximasExceso, horasMaximasContrato)]    
    umbrals_to_values = [horasMaximasRelativas, min(horasMaximasExceso, horasMaximasContrato), max(horasMaximasExceso, horasMaximasContrato, result_value)]
    umbrals_colors = ["Verde","Amarillo","Rojo"]
    

    # value = 95
    umbrals_min_value = min(umbrals_from_values)
    umbrals_max_value = max(umbrals_to_values)

    def load_data_to_fig() -> None:
        """Carga los datos asociados por valor - color dentro de un listado, y luego los asocia con un rango - color
        para el grafico del velocimetro

        """
        range_color_list = list()
        aux_mapping = [
            {
                'valorAsociado' : value, 
                'colorAsociado' : color
            } for (value, color) in zip(umbrals_to_values, umbrals_colors)
        ]
        for index, item in enumerate(aux_mapping):
            previous_value = umbrals_from_values[index]
            range_color_list.append({
                'range': [previous_value, item['valorAsociado']], 
                'color': set_lang_color_name(item['colorAsociado'])
            })
        return range_color_list

    try:
        steps_list = load_data_to_fig()
        tick_values = [0] + [result_value] + umbrals_to_values
        
        tick_text = [
            tick_value for tick_value in tick_values
        ]
    except (OSError,ValueError,TypeError,AttributeError,DivisionByZero) as e:
        logger.error('Ocurrio un error al calcular los valores a asignar al velocimetro (tickValues o tickText)')
        logger.error(f'Detalle del error: {e}')
        logger.error(f'Detalle del traceback: {tr.format_exc()}')
        return None

    if result_value is not None:
        try:
            fig = po.graph_objects.Figure(po.graph_objects.Indicator(
                domain={
                    'x': [0, 1],
                    'y': [0, 1]
                },
                value = result_value,
                mode="gauge",
                delta={'reference': 380},
                gauge={
                        'axis': {'range': [umbrals_min_value, umbrals_max_value],
                        "tickmode": "array",
                        "tickvals": tick_values,
                        "tickangle": 0,
                        "ticktext": tick_text,
                        "tickfont": {'color': 'black', 'size': 14} 

                    },
                    'bar': {'thickness': 0},
                    'steps': steps_list
                },
            ))

            fig.update_layout(
                margin=dict(t=40, b=100),
                paper_bgcolor='rgba(200, 200, 200, 0.5)',  # Fondo de toda la figura semi-transparente
                plot_bgcolor='rgba(200, 200, 200, 0)',   # Fondo del área del gráfico semi-transparente
                title=dict(text=title, font=dict(color="black", size=18)),
                xaxis={'showgrid': False, 'range': [-1, 1], 'visible': False},
                yaxis={'showgrid': False, 'range': [0, 1], 'visible': False}
            )

            # Aguja del velocimetro
            aux = max(min(result_value, umbrals_max_value), umbrals_min_value)
            porcentaje = (aux - umbrals_min_value) / (umbrals_max_value - umbrals_min_value)
            theta_angle = 180 * (1 - porcentaje)

            # Coordenadas
            radio = 1.0
            x_head = radio * cos(radians(theta_angle))
            y_head = radio * sin(radians(theta_angle))

            fig.add_annotation(
                ax=0, ay=0, axref='x', ayref='y',
                x=x_head, y=y_head, xref='x', yref='y',
                showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=4, arrowcolor="black"
            )
        except (OSError,ValueError,TypeError) as e:
            logger.error('Ocurrio un error al armar el grafico para el velocimetro')
            logger.error(f'Detalle del error: {e}')
            logger.error(f'Detalle del traceback: {tr.format_exc()}')
            return None
    else:
        logger.warning('No se encontraron datos para el valor actual de la aguja/flecha del velocimetro al grafico')
        return None
    
    # Valor donde apuntara la aguja del velocimetro
    fig.add_annotation(
        x=0, y=0, xref="x", yref="y",
        text=result_value, showarrow=False,
        font=dict(size=64, color="#000000"),
        align="center", ax=20, ay=-30, opacity=0.8
    )

    fig.add_annotation(
    x=0.5, y=-0.25,  # Más abajo aún
    xref="paper", yref="paper",
    text=f"Total de horas del contrato: {horasMaximasContrato}",
    showarrow=False,
    font=dict(size=20, color="black"),  # Más grande y negra
    align="center"
    )

    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)
    return img_bytes

