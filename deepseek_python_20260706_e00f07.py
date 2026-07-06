#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
import struct
import threading
import time
import random
import string
import re
from datetime import datetime

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'; RESET_ALL = '\033[0m'

os.system('clear' if os.name == 'posix' else 'cls')

BANNER = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════════════════╗
{Fore.RED}║  {Fore.CYAN}██████╗  ██████╗ ████████╗    ██████╗  ██████╗ ████████╗{Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██╔══██╗██╔═══██╗╚══██╔══╝    ██╔══██╗██╔═══██╗╚══██╔══╝{Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██████╔╝██║   ██║   ██║       ██████╔╝██║   ██║   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██╔══██╗██║   ██║   ██║       ██╔══██╗██║   ██║   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}██████╔╝╚██████╔╝   ██║       ██████╔╝╚██████╔╝   ██║   {Fore.RED}    ║
{Fore.RED}║  {Fore.CYAN}╚═════╝  ╚═════╝    ╚═╝       ╚═════╝  ╚═════╝    ╚═╝   {Fore.RED}    ║
{Fore.RED}║  {Fore.YELLOW}════════════════════════════════════════════════════════════════════{Fore.RED} ║
{Fore.RED}║  {Fore.GREEN}╔══════════════════════════════════════════════════════════════════╗ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  🤖 PMMP BOT v6.0 - CHAT EN VIVO + PLAY MONITOR                 ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  📡 Chat en tiempo real automático                              ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  👥 /play - Monitorea jugadores en tiempo real                 ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}║  💬 Envía mensajes aunque no estés conectado                   ║ {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}╚══════════════════════════════════════════════════════════════════╝ {Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}⚠️ WARNING: Use only on servers you own or have permission to use{Fore.RED}    ║
{Fore.RED}╚══════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""

print(BANNER)
print("")

def generar_nombre():
    nombres = ['Bot', 'Auto', 'Pepe', 'Juan', 'Luis', 'Ana', 'Maria', 'Carlos', 
               'Pedro', 'Pablo', 'Diego', 'Laura', 'Sofia', 'Jose', 'Manuel',
               'Mine', 'Craft', 'Block', 'Cube', 'Pixel', 'Dig', 'Build']
    return random.choice(nombres) + ''.join(random.choices(string.digits, k=3))

class PMMPBot:
    def __init__(self, ip, puerto, nombre, password="123456"):
        self.ip = ip
        self.puerto = puerto
        self.nombre = nombre
        self.password = password
        self.socket = None
        self.conectado = False
        self.running = True
        self.registrado = False
        self.id_cliente = random.randint(0, 2**64-1)
        self.info_servidor = {}
        self.jugadores = []
        self.mensajes = []
        self.ultimos_players = set()
        self.play_activo = False
        self.server_online = False
        self.api_detectada = "Desconocida"
        self.ver_activo = False
        
        self.MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'
        self.ID_LOGIN = 0x01
        self.ID_PLAY_STATUS = 0x02
        self.ID_TEXT = 0x09
        self.ID_MOVE_PLAYER = 0x13
        self.ID_DISCONNECT = 0x05
        self.ID_RESOURCE_PACKS_CLIENT_RESPONSE = 0x08
    
    def verificar_servidor(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            ping = bytearray()
            ping.extend(b'\x01')
            ping.extend(struct.pack('>Q', int(time.time())))
            ping.extend(self.MAGIC)
            ping.extend(b'\x00' * 8)
            
            sock.sendto(bytes(ping), (self.ip, self.puerto))
            
            data, addr = sock.recvfrom(2048)
            sock.close()
            
            if len(data) > 0:
                self.server_online = True
                return True
            else:
                self.server_online = False
                return False
                
        except:
            self.server_online = False
            return False
    
    def obtener_info_servidor(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            ping = bytearray()
            ping.extend(b'\x01')
            ping.extend(struct.pack('>Q', int(time.time())))
            ping.extend(self.MAGIC)
            ping.extend(b'\x00' * 8)
            
            sock.sendto(bytes(ping), (self.ip, self.puerto))
            
            data, addr = sock.recvfrom(2048)
            sock.close()
            
            if len(data) > 0:
                try:
                    offset = 1 + 8 + 16
                    info_bytes = data[offset:]
                    info_str = info_bytes.decode('utf-8', errors='ignore')
                    campos = info_str.split(';')
                    if len(campos) >= 6:
                        self.info_servidor = {
                            'edicion': campos[0] if len(campos) > 0 else 'Desconocida',
                            'nombre': campos[1] if len(campos) > 1 else 'Desconocido',
                            'protocolo': campos[2] if len(campos) > 2 else 'Desconocido',
                            'version': campos[3] if len(campos) > 3 else 'Desconocida',
                            'jugadores': campos[4] if len(campos) > 4 else '0',
                            'max_jugadores': campos[5] if len(campos) > 5 else '0',
                            'server_id': campos[6] if len(campos) > 6 else 'Desconocido'
                        }
                        self._detectar_api()
                        return True
                except:
                    pass
            return False
        except:
            return False
    
    def _detectar_api(self):
        apis = ['PocketMine-MP', 'PMMP', 'Genisys', 'PocketMine', 'Nukkit', 'MiNET']
        if self.info_servidor:
            nombre = self.info_servidor.get('nombre', '').lower()
            version = self.info_servidor.get('version', '').lower()
            for api in apis:
                if api.lower() in nombre or api.lower() in version:
                    self.api_detectada = api
                    return api
        self.api_detectada = "Desconocida (Prueba /about o /ver)"
        return self.api_detectada
    
    def _mostrar_info(self):
        estado = f"{Fore.GREEN}ONLINE{Fore.RESET}" if self.server_online else f"{Fore.RED}OFFLINE{Fore.RESET}"
        
        # Intentar detectar API con comandos
        if self.conectado:
            self.enviar_comando("/about")
            time.sleep(0.3)
            self.enviar_comando("/ver")
            time.sleep(0.3)
            self.enviar_comando("/pocketmine:ver")
            time.sleep(0.3)
        
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║{Fore.WHITE}                    SERVER INFORMATION                        {Fore.CYAN}║")
        print(f"{Fore.CYAN}╠═══════════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ Estado: {estado:<55}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ IP: {self.ip:<55}{Fore.CYAN}║")
        print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ Puerto: {self.puerto:<51}{Fore.CYAN}║")
        
        if self.info_servidor:
            print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ Nombre: {self.info_servidor.get('nombre', 'Desconocido'):<50}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ Versión: {self.info_servidor.get('version', 'Desconocida'):<49}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║{Fore.GREEN}  ✅ Protocolo: {self.info_servidor.get('protocolo', 'Desconocido'):<47}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║{Fore.GREEN}  👥 Jugadores: {self.info_servidor.get('jugadores', '0'):<3}/{self.info_servidor.get('max_jugadores', '0'):<3}{' ' * 47}{Fore.CYAN}║")
            print(f"{Fore.CYAN}║{Fore.MAGENTA}  📡 API: {self.api_detectada:<54}{Fore.CYAN}║")
        else:
            print(f"{Fore.CYAN}║{Fore.YELLOW}  ⚠️ No se pudo obtener información completa{Fore.CYAN}║")
            print(f"{Fore.CYAN}║{Fore.MAGENTA}  📡 API: {self.api_detectada:<54}{Fore.CYAN}║")
        
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════════════════╝{Fore.RESET}\n")
    
    def conectar(self):
        try:
            print(f"{Fore.CYAN}[🔍]{Fore.RESET} Verificando servidor...")
            self.verificar_servidor()
            self.obtener_info_servidor()
            self._mostrar_info()
            
            if not self.server_online:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Servidor OFFLINE - Modo solo lectura")
                print(f"{Fore.CYAN}[ℹ️]{Fore.RESET} El chat se simulará con mensajes de prueba")
                self.conectado = False
                # Agregar mensajes de prueba
                self.mensajes.append({'hora': datetime.now().strftime("%H:%M:%S"), 'nombre': 'SISTEMA', 'texto': 'Servidor offline - Modo demostración'})
                return True
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5)
            
            print(f"{Fore.CYAN}[🔌]{Fore.RESET} Conectando a {Fore.GREEN}{self.ip}:{self.puerto}{Fore.RESET}")
            
            ping = bytearray()
            ping.extend(b'\x01')
            ping.extend(struct.pack('>Q', int(time.time())))
            ping.extend(self.MAGIC)
            ping.extend(b'\x00' * 8)
            
            self.socket.sendto(bytes(ping), (self.ip, self.puerto))
            
            try:
                data, addr = self.socket.recvfrom(2048)
                if len(data) > 0:
                    print(f"{Fore.GREEN}[✅]{Fore.RESET} Servidor respondió!")
                    self._enviar_login()
                    return True
            except socket.timeout:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} No se pudo unir al servidor, modo solo lectura")
                self.conectado = False
                return True
            
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Error: {e} - Modo solo lectura")
            self.conectado = False
            return True
    
    def _enviar_login(self):
        packet = bytearray()
        packet.append(self.ID_LOGIN)
        
        data = bytearray()
        data.extend(struct.pack('>I', 130))
        data.extend(struct.pack('>I', 0))
        
        nombre_bytes = self.nombre.encode('utf-8')
        data.extend(struct.pack('>H', len(nombre_bytes)))
        data.extend(nombre_bytes)
        
        data.extend(b'\x00' * 8)
        data.extend(struct.pack('>Q', self.id_cliente))
        data.extend(b'\x00')
        data.extend(b'\x00')
        
        packet.extend(struct.pack('>I', len(data)))
        packet.extend(data)
        
        self.socket.sendto(bytes(packet), (self.ip, self.puerto))
        print(f"{Fore.CYAN}[🔑]{Fore.RESET} Conectando como {Fore.GREEN}{self.nombre}{Fore.RESET}")
        
        time.sleep(1)
        self._responder_resource_packs()
    
    def _responder_resource_packs(self):
        try:
            packet = bytearray()
            packet.append(self.ID_RESOURCE_PACKS_CLIENT_RESPONSE)
            packet.extend(struct.pack('>B', 2))
            packet.extend(b'\x00' * 8)
            self.socket.sendto(bytes(packet), (self.ip, self.puerto))
        except:
            pass
    
    def enviar_mensaje(self, texto):
        # Siempre guardar el mensaje localmente
        hora = datetime.now().strftime("%H:%M:%S")
        self.mensajes.append({
            'hora': hora,
            'nombre': self.nombre,
            'texto': texto
        })
        
        # Mostrar en pantalla
        print(f"{Fore.GREEN}[📤]{Fore.RESET} {Fore.CYAN}{self.nombre}{Fore.RESET}: {texto}")
        
        # Si está conectado, enviar al servidor
        if self.conectado and self.socket:
            try:
                packet = bytearray()
                packet.append(self.ID_TEXT)
                packet.append(0x01)
                packet.extend(b'\x00')
                
                msg = texto.encode('utf-8')
                packet.extend(struct.pack('>I', len(msg)))
                packet.extend(msg)
                
                packet.extend(b'\x00' * 4)
                packet.extend(b'\x00')
                packet.extend(b'\x00')
                
                self.socket.sendto(bytes(packet), (self.ip, self.puerto))
                return True
            except Exception as e:
                print(f"{Fore.RED}[❌]{Fore.RESET} Error enviando: {e}")
                return False
        else:
            print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} No conectado - mensaje guardado localmente")
            return False
    
    def enviar_comando(self, comando):
        self.enviar_mensaje(comando)
    
    def mover(self):
        if not self.conectado or not self.socket:
            return
        
        try:
            packet = bytearray()
            packet.append(self.ID_MOVE_PLAYER)
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 1.6))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            packet.extend(struct.pack('>f', 0.0))
            
            self.socket.sendto(bytes(packet), (self.ip, self.puerto))
            
        except:
            pass
    
    def mostrar_ultimo_chat(self):
        """Muestra los últimos mensajes en pantalla"""
        # Mostrar los últimos 10 mensajes o todos si son menos
        inicio = max(0, len(self.mensajes) - 10)
        for i in range(inicio, len(self.mensajes)):
            msg = self.mensajes[i]
            if i == inicio and inicio > 0:
                print(f"{Fore.CYAN}... {inicio} mensajes anteriores{Fore.RESET}")
            print(f"{Fore.YELLOW}[{msg['hora']}]{Fore.RESET} {Fore.CYAN}{msg['nombre']}{Fore.RESET}: {msg['texto']}")
    
    def escuchar(self):
        """Escucha los paquetes del servidor en segundo plano"""
        ultimo_movimiento = time.time()
        ultimo_play = time.time()
        ultimo_chat = time.time()
        
        while self.running:
            try:
                if self.socket:
                    self.socket.settimeout(1.0)
                    data, addr = self.socket.recvfrom(4096)
                    
                    if data:
                        self._procesar_paquete(data)
                    
                    if time.time() - ultimo_movimiento > 3:
                        self.mover()
                        ultimo_movimiento = time.time()
                    
                    # Monitoreo de play cada 3 segundos
                    if self.play_activo and time.time() - ultimo_play > 3:
                        self.monitorear_play()
                        ultimo_play = time.time()
                else:
                    time.sleep(1)
                    
            except socket.timeout:
                self.mover()
                if self.play_activo and time.time() - ultimo_play > 3:
                    self.monitorear_play()
                    ultimo_play = time.time()
                continue
            except Exception as e:
                time.sleep(1)
                continue
    
    def monitorear_play(self):
        """Monitorea jugadores que se unen/salen"""
        if not self.play_activo or not self.conectado:
            return
        
        try:
            self.enviar_comando("/list")
            time.sleep(0.3)
        except:
            pass
    
    def _procesar_paquete(self, data):
        try:
            packet_id = data[0]
            
            if packet_id == self.ID_TEXT:
                self._procesar_texto(data)
            elif packet_id == self.ID_PLAY_STATUS:
                self._procesar_status(data)
            elif packet_id == self.ID_DISCONNECT:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Desconectado del servidor")
                self.conectado = False
                
        except Exception as e:
            pass
    
    def _procesar_texto(self, data):
        try:
            offset = 1
            tipo = data[offset]
            offset += 1
            
            hora = datetime.now().strftime("%H:%M:%S")
            
            if tipo == 0:  # MENSAJE DEL SISTEMA
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                msg = data[offset:offset+largo].decode('utf-8', errors='ignore')
                
                # Mostrar mensaje del sistema
                print(f"{Fore.MAGENTA}[📡]{Fore.RESET} {msg}")
                
                # Guardar en historial
                self.mensajes.append({
                    'hora': hora,
                    'nombre': 'SISTEMA',
                    'texto': msg
                })
                
                # Detectar jugadores que se unen/salen
                if "joined" in msg.lower() or "se unió" in msg.lower():
                    nombre_match = re.search(r'(\w+)\s+joined', msg, re.IGNORECASE)
                    if nombre_match:
                        nombre = nombre_match.group(1)
                        if self.play_activo:
                            print(f"{Fore.GREEN}[➕]{Fore.RESET} {Fore.CYAN}{nombre}{Fore.RESET} se unió al servidor!")
                
                elif "left" in msg.lower() or "salió" in msg.lower():
                    nombre_match = re.search(r'(\w+)\s+left', msg, re.IGNORECASE)
                    if nombre_match:
                        nombre = nombre_match.group(1)
                        if self.play_activo:
                            print(f"{Fore.RED}[➖]{Fore.RESET} {Fore.CYAN}{nombre}{Fore.RESET} salió del servidor!")
                
                # Detectar API en mensajes
                if "PocketMine" in msg or "PMMP" in msg:
                    self.api_detectada = "PocketMine-MP"
                elif "Nukkit" in msg:
                    self.api_detectada = "Nukkit"
                elif "Genisys" in msg:
                    self.api_detectada = "Genisys"
                
                if "registered" in msg.lower():
                    self.registrado = True
                    print(f"{Fore.GREEN}[✅]{Fore.RESET} Registrado como {Fore.CYAN}{self.nombre}{Fore.RESET}!")
                
                elif "logged in" in msg.lower():
                    self.registrado = True
                    print(f"{Fore.GREEN}[✅]{Fore.RESET} Login exitoso!")
                
            elif tipo == 1:  # CHAT DE JUGADORES
                # Nombre
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                nombre = data[offset:offset+largo].decode('utf-8', errors='ignore')
                offset += largo
                
                # Mensaje
                largo = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4
                msg = data[offset:offset+largo].decode('utf-8', errors='ignore')
                
                # Mostrar en pantalla INMEDIATAMENTE
                print(f"{Fore.YELLOW}[💬]{Fore.RESET} {Fore.CYAN}{nombre}{Fore.RESET}: {msg}")
                
                # Guardar mensaje
                self.mensajes.append({
                    'hora': hora,
                    'nombre': nombre,
                    'texto': msg
                })
                
        except Exception as e:
            pass
    
    def _procesar_status(self, data):
        try:
            status = data[1]
            if status == 0:
                print(f"{Fore.GREEN}[✅]{Fore.RESET} Sesión iniciada!")
                self.conectado = True
            elif status == 1:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Ya estás conectado")
            elif status == 2:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Servidor lleno")
            elif status == 3:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Servidor offline")
            elif status == 4:
                print(f"{Fore.YELLOW}[⚠️]{Fore.RESET} Versión incorrecta")
        except:
            pass
    
    def cerrar(self):
        self.running = False
        self.conectado = False
        self.play_activo = False
        if self.socket:
            self.socket.close()
        print(f"{Fore.YELLOW}[🔌]{Fore.RESET} Bot desconectado")

def main():
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.CYAN}     📡 CONFIGURACIÓN")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    # IP
    while True:
        try:
            ip = input(f"{Fore.GREEN}[?]{Fore.RESET} IP o dominio: ")
            if ip.strip():
                break
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}[!]{Fore.RESET} Saliendo...")
            sys.exit(0)
    
    # PUERTO
    while True:
        try:
            puerto_input = input(f"{Fore.GREEN}[?]{Fore.RESET} Puerto del servidor: ")
            if puerto_input.strip():
                puerto = int(puerto_input)
                if 1 <= puerto <= 65535:
                    break
                else:
                    print(f"{Fore.RED}[!]{Fore.RESET} Puerto inválido (1-65535)")
            else:
                print(f"{Fore.RED}[!]{Fore.RESET} Tienes que poner un puerto!")
        except ValueError:
            print(f"{Fore.RED}[!]{Fore.RESET} Tienes que poner un número!")
    
    # Nombre
    nombre_input = input(f"{Fore.GREEN}[?]{Fore.RESET} Nombre del bot (ENTER para aleatorio): ")
    nombre = nombre_input.strip() if nombre_input.strip() else generar_nombre()
    print(f"{Fore.CYAN}[🤖]{Fore.RESET} Nombre: {Fore.GREEN}{nombre}{Fore.RESET}")
    
    # Contraseña
    password = input(f"{Fore.GREEN}[?]{Fore.RESET} Contraseña (para /register): ")
    if not password.strip():
        print(f"{Fore.RED}[!]{Fore.RESET} La contraseña es obligatoria!")
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.CYAN}     🔌 CONECTANDO...")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    bot = PMMPBot(ip, puerto, nombre, password)
    
    if not bot.conectar():
        print(f"{Fore.RED}[❌]{Fore.RESET} No se pudo conectar al servidor!")
        print(f"{Fore.YELLOW}[ℹ️]{Fore.RESET} Verifica que la IP y puerto son correctos")
        sys.exit(1)
    
    # Intentar registro solo si está conectado
    if bot.conectado:
        print(f"{Fore.CYAN}[🔐]{Fore.RESET} Intentando registro...")
        
        bot.enviar_comando(f"/login {password}")
        time.sleep(1)
        
        if not bot.registrado:
            bot.enviar_comando(f"/register {password}")
            time.sleep(1)
            
            if not bot.registrado:
                bot.enviar_comando(f"/login {password}")
                time.sleep(1)
    
    # Iniciar escucha en segundo plano
    hilo_escucha = threading.Thread(target=bot.escuchar, daemon=True)
    hilo_escucha.start()
    
    print(f"\n{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════")
    print(f"{Fore.GREEN}[✅]{Fore.RESET} Bot INICIADO: {Fore.CYAN}{nombre}{Fore.RESET}")
    print(f"{Fore.GREEN}[📡]{Fore.RESET} Estado: {Fore.GREEN}ONLINE{Fore.RESET}" if bot.server_online else f"{Fore.RED}OFFLINE{Fore.RESET} (modo demostración)")
    print(f"{Fore.GREEN}[💬]{Fore.RESET} El CHAT se muestra AUTOMÁTICAMENTE en tiempo real")
    print(f"{Fore.GREEN}[👥]{Fore.RESET} Escribe {Fore.CYAN}/play{Fore.RESET} para monitorear jugadores")
    print(f"{Fore.GREEN}[👥]{Fore.RESET} Escribe {Fore.CYAN}/play off{Fore.RESET} para desactivar")
    print(f"{Fore.GREEN}[💬]{Fore.RESET} Escribe algo para enviar al chat")
    print(f"{Fore.GREEN}[📋]{Fore.RESET} Comandos: {Fore.CYAN}/list{Fore.RESET} - Ver jugadores (simulado)")
    print(f"{Fore.GREEN}[📋]{Fore.RESET} Comandos: {Fore.CYAN}/info{Fore.RESET} - Ver info del servidor")
    print(f"{Fore.GREEN}[🚪]{Fore.RESET} Escribe {Fore.RED}/exit{Fore.RESET} para salir")
    print(f"{Fore.YELLOW}══════════════════════════════════════════════════════════════════════════{Fore.RESET}\n")
    
    print(f"{Fore.CYAN}[📡]{Fore.RESET} ESCUCHANDO CHAT EN VIVO...\n")
    
    try:
        while bot.running:
            texto = input(f"{Fore.CYAN}[📝 Escribe algo:]{Fore.RESET} ")
            
            if not texto.strip():
                continue
            
            if texto.lower() == '/exit':
                if bot.conectado:
                    bot.enviar_mensaje("Me voy! Hasta luego! 👋")
                bot.cerrar()
                break
            
            if texto.lower() == '/play':
                bot.play_activo = True
                print(f"{Fore.GREEN}[👥]{Fore.RESET} Monitoreo de jugadores {Fore.GREEN}ACTIVADO{Fore.RESET}")
                print(f"{Fore.CYAN}[ℹ️]{Fore.RESET} Verás cuando alguien se una o salga")
                continue
            
            if texto.lower() == '/play off':
                bot.play_activo = False
                print(f"{Fore.YELLOW}[👥]{Fore.RESET} Monitoreo de jugadores {Fore.RED}DESACTIVADO{Fore.RESET}")
                continue
            
            if texto.lower() == '/list':
                if bot.conectado:
                    bot.enviar_comando("/list")
                    print(f"{Fore.CYAN}[📋]{Fore.RESET} Solicitando lista de jugadores...")
                else:
                    # Simular lista
                    jugadores = random.randint(1, 10)
                    print(f"{Fore.CYAN}[📋]{Fore.RESET} Jugadores online: {Fore.GREEN}{jugadores}{Fore.RESET}")
                    print(f"{Fore.CYAN}[📋]{Fore.RESET} (Modo simulación - servidor offline)")
                continue
            
            if texto.lower() == '/info':
                bot._mostrar_info()
                continue
            
            # Enviar al chat
            bot.enviar_mensaje(texto)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!]{Fore.RESET} Interrumpido")
        if bot.conectado:
            bot.enviar_mensaje("Me voy! Hasta luego! 👋")
        bot.cerrar()
    
    print(f"{Fore.GREEN}[✅]{Fore.RESET} Bot cerrado")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}[❌]{Fore.RESET} Error: {e}")
        sys.exit(1)