from pymodbus.client import ModbusTcpClient

PLC_IP = "10.168.64.34"
PLC_PORT = 502
address=3000
count=1
#offset = 3500    
     # register offset (adjust based on mapping)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
client.connect()
#print(client)

result = client.read_coils(address, 1)

if hasattr(result, 'registers'):
    registers = result.registers
    # Convert 16-bit registers to bytes
    if not result.isError():
        print("M3500.1 =", result.bits[0])
    else:
        print("Error:", result)

client.close()
