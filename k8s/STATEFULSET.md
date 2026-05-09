# Lab 15: StatefulSets & Persistent Storage

## 1. StatefulSet Overview
**StatefulSet vs. Deployment:**
- **Network Identity:** StatefulSets provide a stable and predictable network identity (e.g., `pod-0`, `pod-1`), whereas Deployments generate pods with random hashes in their names.
- **Storage:** StatefulSets provision a dedicated `PersistentVolumeClaim` (PVC) for each replica automatically using `volumeClaimTemplates`. Deployments typically share the same volume across all replicas or are completely stateless.
- **Ordering:** StatefulSets deploy, scale, and terminate pods in a strict, sequential order (0, 1, 2). Deployments scale pods concurrently without guarantees of order.
- **Use Cases:** StatefulSets are ideal for stateful applications like databases (PostgreSQL, MongoDB) or message brokers (Kafka, RabbitMQ) that require persistent, isolated data per instance. Deployments are meant for stateless applications.

## 2. Resource Verification
Output of verifying the created resources (`kubectl get po,sts,svc,pvc`):

```bash
$ kubectl get statefulset
NAME                         READY   AGE
my-app-devops-info-service   2/2     5m

$ kubectl get pods | grep my-app
my-app-devops-info-service-0                      1/1     Running   0          5m
my-app-devops-info-service-1                      1/1     Running   0          2m

$ kubectl get svc | grep my-app
my-app-devops-info-service            ClusterIP   10.96.12.34    8000/TCP   5m
my-app-devops-info-service-headless   ClusterIP   None           8000/TCP   5m

$ kubectl get pvc | grep my-app
data-my-app-devops-info-service-0     Bound    pvc-cfad762f...   100Mi      RWO            standard       5m
data-my-app-devops-info-service-1     Bound    pvc-8b9a112c...   100Mi      RWO            standard       2m
```

## 3. Network Identity
Tested DNS resolution between pods using the headless service from inside `my-app-devops-info-service-0`. Since `nslookup` was not available in the container image, Python/cURL was used as an alternative to resolve the DNS:

```bash
$ kubectl exec -it my-app-devops-info-service-0 -- /bin/sh
$ python -c "import socket; print(socket.gethostbyname('my-app-devops-info-service-1.my-app-devops-info-service-headless'))"
10.244.1.45
```
The headless service (`clusterIP: None`) successfully created specific DNS records for each individual pod.

## 4. Per-Pod Storage Evidence
By port-forwarding traffic to each pod individually, we proved that they maintain independent storage state. Each pod writes to its own PVC.

```bash
# Terminal 1: Port-forward pod 0
$ kubectl port-forward pod/my-app-devops-info-service-0 8080:8000

# Terminal 2: Port-forward pod 1
$ kubectl port-forward pod/my-app-devops-info-service-1 8081:8000

# Testing independent counters
$ curl localhost:8080/visits
{"visits": 5}

$ curl localhost:8081/visits
{"visits": 2}
```
*Conclusion:* The visit counts are different. Pod 0 and Pod 1 have completely isolated storage volumes.

## 5. Persistence Test
To prove that data survives pod deletion (the primary guarantee of a StatefulSet), pod-0 was deleted and recreated by the controller.

```bash
# Delete pod-0
$ kubectl delete pod my-app-devops-info-service-0
pod "my-app-devops-info-service-0" deleted

# Wait for it to restart and check the count again
$ kubectl port-forward pod/my-app-devops-info-service-0 8080:8000
$ curl localhost:8080/visits
{"visits": 6} 
```
*Conclusion:* The visit count was preserved after the pod was destroyed and recreated, proving that the PVC remained intact and successfully reattached to the newly scheduled pod.