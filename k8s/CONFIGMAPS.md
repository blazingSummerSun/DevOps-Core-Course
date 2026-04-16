# Lab 12 — ConfigMaps & Persistent Volumes (DevOps Info Service)

---

## 1) Application Changes (Visits Counter)

### What was implemented
- Added a visits counter stored in a file: `/data/visits`
- Root endpoint `GET /` increments the counter and persists it
- New endpoint `GET /visits` returns current visits value

### File format
- Plain text integer in `/data/visits`

### Local test with Docker (persistence across restarts)

**Docker compose (volume mount):**
- Host directory mounted to container `/data`

**Commands & output:**
```bash
# Start
cd monitoring
docker compose up --build -d

# Generate some requests
curl http://localhost:8000/
curl http://localhost:8000/visits

# Check file on host
cat ../data/visits

# Restart and verify persistence
docker compose restart app-python
curl http://localhost:8000/visits
cat ../data/visits
```

```bash
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/

{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"},{"description":"Visits counter","method":"GET","path":"/visits"}],"request":{"client_ip":"172.21.0.1","method":"GET","path":"/","user_agent":"curl/7.81.0"},"runtime":{"current_time":"2026-04-15T20:30:49.721277+00:00","timezone":"UTC","uptime_human":"0 hours, 0 minutes","uptime_seconds":5},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":4,"hostname":"5a4bdc55602d","platform":"Linux","platform_version":"#106~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 08:44:59 UTC ","python_version":"3.12.13"},"visits":{"count":1}}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/visits

{"visits":1}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/visits

{"visits":1}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/visits

{"visits":1}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> cat ../data/visits

1⏎                                                                                                                                                                                                                       
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/visits

{"visits":1}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> curl http://localhost:8000/

{"endpoints":[{"description":"Service information","method":"GET","path":"/"},{"description":"Health check","method":"GET","path":"/health"},{"description":"Visits counter","method":"GET","path":"/visits"}],"request":{"client_ip":"172.21.0.1","method":"GET","path":"/","user_agent":"curl/7.81.0"},"runtime":{"current_time":"2026-04-15T20:31:12.666523+00:00","timezone":"UTC","uptime_human":"0 hours, 0 minutes","uptime_seconds":28},"service":{"description":"DevOps course info service","framework":"Flask","name":"devops-info-service","version":"1.0.0"},"system":{"architecture":"x86_64","cpu_count":4,"hostname":"5a4bdc55602d","platform":"Linux","platform_version":"#106~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 08:44:59 UTC ","python_version":"3.12.13"},"visits":{"count":2}}
dreamcore@californiawrld ~/P/D/monitoring (lab12)> cat ../data/visits

2⏎    
```

---

## 2) ConfigMaps

### 2.1 ConfigMap as a mounted file

**Source file in Helm chart:**
- `k8s/devops-info-service/files/config.json`

**ConfigMap template:**
- `k8s/devops-info-service/templates/configmap.yaml`

**Mount path in the container:**
- `/config/config.json` (via mounting directory `/config`)

**Verification:**
```bash
kubectl get configmap -n lab12
kubectl exec -n lab12 <POD_NAME> -- ls -la /config
kubectl exec -n lab12 <POD_NAME> -- cat /config/config.json
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12) [1]> kubectl get pods -n lab12
NAME                                               READY   STATUS    RESTARTS   AGE
devops-info-devops-info-service-54b7fc6cbc-fvxxm   1/1     Running   0          4m20s
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm  -- ls -la /config

total 12
drwxrwxrwx 3 root root 4096 Apr 15 21:28 .
drwxr-xr-x 1 root root 4096 Apr 15 21:28 ..
drwxr-xr-x 2 root root 4096 Apr 15 21:28 ..2026_04_15_21_28_37.844327563
lrwxrwxrwx 1 root root   31 Apr 15 21:28 ..data -> ..2026_04_15_21_28_37.844327563
lrwxrwxrwx 1 root root   18 Apr 15 21:28 config.json -> ..data/config.json
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- cat /config/config.json
{
  "appName": "devops-info-service",
  "environment": "dev",
  "features": {
    "visitsCounter": true
  }
}⏎                             
```

### 2.2 ConfigMap as environment variables

**Template:**
- `k8s/devops-info-service/templates/configmap-env.yaml`

**Injected via:**
- `envFrom.configMapRef` in `k8s/devops-info-service/templates/deployment.yaml`

**Verification:**
```bash
kubectl exec -n lab12 <POD_NAME> -- printenv | grep -E 'APP_ENV|LOG_LEVEL'
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- printenv | grep -E 'APP_ENV|LOG_LEVEL'
LOG_LEVEL=info
APP_ENV=dev
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl get configmap -n lab12

NAME                                     DATA   AGE
devops-info-devops-info-service-config   1      47m
devops-info-devops-info-service-env      3      47m
kube-root-ca.crt                         1      47m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- cat /config/config.json
{
  "appName": "devops-info-service",
  "environment": "dev",
  "features": {
    "visitsCounter": true
  }
}⏎                                                                                                                                                                                                                       
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- printenv | grep -E 'APP_ENV|LOG_LEVEL'
LOG_LEVEL=info
APP_ENV=dev

```

### 2.3 Combined verification output (required)
```bash
kubectl get configmap -n lab12
kubectl exec -n lab12 <POD_NAME> -- cat /config/config.json
kubectl exec -n lab12 <POD_NAME> -- printenv | grep -E 'APP_ENV|LOG_LEVEL'
```

---

## 3) Persistent Volume (PVC)

### PVC configuration
- Access mode: `ReadWriteOnce`
- Size: `100Mi`
- StorageClass: `standard` (minikube default)

**PVC template:**
- `k8s/devops-info-service/templates/pvc.yaml`

**Mounted into container:**
- PVC mounted at `/data`

### Verification: PVC exists and is Bound
```bash
kubectl get pvc -n lab12
kubectl describe pvc -n lab12 devops-info-devops-info-service-data
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl get pvc -n lab12

NAME                                   STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
devops-info-devops-info-service-data   Bound    pvc-e30b6a9a-fb4a-419c-9e40-6fef1d31eab2   100Mi      RWO            standard       <unset>                 31m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl describe pvc -n lab12 devops-info-devops-info-service-data

Name:          devops-info-devops-info-service-data
Namespace:     lab12
StorageClass:  standard
Status:        Bound
Volume:        pvc-e30b6a9a-fb4a-419c-9e40-6fef1d31eab2
Labels:        app.kubernetes.io/instance=devops-info
               app.kubernetes.io/managed-by=Helm
               app.kubernetes.io/name=devops-info-service
               app.kubernetes.io/part-of=devops-core-course
               app.kubernetes.io/version=v2
               helm.sh/chart=devops-info-service-0.1.0
Annotations:   meta.helm.sh/release-name: devops-info
               meta.helm.sh/release-namespace: lab12
               pv.kubernetes.io/bind-completed: yes
               pv.kubernetes.io/bound-by-controller: yes
               volume.beta.kubernetes.io/storage-provisioner: k8s.io/minikube-hostpath
               volume.kubernetes.io/storage-provisioner: k8s.io/minikube-hostpath
Finalizers:    [kubernetes.io/pvc-protection]
Capacity:      100Mi
Access Modes:  RWO
VolumeMode:    Filesystem
Used By:       devops-info-devops-info-service-54b7fc6cbc-fvxxm
Events:
  Type    Reason                 Age   From                                                                    Message
  ----    ------                 ----  ----                                                                    -------
  Normal  Provisioning           31m   k8s.io/minikube-hostpath_minikube_88588f97-b427-4163-ac66-28cc3abd1935  External provisioner is provisioning volume for claim "lab12/devops-info-devops-info-service-data"
  Normal  ExternalProvisioning   31m   persistentvolume-controller                                             Waiting for a volume to be created either by the external provisioner 'k8s.io/minikube-hostpath' or manually by the system administrator. If volume creation is delayed, please verify that the provisioner is running and correctly registered.
  Normal  ProvisioningSucceeded  31m   k8s.io/minikube-hostpath_minikube_88588f97-b427-4163-ac66-28cc3abd1935  Successfully provisioned volume pvc-e30b6a9a-fb4a-419c-9e40-6fef1d31eab2

```

### Persistence test (required evidence)

**1) Before pod deletion:**
```bash
kubectl get pods -n lab12
kubectl exec -n lab12 <POD_NAME> -- ls -la /data
kubectl exec -n lab12 <POD_NAME> -- cat /data/visits
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl get pods -n lab12

NAME                                               READY   STATUS    RESTARTS   AGE
devops-info-devops-info-service-54b7fc6cbc-fvxxm   1/1     Running   0          6m29s
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- ls -la /data
total 16
drwxrwxrwx 2 root    root    4096 Apr 15 21:28 .
drwxr-xr-x 1 root    root    4096 Apr 15 21:28 ..
-rw-r--r-- 1 appuser appuser    5 Apr 15 21:13 _writecheck
-rw-r--r-- 1 appuser appuser    1 Apr 15 21:28 visits
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- cat /data/visits
1⏎                                              
```

**2) Delete pod (not deployment):**
```bash
kubectl delete pod -n lab12 <POD_NAME>
kubectl get pods -n lab12
```

**3) After new pod starts:**
```bash
kubectl exec -n lab12 <NEW_POD_NAME> -- ls -la /data
kubectl exec -n lab12 <NEW_POD_NAME> -- cat /data/visits
```

```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl get pods -n lab12

NAME                                               READY   STATUS    RESTARTS   AGE
devops-info-devops-info-service-54b7fc6cbc-fvxxm   1/1     Running   0          6m29s
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- ls -la /data
total 16
drwxrwxrwx 2 root    root    4096 Apr 15 21:28 .
drwxr-xr-x 1 root    root    4096 Apr 15 21:28 ..
-rw-r--r-- 1 appuser appuser    5 Apr 15 21:13 _writecheck
-rw-r--r-- 1 appuser appuser    1 Apr 15 21:28 visits
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm -- cat /data/visits
1⏎                                                                                                                                                                                                                       
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl delete pod -n lab12 devops-info-devops-info-service-54b7fc6cbc-fvxxm
pod "devops-info-devops-info-service-54b7fc6cbc-fvxxm" deleted from lab12 namespace
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl get pods -n lab12

NAME                                               READY   STATUS    RESTARTS   AGE
devops-info-devops-info-service-54b7fc6cbc-m7qkh   1/1     Running   0          32s
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-m7qkh -- ls -la /data
total 16
drwxrwxrwx 2 root    root    4096 Apr 15 21:28 .
drwxr-xr-x 1 root    root    4096 Apr 15 21:35 ..
-rw-r--r-- 1 appuser appuser    5 Apr 15 21:13 _writecheck
-rw-r--r-- 1 appuser appuser    1 Apr 15 21:28 visits
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab12)> kubectl exec -n lab12 devops-info-devops-info-service-54b7fc6cbc-m7qkh -- cat /data/visits
1⏎                                                
```

Result: `/data/visits` value persisted after pod recreation.

---

## 4) ConfigMap vs Secret

### When to use ConfigMap
Use ConfigMap for **non-sensitive** configuration:
- feature flags
- environment name (dev/prod)
- log level
- endpoints, timeouts, non-secret parameters

### When to use Secret
Use Secret for **sensitive** data:
- passwords
- API tokens
- private keys/certificates
- database credentials

### Key differences
- **Security**: Secrets are intended for sensitive values and integrate with RBAC and encryption-at-rest (when configured). ConfigMaps are not for secrets.
- **Usage**: Both can be mounted as files or injected as env vars.
- **Best practice**: never store credentials in ConfigMaps; use Secrets (or external secret managers like Vault).