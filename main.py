#!/usr/bin/env python3
"""
Escáner Automotriz Profesional OBD2
Aplicación multiplataforma para diagnosticar vehículos mediante OBD2 Bluetooth
"""

import time
import flet as ft
import threading
from obd import OBDStatus

# Importar la clase principal
from EscanerApp import EscanerApp

def main():
    """Función principal que inicia la aplicación"""
    def app(page: ft.Page):
        # Configurar tema global
        page.theme_mode = ft.ThemeMode.DARK
        
        # Inicializar la aplicación
        app_instance = EscanerApp(page)
        
    # Ejecutar la aplicación Flet
    ft.app(target=app)

if __name__ == "__main__":
    main()
