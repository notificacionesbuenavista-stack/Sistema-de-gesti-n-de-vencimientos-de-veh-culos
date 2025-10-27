import pandas as pd
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json
import os
import io
import sys
import streamlit as st

# ===== CONFIGURACIÓN =====
GOOGLE_SHEET_ID = "1rHnBFkFbfMpxsN95QoI8ojxkIBkaD7WWisnkRwCCCA0"
DIAS_ANTICIPACION = 60  # 2 MESES

# Silenciar prints cuando se usa en web
class SilentOutput:
    def write(self, txt): pass
    def flush(self): pass

def conectar_google_sheets():
    """Conecta con Google Sheets usando Secrets de Streamlit o archivo local"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # INTENTAR USAR SECRETS DE STREAMLIT CLOUD
        try:
            if 'google_sheets' in st.secrets:
                creds_dict = dict(st.secrets["google_sheets"])
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
                client = gspread.authorize(creds)
                sheet = client.open_by_key(GOOGLE_SHEET_ID)
                todas_las_hojas = sheet.worksheets()
                return client, sheet, todas_las_hojas
        except Exception as e:
            pass
        
        # FALLBACK: USAR ARCHIVO LOCAL
        ARCHIVO_CREDENCIALES = "credenciales.json"
        if os.path.exists(ARCHIVO_CREDENCIALES):
            creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=scope)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(GOOGLE_SHEET_ID)
            todas_las_hojas = sheet.worksheets()
            return client, sheet, todas_las_hojas
        else:
            st.error("❌ No se encontraron credenciales. Verifica que el archivo credenciales.json exista o que los Secrets estén configurados en Streamlit Cloud.")
            return None, None, []
            
    except Exception as e:
        st.error(f"❌ Error al conectar con Google Sheets: {str(e)}")
        return None, None, []

def procesar_hoja(worksheet):
    """Procesa una hoja específica y retorna los datos"""
    try:
        all_values = worksheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            return pd.DataFrame()
        
        headers = [
            'No', 'PLACA', 'CHASIS', 'MARCA', 'MODELO', 'CAPACIDAD', 
            'PROPIETARIO', 'CEDULA_NIT', 'CLASE', 'POLIZAS', 'T.O', 
            'MOTOR', 'INTERNO'
        ]
        
        if len(all_values[0]) > len(headers):
            for i in range(len(headers), len(all_values[0])):
                headers.append(f'EXTRA_{i+1}')
        elif len(all_values[0]) < len(headers):
            headers = headers[:len(all_values[0])]
        
        data = []
        for row_num, row in enumerate(all_values[1:], start=2):
            if any(cell != '' for cell in row):
                padded_row = row + [''] * (len(headers) - len(row)) if len(row) < len(headers) else row[:len(headers)]
                data.append(padded_row)
        
        df = pd.DataFrame(data, columns=headers)
        return df
        
    except Exception as e:
        return pd.DataFrame()

def buscar_columnas_relevantes(df, nombre_hoja):
    """Busca automáticamente las columnas importantes en una hoja"""
    columnas_encontradas = {
        'fecha_to': None,
        'fecha_poliza': None,
        'placa': None,
        'chasis': None,
        'modelo': None
    }
    
    for columna in df.columns:
        col_upper = str(columna).strip().upper()
        col_sin_espacios = col_upper.replace(' ', '')
        
        # Buscar columna T.O
        if any(keyword in col_sin_espacios for keyword in ['T.O', 'TO', 'TARJETAOPERACION']):
            if not columnas_encontradas['fecha_to']:
                columnas_encontradas['fecha_to'] = columna
        
        # Buscar columna POLIZAS
        elif any(keyword in col_sin_espacios for keyword in ['POLIZA', 'POLIZAS', 'SEGURO', 'SEGUROS']):
            if not columnas_encontradas['fecha_poliza']:
                columnas_encontradas['fecha_poliza'] = columna
        
        elif any(keyword in col_sin_espacios for keyword in ['PLACA', 'PLACAS', 'PATENTE', 'MATRICULA']):
            if not columnas_encontradas['placa']:
                columnas_encontradas['placa'] = columna
        
        elif any(keyword in col_sin_espacios for keyword in ['CHASIS', 'VIN', 'SERIE', 'NUMEROSERIE']):
            if not columnas_encontradas['chasis']:
                columnas_encontradas['chasis'] = columna
        
        elif any(keyword in col_sin_espacios for keyword in ['MODELO', 'MARCA', 'VEHICULO', 'CARROCERIA']):
            if not columnas_encontradas['modelo']:
                columnas_encontradas['modelo'] = columna
    
    if not columnas_encontradas['placa'] and len(df.columns) > 1:
        columnas_encontradas['placa'] = df.columns[1]
    
    if not columnas_encontradas['chasis'] and len(df.columns) > 2:
        columnas_encontradas['chasis'] = df.columns[2]
    
    if not columnas_encontradas['modelo'] and len(df.columns) > 4:
        columnas_encontradas['modelo'] = df.columns[4]
    
    return columnas_encontradas

def extraer_fecha(valor):
    """Convierte string a fecha manejando múltiples formatos"""
    if pd.isna(valor) or valor in ['', ' ', 'X', 'x', '-', '--', 'N/A']:
        return None
    
    valor_str = str(valor).strip()
    valor_str = valor_str.replace('  ', ' ').replace('\\', '/').replace('|', '/')
    
    formatos = [
        '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y'
    ]
    
    for formato in formatos:
        try:
            fecha = datetime.strptime(valor_str, formato)
            if fecha.year >= 2020 and fecha.year <= 2030:
                return fecha
        except ValueError:
            continue
    
    try:
        fecha = pd.to_datetime(valor_str, errors='coerce')
        if pd.notna(fecha) and fecha.year >= 2020 and fecha.year <= 2030:
            return fecha
    except:
        pass
    
    return None

def verificar_vencimientos_en_hoja_con_dias(df, columnas, nombre_hoja, dias_anticipacion):
    """Encuentra T.O y Pólizas VENCIDOS y por vencer"""
    hoy = datetime.now()
    fecha_limite = hoy + timedelta(days=dias_anticipacion)
    licencias_por_vencer = []
    
    # Verificar T.O
    columna_fecha_to = columnas['fecha_to']
    if columna_fecha_to:
        for index, row in df.iterrows():
            try:
                fecha_to = row[columna_fecha_to]
                fecha_convertida = extraer_fecha(fecha_to)
                
                # INCLUIR TANTO VENCIDOS COMO POR VENCER
                if fecha_convertida:
                    dias_restantes = (fecha_convertida - hoy).days
                    
                    # INCLUIR TODOS LOS VEHÍCULOS VENCIDOS Y LOS QUE ESTÁN DENTRO DEL PERÍODO
                    if fecha_convertida <= fecha_limite:
                        placa = row[columnas['placa']] if columnas['placa'] and pd.notna(row[columnas['placa']]) else f"Veh_{index+2}"
                        chasis = row[columnas['chasis']] if columnas['chasis'] and pd.notna(row[columnas['chasis']]) else "N/A"
                        modelo = row[columnas['modelo']] if columnas['modelo'] and pd.notna(row[columnas['modelo']]) else "N/A"
                        
                        # Determinar estado
                        if dias_restantes < 0:
                            estado = 'VENCIDO'
                        else:
                            estado = 'POR VENCER'
                        
                        licencia_info = {
                            'HOJA': nombre_hoja,
                            'FILA': index + 2,
                            'PLACA': placa,
                            'CHASIS': chasis,
                            'MODELO': modelo,
                            'TIPO_DOCUMENTO': 'T.O',
                            'FECHA_VENCIMIENTO': fecha_convertida.strftime('%d/%m/%Y'),
                            'DIAS_RESTANTES': dias_restantes,
                            'ESTADO': estado,
                            'COLUMNA_FECHA': columna_fecha_to
                        }
                        
                        licencias_por_vencer.append(licencia_info)
                    
            except Exception:
                continue
    
    # Verificar PÓLIZAS
    columna_fecha_poliza = columnas['fecha_poliza']
    if columna_fecha_poliza:
        for index, row in df.iterrows():
            try:
                fecha_poliza = row[columna_fecha_poliza]
                fecha_convertida = extraer_fecha(fecha_poliza)
                
                # INCLUIR TANTO VENCIDOS COMO POR VENCER
                if fecha_convertida:
                    dias_restantes = (fecha_convertida - hoy).days
                    
                    # INCLUIR TODOS LOS VEHÍCULOS VENCIDOS Y LOS QUE ESTÁN DENTRO DEL PERÍODO
                    if fecha_convertida <= fecha_limite:
                        placa = row[columnas['placa']] if columnas['placa'] and pd.notna(row[columnas['placa']]) else f"Veh_{index+2}"
                        chasis = row[columnas['chasis']] if columnas['chasis'] and pd.notna(row[columnas['chasis']]) else "N/A"
                        modelo = row[columnas['modelo']] if columnas['modelo'] and pd.notna(row[columnas['modelo']]) else "N/A"
                        
                        # Determinar estado
                        if dias_restantes < 0:
                            estado = 'VENCIDO'
                        else:
                            estado = 'POR VENCER'
                        
                        licencia_info = {
                            'HOJA': nombre_hoja,
                            'FILA': index + 2,
                            'PLACA': placa,
                            'CHASIS': chasis,
                            'MODELO': modelo,
                            'TIPO_DOCUMENTO': 'PÓLIZA',
                            'FECHA_VENCIMIENTO': fecha_convertida.strftime('%d/%m/%Y'),
                            'DIAS_RESTANTES': dias_restantes,
                            'ESTADO': estado,
                            'COLUMNA_FECHA': columna_fecha_poliza
                        }
                        
                        licencias_por_vencer.append(licencia_info)
                    
            except Exception:
                continue
    
    return licencias_por_vencer

def procesar_todas_las_hojas_con_dias(todas_las_hojas, dias_anticipacion):
    """Procesa todas las hojas con días de anticipación personalizados"""
    todas_las_alertas = []
    resumen_hojas = {}
    
    for worksheet in todas_las_hojas:
        nombre_hoja = worksheet.title
        
        if nombre_hoja in ['DESVINCULADOS']:
            continue
        
        df = procesar_hoja(worksheet)
        if df.empty:
            resumen_hojas[nombre_hoja] = {'total': 0, 'alertas': 0, 'vencidos': 0}
            continue
        
        columnas = buscar_columnas_relevantes(df, nombre_hoja)
        alertas_hoja = verificar_vencimientos_en_hoja_con_dias(df, columnas, nombre_hoja, dias_anticipacion)
        todas_las_alertas.extend(alertas_hoja)
        
        # Contar vencidos
        vencidos_hoja = len([a for a in alertas_hoja if a['ESTADO'] == 'VENCIDO'])
        
        resumen_hojas[nombre_hoja] = {
            'total': len(df),
            'alertas': len(alertas_hoja),
            'vencidos': vencidos_hoja
        }
    
    return todas_las_alertas, resumen_hojas

def generar_reporte_txt(todas_las_alertas, resumen_hojas):
    """Genera contenido de texto para el reporte"""
    if not todas_las_alertas:
        return None
    
    contenido = io.StringIO()
    contenido.write("REPORTE CONSOLIDADO DE VENCIMIENTOS (T.O Y PÓLIZAS) - TODAS LAS EMPRESAS\n")
    contenido.write("=" * 60 + "\n")
    contenido.write(f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    contenido.write(f"Período de alerta: 60 días (2 MESES)\n\n")
    
    contenido.write("RESUMEN POR EMPRESA:\n")
    contenido.write("-" * 40 + "\n")
    
    total_alertas = 0
    total_vencidos = 0
    for hoja, datos in resumen_hojas.items():
        if datos['alertas'] > 0:
            contenido.write(f"{hoja}: {datos['alertas']} alertas ({datos['vencidos']} vencidos) de {datos['total']} vehículos\n")
            total_alertas += datos['alertas']
            total_vencidos += datos['vencidos']
    
    contenido.write(f"\nTOTAL GENERAL: {total_alertas} alertas ({total_vencidos} VENCIDOS)\n\n")
    
    contenido.write("ALERTAS DETALLADAS (NIVELES DE URGENCIA):\n")
    contenido.write("⛔ VENCIDO | 🔴 URGENTE (≤15 días) | 🟠 ALERTA (16-30 días) | 🟢 INFORMATIVO (31-60 días)\n")
    contenido.write("=" * 80 + "\n")
    
    # Ordenar: vencidos primero, luego por días restantes
    alertas_ordenadas = sorted(todas_las_alertas, key=lambda x: (0 if x['ESTADO'] == 'VENCIDO' else 1, x['DIAS_RESTANTES']))
    
    empresa_actual = ""
    for alerta in alertas_ordenadas:
        if alerta['HOJA'] != empresa_actual:
            empresa_actual = alerta['HOJA']
            contenido.write(f"\nEMPRESA: {empresa_actual}\n")
            contenido.write("-" * 40 + "\n")
        
        if alerta['ESTADO'] == 'VENCIDO':
            nivel = "⛔ VENCIDO"
            dias_texto = f"{abs(alerta['DIAS_RESTANTES'])} días vencido"
        elif alerta['DIAS_RESTANTES'] <= 15:
            nivel = "🔴 URGENTE"
            dias_texto = f"{alerta['DIAS_RESTANTES']} días"
        elif alerta['DIAS_RESTANTES'] <= 30:
            nivel = "🟠 ALERTA"
            dias_texto = f"{alerta['DIAS_RESTANTES']} días"
        else:
            nivel = "🟢 INFORMATIVO"
            dias_texto = f"{alerta['DIAS_RESTANTES']} días"
        
        contenido.write(f"{nivel}\n")
        contenido.write(f"Tipo: {alerta['TIPO_DOCUMENTO']}\n")
        contenido.write(f"Placa: {alerta['PLACA']}\n")
        contenido.write(f"Modelo: {alerta['MODELO']}\n")
        contenido.write(f"Vencimiento: {alerta['FECHA_VENCIMIENTO']} ({dias_texto})\n")
        contenido.write(f"Chasis: {alerta['CHASIS']}\n")
        contenido.write(f"Fila: {alerta['FILA']}\n")
        contenido.write("-" * 30 + "\n")
    
    return contenido.getvalue()
