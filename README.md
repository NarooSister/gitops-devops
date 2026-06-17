# GitOps

## 목표
GitHub Actions + ArgoCD + Helm + Kubernetes 기반 GitOps 배포 흐름 실습

## 현재 구현한 것
- FastAPI API 서버
- Docker image build
- kind 기반 로컬 Kubernetes 클러스터
- platform namespace manifest 분리
- Helm Chart 배포
- ConfigMap / Secret 환경변수 주입
- readinessProbe / livenessProbe
- ClusterIP Service
- ingress-nginx 기반 Ingress 라우팅`
- my-api.localhost 접근 확인

## 아키텍처
Client → Ingress Controller → Ingress → Service → Pod

## 로컬 실행 순서
1. kind cluster 생성
2. namespace 적용
3. Docker image load
4. ingress-nginx 설치
5. Helm 배포
6. curl 테스트

## 다음 단계
- GitHub Actions image build/push
- commit SHA 기반 image tag
- Helm values.yaml image tag 자동 변경
- ArgoCD Application 생성
- auto sync / rollback 실습