# Troubleshooting
> Common issues, and why each one happens.

### The dashboard is slow on the first load (Azure)
The apps scale to zero after ~5 minutes of inactivity (`min_replicas = 0`) to stay free. The first request wakes them and takes a few seconds. Not a bug - load the page once before you need it.

---

### Streamlit shows a red error box on startup
The frontend checks `/health` at startup and stops with a readable message when the backend isn't reachable.

* **Local:** is the backend running on `http://localhost:8000`?

* **Docker:** the frontend must reach the backend by service name - `BACKEND_URL=http://backend:8000`. `localhost` inside a container means the container itself.

* It can also flash once at `compose up` if the frontend checks before the backend has finished starting - reload the page.

---

### Terraform can't find the subscription
* `ARM_SUBSCRIPTION_ID` lives only in the terminal you exported it in. New window -> export again:

```bash
export ARM_SUBSCRIPTION_ID=$(az account show --query id --output tsv)
```
---

### The frontend image won't run on its own
* By design. `BACKEND_URL` is never baked into the image - it's a property of the deployment, set by compose or Terraform. Run alone, the frontend falls back to `localhost` (itself) and shows the red box. That's exactly what keeps the same image usable in both Docker and Azure.

---

### Docker build fails: "failed to open file ... README.md"

* Each members `pyproject.toml` declares `readme = "README.md"`, and the `Dockerfile` copies it - so `backend/README.md` and `frontend/README.md` must exist (even if short)

---

### There's no `curl` inside the containers
* The uv base image is slim and ships no `curl`. To check an endpoint from inside an `Azure app`, exec in and use `Python` instead (`az containerapp exec -n backend -g rg-eclipsebord`, then a short `urllib.request` snippet) or just open the public `/health` URL in a browser.

---

### A filter returns nothing
* An empty result with status `200` is valid - e.g. `?body=lunar&eclipse_type=A`, since annular eclipses only exist in the solar catalog. An invalid *value* returns `422` with a message from `Pydantic`.