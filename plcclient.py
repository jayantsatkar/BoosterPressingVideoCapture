import threading
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException

class PLCClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, ip=None, port=None,logger=None):
        #Only create one instance, thread safe
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PLCClient, cls).__new__(cls)
                    # Initialize only once
                    cls._instance._initialize = False
        return cls._instance

    def __init__(self, ip = None, port = None, logger = None):
        if getattr(self, "_initialized", False):
            return
        
        self.ip = ip
        self.port = port
        self.logger = logger
        self.client = None
        self.connected = False
        self.connect()
        self._initialized = True
        self.logger.info('PLC Init called')


    def connect(self):
       if self.client is None:
            self.client = ModbusTcpClient(host = self.ip,port = self.port)
            self.connected = self.client.connect()
            if self.logger:
                self.logger.info(f"PLC connected: {self.connected}")
            else:
                print(f"PLC connected: {self.connected}")

    def read_dmc_number(self, start_address=510, count=10):

        """
        Read DMC number stored in D registers (e.g., D510-D519),
        then swap alternate characters (pairwise).
        Returns the swapped DMC number as a string.
        """
        if not self.connected:
           self.connect()

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

    def read_bool(self, address):
        """Read a single coil"""
        if not self.connected:
            self.connect()
        rr = self.client.read_coils(address, 1)
        if rr.isError():
            return None
        return bool(rr.bits[0])

    def write_bool(self, address, value):
        """Write a single coil"""
        if not self.connected:
            self.connect()
        self.client.write_coil(address, value)

    def close(self):
        if self.client and self.connected:
            self.client.close()
            self.connected = False