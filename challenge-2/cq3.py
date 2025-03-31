import pyshark
from pyshark.packet.packet import Packet

# Load pcap file
pcap_file = "challenge-2/challenge2.pcapng"
capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")

mqtt_subscribe = []
for packet in capture:
    mqtt_msgtype = int(packet.mqtt.get("mqtt.msgtype"))
    mqtt_topic = packet.mqtt.get("mqtt.topic")
    ip_dst = packet.ip.dst if hasattr(packet, "ip") else packet.ipv6.dst
    if (
        mqtt_msgtype == 8
        and "#" in mqtt_topic
        and ip_dst in ["35.158.43.69", "35.158.34.213", "18.192.151.104"]
    ):
        mqtt_subscribe.append(packet)

capture.close()

# Determine amound of unique clients
unique_clients = set()
for packet in mqtt_subscribe:
    ip_src = packet.ip.src if hasattr(packet, "ip") else packet.ipv6.src
    tcp_src = packet.tcp.srcport
    if ip_src:
        unique_clients.add(f"{ip_src}:{tcp_src}")

# Print the number of unique clients
print(f"Number of unique clients: {len(unique_clients)}")
print(f"Unique clients:", unique_clients)
