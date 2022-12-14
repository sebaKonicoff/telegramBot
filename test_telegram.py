from config import * #importamos el token
from flask import Flask, request #para crear el servidor web
from pyngrok import ngrok, conf #para crear un tunel entre nuestro servidor web local e internet (obtener una url publica)
import telebot #para menejar la API de telegram
import threading #para ejecutar hilos
from datetime import datetime
import time
import calendar
from waitress import serve #para ejecutar el servidor en un entorno de producción

#instanciamos el bot de telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

#insanciar servidor web de Flask
web_server = Flask(__name__)

#gestionar las peticions POST enviadas al servidor web
@web_server.route('/', methods=['POST'])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return "OK", 200

#responde al comando /start /hola
@bot.message_handler(commands=["start", "hola"])
def cmd_start(message):
    """Muestra las opciones del bot"""
    bot.reply_to(message, 'Hola!! ¿Qué te gustaría hacer?\n' +
                            'Comandos: \n' +
                            'vale: Fecha de su cumple.\n' + 
                            'nos: Fecha desde que comenzamos.\n' +
                            'exa: fecha para cambiar passw')

@bot.message_handler(commands=["lapio"])
def cmd_vale(message):
    bot.reply_to(message, "La fecha de su cumple es: \n" +
                            "24/06")

@bot.message_handler(commands=["nos"])
def cmd_vale(message):
    fechaComienzo = datetime(2022,5,14)
    now = datetime.now()
    tiempoJ = (now.year - fechaComienzo.year) * 12 + now.month - fechaComienzo.month 
    bot.reply_to(message, "Fecha de comienzo: \n" +
                            "14/05/2022. \n" + 
                            "Llevamos: " + str(tiempoJ) + " meses.")
                            
@bot.message_handler(commands=["exa"])
def cmd_exa(message):
    datenow = datetime.now()
    diasFaltantes = 30 - datenow.day
    bot.reply_to(message, "Fecha de caducidad: \n" +
                            "Día 30 del mes. \n" +
                            "Faltan " + str(diasFaltantes) + " dias para cambiar passw.")


#responde a los mensajes de texto que no son comandos
@bot.message_handler(content_types=["text"])
def bot_mensaje_testo(message):
    """Gestiona los mensajes de texto"""
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Comando no disponible")
    else:
        bot.send_message(message.chat.id, "ERROR. Por favor ingrese un comando '/'")

def enviarMensaje():
    fechaActual = datetime.now()
    if fechaActual.day == 25:
        bot.send_message(MI_CHAT_ID, "Aviso!!, tienes que cambiar la contraseña del exa, vence en 5 días.")
    if fechaActual.day == 23 and fechaActual.month == 6:
        bot.send_message(MI_CHAT_ID, "Mañana es el cumple de Lapio")
    if fechaActual.day == 7 and fechaActual.month == 2:
        bot.send_message(MI_CHAT_ID, "Mañana es el cumple de Moni")

#MAIN ########################
if __name__ == '__main__':
    #configuramos los comandos disponibles del bot
    bot.set_my_commands([
        telebot.types.BotCommand("/start", "da la bienvenida"),
        telebot.types.BotCommand("/lapio", "su fecha de cumpleaños"),
        telebot.types.BotCommand("/nos", "fecha de comienzo"),
        telebot.types.BotCommand("/exa", "fecha para cambiar passw")
    ])
    print('Iniciando el bot')
    hilo_bot = threading.Thread(name="hilo_bot", target=enviarMensaje)
    hilo_bot.start()
    conf.get_default().config_path = "./config_ngrok.yml" #ruta donde queremos que se guarde el archivod e config de ngrok 
    conf.get_default().region = "sa" #definir region de servidor de ngrok (sa = south america)
    ngrok.set_auth_token(NGROK_TOKEN) #creamos el erchivo de credenciales de la API de ngrok
    ngrok_tunel = ngrok.connect(5000, bind_tls=True) #creamos tunel https en el puerto 5000
    ngrok_url = ngrok_tunel.public_url #url del tunel de https creado
    bot.remove_webhook() #eliminamos el webhook
    time.sleep(1)
    bot.set_webhook(url=ngrok_url) #definimos el webhook
    #arrancamos el servidor
    serve(web_server, host="0.0.0.0", port=5000)
    #"0.0.0.0" con esta dirIP le decimos que el servidor web local va a estar disponible a todas las ip de nuestra red local



    #hilo_bot = threading.Thread(name="hilo_bot", target=recibir_mensajes)
    #hilo_bot.start()
    #para enviar un mensaje
    #bot.send_message(MI_CHAT_ID, "Renovar clave EXA")