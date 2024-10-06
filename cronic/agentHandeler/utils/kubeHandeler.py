from kubernetes import client, config
from kubernetes.client import V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1EnvVar
config.load_kube_config()

class KubeHandeler:
    def __init__(self, agentImage) -> None:
        self.agentImage = agentImage

def create_pod_object():
    env_vars = [
        V1EnvVar(name="MY_ENV_VAR", value="my-value"),
        V1EnvVar(name="ANOTHER_ENV_VAR", value="another-value")
    ]
    pod = V1Pod(
        api_version="v1",
        kind="Pod",
        metadata=V1ObjectMeta(name="my-pod"),
        spec=V1PodSpec(containers=[
            V1Container(
                name="my-container",
                image="nginx",  # Example container image
                ports=[client.V1ContainerPort(container_port=80)],
                env=env_vars  # Adding the environment variables
            )
        ])
    )
    return pod
def deploy_pod(api_instance, pod, namespace='default'):
    try:
        api_response = api_instance.create_namespaced_pod(
            namespace=namespace,
            body=pod)
        
        print("Pod created. Status='%s'" % str(api_response.status))
    except client.exceptions.ApiException as e:
        print("Exception when creating a Pod: %s\n" % e)

if __name__ == '__main__':
    # Create a Pod object
    my_pod = create_pod_object()

    # Create an API instance
    v1 = client.CoreV1Api()

    # Deploy the Pod
    deploy_pod(v1, my_pod)
