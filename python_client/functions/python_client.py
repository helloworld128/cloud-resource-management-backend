# -*- coding: utf-8 -*-

import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
import random
import time
from kubernetes.stream import stream
config.load_kube_config()
v1 = client.CoreV1Api()


def create_namespaced_service(problem_id):
    metadata = client.V1ObjectMeta(
        name="service-"+str(problem_id), labels={"problem_id"+str(problem_id): str(problem_id)})
    service_port = client.V1ServicePort(
        name="port", port=30306, target_port=22, protocol="TCP")
    ports = [service_port]
    spec = client.V1ServiceSpec(type="ClusterIp", ports=ports, selector={
                                "problem_id"+str(problem_id): str(problem_id)})
    status = client.V1ServiceStatus()
    body = client.V1Service("v1", "Service", metadata, spec, status)
    try:
        api_response = v1.create_namespaced_service("default", body)
        return "Success"
    except ApiException as e:
        return "Failed"


def create_persistent_volume(problem_id, index, storage="5Gi"):
    metadata = client.V1ObjectMeta(
        name="pv-"+str(problem_id)+"-"+str(index), labels={"problem_id"+str(problem_id): str(problem_id)})
    nfs = client.V1NFSVolumeSource(
        path="/home/ubuntu/data/problems/"+str(problem_id), server="172.21.1.1")
    spec = client.V1PersistentVolumeSpec(capacity={"storage": "5Gi"},
                                         access_modes=["ReadWriteOnce"],
                                         storage_class_name="nfs",
                                         nfs=nfs
                                         )
    status = client.V1PersistentVolumeStatus()
    body = client.V1PersistentVolume(
        "v1", "PersistentVolume", metadata, spec, status)

    try:
        api_response = v1.create_persistent_volume(body)
        return "Success"

    except ApiException as e:
        return 'Failed'


def create_namespaced_persistent_volume_claim(problem_id, index, storage="5Gi"):
    metadata = client.V1ObjectMeta(
        name="pvc-"+str(problem_id)+"-"+str(index), labels={"problem_id"+str(problem_id): str(problem_id)})
    req = client.V1ResourceRequirements(requests={"storage": storage})
    label_selector = client.V1LabelSelector(
        match_labels={"problem_id"+str(problem_id): str(problem_id)})
    spec = client.V1PersistentVolumeClaimSpec(
        access_modes=["ReadWriteOnce"], resources=req, storage_class_name="nfs", selector=label_selector)
    status = client.V1PersistentVolumeClaimStatus(
        access_modes=["ReadWriteOnce"])
    body = client.V1PersistentVolumeClaim(
        "v1", "PersistentVolumeClaim", metadata, spec, status)

    try:
        api_response = v1.create_namespaced_persistent_volume_claim(
            "default", body)
        return 'Success'
    except ApiException as e:
        return "Failed"


def create_working_namespaced_pod(problem_id, index, storage="1Gi", image="mysshd"):
    pod_config = {
        "metadata": {"name": "pod-"+str(problem_id)+"-"+str(index), "labels": {"problem_id"+str(problem_id): str(problem_id)}},
        "spec": {
            "volumes": [
                {
                    "name": "pv-"+str(problem_id)+"-"+str(index),
                    "persistentVolumeClaim":
                        {
                            "claimName": "pvc-"+str(problem_id)+"-"+str(index)
                    }
                },
            ],
            "containers": [
                {
                    "name": "container-"+str(problem_id)+"-"+str(index),
                    "image": image,
                    "imagePullPolicy": "IfNotPresent",
                    "volumeMounts": [
                        {"name": "pv-"+str(problem_id)+"-"+str(index),
                            "mountPath": "/mnt"},
                    ],
                    "ports": [
                        {
                            "containerPort": 22
                        },
                    ]
                }
            ],
        },
    }
    try:
        api_response = v1.create_namespaced_pod("default", pod_config)
        return "Success"
    except ApiException as e:
        return 'Failed'


def list_namespaced_pod(namespace_name="default"):
    try:
        api_response = v1.list_namespaced_pod(namespace_name)
        return "Success"
    except ApiException as e:
        return "Failed"


def list_serviced_pod(problem_id):
    label_selector = "problem_id"+str(problem_id)
    try:
        api_response = v1.list_namespaced_pod(
            namespace='default', label_selector=label_selector)
        for pod in api_response.items:
            return "Success"
    except ApiException as e:
        return "Failed"


def del_persistent_volume(problem_id):
    name = "pv-"+str(problem_id)
    body = client.V1DeleteOptions()
    try:
        api_response = v1.delete_persistent_volume(name, body=body)
        return "Success"
    except ApiException as e:
        return "Failed"


def del_namespaced_persistent_volume_claim(problem_id):
    name = "pvc-"+str(problem_id)
    body = client.V1DeleteOptions()

    try:
        api_response = v1.delete_namespaced_persistent_volume_claim(
            name, "default", body=body)
        return "Success"
    except ApiException as e:
        return "Failed"


def del_namespaced_pod(problem_id):
    name = 'pod-'+str(problem_id)
    body = client.V1DeleteOptions()

    try:
        api_response = v1.delete_namespaced_pod(name, "default", body=body)
        return "Success"
    except ApiException as e:
        return "Failed"


def create_service(problem_id, count, image):
    '''
    创建某一个题目对应的service，并创建指定数量的初始pod
    '''
    status = None
    cluster_ip = None
    port = None
    metadata = client.V1ObjectMeta(
        name="service-"+str(problem_id), labels={"problem_id"+str(problem_id): str(problem_id)})
    service_port = client.V1ServicePort(
        name="port", port=30306, target_port=22, protocol="TCP")
    ports = [service_port]
    spec = client.V1ServiceSpec(type="ClusterIP", ports=ports, selector={
                                "problem_id"+str(problem_id): str(problem_id)})
    status = client.V1ServiceStatus()
    body = client.V1Service("v1", "Service", metadata, spec, status)
    try:
        api_response = v1.create_namespaced_service("default", body)
        status = "Success"
        cluster_ip = api_response.spec.cluster_ip
        port = api_response.spec.ports[0].port
    except ApiException as e:
        status = "Failed"
    result, _ = add_pod(problem_id, count, image, [])
    return status, cluster_ip, port


def exec_command_by_list(pod_list, commands):
    '''
    在指定的pod list中执行命令
    '''
    status = "Success"
    output = {}
    c = Configuration()
    c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    try:
        for pod_name in pod_list:
            resp = None
            try:
                resp = v1.read_namespaced_pod(name=pod_name,
                                              namespace='default')
            except ApiException as e:
                if e.status != 404:
                    status = "Failed"
            if not resp:
                status = "Failed"
            exec_command = ['/bin/sh']
            resp = stream(core_v1.connect_get_namespaced_pod_exec,
                          pod_name,
                          'default',
                          command=exec_command,
                          stderr=True, stdin=True,
                          stdout=True, tty=False,
                          _preload_content=False)
            if len(commands) > 0:
                for command in commands:
                    resp.write_stdin(command)
                    sdate = resp.readline_stdout(timeout=3)
                    if pod_name not in output.keys():
                        output[pod_name] = []
                    output[pod_name].append(sdate)
            resp.close()
    except ApiException as e:
        status = "Failed"
    return status, output


def add_pod(problem_id, count, image, command):
    '''
    为某一个service创建一定数目的pod
    '''
    status = "Success"
    success_num = 0
    pod_name_list = []
    for i in range(count):
        index = random.randint(0, 10000)
        pod_name_list.append("pod-"+str(problem_id)+"-"+str(index))
        create_namespaced_service(problem_id=problem_id)
        create_persistent_volume(
            problem_id=problem_id, index=index, storage="1Gi")
        create_namespaced_persistent_volume_claim(
            problem_id=problem_id, index=index, storage="1Gi")
        result = create_working_namespaced_pod(
            problem_id=problem_id, index=index, storage="1Gi", image=image)
        while True:
            resp = v1.read_namespaced_pod(name=pod_name_list[0], namespace='default')
            if resp.status.phase != 'Pending':
                break
            time.sleep(1)
        if result == "Success":
            success_num += 1
    if success_num != count:
        status = "Failed1"
    status2, _ = exec_command_by_list(pod_name_list, command)
    if status2 == "Failed2":
        status = status2
    return status, pod_name_list


def delete_pod_by_list(names):
    '''
    删除list中的pod（包含删除相关的pv,pvc）
    '''
    status = "Success"
    for name in names:
        body = client.V1DeleteOptions()
        try:
            api_response = v1.delete_namespaced_pod(name, "default", body=body)
            api_response = v1.delete_namespaced_persistent_volume_claim(
                'pvc-'+name[4:], "default", body=body)
            api_response = v1.delete_persistent_volume(
                'pv-'+name[4:], body=body)
        except ApiException as e:
            status = "Failed"
    return status


def delete_service(problem_id):
    '''
    删除指定的service
    '''
    name = "service-"+str(problem_id)
    body = client.V1DeleteOptions()
    status = "Success"
    try:
        api_response = v1.delete_namespaced_service(name, "default")
    except ApiException as e:
        status = "Failed"
    return status


def delete_pod_by_service(problem_id):
    '''
    删除某个service下的所有pod
    '''
    status = "Success"
    label_selector = "problem_id"+str(problem_id)
    try:
        api_response = v1.list_namespaced_pod(
            namespace='default', label_selector=label_selector)
        podlist = []
        for pod in api_response.items:
            podlist.append(pod.metadata.name)
    except ApiException as e:
        status = "Failed"
    for name in podlist:
        body = client.V1DeleteOptions()
        try:
            api_response = v1.delete_namespaced_pod(name, "default", body=body)
            api_response = v1.delete_namespaced_persistent_volume_claim(
                'pvc-'+name[4:], "default", body=body)
            api_response = v1.delete_persistent_volume(
                'pv-'+name[4:], body=body)
        except ApiException as e:
            status = "Failed"
    return status


def exec_command_by_service(problem_id, commands):
    '''
    在指定的service下的所有pod里面执行命令
    '''
    label_selector = "problem_id"+str(problem_id)
    status = "Success"
    output = {}
    c = Configuration()
    c.assert_hostname = False
    Configuration.set_default(c)
    core_v1 = core_v1_api.CoreV1Api()
    try:
        api_response = v1.list_namespaced_pod(
            namespace='default', label_selector=label_selector)
        podlist = []
        for pod in api_response.items:
            podlist.append(pod.metadata.name)
        for pod_name in podlist:
            resp = None
            exec_command = ['/bin/sh']
            try:
                resp = stream(core_v1.connect_get_namespaced_pod_exec,
                              pod_name,
                              'default',
                              command=exec_command,
                              stderr=True, stdin=True,
                              stdout=True, tty=False,
                              _preload_content=False)
            except ApiException as e:
                status = "Failed"
            for command in commands:
                resp.write_stdin(command)
                sdate = resp.readline_stdout(timeout=3)
                if pod_name not in output.keys():
                    output[pod_name] = []
                output[pod_name].append(sdate)
        resp.close()
    except ApiException as e:
        status = "Failed"
    return status, output


def judge(problem_id, image, cmd, max_time, max_memory, max_cpu_percentage):
    '''
    评测函数
    '''
    _, pod_name_list = add_pod(problem_id, 1, image, [])
    while True:
        resp = v1.read_namespaced_pod(
            name=pod_name_list[0], namespace='default')
        if resp.status.phase != 'Pending':
            break
        time.sleep(1)
    status, output = exec_command_by_list(pod_name_list, cmd)
    _, memory_output = exec_command_by_list(pod_name_list, ["cat /sys/fs/cgroup/memory/memory.usage_in_bytes\n"])
    memory_usage = int(memory_output[pod_name_list[0]][0])/1000000
    _ = delete_pod_by_list(pod_name_list)
    stdout = output[pod_name_list[0]][0]#读取标准输出
    retout = stdout
    out_list = stdout.split(" ")
    stdout = out_list[0]
    time_cost = int(out_list[1])
    if stdout == "1":
        stdout = "Wrong Answer"
    else: 
        if stdout == "0":
            stdout = "Accepted"
        else: 
            if stdout == None:
                stdout = "Runtime Error"
            else:
                stdout = "Judge Script Error"
    if time_cost > max_time:
        stdout = "Time Limit Exceeded"
    if memory_usage > max_memory:
        stdout = "Memory Limit Exceeded"
    return status, retout, stdout

if __name__ == "__main__":
    pass
