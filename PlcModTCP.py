import time
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

class PLCClient:

    def __init__(self, ip_address, port=502):
        self.ip_address = ip_address
        self.port = port
        self.client = None
       
    def connect_to_plc(self):
        """Connect to the Mitsubishi PLC using Modbus TCP."""
        try:
            self.client = ModbusTcpClient(host=self.ip_address, port=self.port)
            connection = self.client.connect()
            if connection:
                print(f"✅ Successfully connected to PLC at {self.ip_address}:{self.port}")
                #self.logger.info(f"✅ Successfully connected to PLC at {self.ip_address}:{self.port}")
                return True
            else:
                print(f"❌ Failed to connect to PLC at {self.ip_address}:{self.port}")
                #self.logger.error(f"❌ Failed to connect to PLC at {self.ip_address}:{self.port}")
                return False

        except Exception as e:

            print(f"❌ Error connecting to PLC: {str(e)}")

            return False

   
    def read_dmc_number(self, start_address=510, count=10):

        """
        Read DMC number stored in D registers (e.g., D510-D519),
        then swap alternate characters (pairwise).
        Returns the swapped DMC number as a string.
        """
        if not self.client or not self.client.connected:
            print("❌ PLC not connected")
            return None

        try:
            response = self.client.read_holding_registers(address=start_address, count=count)
            if hasattr(response, 'registers'):
                registers = response.registers
                # Convert 16-bit registers to bytes
                byte_data = b''.join(reg.to_bytes(2, byteorder='big') for reg in registers)
                # Try to decode as ASCII string (strip null bytes)
                dmc_number = byte_data.decode('ascii', errors='ignore').strip('\x00')
                print(f"📥 Original DMC Number from D{start_address}-D{start_address+count-1}: {dmc_number}")
                # Swap alternate characters (pairwise swap)
                swapped = ''.join(dmc_number[i+1] + dmc_number[i] for i in range(0, len(dmc_number)-1, 2))
                # If odd length, keep last char
                if len(dmc_number) % 2 != 0:
                    swapped += dmc_number[-1]
                print(f"🔄 Swapped DMC Number: {swapped}")
                #return swapped[:10]
                return swapped

            else:
                print(f"❌ Error reading DMC number: Response has no registers attribute")
                return None

        except ModbusException as e:
            print(f"❌ Modbus error reading DMC number: {str(e)}")
            return None

        except Exception as e:
            print(f"❌ Unexpected error reading DMC number: {str(e)}")
            return None


    def close_connection(self):

        """Close the PLC connection."""
        if self.client:
            try:
                self.client.close()
                print("🔌 Connection closed")
            except Exception as e:
                print(f"❌ Error closing connection: {str(e)}")
 

def get_dmc_number(plc_ip="10.168.158.230", plc_port=502, start_address=510, count=10):

    """
    External function to get DMC number from PLC.
    Returns the swapped DMC number as a string, or None if failed.
    """
    plc_client = PLCClient(plc_ip, plc_port)
    print('plc_ip=',plc_ip, ',plc_port=',plc_port, ',start_address=',start_address,',count=', count)
    try:
        if plc_client.connect_to_plc():
            dmc_number = plc_client.read_dmc_number(start_address, count)
            return dmc_number

        else:
            print("❌ Failed to connect to PLC")
            return None

    except Exception as e:
        print(f"❌ Error getting DMC number: {str(e)}")
        return None
    finally:
        plc_client.close_connection()


# def main():

#     """Example usage of the PLC client."""

#     # PLC configuration
#     plc_ip = "10.168.158.230"
#     plc_port = 502

#     # Create PLC client instance
#     plc_client = PLCClient(plc_ip, plc_port)

#     if plc_client.connect_to_plc():

#         try:

#             # Read DMC number

#             dmc_number = plc_client.read_dmc_number(start_address=510, count=10)

#             if dmc_number:

#                 print(f"Final DMC Number: {dmc_number}")

           

#             # Example of other operations

#             # plc_client.write_to_d_register(address=516, value=5678)

#             # plc_client.read_d_register(address=516, count=1)

           

#         finally:

#             plc_client.close_connection()


if __name__ == "__main__":
    # Test the get_dmc_number function
    dmc = get_dmc_number()
    if dmc:
        print(f"Retrieved DMC Number: {dmc}")
    else:
        print("Failed to rerieve DMC number")