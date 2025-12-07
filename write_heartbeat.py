from pymodbus.client import ModbusTcpClient
import time

PLC_IP = "10.168.64.104"
PLC_PORT = 502
UNIT_ID = 0           # Mitsubishi module slave id

address = 5         # register offset (adjust based on mapping)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
client.connect()
#print(client)
#response = client.read_holding_registers(address=address, count=1)
toggle = True
while True:
    try:
        client.write_register(address= address,value= toggle)
        toggle = not toggle
        time.sleep(0.5)

    except Exception as ex:
    #                  self.logger.error(f"Heartbeat error: {ex}")
        print('Error')
           
        
