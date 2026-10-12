import json
import os
import urllib.error
import urllib.parse
import urllib.request


class SanityError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"Sanity request failed ({status}): {body}")
        self.status = status


class SanityManager:
    """Sanity HTTP API client. Stdlib only; the write token stays in the Lambda."""

    def __init__(self):
        self.dataset = os.environ["SANITY_DATASET"]
        self.base_url = (
            f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io"
            f"/v{os.environ['SANITY_API_VERSION']}"
        )
        self.token = os.environ["SANITY_TOKEN"]

    def _request(self, method: str, url: str, data=None, headers=None) -> dict:
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", **(headers or {})},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as exc:
            raise SanityError(exc.code, exc.read()[:500].decode(errors="replace"))
        except urllib.error.URLError as exc:
            raise SanityError(0, str(exc.reason))

    def mutate(self, mutations: list[dict]) -> dict:
        return self._request(
            "POST",
            f"{self.base_url}/data/mutate/{self.dataset}?returnIds=true",
            data=json.dumps({"mutations": mutations}).encode(),
            headers={"Content-Type": "application/json"},
        )

    def query(self, groq: str, params: dict | None = None):
        query = {"query": groq}
        for name, value in (params or {}).items():
            query[f"${name}"] = json.dumps(value)
        url = (
            f"{self.base_url}/data/query/{self.dataset}?{urllib.parse.urlencode(query)}"
        )

        return self._request("GET", url).get("result")

    def upload_asset(
        self, kind: str, body, filename: str, content_type: str, content_length: int
    ) -> str:
        """Stream `body` to Sanity. `kind` is "image" or "file". Returns the asset id."""
        query = urllib.parse.urlencode({"filename": filename})
        response = self._request(
            "POST",
            f"{self.base_url}/assets/{kind}s/{self.dataset}?{query}",
            data=body,
            headers={
                "Content-Type": content_type,
                "Content-Length": str(content_length),
            },
        )

        return response["document"]["_id"]
