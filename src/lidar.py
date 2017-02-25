import smbus
import time
bus = smbus.SMBus(1)
address = 0x62

import argparse

parser = argparse.ArgumentParser(description='WOPR-JR LIDAR processing')
parser.add_argument('-show', '--show', action='store_true', help='show distance')
parser.add_argument('-p', '--publish', action='store_true', help='publish to networktables')
parser.add_argument('-ip', '--address', type=str, default="roboRIO-3966-frc.local", help='network tables address')
parser.add_argument('-did', '--dashboardid', type=str, default="Distance", help='smart dashboard publish ID')
parser.add_argument('-t', '--table', type=str, default="lidar", help='smart dashboard publish ID')

args = parser.parse_args()

def write(value):
        bus.write_byte_data(address, 0, value)
        return -1

def range():
        range1 = bus.read_byte_data(address, 0x0f)
        range2 = bus.read_byte_data(address, 0x10)
        range3 = (range1 << 8) + range2
        return range3

if args.publish:
        from networktables import NetworkTables
        NetworkTables.initialize(server=args.address)
        sd = NetworkTables.getTable("SmartDashboard")
        table = NetworkTables.getTable(args.table)

while True:
        try:
                write(0x04)
                time.sleep(0.02)
                rng = range()
                
                if args.show:
                        print rng

                if args.publish:
                        stable = table.getSubTable("distance")
                        if not sd.putNumber(args.dashboardid, rng):
                                sd.delete(args.dashboardid)
                                print ("Couldn't publish to smart dashboard\n")
                                
                        worked = True
                        worked = worked and stable.putNumber(args.dashboardid, rng)

                        if not worked:
                                print ("Error while writing to table\n")
        except Exception:
                time.sleep(1.0)
                pass
