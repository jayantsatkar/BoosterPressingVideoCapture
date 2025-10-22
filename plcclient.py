import threading
import time
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException , ConnectionException

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
        """Try to connect or reconnect"""

        try:
            if self.client is None:
                self.client = ModbusTcpClient(host = self.ip,port = self.port)

            if not self.client.connected: 
                self.connected = self.client.connect()
                if self.logger:
                    self.logger.info(f"PLC connected: {self.connected}")
                else:
                    print(f"PLC connected: {self.connected}")
        except Exception as ex:
            self.connected = False
            if self.logger:
                 self.logger.error(f"PLC connection error: {ex}")
            else:
                print("PLC connection error:", ex)
            time.sleep(2)

    def ensure_connection(self):
        """Ensure we have a valid connection"""
        if not self.client or not self.client.connected:
            self.connect()


    def read_dmc_number(self, start_address=510, count=10):

        """
        Read DMC number stored in D registers (e.g., D510-D519),
        then swap alternate characters (pairwise).
        Returns the swapped DMC number as a string.
        """
        # if not self.connected:
        #    self.connect()

        try:
            self.ensure_connection()
            response = self.client.read_holding_registers(address=start_address, count=count)
            if response.isError():
                raise ConnectionException("Modbus read error")
            
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

        except Exception as ex:
            print(f"❌ Unexpected error reading DMC number: {str(ex)}")
            self.connected = False
            if self.logger:
                self.logger.error(f"PLC read_dmc_number error: {ex}")
            else:
                print("PLC read_dmc_number error:", ex)
            self.connect()
            return None

    def read_bool(self, address):
        """Read a single coil safely with reconnect"""
        try:
            self.ensure_connection()
            rr = self.client.read_coils(address = address, count = 1)
            if rr.isError():
                raise ConnectionException("Modbus read error")
            return bool(rr.bits[0])

        except Exception as ex:
            self.connected = False
            if self.logger:
                self.logger.error(f"PLC read_bool error: {ex}")
            else:
                print("PLC read_bool error:", ex)
            self.connect()
            return None
            

    def write_bool(self, address, value):
        """Write a single coil"""
        try:
            self.ensure_connection()
            self.client.write_coil(address=address, value=value)
        except Exception as ex:
            self.connected = False
            if self.logger:
                self.logger.error(f"PLC write_bool error: {ex}")
            else:
                print("PLC write_bool error:", ex)
            self.connect()

    # def close(self):
    #     if self.client and self.connected:
    #         self.client.close()
    #         self.connected = False

    def close(self):
        """Close the connection gracefully"""
        if self.client and self.client.connected:
            self.client.close()
            self.connected = False
            if self.logger:
                self.logger.info("PLC connection closed")