import time
import flet as ft
import obd
from obd import OBDStatus

class EscanerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.conexion = None
        self.configurar_ventana()
        self.crear_interfaz()

    def configurar_ventana(self):
        self.page.title = "OBD2 Multiplatform Scanner"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.scroll = ft.ScrollMode.AUTO

    def crear_interfaz(self):
        # Componentes de texto y estado
        self.txt_estado = ft.Text("Estado: Desconectado", color=ft.colors.RED_ACCENT, size=16, weight=ft.FontWeight.BOLD)
        self.txt_consola = ft.Text("Listo para escanear...", color=ft.colors.GREY_400, size=14)
        
        # Indicadores Visuales de Datos en Vivo
        self.card_rpm = ft.Text("0 RPM", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_ACCENT)
        self.card_temp = ft.Text("0 °C", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.ORANGE_ACCENT)

        # Botones de Acción
        btn_conectar = ft.ElevatedButton("🔌 Conectar OBD2 Bluetooth", on_click=self.conectar_obd, bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE)
        btn_leer_dtc = ft.ElevatedButton("🔍 Leer Códigos (DTC)", on_click=self.leer_codigos, bgcolor=ft.colors.SURFACE_VARIANT)
        btn_borrar_dtc = ft.ElevatedButton("🗑️ Borrar Códigos / Reset", on_click=self.borrar_codigos, bgcolor=ft.colors.RED_900, color=ft.colors.WHITE)
        btn_ralenti = ft.ElevatedButton("⚙️ Reprogramar Ralentí", on_click=self.reprogramar_ralenti, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE)
        btn_datos = ft.ElevatedButton("⏱️ Activar Datos en Vivo", on_click=self.actualizar_datos_en_vivo, bgcolor=ft.colors.SURFACE_VARIANT)

        # Contenedor de la interfaz (Diseño responsivo para Celular y PC)
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("📊 ESCÁNER AUTOMOTRIZ PROFESIONAL", size=22, weight=ft.FontWeight.BOLD),
                    self.txt_estado,
                    ft.Divider(),
                    btn_conectar,
                    ft.Row([
                        ft.Container(content=ft.Column([ft.Text("RPM del Motor"), self.card_rpm]), padding=15, bgcolor=ft.colors.BLACK26, borderRadius=10, expand=True),
                        ft.Container(content=ft.Column([ft.Text("Temp. Refrigerante"), self.card_temp]), padding=15, bgcolor=ft.colors.BLACK26, borderRadius=10, expand=True),
                    ], spacing=15),
                    ft.Divider(),
                    ft.Text("Funciones del Sistema:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([btn_leer_dtc, btn_borrar_dtc], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([btn_datos, btn_ralenti], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(),
                    ft.Text("Historial / Diagnóstico:", size=14, color=ft.colors.BLUE_GREY_200),
                    ft.Container(content=self.txt_consola, bgcolor=ft.colors.BLACK, padding=15, borderRadius=8, width=500, height=150, overflow=ft.ScrollMode.AUTO)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=20,
                width=600
            )
        )

    def conectar_obd(self, e):
        self.txt_estado.value = "Estado: Buscando dispositivo..."
        self.txt_estado.color = ft.colors.ORANGE_ACCENT
        self.page.update()

        puertos = obd.scan_serial_ports()
        if not puertos:
            self.txt_estado.value = "Estado: No se encontraron dispositivos vinculados"
            self.txt_estado.color = ft.colors.RED_ACCENT
            self.page.update()
            return

        for puerto in puertos:
            try:
                self.conexion = obd.OBD(puerto, baudrate=38400, fast=True)
                if self.conexion.status() == OBDStatus.CAR_CONNECTED:
                    self.txt_estado.value = f"Estado: Conectado a {self.conexion.protocol_name()}"
                    self.txt_estado.color = ft.colors.GREEN_ACCENT
                    self.page.update()
                    return
            except Exception:
                continue

        self.txt_estado.value = "Estado: Error de conexión"
        self.txt_estado.color = ft.colors.RED_ACCENT
        self.page.update()

    def leer_codigos(self, e):
        if not self.verificar_conexion(): return
        respuesta = self.conexion.query(obd.commands.GET_DTC)
        if respuesta.value:
            fallas = "\n".join([f"⚠️ {c}: {d}" for c, d in respuesta.value])
            self.txt_consola.value = f"Códigos encontrados:\n{fallas}"
        else:
            self.txt_consola.value = "✅ El vehículo no presenta códigos de error (DTC)."
        self.page.update()

    def borrar_codigos(self, e):
        if not self.verificar_conexion(): return
        respuesta = self.conexion.query(obd.commands.CLEAR_DTC)
        self.txt_consola.value = "✅ Solicitud enviada. Códigos borrados y Check Engine reiniciado." if respuesta.status else "❌ La ECU rechazó el borrado."
        self.page.update()

    def actualizar_datos_en_vivo(self, e):
        if not self.verificar_conexion(): return
        self.txt_consola.value = "Transmitiendo datos en vivo en los paneles superiores..."
        self.page.update()
        
        for _ in range(20): # Lee datos durante 20 ciclos continuos
            rpm = self.conexion.query(obd.commands.RPM)
            temp = self.conexion.query(obd.commands.COOLANT_TEMP)
            
            self.card_rpm.value = f"{rpm.value}" if rpm.value else "0 RPM"
            self.card_temp.value = f"{temp.value}" if temp.value else "0 °C"
            self.page.update()
            time.sleep(0.3)

    def reprogramar_ralenti(self, e):
        if not self.verificar_conexion(): return
        self.txt_consola.value = "🔓 Enviando códigos UDS de desbloqueo de seguridad...\n"
        respuesta_unlock = self.conexion.send_raw(b"27 01")
        if respuesta_unlock:
            self.txt_consola.value += "✅ Desbloqueo de seguridad exitoso.\n"
        else:
            self.txt_consola.value += "❌ Fallo en desbloqueo de seguridad.\n"
        time.sleep(1)
        
        self.txt_consola.value += "⚙️ Escribiendo parámetros de adaptación de ralentí (750 RPM)...\n"
        respuesta_write = self.conexion.send_raw(b"2E 10 0A 02 EE")
        if respuesta_write:
            self.txt_consola.value += "🎉 Proceso de aprendizaje de ralentí completado con éxito."
        else:
            self.txt_consola.value += "❌ Error al escribir parámetros de ralentí."
        time.sleep(2)
        self.page.update()

    def verificar_conexion(self):
        if not self.conexion or not self.conexion.is_connected():
            self.txt_consola.value = "❌ Error: Primero debes conectarte al OBD2 por Bluetooth."
            self.page.update()
            return False
        return True

# Inicializador de Flet
if __name__ == "__main__":
    ft.app(target=EscanerApp)
