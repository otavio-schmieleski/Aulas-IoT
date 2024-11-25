from flask import render_template
from app import app
import RPi.GPIO as gpio 
import time as delay
from datetime import datetime
from urllib.request import urlopen
import requests


ledVermelho, ledVerde = 11, 12
pin_e = 16
pin_t = 15
urlBase = 'https://api.thingspeak.com/update?api_key='
keyWrite = 'PZTZJH6WNKIFWOME'
sensorDistancia = '&field1='
urlBase_read = 'https://api.thingspeak.com/channels/'
readKey = '/last?key=3BE8TI8EO588TTUP'
channels = '2746094'
field1 = '/fields/1/'
field2 = '/fields/2/'
ocupacao = 0
lixeira_v = 20
lista_registro = []


gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)
gpio.setup(ledVermelho, gpio.OUT)
gpio.setup(ledVerde, gpio.OUT)

gpio.output(ledVermelho, gpio.LOW)
gpio.output(ledVerde, gpio.LOW)


def abre_tampa():
    while i <= 3:
        gpio.output(ledVerde, gpio.HIGH)
        delay.sleep(3)
        gpio.output(ledVerde, gpio.LOW)
        delay.sleep(3)
        i += 1

def fecha_tampa():
    while i <= 3:
        gpio.output(ledVermelho, gpio.HIGH)
        delay.sleep(3)
        gpio.output(ledVermelho, gpio.LOW)
        delay.sleep(3)
        i += 1
        
def status_lixeira():
    disponivel = True
    while True:
        if ocupacao < 100:
            gpio.output(ledVerde, gpio.HIGH)
            disponivel = True
        else:
            gpio.output(ledVermelho, gpio.HIGH)
            disponivel = False
        return disponivel

def resgitro_tampa():
    now = datetime.now()
    # Formata a data e hora no padrão desejado
    time = now.strftime("%d/%m/%Y %H:%M")
    lista_registro.append(time)
    return lista_registro

def testaConexao():
    try:
        urlopen('https://www.materdei.edu.br/pt', timeout=1)
        return True
    except:
        return False

def distancia():
    gpio.output(pin_t, True)
    delay.sleep(0.000001)
    gpio.output(pin_t, False)
    tempo_i = delay.time()
    tempo_f = delay.time()
    while gpio.input(pin_e) == False:
        tempo_i = delay.time()
    while gpio.input(pin_e) == True:
        tempo_f = delay.time()
        temp_d = tempo_f - tempo_i
        distancia = (temp_d*34300) / 2
    
    ocupacao_l = (distancia/lixeira_v)*100
    ocupacao_f = 100-ocupacao_l
    ocupacao_lixeira = ('{0:0.0f}%'.format(ocupacao_f))

    return ocupacao_lixeira

def envia_dados():
    if testaConexao() == True:
        while True:
            urlDados = (urlBase + keyWrite + sensorDistancia + str(distancia()))
            retorno = requests.post(urlDados)

            if retorno.status_code == 200:
                print('Dados envidados com sucesso')
            else:
                print('Erro ao enviar dados: '+ retorno.status_code)

            delay.sleep(20)

    else:
        print('Sem conexão')
        
def consulta_dados():
    if testaConexao() == True:
        print('Conexão OK')

        while True:
            consultaDistancia = requests.get(urlBase + channels + field1 + readKey)

            print(consultaDistancia.text)
            delay.sleep(20)
    else:
        print('Sem conexão com a INTERNET')


@app.route('/')
def index():
    templateData = {
        'abre_tampa': abre_tampa(),
        'fecha_tampa': fecha_tampa(),
        'status_lixeira': status_lixeira(),
        'ocup_lixeira': distancia(),
        'registro_tampa': resgitro_tampa()
    }
    return render_template('index.html', **templateData)

@app.route('/abre-tampa')
def index():
   abre_tampa()
   templateData = {
        'registro_tampa': resgitro_tampa()
    }
   return render_template('index.html', **templateData)

@app.route('/fechar-tampa')
def index():
    fecha_tampa()
    templateData = {
        'registro_tampa': resgitro_tampa()
    }
    return render_template('index.html', **templateData)