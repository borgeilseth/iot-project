import pyshark
from utils import unique_clients, extract_dns_ips

PCAP_FILE = "challenge-2/challenge2.pcapng"
HOSTNAME = "broker.hivemq.com"


def main():
    # Extract IPs from DNS packets
    ips = extract_dns_ips(PCAP_FILE, HOSTNAME)

    # Find MQTT subscribers
    packets = find_mqtt_subscribers(PCAP_FILE, ips)

    # Filter packets to find unique clients
    clients = unique_clients(packets)

    print(f"Number of unique clients: {len(clients)}")


# Load pcap file
def find_mqtt_subscribers(pcap_file, ips):
    capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")
    mqtt_subscribers = []
    for packet in capture:
        mqtt_msgtype = packet.mqtt.get("mqtt.msgtype")
        mqtt_topic = packet.mqtt.get("mqtt.topic")
        ip_dst = packet.ip.dst if hasattr(packet, "ip") else packet.ipv6.dst

        if mqtt_msgtype == "8" and "#" in mqtt_topic and ip_dst in ips:
            mqtt_subscribers.append(packet)

    capture.close()
    return mqtt_subscribers


if __name__ == "__main__":
    main()
