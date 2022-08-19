import time

import serial
from modbus_tk import modbus_rtu

from ModbusCOM import switchPortInterval


class ModbusRTU_Singleton:
    master:modbus_rtu.RtuMaster = None

    port_name = ""
    baud = ""
    byteSize = ""
    parity = ""
    stopBits = ""

    @staticmethod
    def InitPort(port_name, baud, byteSize, parity, stopBits):
        if ModbusRTU_Singleton.port_name != port_name or ModbusRTU_Singleton.baud != baud or ModbusRTU_Singleton.byteSize != byteSize or ModbusRTU_Singleton.parity != parity or ModbusRTU_Singleton.stopBits != stopBits:
            if ModbusRTU_Singleton.master is not None:
                ModbusRTU_Singleton.master.close()
                print("Master define is changed.Wait for serial port ready")
                time.sleep(switchPortInterval)
            ModbusRTU_Singleton.master = modbus_rtu.RtuMaster(serial.Serial(
                port=port_name, baudrate=baud, bytesize=byteSize, parity=parity, stopbits=stopBits))
            ModbusRTU_Singleton.master.set_timeout(1.0)

            ModbusRTU_Singleton.port_name = port_name
            ModbusRTU_Singleton.baud = baud
            ModbusRTU_Singleton.byteSize = byteSize
            ModbusRTU_Singleton.parity = parity
            ModbusRTU_Singleton.stopBits = stopBits