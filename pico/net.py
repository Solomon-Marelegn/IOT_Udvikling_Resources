import network
import time

def get_signal_strength(ap):
    return ap[3]

def net_connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    all_aps = wlan.scan()
    filtered_aps = []
    for ap in all_aps:
        if ap[0].decode('utf-8') == ssid:
            filtered_aps.append(ap)
            
    if len(filtered_aps) == 0:
        return
    
    sorted_aps = sorted(filtered_aps, key=get_signal_strength, reverse=True)

    selected_ap = sorted_aps[0]
    mac_address = ':'.join(['{:02x}'.format(b) for b in selected_ap[1]])
    wlan.connect(ssid, password)

    timeout = 20
    start_time = time.time()

    while not wlan.isconnected():
        print('Connecting to {}: Waiting...'.format(ssid))
        time.sleep(1)

        if time.time() - start_time > timeout:
            print('Connection timeout. Unable to connect to {}.'.format(ssid))
            break

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print(f"ip {ip}  ap_mac {mac_address}, dbm {selected_ap[3]}")
        return (mac_address)
    


