from kubernetes import client, config
from kubernetes.client import V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1EnvVar, V1SecurityContext
config.load_kube_config()

class KubeHandeler:
    def __init__(self, agentImage) -> None:
        self.agentImage = agentImage
        self.v1Client = client.CoreV1Api()

    def createPodObj(self, agentId, tasks, packages, masterEndpoint):
        env_vars = [
            V1EnvVar(name="TASKLIST", value=tasks),
            V1EnvVar(name="PACKAGES", value=packages),
            V1EnvVar(name="MASTERENDPOINT", value=masterEndpoint),
            V1EnvVar(name="AGENTID", value=agentId)
        ]
        pod = V1Pod(
            api_version="v1",
            kind="Pod",
            metadata=V1ObjectMeta(name=agentId),
            spec=V1PodSpec(containers=[
                V1Container(
                    name=f"container-{agentId}",
                    image=self.agentImage,  # Example container image
                    ports=[client.V1ContainerPort(container_port=80)],
                    env=env_vars,  # Adding the environment variables
                    security_context=V1SecurityContext(privileged=True)
                )
            ])
        )
        return pod
    def deployPod(self, pod, namespace='default'):
        try:
            api_response = self.v1Client.create_namespaced_pod(
                namespace=namespace,
                body=pod)
            
            print("Pod created. Status='%s'" % str(api_response.status))
        except client.exceptions.ApiException as e:
            print("Exception when creating a Pod: %s\n" % e)

    def createPod(self, agentId, tasks, packages, masterEndpoint):
        podObj = self.createPodObj(agentId=agentId, tasks=tasks, packages=packages, masterEndpoint=masterEndpoint)
        self.deployPod(podObj)









def main():
    k8 = KubeHandeler(agentImage="ubuntu")
    k8.createPod("122222222222222222222","asdnoiuah sdiaidhiuashdi uhaisdhiausdiuash",'[asd,asd,asd]',"test.com")




if __name__ == '__main__':
    main()
