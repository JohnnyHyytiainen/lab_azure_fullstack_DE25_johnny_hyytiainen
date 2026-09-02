# Setup & Deployment

Full command list for all three environments. For the local happy path the README.

> Quickstart is enough - this adds Docker, Azure, and teardown.

## Prerequisites
- [uv](https://docs.astral.sh/uv/), Python 3.13

- [Docker](https://docs.docker.com/get-docker/) - for the container and Azure steps

- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) and [Terraform](https://developer.hashicorp.com/terraform/install) ≥ 1.9 - Azure step only

## 1)  Local
Two Python processes on one machine, talking over `localhost`. 

The frontend falls back to
`http://localhost:8000` when `BACKEND_URL` is unset, so nothing needs configuring.

```bash
uv sync

# Terminal 1 - backend -> http://localhost:8000/docs
uv run uvicorn backend.api:app --reload

# Terminal 2 - frontend -> http://localhost:8501
uv run streamlit run frontend/src/frontend/dashboard.py
```

## 2)  Docker
The same two processes as two images on a shared network. 

The frontend now reaches the backend by its **service name** (`backend`), not `localhost` - compose sets `BACKEND_URL=http://backend:8000`.

```bash
# Build and start both, detached
docker compose up --build -d  # dashboard on http://localhost:8501

# Stop and remove the network
docker compose down
```

## 3)  Azure (Terraform)
Builds the whole environment as code: a resource group, a private registr, a passwordless managed identity with `AcrPull`, a Container Apps environment, and the two apps. Reproducing this will *require* your *own* Azure subscription.

It takes **two applies** with a `docker push` between them - a container app can't pull an image
that isn't in the registry yet.

```bash
# ----- in infra/ -----

cd infra

az login

export ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv) # not hardcoded in the .tf

terraform init

terraform apply -target=azurerm_container_registry.acr # apply #1: resource group + registry

# ----- in the repo root -----

cd ..

az acr login --name eclipsebordjh

docker compose build

docker push eclipsebordjh.azurecr.io/backend:v1

docker push eclipsebordjh.azurecr.io/frontend:v1

# ----- back in infra/ -----

cd infra

terraform plan -out=tfplan && terraform apply tfplan # apply #2: identity, role, env, apps

terraform output # frontend_url, backend_url
```

`ARM_SUBSCRIPTION_ID` lives only in the terminal you exported it in - new window, export again.

Verify the backend is serving:
```bash
curl "$(terraform output -raw backend_url)/health" # {"status":"ok""rows":23962}
```

## 4) Teardown
```bash
cd infra

terraform destroy
```