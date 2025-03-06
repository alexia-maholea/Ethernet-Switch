# #!/usr/bin/python3
# import sys
# import struct
# import wrapper
# import threading
# import time
# from wrapper import recv_from_any_link, send_to_link, get_switch_mac, get_interface_name

# root_bridge_id = 0

# def read_config_file(switch_id):
#     vlan = {}

#     config_file_path = f'configs/switch{switch_id}.cfg'
    
#     with open(config_file_path, 'r') as file:
#         # switch priority
#         switch_priority = int(file.readline().strip())

#         index = 0
#         # configuratia in sine
#         for line in file:
#             stripped = line.strip()
#             if stripped != "":
#                 parts = stripped.split()
#                 if parts[1] == 'T':
#                     vlan[index] = (parts[0], -1, 'trunk')
#                 else:
#                     vlan_id = int(parts[1])
#                     vlan[index] = (parts[0], vlan_id, 'access')
#                 index += 1

#     return switch_priority, vlan


# def parse_ethernet_header(data):
#     # Unpack the header fields from the byte array
#     #dest_mac, src_mac, ethertype = struct.unpack('!6s6sH', data[:14])
#     dest_mac = data[0:6]
#     src_mac = data[6:12]
    
#     # Extract ethertype. Under 802.1Q, this may be the bytes from the VLAN TAG
#     ether_type = (data[12] << 8) + data[13]

#     vlan_id = -1
#     # Check for VLAN tag (0x8100 in network byte order is b'\x81\x00')
#     if ether_type == 0x8200:
#         vlan_tci = int.from_bytes(data[14:16], byteorder='big')
#         vlan_id = vlan_tci & 0x0FFF  # extract the 12-bit VLAN ID
#         ether_type = (data[16] << 8) + data[17]

#     return dest_mac, src_mac, ether_type, vlan_id

# def create_vlan_tag(vlan_id):
#     # 0x8100 for the Ethertype for 802.1Q
#     # vlan_id & 0x0FFF ensures that only the last 12 bits are used
#     return struct.pack('!H', 0x8200) + struct.pack('!H', vlan_id & 0x0FFF)

# def send_bdpu_every_sec(own_bridge_id, interfaces, vlan):
#     global root_bridge_id
    
#     while True:
#         if own_bridge_id == root_bridge_id:
#             src_mac = get_switch_mac()
#             dst_mac = b'\01\x80\xc2\x00\x00\x00'

#             root_bridge_id = own_bridge_id
#             sender_bridge_id = own_bridge_id
#             sender_path_cost = 0

#             bpdu = dst_mac + src_mac + struct.pack('!Q', root_bridge_id) + struct.pack('!Q', sender_bridge_id) + struct.pack('!Q', sender_path_cost)
#             for i in interfaces:
#                 if vlan[i][2] == 'trunk':
#                     send_to_link(i, len(bpdu), bpdu)

#         time.sleep(1)

# def forward_frame(send_interface, length, data, vlan, vlan_id, interface, states):
#     # trimitem pe trunk port
#     if vlan[send_interface][2] == 'trunk':
#         # vine de pe trunk port
#         if vlan_id != -1:
#             print(f"sending on trunk port from {interface} to {send_interface}")
#             send_to_link(send_interface, length, data)
#         else:
#             # adăugăm tag-ul
#             not_tagged = data[0:12] + create_vlan_tag(vlan[interface][1]) + data[12:]
#             length += 4
#             print(f"sending on trunk port from {interface} to {send_interface}")

#             send_to_link(send_interface, length, not_tagged)
#     # trimitem pe access port
#     elif vlan[send_interface][2] == 'access':
#         # vine de pe trunk port
#         if vlan_id != -1 and vlan_id == vlan[send_interface][1]:
#             # scoatem tag-ul
#             not_tagged = data[0:12] + data[16:]
#             length -= 4
#             print(f"sending on acc port from {interface} to {send_interface}")

#             send_to_link(send_interface, length, not_tagged)
#         else:
#             if vlan[send_interface][1] == vlan[interface][1]:
#                 print(f"sending on acc port from {interface} to {send_interface}")
#                 send_to_link(send_interface, length, data)

# def main():
#     # init returns the max interface number. Our interfaces
#     # are 0, 1, 2, ..., init_ret value + 1
#     global root_bridge_id

#     switch_id = sys.argv[1]

#     switch_priority, vlan = read_config_file(switch_id)

#     num_interfaces = wrapper.init(sys.argv[2:])
#     interfaces = range(0, num_interfaces)

#     # print("# Starting switch with id {}".format(switch_id), flush=True)
#     # print("[INFO] Switch MAC", ':'.join(f'{b:02x}' for b in get_switch_mac()))


#     # initializare
#     states = {}
#     for o in interfaces:
#         if vlan[o][2] == 'trunk':
#             states[o] = 'BLOCKING'
#         else:
#             states[o] = 'LISTENING'
    
#     own_bridge_id = switch_priority
#     root_bridge_id = own_bridge_id
#     root_path_cost = 0
#     root_port = -1

#     if own_bridge_id == root_bridge_id:
#         for o in interfaces:
#             states[o] = 'LISTENING'

#     MAC_Table = {}

#     # Create and start a new thread that deals with sending BDPU
#     t = threading.Thread(target=send_bdpu_every_sec, args=(own_bridge_id, interfaces, vlan))

#     t.start()

#     # Printing interface names
#     # for i in interfaces:
#         # print(get_interface_name(i))

#     while True:
#         # Note that data is of type bytes([...]).
#         # b1 = bytes([72, 101, 108, 108, 111])  # "Hello"
#         # b2 = bytes([32, 87, 111, 114, 108, 100])  # " World"
#         # b3 = b1[0:2] + b[3:4].
#         interface, data, length = recv_from_any_link()

#         dest_mac, src_mac, ethertype, vlan_id = parse_ethernet_header(data)

#         # Print the MAC src and MAC dst in human readable format
#         dest_mac = ':'.join(f'{b:02x}' for b in dest_mac)
#         src_mac = ':'.join(f'{b:02x}' for b in src_mac)

#         # Note. Adding a VLAN tag can be as easy as
#         # tagged_frame = data[0:12] + create_vlan_tag(10) + data[12:]

#         # print(f'Destination MAC: {dest_mac}')
#         # print(f'Source MAC: {src_mac}')
#         # print(f'EtherType: {ethertype}')

#         # print("Received frame of size {} on interface {}".format(length, interface), flush=True)

#         MAC_Table[src_mac] = interface

#         # adresa multicast
#         if dest_mac == '01:80:c2:00:00:00':
#             # primit bpdu
#             bpdu_root_bridge_id = struct.unpack('!Q', data[12:20])[0]
#             bpdu_sender_bridge_id = struct.unpack('!Q', data[20:28])[0]
#             bpdu_sender_path_cost = struct.unpack('!Q', data[28:36])[0]

#             if bpdu_root_bridge_id < root_bridge_id:
#                 old_root_bridge_id = root_bridge_id
#                 root_bridge_id = bpdu_root_bridge_id
#                 root_path_cost = bpdu_sender_path_cost + 10
#                 root_port = interface

#                 if old_root_bridge_id == own_bridge_id:
#                     for i in interfaces:
#                         if vlan[i][2] == 'trunk' and i != root_port:
#                             states[i] = 'BLOCKING'
                
#                 if states[interface] == 'BLOCKING':
#                     states[interface] = 'LISTENING'

#                 new_src_mac = get_switch_mac()
#                 new_dst_mac = b'\01\x80\xc2\x00\x00\x00'

#                 bpdu = new_dst_mac + new_src_mac + struct.pack('!Q', root_bridge_id) + struct.pack('!Q', own_bridge_id) + struct.pack('!Q', root_path_cost)
#                 for i in interfaces:
#                     if vlan[i][2] == 'trunk' and i != interface:
#                         send_to_link(i, len(bpdu), bpdu)
        
#             elif bpdu_root_bridge_id == root_bridge_id:
#                 if interface == root_port and bpdu_sender_path_cost + 10 < root_path_cost:
#                     root_path_cost = bpdu_sender_path_cost + 10
#                 elif interface != root_port:
#                     if bpdu_sender_path_cost > root_path_cost:
#                         if states[interface] != 'LISTENING':
#                             states[interface] = 'LISTENING'

#             elif bpdu_sender_bridge_id == own_bridge_id:
#                 states[interface] = 'BLOCKING'
#             else:
#                 continue
            
#             if own_bridge_id == root_bridge_id:
#                 for i in interfaces:
#                     if vlan[i][2] == 'trunk' and i != root_port:
#                         states[i] = 'LISTENING'
#             else:
#                 continue
                    
#         elif dest_mac != 'ff:ff:ff:ff:ff:ff' and dest_mac in MAC_Table and MAC_Table[dest_mac] in interfaces:
#             if states[MAC_Table[dest_mac]] == 'LISTENING':
#                 # trimitem pe portul pe care am invatat ca se afla destinatia
#                 forward_frame(MAC_Table[dest_mac], length, data, vlan, vlan_id, interface, states)
#             else:
#                 continue
#         else:
#             # facem flooding
#             for o in interfaces:
#                 if o != interface and states[o] == 'LISTENING':
#                     forward_frame(o, length, data, vlan, vlan_id, interface, states)

#         # data is of type bytes.
#         # send_to_link(i, length, data)

# if __name__ == "__main__":
#     main()

#!/usr/bin/python3
import sys
import struct
import wrapper
import threading
import time
from wrapper import recv_from_any_link, send_to_link, get_switch_mac, get_interface_name

mac_table={}
vlan = {}
def parse_ethernet_header(data):
    # Unpack the header fields from the byte array
    #dest_mac, src_mac, ethertype = struct.unpack('!6s6sH', data[:14])
    dest_mac = data[0:6]
    src_mac = data[6:12]
    
    # Extract ethertype. Under 802.1Q, this may be the bytes from the VLAN TAG
    ether_type = (data[12] << 8) + data[13]

    vlan_id = -1
    # Check for VLAN tag (0x8100 in network byte order is b'\x81\x00')
    if ether_type == 0x8200:
        vlan_tci = int.from_bytes(data[14:16], byteorder='big')
        vlan_id = vlan_tci & 0x0FFF  # extract the 12-bit VLAN ID
        ether_type = (data[16] << 8) + data[17]

    return dest_mac, src_mac, ether_type, vlan_id

def create_vlan_tag(vlan_id):
    # 0x8100 for the Ethertype for 802.1Q
    # vlan_id & 0x0FFF ensures that only the last 12 bits are used
    return struct.pack('!H', 0x8200) + struct.pack('!H', vlan_id & 0x0FFF)

def send_bdpu_every_sec():
    while True:
        # TODO Send BDPU every second if necessary
        time.sleep(1)
        
def forward_with_learning(interface, dest_mac, src_mac, data, interfaces, length, vlan_id): 
    global mac_table, vlan
    mac_table[src_mac, vlan_id] = interface

    if dest_mac != "ff:ff:ff:ff:ff:ff":
        if (dest_mac, vlan_id) in mac_table:
            dest_interface = mac_table[(dest_mac, vlan_id)]
            # se duce pe trunk port
            if vlan[dest_interface] == -999:
                # a venit de pe acces
                if vlan_id == -1:
                    tagged_frame = data[0:12] + create_vlan_tag(vlan[interface]) + data[12:]
                    send_to_link(dest_interface, length + 4, tagged_frame)
                else:
                    send_to_link(dest_interface, length, data)
            # se duce pe access
            else:
                # a venit de pe acces
                if vlan_id == -1 and vlan[interface] == vlan[dest_interface]:
                    send_to_link(dest_interface, length, data)
                elif vlan_id == vlan[dest_interface]:
                    tagged_frame = data[0:12] + data[16:]
                    send_to_link(dest_interface, length - 4, tagged_frame)

        else:
            for i in interfaces:
                if i != interface:
                    # se duce pe trunk port
                    if vlan[i] == -999:
                    # vine de pe trunk port
                        if vlan_id != -1:
                            send_to_link(i, length, data)
                        else:
                            tagged_frame = data[0:12] + create_vlan_tag(vlan[interface]) + data[12:]
                            send_to_link(i, length + 4, tagged_frame)
                    # se duce pe access
                    else:
                        # vine de pe trunk port
                        if vlan_id != -1 and vlan_id == vlan[i]:
                            tagged_frame = data[0:12] + data[16:]
                            send_to_link(i, length - 4, tagged_frame)
                        elif vlan[i] == vlan[interface]:
                            send_to_link(i, length, data)
    else: 
        for i in interfaces:
            if i != interface:
                if vlan[i] == -999:
                # se duce pe trunk port
                    if vlan_id != -1:
                        send_to_link(i, length, data)
                    else :
                        tagged_frame = data[0:12] + data[16:]
                        send_to_link(i, length - 4, tagged_frame)
                # se duce pe access
                else:
                    if vlan_id != -1 and vlan_id == vlan[i]:
                        tagged_frame = data[0:12] + create_vlan_tag(vlan_id) + data[12:]
                        send_to_link(i, length + 4, tagged_frame)
                    elif vlan[i] == vlan[interface]:
                        send_to_link(i, length, data)

def access_or_trunk(config):
    global vlan
    with open(config, "r") as file:
        lines = file.readlines()
        lines = lines[1:]

        nr = 0
        for i in lines:
            secv = i.split()
            interface = secv[0]
            id = secv[1].strip()
            if id != 'T':
                vlan[nr] = int(id)
            elif id == 'T':
                vlan[nr] = -999
            nr += 1
            

    



def main():
    # init returns the max interface number. Our interfaces
    # are 0, 1, 2, ..., init_ret value + 1
    global vlan, mac_table
    switch_id = sys.argv[1]
    config = f"configs/switch{switch_id}.cfg"
    num_interfaces = wrapper.init(sys.argv[2:])
    interfaces = range(0, num_interfaces)

    access_or_trunk(config)

    print(f"vlan: {vlan}")
    print("# Starting switch with id {}".format(switch_id), flush=True)
    print("[INFO] Switch MAC", ':'.join(f'{b:02x}' for b in get_switch_mac()))

    # Create and start a new thread that deals with sending BDPU
    t = threading.Thread(target=send_bdpu_every_sec)
    t.start()

    # Printing interface names
    for i in interfaces:
        print(get_interface_name(i))

    while True:
        # Note that data is of type bytes([...]).
        # b1 = bytes([72, 101, 108, 108, 111])  # "Hello"
        # b2 = bytes([32, 87, 111, 114, 108, 100])  # " World"
        # b3 = b1[0:2] + b[3:4].
        interface, data, length = recv_from_any_link()

        dest_mac, src_mac, ethertype, vlan_id = parse_ethernet_header(data)

        # Print the MAC src and MAC dst in human readable format
        dest_mac = ':'.join(f'{b:02x}' for b in dest_mac)
        src_mac = ':'.join(f'{b:02x}' for b in src_mac)

        # Note. Adding a VLAN tag can be as easy as
        # tagged_frame = data[0:12] + create_vlan_tag(10) + data[12:]

        print(f'Destination MAC: {dest_mac}')
        print(f'Source MAC: {src_mac}')
        print(f'EtherType: {ethertype}')

        print("Received frame of size {} on interface {}".format(length, interface), flush=True)

        # TODO: Implement forwarding with learning
        forward_with_learning(interface, dest_mac, src_mac, data, interfaces, length, vlan_id)

        # TODO: Implement VLAN support
    
        # TODO: Implement STP support

        # data is of type bytes.
        # send_to_link(i, length, data)

if __name__ == "__main__":
    main()
