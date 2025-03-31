import pyshark
from utils import unique_clients

PCAP_FILE = "challenge-2/challenge2.pcapng"


def main():
    mqtt_will = find_mqtt_will(PCAP_FILE)
    clients = unique_clients(mqtt_will)

    print(f"Number of unique clients: {len(clients)}")


def find_mqtt_will(pcap_file):
    capture = pyshark.FileCapture(pcap_file, display_filter="mqtt")
    mqtt_will = []
    for packet in capture:
        mqtt_willtopic = packet.mqtt.get("mqtt.willtopic")
        if mqtt_willtopic and mqtt_willtopic.startswith("university"):
            mqtt_will.append(packet)

    capture.close()
    return mqtt_will


if __name__ == "__main__":
    main()
