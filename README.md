# GitOps DevOps Project

FastAPI 어플리케이션을 대상으로 **GitHub Actions + GHCR + Helm + ArgoCD + Kubernetes** 기반 GitOps 배포 흐름을 구현한 프로젝트입니다.

목표는 단순 배포가 아니라, 코드 변경이 이미지 빌드 → 배포 선언 변경 → ArgoCD Sync → Kubernetes Rolling Update로 이어지는 전체 흐름을 직접 이해하는 것입니다.

---

## Architecture

```text
Developer
  → GitHub Push
  → GitHub Actions
  → Docker Image Build
  → GHCR Push
  → Helm values.yaml image tag update
  → Git Commit
  → ArgoCD Sync
  → Kubernetes Deployment
  → Pod Rolling Update
```

서비스 트래픽 흐름:

```text
Client
  → Ingress Controller
  → Ingress
  → Service
  → Endpoint
  → Pod
```

---

## Tech Stack

* FastAPI
* Docker
* Kubernetes
* kind
* Helm
* GitHub Actions
* GHCR
* ArgoCD
* ingress-nginx

---

## Key Features

### 1. Helm 기반 Kubernetes 리소스 관리

Kubernetes 리소스를 Helm Chart로 관리합니다.

```text
templates/   = Kubernetes 리소스 구조
values.yaml  = 환경별 설정값
```

관리 리소스:

* Deployment
* Service
* Ingress
* ConfigMap
* Secret
* readinessProbe / livenessProbe

---

### 2. GitHub Actions 기반 CI

코드가 push되면 GitHub Actions가 실행됩니다.

```text
app 코드 변경
  → Docker image build
  → GHCR push
  → commit SHA 기반 image tag 생성
  → Helm values.yaml image tag 자동 수정
  → Git commit/push
```

이미지 태그는 `latest`도 함께 push하지만, 실제 배포 선언에는 commit SHA tag를 사용합니다.

```yaml
image:
  repository: ghcr.io/naroosister/gitops-devops/my-api
  tag: <commit-sha>
```

commit SHA tag를 사용한 이유:

* 배포 버전 추적 가능
* Git commit과 container image 연결 가능
* rollback 시 대상 버전 식별 용이
* `latest` 사용 시 발생하는 불명확성 방지

---

### 3. ArgoCD 기반 GitOps CD

ArgoCD는 Git 저장소의 Helm Chart를 감시합니다.

```text
Git desired state
  → ArgoCD detects change
  → Helm template rendering
  → Compare with Kubernetes live state
  → Sync
```

GitHub Actions는 클러스터에 직접 배포하지 않습니다.

```text
GitHub Actions
= image build/push
= Git desired state update

ArgoCD
= Git desired state를 Kubernetes live state에 반영
```

---

### 4. Namespace 생명주기 분리

Namespace는 Helm Chart 안에서 생성하지 않고 `platform/` 경로로 분리했습니다.

```text
platform/namespaces/my-api.yaml
```

이유:

* Namespace는 애플리케이션 리소스보다 플랫폼 운영 경계에 가까움
* ResourceQuota, LimitRange, NetworkPolicy, RBAC 등과 함께 관리 가능
* 애플리케이션 배포 생명주기와 Namespace 생명주기 분리

---

## Directory Structure

```text
.
├── app/
│   └── FastAPI application
├── helm/
│   └── my-api/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── platform/
│   └── namespaces/
├── argocd/
│   └── applications/
├── kind/
│   └── cluster.yaml
└── .github/
    └── workflows/
```

---

## Local Run

### 1. kind cluster 생성

```powershell
kind create cluster --config kind\cluster.yaml --image kindest/node:v1.30.0
```

### 2. Namespace 적용

```powershell
kubectl apply -f platform\namespaces\my-api.yaml
```

### 3. ingress-nginx 설치

```powershell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

kubectl rollout status deployment/ingress-nginx-controller -n ingress-nginx --timeout=120s
```

### 4. ArgoCD 설치

```powershell
kubectl create namespace argocd

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 5. ArgoCD Application 적용

```powershell
kubectl apply -f argocd\applications\my-api.yaml
```

### 6. 서비스 확인

```powershell
kubectl get pods -n my-api
kubectl get ingress -n my-api

curl.exe http://my-api.localhost/
curl.exe http://my-api.localhost/config
```

---

## Troubleshooting

### Helm release namespace 충돌

Helm release가 `default` namespace에 생성된 상태에서 `my-api` namespace로 재배포하며 ownership 충돌이 발생했습니다.

해결:

* 기존 release 삭제
* Helm 배포 namespace 명시
* Namespace를 Helm Chart 밖으로 분리

---

* targetPort / containerPort

---

## What I Learned

* CI와 CD 책임 분리
* Git desired state와 Kubernetes live state 개념
* Helm Chart 렌더링 흐름
* ArgoCD Sync 동작 방식
* Synced와 Healthy의 차이
* Deployment rolling update 동작
* readinessProbe와 livenessProbe 차이
* Ingress, Service, Endpoint, Pod 트래픽 흐름
* GitOps 기반 배포 추적성과 rollback 개념

---

## Next Steps

* Argo Rollouts 기반 blue-green/canary 배포
* healthcheck 실패 시 abort/rollback 실습
* Secret 관리 개선

  * Sealed Secrets
  * SOPS
  * External Secrets Operator
* dev/stg/prod values 분리
* Resource requests/limits 추가
* ResourceQuota / LimitRange 추가
* HPA 구성
* Gateway API 학습
