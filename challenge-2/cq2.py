import pyshark

#Helping funciton to find the number X of unique Confirmable GET requests for the resource
def number_of_different_CON_req(resource):
    capture = pyshark.FileCapture(pcap_file, display_filter="coap.code==1 && ip.addr==134.102.218.18")
    
    CON_GET_tokens = []

    for packet in capture:
        if hasattr(packet, "coap"):
            coap_type = int(packet.coap.get("coap.type"))
            coap_code = int(packet.coap.get("coap.code"))
            coap_token = packet.coap.get("coap.token")
            coap_resource = packet.coap.get("coap.opt.uri_path")

            # Check if it is a Confirmable GET request (coap.type = 0, coap.code = 1) and the given resource
            if coap_type == 0 and coap_code == 1 and coap_resource == resource:
                if coap_token not in CON_GET_tokens:
                    CON_GET_tokens.append(coap_token)

    capture.close()              
    # Return the number X of unique Confirmable GET requests for the resource
    return len(CON_GET_tokens)

#Helping funciton to find the number Y of unique Non-Confirmable GET requests for the resource
def number_of_different_NON_req(resource):
    capture = pyshark.FileCapture(pcap_file, display_filter="coap.code==1 && ip.addr==134.102.218.18")
    
    NON_GET_tokens = []

    for packet in capture:
        if hasattr(packet, "coap"):
            coap_type = int(packet.coap.get("coap.type"))
            coap_code = int(packet.coap.get("coap.code"))
            coap_token = packet.coap.get("coap.token")
            coap_resource = packet.coap.get("coap.opt.uri_path")

            # Check if it is a Non-Confirmable GET request (coap.type = 1, coap.code = 1) and the given resource
            if coap_type == 1 and coap_code == 1 and coap_resource == resource:
                if coap_token not in NON_GET_tokens:
                    NON_GET_tokens.append(coap_token)

    capture.close()              
    # Return the number Y of unique Non-Confirmable GET requests for the resource
    return len(NON_GET_tokens)


# For each resource, find X=number_of_different_CON_req for the resource AND Y=number_of_different_NON_req for the resource
# Then count for how many resources X=Y (with X>0). 
def number_of_unique_CON_and_NON_GET_requests(pcap_file): 
    # Filter by GET requests (coap.code==1) and only packets sent to the coap.me public server (ip.addr==134.102.218.18)
    capture = pyshark.FileCapture(pcap_file, display_filter="coap.code==1 && ip.addr==134.102.218.18")

    resources = []
    count = 0

    for packet in capture:
        if hasattr(packet, "coap"):
            coap_resource = packet.coap.get("coap.opt.uri_path")

            if coap_resource not in resources:
                resources.append(coap_resource)
                X = number_of_different_CON_req(coap_resource)
                Y = number_of_different_NON_req(coap_resource)
                if X > 0 and X == Y:
                    count+=1

    print(f"RESULT:\nNumber of resources that received the same number of unique Confirmable and Non Confirmable GET requests: ", count)
    capture.close()              
    
pcap_file = "challenge-2/challenge2.pcapng"
number_of_unique_CON_and_NON_GET_requests(pcap_file)




### DELETE (but does work as well) ###

def count_matching_resources(pcap_file):
    # Dictionary to store the number of unique CONF and NON GET requests per resource
    resource_requests = {}

    # Open the pcap file and filter only CoAP GET requests
    capture = pyshark.FileCapture(pcap_file, display_filter="coap.code==1 && ip.addr==134.102.218.18")

    for packet in capture:
        if hasattr(packet, "coap"):
            coap_type = int(packet.coap.get("coap.type"))  # 0 = CONF, 1 = NON
            uri_path = packet.coap.get("coap.opt.uri_path")  # Get resource path

            if uri_path not in resource_requests:
                resource_requests[uri_path] = {"CONF": set(), "NON": set()}

            # Track unique requests based on Message ID (MID)
            message_id = packet.coap.get("coap.mid")
            if coap_type == 0:  # Confirmable request
                resource_requests[uri_path]["CONF"].add(message_id)
            elif coap_type == 1:  # Non-Confirmable request
                resource_requests[uri_path]["NON"].add(message_id)

    capture.close()

    # Count how many resources have X = Y with X > 0
    matching_resources_count = 0
    for resource, requests in resource_requests.items():
        num_conf = len(requests["CONF"])
        num_non = len(requests["NON"])
        if num_conf == num_non and num_conf > 0:
            matching_resources_count += 1

    print(f"Number of resources with X = Y (X > 0): {matching_resources_count}")

# Run the function on your pcap file
# pcap_file = "challenge-2/challenge2.pcapng"
# count_matching_resources(pcap_file)