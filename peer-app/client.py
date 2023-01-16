from jsonrpclib import Server
import sys
from datetime import datetime
from latency import get_jitter, get_latency
from discovery import get_cluster_info, save_cluster_info, generate_cluster_info, update_server_leader, update_leader_on_cluster
from election import choose_network_leader
# from throughput import get_throughtput
import os

cluster_list = [{"id": 1, "cluster_name": "cis-lib1", "ip": "196.32.212.213:5141"},
                {"id": 2, "cluster_name": "dicts-01", "ip": "http://localhost:5142"}]


def main():
    port = 5100
    # port = os.getenv('PORT', 5141)
    server = Server(f'http://localhost:{port}')


    try:
        # INSERT NETWORK METRICS      
        print('cluster list')
        clusters_list = get_cluster_info() # fetch and print cluster list 
        print(clusters_list)
        print('current cluster')
        print(clusters_list['current_cluster']['cluster_id'])
        if not clusters_list:
            return
        # loop through cluster list while getting metrics on latency and jitter then store them
        for cluster in clusters_list["clusters_list"]:
            print(cluster[2])
            print(cluster[3])
            store_metrics(server,cluster[2], cluster[3], cluster[0])

        #only using network metrics
        network_metrics = retrive_network_metrics(server) 
        print('choose leader')
        choosen_cluster_id = choose_network_leader(network_metrics)
        update_leader_on_cluster(clusters_list['current_cluster']['cluster_id'],choosen_cluster_id)
        update_server_leader(clusters_list['current_cluster']['cluster_id'],choosen_cluster_id)

        # INSERT AVAILABILITY METRICS
        # cluster_id = 1
        # availability_score = 0
        # date = '28-10-2022'
        # print("Insert availability data..")
        # metrics = (cluster_id, availability_score, date)
        # print(server.insert_availability(metrics))

        # RETRIEVE all network METRICS
        # print("GET network data..")
        # print(server.select_all_network_metrics())

        # RETRIEVE METRICS per cluster
        # cluster_id = 1
        # metric_type = "network"
        # print("Retrieve  " + metric_type +
        #       " data for cluster " + str(cluster_id))
        # print(server.select_metrics_by_cluster(cluster_id, metric_type))

        # Retrieve all cluster info from local db 
        # cluster_id=1
        # name="staging-cluster"
        # ip_address="196.32.212.213"
        # port=6443
        # cluster_info = dict(cluster_id=2,name="staging-cluster", ip_address="localhost", port=5142)
        # print(save_cluster_info(cluster_info))
        # generate_cluster_info()


    except:
        print("Error: ", sys.exc_info())


def store_metrics(server, host, port, cluster_id):
    latency_values = get_latency(host,port)
    jitter = get_jitter(latency_values)
    date = '13-01-2023'
    # throughput = get_throughtput()
    throughput = 20
    metrics = (cluster_id, throughput,round(latency_values[0],3),jitter, date)
    print(metrics)
    print("Inserting network data: latency, throughput & jitter..")
    resp = server.insert_network(metrics)
    print(resp)

def retrive_network_metrics(server):
    print('getting network metrics')
    resp = server.select_all_network_metrics()

    if resp["status"] != 201:
        print('failed to retrive local network metrics')
        return
    print(resp['network data'])
    return resp['network data']
    


if __name__ == '__main__':
    main()
