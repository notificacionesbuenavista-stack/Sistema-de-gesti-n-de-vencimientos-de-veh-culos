import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sistema_base import *

def main():
    st.set_page_config(
        page_title="Grupo Buena Vista - Gestión de Vencimientos",
        page_icon="🚛",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ===== DISEÑO ESTILO APPLE PREMIUM MEJORADO =====
    st.markdown("""
    <style>
    /* Importar fuente San Francisco (similar a Apple) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', 'Segoe UI', sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    /* Fondo suave estilo Apple */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
        background-attachment: fixed;
    }
    
    /* SIDEBAR PREMIUM AZUL - CORREGIDO */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%) !important;
        border-right: none !important;
        box-shadow: 4px 0 24px rgba(30, 58, 138, 0.15);
    }
    
    section[data-testid="stSidebar"] > div {
        background: transparent !important;
    }
    
    /* ========== BOTÓN HAMBURGUESA MEJORADO ========== */
    
    /* Botón cuando sidebar está cerrado (visible en área principal) */
    .stApp button[kind="header"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        box-shadow: 0 4px 16px rgba(30, 58, 138, 0.35), 0 2px 6px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
    }
    
    .stApp button[kind="header"]:hover {
        background: linear-gradient(135deg, #2563EB 0%, #60A5FA 100%) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 8px 24px rgba(30, 58, 138, 0.45), 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    .stApp button[kind="header"]:active {
        transform: translateY(0px) scale(1) !important;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.3) !important;
    }
    
    /* Botón cuando sidebar está abierto (dentro del sidebar azul) */
    section[data-testid="stSidebar"] button[kind="header"] {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 1) !important;
        border-radius: 12px !important;
        padding: 10px 12px !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2), 0 2px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
    }
    
    section[data-testid="stSidebar"] button[kind="header"]:hover {
        background: rgba(255, 255, 255, 1) !important;
        transform: translateY(-2px) scale(1.05) !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25), 0 4px 12px rgba(0, 0, 0, 0.15) !important;
        border-color: rgba(255, 255, 255, 1) !important;
    }
    
    section[data-testid="stSidebar"] button[kind="header"]:active {
        transform: translateY(0px) scale(1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Color del ícono del botón hamburguesa - SIEMPRE VISIBLE */
    button[kind="header"] svg {
        color: #FFFFFF !important;
        width: 24px !important;
        height: 24px !important;
        stroke-width: 2.5px !important;
    }
    
    /* En el sidebar, el ícono debe ser oscuro */
    section[data-testid="stSidebar"] button[kind="header"] svg {
        color: #1E3A8A !important;
    }
    
    /* Botones sidebar estilo Apple */
    section[data-testid="stSidebar"] .stButton button {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(20px);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 14px;
        padding: 14px 24px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        width: 100%;
        letter-spacing: 0.3px;
    }
    
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        border-color: rgba(255, 255, 255, 0.5);
    }
    
    section[data-testid="stSidebar"] .stButton button:active {
        transform: translateY(0px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Header premium */
    .main-header {
        text-align: center;
        padding: 32px 40px;
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
        border-radius: 24px;
        margin-bottom: 48px;
        color: white;
        box-shadow: 0 16px 48px rgba(30, 58, 138, 0.25), 0 0 1px rgba(30, 58, 138, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 30% 50%, rgba(255,255,255,0.1) 0%, transparent 60%);
        pointer-events: none;
    }
    
    .header-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 28px;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    
    .logo-header {
        border-radius: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.5);
        background: white;
        padding: 10px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .logo-header:hover {
        transform: scale(1.08) translateY(-4px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        border-color: rgba(255, 255, 255, 0.8);
    }
    
    .header-text {
        flex: 1;
        max-width: 600px;
    }
    
    .main-header h1 {
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(135deg, #FFFFFF 0%, #E0F2FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .main-header p {
        font-size: 1.35rem;
        font-weight: 400;
        opacity: 0.95;
        margin: 12px 0 0 0;
        letter-spacing: 0.3px;
    }
    
    /* Sidebar content */
    .sidebar-content {
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 28px;
        margin: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    }
    
    .sidebar-title {
        font-size: 1.7rem;
        font-weight: 700;
        margin-bottom: 28px;
        text-align: center;
        color: white;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .info-text {
        color: rgba(255, 255, 255, 0.85) !important;
        font-size: 0.9rem !important;
        font-weight: 400 !important;
        background: transparent !important;
        padding: 0 !important;
        margin: 12px 0 24px 0 !important;
        text-align: center !important;
        line-height: 1.5 !important;
        letter-spacing: 0.2px;
    }
    
    /* Slider estilo Apple */
    section[data-testid="stSidebar"] .stSlider > div > div > div {
        background: linear-gradient(90deg, rgba(255,255,255,0.4), rgba(255,255,255,0.6)) !important;
        height: 6px !important;
        border-radius: 10px !important;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
    }
    
    section[data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: white !important;
        border: none !important;
        height: 22px !important;
        width: 22px !important;
        border-radius: 50% !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.25), 0 1px 3px rgba(0,0,0,0.2) !important;
        transition: all 0.2s ease !important;
    }
    
    section[data-testid="stSidebar"] .stSlider > div > div > div > div:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    }
    
    section[data-testid="stSidebar"] .stSlider label {
        color: white !important;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
    }
    
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: white !important;
    }
    
    .sidebar-separator {
        height: 1px;
        background: rgba(255, 255, 255, 0.25);
        margin: 28px 0;
        border: none;
    }
    
    /* Tarjetas de métricas estilo Apple */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 24px;
        padding: 32px 28px;
        border: 1px solid rgba(226, 232, 240, 0.8);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 48px rgba(30, 58, 138, 0.15), 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: #3B82F6;
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin: 8px 0;
        line-height: 1;
        letter-spacing: -1px;
    }
    
    .metric-label {
        font-size: 0.95rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }
    
    /* Gráficos premium - ELIMINAR CONTENEDORES BLANCOS */
    .chart-container {
        background: transparent !important;
        border-radius: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0 !important;
    }
    
    .chart-container:hover {
        box-shadow: none !important;
    }
    
    /* Sección de tabla mejorada - ESTILO APPLE PREMIUM */
    .table-section {
        background: white;
        border-radius: 24px;
        padding: 36px;
        margin: 32px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .table-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        padding-bottom: 20px;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .table-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .table-count {
        font-size: 1rem;
        font-weight: 600;
        color: #64748B;
        background: #f1f5f9;
        padding: 8px 16px;
        border-radius: 12px;
    }
    
    /* Tabla con estilo APPLE PREMIUM - MEJORADA CON PUNTOS DE COLOR */
    .dataframe {
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif !important;
    }
    
    .dataframe thead tr {
        background: linear-gradient(135deg, #1E3A8A, #2563EB) !important;
    }
    
    .dataframe thead th {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 16px 20px !important;
        border: none !important;
        letter-spacing: 0.5px;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        position: relative;
    }
    
    .dataframe thead th:hover {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    .dataframe thead th:active {
        background: rgba(255, 255, 255, 0.2) !important;
    }
    
    .dataframe tbody td {
        padding: 16px 20px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        font-size: 0.95rem;
        color: #334155;
        transition: all 0.2s ease;
        position: relative;
    }
    
    .dataframe tbody tr {
        transition: all 0.2s ease !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f8fafc !important;
        transform: translateX(4px);
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #fafbfc !important;
    }
    
    .dataframe tbody tr:nth-child(even):hover {
        background-color: #f1f5f9 !important;
    }
    
    /* Indicador de ordenamiento en headers */
    .dataframe thead th[aria-sort]::after {
        content: "↕";
        margin-left: 8px;
        opacity: 0.6;
        font-size: 0.8em;
    }
    
    .dataframe thead th[aria-sort="ascending"]::after {
        content: "↑";
        opacity: 1;
    }
    
    .dataframe thead th[aria-sort="descending"]::after {
        content: "↓";
        opacity: 1;
    }
    
    /* Botones de descarga estilo Apple */
    .stDownloadButton button {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(30, 58, 138, 0.25) !important;
        width: 100% !important;
        letter-spacing: 0.3px !important;
    }
    
    .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(30, 58, 138, 0.35) !important;
        background: linear-gradient(135deg, #1E3A8A, #2563EB) !important;
    }
    
    .stDownloadButton button:active {
        transform: translateY(0px) !important;
    }
    
    /* Animaciones suaves */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Estado de éxito premium */
    .success-state {
        text-align: center;
        padding: 64px 48px;
        background: linear-gradient(135deg, #10B981, #059669);
        border-radius: 24px;
        color: white;
        margin: 32px 0;
        box-shadow: 0 16px 48px rgba(5, 150, 105, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .success-state::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.1) 0%, transparent 70%);
    }
    
    .success-state h2 {
        position: relative;
        z-index: 1;
        font-weight: 700;
        font-size: 2.2rem;
    }
    
    .success-state p {
        position: relative;
        z-index: 1;
        font-size: 1.3rem;
        opacity: 0.95;
    }
    
    .sidebar-text {
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.95rem;
        letter-spacing: 0.3px;
    }
    
    /* Títulos de sección */
    h3 {
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        margin: 32px 0 20px 0 !important;
        letter-spacing: -0.5px !important;
    }
    
    /* Pantalla de bienvenida */
    .welcome-screen {
        text-align: center;
        padding: 96px 48px;
        background: white;
        border-radius: 24px;
        border: 2px dashed #e2e8f0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04);
        animation: fadeInUp 0.6s ease;
    }
    
    .welcome-screen h2 {
        color: #64748B;
        font-weight: 600;
        margin-bottom: 20px;
        font-size: 2rem;
    }
    
    .welcome-screen p {
        color: #94a3b8;
        font-size: 1.2rem;
        line-height: 1.8;
    }
    
    .welcome-screen .highlight {
        color: #1E3A8A;
        font-weight: 600;
    }
    
    .welcome-info {
        margin-top: 40px;
        color: #cbd5e1;
        font-size: 0.95rem;
    }
    
    /* Eliminar el selectbox de ordenamiento */
    .element-container:has(.stSelectbox) {
        display: none !important;
    }
    
    /* Estilos para los puntos de color en la tabla */
    .vencido-dot::before {
        content: '⛔ ';
        margin-right: 8px;
    }
    
    .urgente-dot::before {
        content: '🔴 ';
        margin-right: 8px;
    }
    
    .alerta-dot::before {
        content: '🟠 ';
        margin-right: 8px;
    }
    
    .informativo-dot::before {
        content: '🟢 ';
        margin-right: 8px;
    }
    
    .lejano-dot::before {
        content: '🔵 ';
        margin-right: 8px;
    }
    
    /* Estilos específicos para estado VENCIDO */
    .estado-vencido {
        color: #DC2626 !important;
        font-weight: 700 !important;
    }
    
    .estado-por-vencer {
        color: #059669 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ===== HEADER PRINCIPAL =====
    logo_url = "https://i.ibb.co/r2sCDV3G/Captura-de-pantalla-2025-10-07-143722.png"
    
    st.markdown(f"""
    <div class="main-header">
        <div class="header-content">
            <img src="{logo_url}" class="logo-header" width="120" alt="Logo Grupo Buena Vista">
            <div class="header-text">
                <h1>🚛 Grupo Buena Vista</h1>
                <p>Gestión Inteligente de Vencimientos (T.O y Pólizas)</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <div class="sidebar-title">⚙️ Configuración</div>
        """, unsafe_allow_html=True)
        
        dias_alertas = st.slider(
            "**Días de anticipación**",
            min_value=30,
            max_value=90,
            value=60,
            help="Período para alertas de vencimiento"
        )
        
        st.markdown("""
        <div class="info-text">
            Establece el período de anticipación para las alertas
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr class="sidebar-separator">', unsafe_allow_html=True)
        
        if st.button("**🔄 Actualizar Datos**", use_container_width=True, type="primary"):
            st.session_state.actualizar = True
        
        st.markdown("""
        <div class="info-text">
            Sincroniza con Google Sheets
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(255,255,255,0.25);'>
            <p class="sidebar-text">Sistema de Gestión<br>Grupo Buena Vista 2025</p>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ===== CONTENIDO PRINCIPAL =====
    if 'actualizar' in st.session_state and st.session_state.actualizar:
        with st.spinner("🔄 Conectando con Google Sheets..."):
            client, sheet, todas_las_hojas = conectar_google_sheets()
            if todas_las_hojas:
                todas_las_alertas, resumen_hojas = procesar_todas_las_hojas_con_dias(todas_las_hojas, dias_alertas)
                mostrar_interfaz_moderna(todas_las_alertas, resumen_hojas, dias_alertas)
            else:
                st.error("❌ Error al conectar con Google Sheets")
        st.session_state.actualizar = False
    else:
        # PANTALLA DE BIENVENIDA
        st.markdown("""
        <div class="welcome-screen">
            <h2>👋 Bienvenido al Sistema</h2>
            <p>Presiona <span class="highlight">"Actualizar Datos"</span> en el panel lateral<br>para comenzar a gestionar los vencimientos</p>
            <div class="welcome-info">
                <p>📊 Monitoreo de T.O y Pólizas sincronizado con Google Sheets</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def mostrar_interfaz_moderna(todas_las_alertas, resumen_hojas, dias_alertas):
    """Muestra los resultados con diseño premium estilo Apple"""
    
    # ===== MÉTRICAS PRINCIPALES =====
    st.markdown("### 📊 Resumen General")
    
    total_empresas = len(resumen_hojas)
    total_vehiculos = sum([d['total'] for d in resumen_hojas.values()])
    total_alertas = len(todas_las_alertas)
    
    # Contar alertas por tipo y estado
    alertas_to = len([a for a in todas_las_alertas if a['TIPO_DOCUMENTO'] == 'T.O'])
    alertas_poliza = len([a for a in todas_las_alertas if a['TIPO_DOCUMENTO'] == 'PÓLIZA'])
    total_vencidos = len([a for a in todas_las_alertas if a['ESTADO'] == 'VENCIDO'])
    total_por_vencer = len([a for a in todas_las_alertas if a['ESTADO'] == 'POR VENCER'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Empresas</div>
            <div class="metric-value">{total_empresas}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vehículos</div>
            <div class="metric-value">{total_vehiculos}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Alertas</div>
            <div class="metric-value">{total_alertas}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Vencidos</div>
            <div class="metric-value" style="color: #DC2626;">{total_vencidos}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Por Vencer</div>
            <div class="metric-value" style="color: #059669;">{total_por_vencer}</div>
        </div>
        """, unsafe_allow_html=True)
    
    if not todas_las_alertas:
        st.markdown("""
        <div class="success-state">
            <h2>🎉 ¡Excelente! Todo al día</h2>
            <p>No hay vencimientos en el período seleccionado</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # ===== GRÁFICOS =====
    st.markdown("### 📈 Visualizaciones")
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico por tipo de documento
        fig1 = px.bar(
            x=['T.O', 'PÓLIZA'],
            y=[alertas_to, alertas_poliza],
            title="📋 Alertas por Tipo de Documento",
            labels={'x': 'Tipo', 'y': 'Número de Alertas'},
            color=[alertas_to, alertas_poliza],
            color_continuous_scale='blues'
        )
        fig1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1E293B", family="Inter"),
            title_font=dict(size=20, weight=600),
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_graf2:
        # Distribución por estado (VENCIDO vs POR VENCER)
        fig2 = px.pie(
            values=[total_vencidos, total_por_vencer],
            names=['⛔ VENCIDOS', '🟢 POR VENCER'],
            title="🎯 Estado de Documentos",
            color_discrete_sequence=['#DC2626', '#059669']
        )
        fig2.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#1E293B", family="Inter"),
            title_font=dict(size=20, weight=600),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # ===== TABLA CON DISEÑO APPLE PREMIUM =====
    st.markdown(f"""
    <div style="margin: 32px 0 24px 0;">
        <div class="table-header">
            <div class="table-title">
                📋 Alertas Detalladas
                <span class="table-count">{len(todas_las_alertas)} registros</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear DataFrame para mostrar
    df_alertas = pd.DataFrame(todas_las_alertas)
    
    # ELIMINAR COLUMNAS INNECESARIAS
    columnas_a_eliminar = ['COLUMNA_FECHA', 'FILA']
    columnas_disponibles = df_alertas.columns.tolist()
    
    for columna in columnas_a_eliminar:
        if columna in columnas_disponibles:
            df_alertas = df_alertas.drop(columns=[columna])
    
    # Reordenar columnas para mejor visualización
    columnas_ordenadas = ['HOJA', 'TIPO_DOCUMENTO', 'PLACA', 'CHASIS', 'MODELO', 'FECHA_VENCIMIENTO', 'DIAS_RESTANTES', 'ESTADO']
    columnas_disponibles_ordenadas = [col for col in columnas_ordenadas if col in df_alertas.columns]
    df_alertas = df_alertas[columnas_disponibles_ordenadas]
    
    # Función para determinar el emoji/color según el estado y días restantes
    def get_alert_emoji(dias, estado):
        if estado == 'VENCIDO':
            return '⛔'
        elif dias <= 15:
            return '🔴'
        elif dias <= 30:
            return '🟠'
        elif dias <= 60:
            return '🟢'
        else:
            return '🔵'

    # Aplicar emojis a la columna DIAS_RESTANTES
    if 'DIAS_RESTANTES' in df_alertas.columns and 'ESTADO' in df_alertas.columns:
        df_alertas['DIAS_RESTANTES'] = df_alertas.apply(
            lambda x: f"{get_alert_emoji(x['DIAS_RESTANTES'], x['ESTADO'])} {int(x['DIAS_RESTANTES'])} días", 
            axis=1
        )
    
    # Función para aplicar colores según estado y urgencia
    def color_filas(val):
        if '⛔' in str(val):
            return 'color: #DC2626; font-weight: 700;'
        elif '🔴' in str(val):
            return 'color: #DC2626; font-weight: 600;'
        elif '🟠' in str(val):
            return 'color: #D97706; font-weight: 600;'
        elif '🟢' in str(val):
            return 'color: #059669; font-weight: 500;'
        else:
            return 'color: #3B82F6; font-weight: 500;'
    
    # Aplicar estilos a la tabla
    if 'DIAS_RESTANTES' in df_alertas.columns:
        styled_df = df_alertas.style.applymap(color_filas, subset=['DIAS_RESTANTES'])
        
        # También aplicar estilo a la columna ESTADO si existe
        if 'ESTADO' in df_alertas.columns:
            def color_estado(val):
                if val == 'VENCIDO':
                    return 'color: #DC2626; font-weight: 700;'
                else:
                    return 'color: #059669; font-weight: 600;'
            
            styled_df = styled_df.applymap(color_estado, subset=['ESTADO'])
    else:
        styled_df = df_alertas.style
    
    # Mostrar tabla
    st.markdown(
        styled_df.to_html(escape=False, index=False), 
        unsafe_allow_html=True
    )
    
    # Botón de descarga
    csv = pd.DataFrame(todas_las_alertas).to_csv(index=False)
    st.download_button(
        label="**📥 Descargar CSV**",
        data=csv,
        file_name=f"alertas_vencimientos_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

if __name__ == "__main__":
    main()