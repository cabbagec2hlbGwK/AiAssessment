from kubernetes import client, config
from kubernetes.client import V1Pod, V1ObjectMeta, V1PodSpec, V1Container, V1EnvVar, V1SecurityContext
config.load_kube_config()
#---------------



if __name__ == '__main__':
    main()
