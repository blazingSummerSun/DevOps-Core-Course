
## 1) Kubernetes Secrets

### 1.1 Output of creating and viewing your secret

**Create secret**
```bash
kubectl create secret generic app-credentials \
  --from-literal=username='demo-user' \
  --from-literal=password='demo-pass-123'
```

Output:
```text
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl create secret generic app-credentials \
                                                               --from-literal=username='demo-user' \
                                                               --from-literal=password='demo-pass-123'
error: failed to create secret secrets "app-credentials" already exists

```

**View secret YAML**
```bash
kubectl get secret app-credentials -o yaml
```

Output:
```yaml
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11) [1]> kubectl get secret app-credentials -o yaml

apiVersion: v1
data:
  password: ZGVtby1wYXNzLTEyMw==
  username: ZGVtby11c2Vy
kind: Secret
metadata:
  creationTimestamp: "2026-04-09T17:47:35Z"
  name: app-credentials
  namespace: default
  resourceVersion: "154984"
  uid: b24fc3ed-9f4c-4c19-afa2-8ae8b9af0260
type: Opaque

```

### 1.2 Decoded secret values demonstration

Decode (example):
```bash
kubectl get secret app-credentials -o jsonpath='{.data.username}' | base64 --decode; echo
kubectl get secret app-credentials -o jsonpath='{.data.password}' | base64 --decode; echo
```

Output (sanitized):
```text
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get secret app-credentials -o jsonpath='{.data.username}' | base64 --decode; echo

demo-user
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> 
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get secret app-credentials -o jsonpath='{.data.password}' | base64 --decode; echo

demo-pass-123

```

### 1.3 Explanation of base64 encoding vs encryption

- **Base64 is encoding, not encryption.** It is reversible without any key. Kubernetes Secrets are commonly stored in manifests and transmitted as base64 strings, but that does not provide confidentiality.
- Without additional measures, anyone with sufficient Kubernetes API permissions (e.g., `get secrets`) can retrieve and decode secret values.
- To protect secrets **at rest** (in etcd), Kubernetes supports **encryption at rest** (API server EncryptionConfiguration). This encrypts secret data stored in etcd, but authorized API callers will still receive the decrypted values.

---

## 2) Helm Secret Integration

### 2.1 Chart structure showing secrets.yaml

Relevant chart files:
- `k8s/devops-info-service/templates/secrets.yaml` — creates `Secret`
- `k8s/devops-info-service/templates/deployment.yaml` — consumes secret via `envFrom.secretRef`
- `k8s/devops-info-service/values.yaml` — contains placeholder values (`change-me`)

**secrets.yaml (structure)**
```yaml
# (paste sanitized version of your templates/secrets.yaml or the key parts)
PASTE_SECRETS_YAML_TEMPLATE_SNIPPET_HERE
```

### 2.2 How secrets are consumed in deployment

Deployment uses `envFrom` + `secretRef` (all keys from the Secret become env vars):

```yaml
{{- if .Values.secret.enabled }}
envFrom:
  - secretRef:
      name: {{ if .Values.secret.nameOverride }}{{ .Values.secret.nameOverride }}{{ else }}{{ printf "%s-secret" (include "devops-info-service.fullname" .) }}{{ end }}
{{- end }}
```

### 2.3 Verification output (env vars in pod, excluding actual values)

**Verify Secret exists**
```bash
kubectl get secret | grep devops-info-service
kubectl get secret hooktest-devops-info-service-secret -o yaml
```

Output:
```text
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get secret | grep devops-info-service

hooktest-devops-info-service-secret   Opaque               2      73m
```

```yaml
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get secret hooktest-devops-info-service-secret -o yaml

apiVersion: v1
data:
  password: Y2hhbmdlLW1l
  username: Y2hhbmdlLW1l
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: hooktest
    meta.helm.sh/release-namespace: default
  creationTimestamp: "2026-04-09T18:07:41Z"
  labels:
    app.kubernetes.io/instance: hooktest
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: devops-info-service
    app.kubernetes.io/part-of: devops-core-course
    app.kubernetes.io/version: v2
    helm.sh/chart: devops-info-service-0.1.0
  name: hooktest-devops-info-service-secret
  namespace: default
  resourceVersion: "155949"
  uid: 4b46348f-2ea1-4922-bb56-665398feee56
type: Opaque

```

**Verify pod consumes secret (no values shown in describe)**
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11) [1]> kubectl get pods
NAME                                           READY   STATUS    RESTARTS        AGE
hooktest-devops-info-service-65dcbf86d-6qj42   1/1     Running   2 (9m58s ago)   72m
hooktest-devops-info-service-65dcbf86d-8rn64   1/1     Running   2 (9m58s ago)   72m
hooktest-devops-info-service-65dcbf86d-blsj2   1/1     Running   2 (9m58s ago)   72m
hooktest-devops-info-service-65dcbf86d-jvsm6   1/1     Running   2 (9m58s ago)   72m
hooktest-devops-info-service-65dcbf86d-q4drc   1/1     Running   2 (9m58s ago)   72m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl describe pod hooktest-devops-info-service-65dcbf86d-6qj42

Name:             hooktest-devops-info-service-65dcbf86d-6qj42
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Thu, 09 Apr 2026 21:10:23 +0300
Labels:           app.kubernetes.io/instance=hooktest
                  app.kubernetes.io/name=devops-info-service
                  app.kubernetes.io/part-of=devops-core-course
                  pod-template-hash=65dcbf86d
Annotations:      <none>
Status:           Running
IP:               10.244.0.117
IPs:
  IP:           10.244.0.117
Controlled By:  ReplicaSet/hooktest-devops-info-service-65dcbf86d
Containers:
  devops-info-service:
    Container ID:   docker://82c786f79c6b352963eb92e0171aed839ee5e9a7741aad9ff864907ecc01f473
    Image:          sincere99/devops-app:v2
    Image ID:       docker-pullable://sincere99/devops-app@sha256:978ef3a3ef7e6d2ac13c1ae6947d1387848be9de7fe8ed1db462aab0e23691fc
    Port:           5000/TCP (http)
    Host Port:      0/TCP (http)
    State:          Running
      Started:      Thu, 09 Apr 2026 22:13:05 +0300
    Last State:     Terminated
      Reason:       Error
      Exit Code:    137
      Started:      Thu, 09 Apr 2026 22:11:56 +0300
      Finished:     Thu, 09 Apr 2026 22:12:40 +0300
    Ready:          True
    Restart Count:  2
    Limits:
      cpu:     200m
      memory:  256Mi
    Requests:
      cpu:      100m
      memory:   128Mi
    Liveness:   http-get http://:5000/health delay=10s timeout=2s period=5s #success=1 #failure=3
    Readiness:  http-get http://:5000/health delay=5s timeout=2s period=3s #success=1 #failure=3
    Environment Variables from:
      hooktest-devops-info-service-secret  Secret  Optional: false
    Environment:                           <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-vltfp (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       True 
  ContainersReady             True 
  PodScheduled                True 
Volumes:
  kube-api-access-vltfp:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason          Age                  From     Message
  ----     ------          ----                 ----     -------
  Warning  Failed          11m                  kubelet  Error: failed to sync secret cache: timed out waiting for the condition
  Warning  FailedSync      10m (x2 over 10m)    kubelet  error determining status: rpc error: code = Unavailable desc = connection error: desc = "error reading server preface: read unix @->/run/cri-dockerd.sock: read: connection reset by peer"
  Normal   SandboxChanged  10m (x3 over 11m)    kubelet  Pod sandbox changed, it will be killed and re-created.
  Warning  Unhealthy       10m                  kubelet  Readiness probe failed: Get "http://10.244.0.114:5000/health": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
  Warning  BackOff         10m (x4 over 10m)    kubelet  Back-off restarting failed container devops-info-service in pod hooktest-devops-info-service-65dcbf86d-6qj42_default(5c2b81f2-a978-4762-a2ee-d646453b52b5)
  Normal   Pulled          9m42s (x4 over 72m)  kubelet  Container image "sincere99/devops-app:v2" already present on machine and can be accessed by the pod
  Normal   Created         9m42s (x3 over 72m)  kubelet  Container created
  Normal   Started         9m42s (x3 over 72m)  kubelet  Container started

```

**Verify environment variables inside container**
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl exec -it hooktest-devops-info-service-65dcbf86d-6qj42 -- /bin/sh -c 'env | sort | grep -E "username|password"'

password=change-me
username=change-me

```

Notes:
- `kubectl describe pod` shows only references to Secrets (not the values).
- Actual values are visible only from inside the container environment (or to principals with permission to read Secrets).

---

## 3) Resource Management

### 3.1 Resource limits configuration

Configured in `values.yaml` and applied in Deployment as:
```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "200m"
    memory: "256Mi"
```

Proof applied (from pod describe):
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl describe pod hooktest-devops-info-service-65dcbf86d-6qj42
Name:             hooktest-devops-info-service-65dcbf86d-6qj42
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Thu, 09 Apr 2026 21:10:23 +0300
Labels:           app.kubernetes.io/instance=hooktest
                  app.kubernetes.io/name=devops-info-service
                  app.kubernetes.io/part-of=devops-core-course
                  pod-template-hash=65dcbf86d
Annotations:      <none>
Status:           Running
IP:               10.244.0.117
IPs:
  IP:           10.244.0.117
Controlled By:  ReplicaSet/hooktest-devops-info-service-65dcbf86d
Containers:
  devops-info-service:
    Container ID:   docker://82c786f79c6b352963eb92e0171aed839ee5e9a7741aad9ff864907ecc01f473
    Image:          sincere99/devops-app:v2
    Image ID:       docker-pullable://sincere99/devops-app@sha256:978ef3a3ef7e6d2ac13c1ae6947d1387848be9de7fe8ed1db462aab0e23691fc
    Port:           5000/TCP (http)
    Host Port:      0/TCP (http)
    State:          Running
      Started:      Thu, 09 Apr 2026 22:13:05 +0300
    Last State:     Terminated
      Reason:       Error
      Exit Code:    137
      Started:      Thu, 09 Apr 2026 22:11:56 +0300
      Finished:     Thu, 09 Apr 2026 22:12:40 +0300
    Ready:          True
    Restart Count:  2
    Limits:
      cpu:     200m
      memory:  256Mi
    Requests:
      cpu:      100m
      memory:   128Mi
    Liveness:   http-get http://:5000/health delay=10s timeout=2s period=5s #success=1 #failure=3
    Readiness:  http-get http://:5000/health delay=5s timeout=2s period=3s #success=1 #failure=3
    Environment Variables from:
      hooktest-devops-info-service-secret  Secret  Optional: false
    Environment:                           <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-vltfp (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       True 
  ContainersReady             True 
  PodScheduled                True 
Volumes:
  kube-api-access-vltfp:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type     Reason          Age                From     Message
  ----     ------          ----               ----     -------
  Warning  Failed          19m                kubelet  Error: failed to sync secret cache: timed out waiting for the condition
  Warning  FailedSync      19m (x2 over 19m)  kubelet  error determining status: rpc error: code = Unavailable desc = connection error: desc = "error reading server preface: read unix @->/run/cri-dockerd.sock: read: connection reset by peer"
  Normal   SandboxChanged  18m (x3 over 19m)  kubelet  Pod sandbox changed, it will be killed and re-created.
  Warning  Unhealthy       18m                kubelet  Readiness probe failed: Get "http://10.244.0.114:5000/health": context deadline exceeded (Client.Timeout exceeded while awaiting headers)
  Warning  BackOff         18m (x4 over 18m)  kubelet  Back-off restarting failed container devops-info-service in pod hooktest-devops-info-service-65dcbf86d-6qj42_default(5c2b81f2-a978-4762-a2ee-d646453b52b5)
  Normal   Pulled          17m (x4 over 80m)  kubelet  Container image "sincere99/devops-app:v2" already present on machine and can be accessed by the pod
  Normal   Created         17m (x3 over 80m)  kubelet  Container created
  Normal   Started         17m (x3 over 80m)  kubelet  Container started

```

### 3.2 Explanation of requests vs limits

- **Requests**: what the scheduler uses to place the Pod on a node (guaranteed reservation).
- **Limits**: hard caps on usage.  
  - CPU above limit is throttled.
  - Memory above limit can trigger OOMKill for the container.

### 3.3 How to choose appropriate values

Practical approach:
1. Start with observed usage (metrics, load testing).
2. Set **requests** close to typical steady-state consumption.
3. Set **limits** to allow spikes but still protect node stability.
4. Revisit values after monitoring in real workload conditions.

---

## 4) Vault Integration

### 4.1 Vault installation verification (`kubectl get pods`)

```bash
dreamcore@californiawrld:~$ helm repo add hashicorp https://helm.releases.hashicorp.com
"hashicorp" has been added to your repositories

```

```bash
kubectl get pods -n vault
```

Output:
```text
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get pods -n vault

NAME                                   READY   STATUS    RESTARTS   AGE
vault-0                                1/1     Running   0          17m
vault-agent-injector-8c76487db-6dzfc   1/1     Running   0          17m

```

### 4.2 Policy and role configuration (sanitized)

```bash
vault secrets enable -path=secret kv-v2

vault kv put secret/devops-info-service/config username="REDACTED" password="REDACTED"

vault auth enable kubernetes

cat > devops-info-policy.hcl <<'EOF'
path "secret/data/devops-info-service/config" {
  capabilities = ["read"]
}
EOF
vault policy write devops-info devops-info-policy.hcl

# Role bound to Kubernetes service account
vault write auth/kubernetes/role/devops-info \
  bound_service_account_names="devops-info-sa" \
  bound_service_account_namespaces="default" \
  policies="devops-info" \
  ttl="1h"
```

my output
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11) [2]> kubectl get pods -n vault

NAME                                   READY   STATUS    RESTARTS   AGE
vault-0                                1/1     Running   0          21m
vault-agent-injector-8c76487db-6dzfc   1/1     Running   0          21m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get svc -n vault

NAME                       TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)             AGE
vault                      ClusterIP   10.111.111.162   <none>        8200/TCP,8201/TCP   21m
vault-agent-injector-svc   ClusterIP   10.104.177.191   <none>        443/TCP             21m
vault-internal             ClusterIP   None             <none>        8200/TCP,8201/TCP   21m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl exec -it -n vault vault-0 -- /bin/sh

/ $ export VAULT_ADDR="http://127.0.0.1:8200"
/ $ 
/ $ export VAULT_ADDR="http://127.0.0.1:8200"
/ $ vault status
Key             Value
---             -----
Seal Type       shamir
Initialized     true
Sealed          false
Total Shares    1
Threshold       1
Version         1.21.2
Build Date      2026-01-06T08:33:05Z
Storage Type    inmem
Cluster Name    vault-cluster-1545af05
Cluster ID      ebde7685-ae60-948f-1269-226252e53d54
HA Enabled      false
/ $ export VAULT_ADDR="http://127.0.0.1:8200"
/ $ vault secrets enable -path=secret kv-v2
Error enabling: Error making API request.

URL: POST http://127.0.0.1:8200/v1/sys/mounts/secret
Code: 400. Errors:

* path is already in use at secret/
/ $ vault kv put secret/devops-info-service/config \
>   username="vault-user" \
>   password="vault-pass-123"
============= Secret Path =============
secret/data/devops-info-service/config

======= Metadata =======
Key                Value
---                -----
created_time       2026-04-09T19:39:18.855022475Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1
/ $ vault kv get secret/devops-info-service/config
============= Secret Path =============
secret/data/devops-info-service/config

======= Metadata =======
Key                Value
---                -----
created_time       2026-04-09T19:39:18.855022475Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key         Value
---         -----
password    vault-pass-123
username    vault-user

/ $ vault auth enable kubernetes
Success! Enabled kubernetes auth method at: kubernetes/

/ $ vault write auth/kubernetes/config \
>   kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
Success! Data written to: auth/kubernetes/config
/ $ vault read auth/kubernetes/config
Key                                  Value
---                                  -----
disable_iss_validation               true
disable_local_ca_jwt                 false
issuer                               n/a
kubernetes_ca_cert                   n/a
kubernetes_host                      https://10.96.0.1:443
pem_keys                             []
token_reviewer_jwt_set               false
use_annotations_as_alias_metadata    false

/ $ cat > /tmp/devops-info-policy.hcl <<'EOF'
> path "secret/data/devops-info-service/config" {
>   capabilities = ["read"]
> }
> EOF
/ $ 
/ $ vault policy write devops-info /tmp/devops-info-policy.hcl
Success! Uploaded policy: devops-info
/ $ vault policy read devops-info

```
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11) [SIGINT]> kubectl create serviceaccount devops-info-sa -n default

serviceaccount/devops-info-sa created

```
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl exec -it -n vault vault-0 -- /bin/sh

/ $ vault write auth/kubernetes/role/devops-info \
>   bound_service_account_names="devops-info-sa" \
>   bound_service_account_namespaces="default" \
>   policies="devops-info" \
>   ttl="1h"
WARNING! The following warnings were returned from Vault:

  * Role devops-info does not have an audience configured. While audiences are
  not required, consider specifying one if your use case would benefit from
  additional JWT claim verification.

/ $ vault read auth/kubernetes/role/devops-info
Key                                         Value
---                                         -----
alias_name_source                           serviceaccount_uid
bound_service_account_names                 [devops-info-sa]
bound_service_account_namespace_selector    n/a
bound_service_account_namespaces            [default]
policies                                    [devops-info]
token_bound_cidrs                           []
token_explicit_max_ttl                      0s
token_max_ttl                               0s
token_no_default_policy                     false
token_num_uses                              0
token_period                                0s
token_policies                              [devops-info]
token_ttl                                   1h
token_type                                  default
ttl                                         1h
```

Output:
```text
NOT_AVAILABLE_DUE_TO_INSTALLATION_FAILURE
```

### 4.4 Explanation of the sidecar injection pattern

- Vault Agent Injector mutates the Pod spec at admission time.
- It injects a **vault-agent** sidecar container and volumes.
- The agent authenticates to Vault (via Kubernetes auth), fetches secrets, and writes them into files.
- The application container reads secrets from injected files instead of having them stored in Kubernetes Secrets or baked into images.

---

## 5) Security Analysis

### 5.1 Comparison: K8s Secrets vs Vault

**Kubernetes Secrets**
- Pros: built-in, simple, integrates everywhere in Kubernetes.
- Cons: base64 only (encoding), requires extra configuration for encryption at rest; access control is primarily RBAC; rotation/audit are limited compared to dedicated secret managers.

**HashiCorp Vault**
- Pros: centralized secret management


## Task 1
- By default, Kubernetes stores Secrets in etcd as base64, and without encryption at rest enabled, secrets are effectively stored in plaintext (base64 is easily reversible). 
- To ensure secrets are encrypted on disk, enable EncryptionConfiguration (encryption at rest) for the API server so that data written to etcd is encrypted (e.g., aescbc / kms ). 
- Even with encryption at rest, API access (RBAC) remains critical—whoever can retrieve the secret can also retrieve the decrypted value.

## Task 2 outputs
```bash
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> helm upgrade --install hooktest ./k8s/devops-info-service

Release "hooktest" has been upgraded. Happy Helming!
NAME: hooktest
LAST DEPLOYED: Thu Apr  9 21:21:40 2026
NAMESPACE: default
STATUS: deployed
REVISION: 4
DESCRIPTION: Upgrade complete
TEST SUITE: None
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> kubectl get secret | grep devops-info-service

hooktest-devops-info-service-secret   Opaque               2      14m
dreamcore@californiawrld ~/P/DevOps-Core-Course (lab11)> bash
dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl get secret $(kubectl get secret | awk '/devops-info-service/ && /-secret/ {print $1; exit}') -o yaml
apiVersion: v1
data:
  password: Y2hhbmdlLW1l
  username: Y2hhbmdlLW1l
kind: Secret
metadata:
  annotations:
    meta.helm.sh/release-name: hooktest
    meta.helm.sh/release-namespace: default
  creationTimestamp: "2026-04-09T18:07:41Z"
  labels:
    app.kubernetes.io/instance: hooktest
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: devops-info-service
    app.kubernetes.io/part-of: devops-core-course
    app.kubernetes.io/version: v2
    helm.sh/chart: devops-info-service-0.1.0
  name: hooktest-devops-info-service-secret
  namespace: default
  resourceVersion: "155949"
  uid: 4b46348f-2ea1-4922-bb56-665398feee56
type: Opaque
dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl get pods | grep devops-info-service
hooktest-devops-info-service-65dcbf86d-6qj42   1/1     Running   0          11m
hooktest-devops-info-service-65dcbf86d-8rn64   1/1     Running   0          12m
hooktest-devops-info-service-65dcbf86d-blsj2   1/1     Running   0          12m
hooktest-devops-info-service-65dcbf86d-jvsm6   1/1     Running   0          11m
hooktest-devops-info-service-65dcbf86d-q4drc   1/1     Running   0          11m
dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl describe pod hooktest-devops-info-service-65dcbf86d-6qj42
Name:             hooktest-devops-info-service-65dcbf86d-6qj42
Namespace:        default
Priority:         0
Service Account:  default
Node:             minikube/192.168.49.2
Start Time:       Thu, 09 Apr 2026 21:10:23 +0300
Labels:           app.kubernetes.io/instance=hooktest
                  app.kubernetes.io/name=devops-info-service
                  app.kubernetes.io/part-of=devops-core-course
                  pod-template-hash=65dcbf86d
Annotations:      <none>
Status:           Running
IP:               10.244.0.101
IPs:
  IP:           10.244.0.101
Controlled By:  ReplicaSet/hooktest-devops-info-service-65dcbf86d
Containers:
  devops-info-service:
    Container ID:   docker://69cc438aeb7178c977c5c895ff12572ba22e3bb50b809f1cbac4f7825eb609e6
    Image:          sincere99/devops-app:v2
    Image ID:       docker-pullable://sincere99/devops-app@sha256:978ef3a3ef7e6d2ac13c1ae6947d1387848be9de7fe8ed1db462aab0e23691fc
    Port:           5000/TCP (http)
    Host Port:      0/TCP (http)
    State:          Running
      Started:      Thu, 09 Apr 2026 21:10:23 +0300
    Ready:          True
    Restart Count:  0
    Limits:
      cpu:     200m
      memory:  256Mi
    Requests:
      cpu:      100m
      memory:   128Mi
    Liveness:   http-get http://:5000/health delay=10s timeout=2s period=5s #success=1 #failure=3
    Readiness:  http-get http://:5000/health delay=5s timeout=2s period=3s #success=1 #failure=3
    Environment Variables from:
      hooktest-devops-info-service-secret  Secret  Optional: false
    Environment:                           <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-vltfp (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True 
  Initialized                 True 
  Ready                       True 
  ContainersReady             True 
  PodScheduled                True 
Volumes:
  kube-api-access-vltfp:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    Optional:                false
    DownwardAPI:             true
QoS Class:                   Burstable
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  12m   default-scheduler  Successfully assigned default/hooktest-devops-info-service-65dcbf86d-6qj42 to minikube
  Normal  Pulled     12m   kubelet            Container image "sincere99/devops-app:v2" already present on machine and can be accessed by the pod
  Normal  Created    12m   kubelet            Container created
  Normal  Started    12m   kubelet            Container started

dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl get secret app-credentials -o jsonpath='{.data.username}' | base64 --decode; echo
demo-user
dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl get secret app-credentials -o jsonpath='{.data.password}' | base64 --decode; echo
demo-pass-123
dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ 


dreamcore@californiawrld:~/PycharmProjects/DevOps-Core-Course$ kubectl describe pod hooktest-devops-info-service-65dcbf86d-6qj42 | sed -n '/Environment Variables from:/,/Mounts:/p'
    Environment Variables from:
      hooktest-devops-info-service-secret  Secret  Optional: false
    Environment:                           <none>
    Mounts:

```