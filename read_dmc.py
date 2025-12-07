from pymodbus.client import ModbusTcpClient

PLC_IP = "10.168.64.104"
PLC_PORT = 502
UNIT_ID = 0           # Mitsubishi module slave id
start_address=10
count=6
#offset = 3500    
     # register offset (adjust based on mapping)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
client.connect()
#print(client)

response = client.read_holding_registers(address=start_address, count=count)
#if response.isError():
#    raise ConnectionException("Modbus read error")
            
if hasattr(response, 'registers'):
    registers = response.registers
    # Convert 16-bit registers to bytes
    byte_data = b''.join(reg.to_bytes(2, byteorder='big') for reg in registers)
    # Try to decode as ASCII string (strip null bytes)
    dmc_number = byte_data.decode('ascii', errors='ignore').strip('\x00')
    print(f"📥 Original DMC Number from D{start_address}-D{start_address+count-1}: {dmc_number}")
    # Swap alternate characters (pairwise swap)
    swapped = ''.join(dmc_number[i+1] + dmc_number[i] for i in range(0, len(dmc_number)-1, 2))

    print('Swapped',swapped)
    # If odd length, keep last char
    if len(dmc_number) % 2 != 0:
        swapped += dmc_number[-1]
        print(f"🔄 Swapped DMC Number: {swapped}")

client.close()
