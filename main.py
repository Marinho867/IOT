import network
import time
import dht
import machine
from umqtt.simple import MQTTClient

# Configurações de Wi-Fi
ssid = "Wokwi-GUEST"
password = ""

# Configurações do Adafruit IO (MQTT)
aio_user = "Wellemay"  # Nome de usuário do Adafruit IO
aio_key = "aio_ZgtE43EusNcuwXD08b1Fm2lhXPCe"  # Sua chave de API do Adafruit IO
aio_feed = "Wellemay/feeds/well-dot-teste"  # Feed correto

mqtt_broker = "io.adafruit.com"
mqtt_port = 1883

# Configuração do DHT22
sensor = dht.DHT22(machine.Pin(15))

# Configuração dos LEDs
led_temp_high = machine.Pin(2, machine.Pin.OUT)  # GPIO 2 para LED de temperatura alta
led_temp_low = machine.Pin(5, machine.Pin.OUT)   # GPIO 4 para LED de temperatura baixa
led_hum = machine.Pin(4, machine.Pin.OUT)        # GPIO 5 para LED de umidade

# Função para conectar ao Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado ao Wi-Fi")

# Função para enviar dados via MQTT
def send_data(client):
    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            humidity = sensor.humidity()
            payload = f"{temp},{humidity}"
            client.publish(aio_feed, payload)
            print("Dados enviados:", payload)

            # Controle do LED de temperatura alta (acende se temp > 24°C)
            if temp > 24:
                led_temp_high.on()  # Acende o LED de temperatura alta
            else:
                led_temp_high.off()  # Apaga o LED de temperatura alta

            # Controle do LED de temperatura baixa (acende se temp < 17°C)
            if temp < 17:
                led_temp_low.on()  # Acende o LED de temperatura baixa
            else:
                led_temp_low.off()  # Apaga o LED de temperatura baixa
            
            # Controle do LED de umidade (acende se umidade < 50%, apaga se umidade > 60%)
            if humidity < 50:
                led_hum.on()  # Acende o LED de umidade baixa
            elif humidity > 60:
                led_hum.off()  # Apaga o LED de umidade alta

            time.sleep(30)  # Envia e verifica a cada 30 segundos
            
        except OSError as e:
            print("Erro de conexão ou sensor:", e)
            time.sleep(5)  # Espera 5 segundos antes de tentar novamente

# Função para reconectar ao MQTT se a conexão cair
def reconnect_mqtt(client):
    try:
        client.connect()
        print("Reconectado ao MQTT")
    except Exception as e:
        print("Falha na reconexão com o MQTT:", e)
        time.sleep(5)  # Espera antes de tentar novamente

# Conexão MQTT
connect_wifi()
client = MQTTClient("client_id", mqtt_broker, user=aio_user, password=aio_key, port=mqtt_port)

# Tenta conectar ao MQTT
try:
    client.connect()
    print("Conectado ao MQTT")
except Exception as e:
    print("Falha na conexão com o MQTT:", e)

# Chama a função de enviar dados
send_data(client)

