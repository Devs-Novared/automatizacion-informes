import logging
from flask import Flask, jsonify
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element 
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd

import plotly.io as pio      # Para guardar el gráfico como imagen
from io import BytesIO 

from src.shared import ARCHER_IDS, URL
#from src.archer_api_handler import archer_login, get_all_tree_sub_elements, get_tree_element, get_data_of_content_id

logger = logging.getLogger(__name__)


def grafico_linea_HorasConsumidas(resultado_mensual, titulo="Horas Consumidas - Soporte Evolutivo", etiqueta_x="Fecha de carga de Horas", etiqueta_y="Horas Cargadas Normales"):
    """
    Crea un gráfico de línea básico con Plotly Express usando los valores de `resultado_mensual`.

    Args:
        resultado_mensual (list): Lista de diccionarios con claves 'mes' y 'totalHorasMensual'.
        titulo (str): Título del gráfico.
        etiqueta_x (str): Etiqueta para el eje X.
        etiqueta_y (str): Etiqueta para el eje Y.
    """
    # Extraemos los meses y las sumas para el gráfico
    meses = [item['mes'] for item in resultado_mensual]
    totalHorasMensual = [item['totalHorasMensual'] for item in resultado_mensual]
    
    # Crear un DataFrame para los datos
    data = pd.DataFrame({
        etiqueta_x: meses,
        etiqueta_y: totalHorasMensual
    })
    
    # Crear el gráfico de línea
    fig = px.line(data, x=etiqueta_x, y=etiqueta_y, title=titulo)
    
    # Mostrar el gráfico
    fig.show()

    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)  # Volver al principio del archivo en memoria
    
    
    if img_bytes.getbuffer().nbytes > 0:
        print("La imagen se guardó correctamente en memoria.")
    else:
        print("Hubo un error al guardar la imagen en memoria.")

    return img_bytes


def grafico_linea_TicketsConsumidos(resultado_mensual_tickets, titulo="Tickets Consumidos - Soporte Evolutivo", etiqueta_x="Mes", etiqueta_y="Tickets Totales"):
    """
    Crea un gráfico de línea básico con Plotly Express usando los valores de `resultado_mensual_tickets`.

    Args:
        resultado_mensual_tickets (list): Lista de diccionarios con claves 'mes' y 'totalTicketsMensual'.
        titulo (str): Título del gráfico.
        etiqueta_x (str): Etiqueta para el eje X.
        etiqueta_y (str): Etiqueta para el eje Y.
    """
    # Extraemos los meses y los totales de tickets para el gráfico
    meses = [item['mes'] for item in resultado_mensual_tickets]
    totalTicketsMensual = [item['totalTicketsMensual'] for item in resultado_mensual_tickets]
    
    # Crear un DataFrame para los datos
    data = pd.DataFrame({
        etiqueta_x: meses,
        etiqueta_y: totalTicketsMensual
    })
    
    # Crear el gráfico de línea
    fig = px.line(data, x=etiqueta_x, y=etiqueta_y, title=titulo)
    
    # Agregar valores referenciales en los ejes
    # Los valores referenciales son los mismos que los totales de tickets por mes
    fig.update_xaxes(
        tickvals=meses,  # Valores de los meses en el eje X
        ticktext=meses  # Usamos los mismos valores como etiquetas
    )
    fig.update_yaxes(
        tickvals=totalTicketsMensual,  # Los valores de tickets totales para las marcas en el eje Y
        ticktext=[str(ticket) for ticket in totalTicketsMensual]  # Etiquetas con los valores de tickets
    )
    
    # Mostrar el gráfico
    fig.show()

    img_bytes = BytesIO()
    pio.write_image(fig, img_bytes, format='png')
    img_bytes.seek(0)  # Volver al principio del archivo en memoria

    if img_bytes.getbuffer().nbytes > 0:
        print("La imagen se guardó correctamente en memoria.")
    else:
        print("Hubo un error al guardar la imagen en memoria.")
    
    
    return img_bytes


def generar_tabla_tickets(tickets, nombre_archivo='tickets_table.png'):
    """
    Función para generar una tabla a partir de los datos de los tickets y guardarla como una imagen PNG.
    
    :param tickets: Lista de diccionarios con los datos de los tickets.
    :param nombre_archivo: Nombre del archivo PNG donde se guardará la imagen de la tabla.
    """
    # Crear un DataFrame de pandas a partir de los datos de los tickets
    df = pd.DataFrame(tickets)
    
    # Crear la tabla en matplotlib
    fig, ax = plt.subplots(figsize=(10, 4))  # Tamaño de la imagen
    ax.axis('tight')
    ax.axis('off')

    # Mostrar la tabla en el gráfico
    tabla = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center', colColours=['#f2f2f2']*len(df.columns))

    # Ajustar el estilo
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1.2, 1.2)

    # Guardar la tabla como imagen PNG
    plt.savefig(nombre_archivo, bbox_inches='tight', pad_inches=0.05, dpi=300)
