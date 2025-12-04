from pymodbus.client import ModbusTcpClient

PLC_IP = "10.168.64.34"
PLC_PORT = 502
UNIT_ID = 0           # Mitsubishi module slave id

offset = 3500         # register offset (adjust based on mapping)

client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
client.connect()
#print(client)
response = client.read_holding_registers(address=3500, count=1)
if hasattr(response, 'registers'):
                registers = response.registers[0]
                print(registers)

                # Convert 16-bit registers to bytes
                # byte_data = b''.join(reg.to_bytes(2, byteorder='big') for reg in registers)
                # # Try to decode as ASCII string (strip null bytes)
                # dmc_number = byte_data.decode('ascii', errors='ignore').strip('\x00')
                # print(dmc_number)
                #print(f"📥 Original DMC Number from D{start_address}-D{start_address+count-1}: {dmc_number}")
                # Swap alternate characters (pairwise swap)
                #swapped = ''.join(dmc_number[i+1] + dmc_number[i] for i in range(0, len(dmc_number)-1, 2))
            
# rr = client.read_holding_registers(address=offset, count=1, slave=UNIT_ID)
# rr = client.read_input_registers(address=offset, count=1, slave=UNIT_ID)
#print(response)
# if rr.isError():
#     print("Modbus error:", rr)
# else:
#     value = rr.registers[0]
#     bit1 = (value >> 1) & 1
#     print(f"D3500 raw={value}, bit1={bit1}")

client.close()
