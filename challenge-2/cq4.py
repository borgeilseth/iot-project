import pyshark

"""
How many different MQTT clients specify a last Will Message to be 
directed to a topic having as first level "university"?
"""

pcap_file = "challenge-2/challenge2.pcapng"
capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")

mqtt_will = []
for packet in capture:
    mqtt_willmsg = packet.mqtt.get("mqtt.willmsg")
    mqtt_willtopic = packet.mqtt.get("mqtt.willtopic")
    if mqtt_willmsg and mqtt_willtopic.startswith("university"):
        mqtt_will.append(packet)

capture.close()

unique_clients = set()
for packet in mqtt_will:
    ip_src = packet.ip.src if hasattr(packet, "ip") else packet.ipv6.src
    is_ipv6 = hasattr(packet, "ipv6")
    tcp_src = packet.tcp.srcport
    if ip_src:
        if is_ipv6:
            unique_clients.add(f"[{ip_src}]:{tcp_src}")
        else:
            unique_clients.add(f"{ip_src}:{tcp_src}")


print(f"Number of unique clients: {len(unique_clients)}")
print(f"Unique clients:", unique_clients)
