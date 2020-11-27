#### 2020-11-27

# Running Kubebuilder Tests in a Docker Container

Kubebuilder's `suite_test.go` requires kubetools (etcd, kube-apiserver) to run. If you want to run them in a docker container (on Jenkins, for example), you're going to need a docker image with them installed. Fortunately, there is one, `gcr.io/kubebuilder/thirdparty-{linux,darwin}:<version>`. Unfortunately, it doesn't have golang installed, somewhat scuppering the plan to run go based tests on it.

## Getting golang and kubetools Together

One solution is to maintain you own images - `FROM golang`, and install kubetools. This would mean maintaining your own Dockerfiles with all the combinations of golang version and kubetools version you might need. No thank you.

## Injecting kubetools into golang Container

A better solution is to use an [init container](https://kubernetes.io/docs/concepts/workloads/pods/init-containers/) to inject the kubetools binaries into the golang container:

```
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: golang
    image: golang:1.13
    env:
    - name: KUBEBUILDER_ASSETS
      value: /kubetools/kubebuilder/bin/
    - name: KUBEBUILDER_ATTACH_CONTROL_PLANE_OUTPUT
      value: true
    command:
    - sleep
    args:
    - infinity
    volumeMounts:
    - name: kubetools
      mountPath: "/kubetools"
  initContainers:
  - name: inject-kubetools
    image: gcr.io/kubebuilder/thirdparty-linux:1.16.4
    commmand:
    - tar
    - zxf
    - "/kubebuilder_linux_amd64.tar.gz"
    - "-C"
    - "/kubetools/"
    volumeMounts:
    - name: kubetools
      mountPath: "/kubetools"
  volumes:
  - name: kubetools
    emptyDir: {}
```

This example will:

1. Create a temporary container from the kubetools image with a mounted volume
1. Extract the kubebuilder archive to that volume
1. Create a container from the golang image with the same mounted volume

This gives you a single container with both golang and kubetools installed, capable of executing kubebuilder's test suite.

