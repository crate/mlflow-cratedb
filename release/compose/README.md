# MLflow with Docker Compose (CrateDB + S3-Compatible Storage)

This directory provides a **Docker Compose** setup for running
**MLflow** locally with a **CrateDB** backend store and **RustFS**
for S3-compatible artifact storage.

---

## Overview

- **MLflow Tracking Server**  
  Serves the REST API and UI (default: `http://localhost:5000`).

- **CrateDB**  
  Stores MLflow's metadata (experiments, runs, params, metrics).

- **RustFS Artifact Storage**  
  Stores model files and run artifacts.

---

## Prerequisites

- **Git**
- **Docker** and **Docker Compose**
- On macOS/Windows: Docker Desktop
- On Linux: Docker Engine + compose plugin

Verify installation:

```bash
docker --version
docker compose version
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/crate/mlflow-cratedb.git
cd mlflow-cratedb/release/compose
```

---

## 2. Configure Environment

Copy and customize the environment file:

```bash
cp .env.dev.example .env
```

The `.env` file defines:

- MLflow server port
- CrateDB credentials
- S3 bucket name
- S3-compatible endpoint URL
- Backend-specific configuration for RustFS

**Common variables**:

- **CrateDB**

  - `CRATEDB_USER=crate`
  - `CRATEDB_PASSWORD=crate`
  - `CRATEDB_SCHEMA=mlflow`

- **S3**

  - `AWS_ACCESS_KEY_ID=s3admin`
  - `AWS_SECRET_ACCESS_KEY=s3admin`
  - `AWS_DEFAULT_REGION=us-east-1`
  - `S3_BUCKET=mlflow`

- **RustFS**

  - `RUSTFS_CONSOLE_ENABLE=true`

- **MLflow**
  - `MLFLOW_VERSION=latest`
  - `MLFLOW_HOST=0.0.0.0`
  - `MLFLOW_PORT=5000`
  - `MLFLOW_BACKEND_STORE_URI=crate://${CRATEDB_USER}:${CRATEDB_PASSWORD}@cratedb:4200/?schema=${CRATEDB_SCHEMA}`
  - `MLFLOW_ARTIFACTS_DESTINATION=s3://${S3_BUCKET}`
  - `MLFLOW_S3_ENDPOINT_URL=http://storage:9000`

---

## 3. Launch the stack

Inside directory `release/compose`:

```bash
docker compose up --wait --detach
```

This will:

- Start CrateDB
- Start RustFS
- Start MLflow
- Create the S3 bucket if it doesn't exist

Check status:

```bash
docker compose ps
```

Tail logs:

```bash
docker compose logs --follow
```
```bash
docker compose logs -f mlflow
docker compose logs -f cratedb
docker compose logs -f storage
```

---

## 4. Access MLflow

Once running, navigate to `http://localhost:5000` (or the port defined in `.env`).
You can now log runs, metrics, artifacts, and models to your local MLflow instance.

---

## 5. Shutdown

Stop and remove containers.
```bash
docker compose down
```

Reset the whole stack, including volumes.
```bash
docker compose down --remove-orphans --volumes
```

---

## Tips & Troubleshooting

### RustFS Notes (important)

- Set **server domains/host** so virtual-hosted requests can be resolved by RustFS:

  ```env
  RUSTFS_SERVER_DOMAINS=storage:9000
  ```

  (match the compose service DNS name)

- Prefer AWS CLI **`s3api`** for bucket creation. Some S3 clients default to
  **path-style** on custom endpoints; if bucket creation fails with
  `InvalidBucketName`, switch to `s3api` or a client like MinIO `mc`.

- Inside MLflow, use the internal endpoint:
  ```env
  MLFLOW_S3_ENDPOINT_URL=http://storage:9000
  MLFLOW_ARTIFACTS_DESTINATION=s3://mlflow/
  ```

### Healthcheck Example

RustFS usually responds on `/health` with a json that contains the status of the server:
```sh
curl -s http://127.0.0.1:9000/health | grep -q '"status":"connected"'
```
CrateDB also responds with a corresponding JSON document.
```sh
curl -s http://127.0.0.1:4200 | grep -q '"ok" : true'
```

Use that in a container healthcheck (no `-f`, 4xx may appear during bootstrap).

---

### Artifact Upload Issues

Verify:

- `MLFLOW_ARTIFACTS_DESTINATION=s3://<bucket>/`
- `MLFLOW_S3_ENDPOINT_URL=http://<service>:<port>`
- AWS credentials match the backend configuration

To verify S3 storage is working:

```bash
aws --endpoint-url=${MLFLOW_S3_ENDPOINT_URL} s3api list-buckets

echo hi > /tmp/t.txt
aws --endpoint-url=${MLFLOW_S3_ENDPOINT_URL} s3 cp /tmp/t.txt s3://${S3_BUCKET}/t.txt
aws --endpoint-url=${MLFLOW_S3_ENDPOINT_URL} s3 cp s3://${S3_BUCKET}/t.txt -
```

If this passes, MLflow can read and write artifacts to RustFS.

### Troubleshooting

- `InvalidBucketName` on create-bucket → use `s3api` (virtual-host friendly)
  or MinIO `mc`; ensure `RUSTFS_SERVER_DOMAINS` matches the S3 hostname.
- Endpoint issues from MLflow → make sure `MLFLOW_S3_ENDPOINT_URL` uses the
  **service name** visible from MLflow (e.g., `http://storage:9000`).
- If you see port conflict errors, edit `.env` and restart all containers
  using `docker compose down && docker compose up --wait --detach`.

---

## Next Steps

- Point your training scripts to this server:
  ```bash
  export MLFLOW_TRACKING_URI=http://localhost:5000
  ```
- Start logging runs with `mlflow.start_run()` (Python) or the MLflow CLI.
- Customize the `.env` and `compose.yml` files to fit your local workflow
  (e.g., change image tags, add volumes, etc.).

---

**You now have a fully local MLflow stack with persistent metadata and artifact
storage—ideal for development and experimentation.**
