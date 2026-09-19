import json
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class ExtractedEndpoint(BaseModel):
    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[Dict[str, Any]]] = None
    request_body: Optional[Dict[str, Any]] = None
    responses: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None

class OpenAPIDiscoveryResult(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    base_url: str
    endpoints: List[ExtractedEndpoint]
    security_schemes: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

class OpenAPIParser:
    @staticmethod
    def parse(content: str) -> OpenAPIDiscoveryResult:
        """
        Parses JSON or YAML OpenAPI specification (Swagger 2.0 / OpenAPI 3.0 / 3.1).
        Validates basic structure and extracts endpoint metadata.
        """
        if not content or not content.strip():
            raise ValueError("Invalid OpenAPI format: Content is empty")

        # Try parsing as JSON first, fallback to YAML
        try:
            data = json.loads(content)
        except Exception:
            try:
                data = yaml.safe_load(content)
            except Exception as ye:
                raise ValueError(f"Invalid OpenAPI format: Must be valid JSON or YAML: {str(ye)}")

        if not isinstance(data, dict):
            raise ValueError("Invalid OpenAPI format: Root element must be a dictionary object")

        # Check for OpenAPI / Swagger version markers
        is_swagger2 = "swagger" in data
        is_openapi3 = "openapi" in data

        if not (is_swagger2 or is_openapi3):
            raise ValueError("Invalid OpenAPI format: Missing 'openapi' or 'swagger' version declaration.")

        # Extract Info object
        info = data.get("info", {})
        title = info.get("title", "Imported API Specification")
        version = str(info.get("version", "1.0.0"))
        description = info.get("description")

        # Extract Base URL
        base_url = "http://localhost:8000"
        if is_openapi3:
            servers = data.get("servers", [])
            if servers and isinstance(servers, list) and "url" in servers[0]:
                base_url = servers[0]["url"]
        elif is_swagger2:
            host = data.get("host", "localhost:8000")
            base_path = data.get("basePath", "/")
            schemes = data.get("schemes", ["http"])
            base_url = f"{schemes[0]}://{host.rstrip('/')}/{base_path.lstrip('/')}".rstrip('/')

        # Extract Security Schemes
        security_schemes = {}
        if is_openapi3:
            security_schemes = data.get("components", {}).get("securitySchemes", {})
        elif is_swagger2:
            security_schemes = data.get("securityDefinitions", {})

        # Extract Global Tags
        tags = [t.get("name") for t in data.get("tags", []) if isinstance(t, dict) and "name" in t]

        # Extract Endpoints
        paths = data.get("paths", {})
        extracted_endpoints: List[ExtractedEndpoint] = []

        if isinstance(paths, dict):
            for path_str, path_item in paths.items():
                if not isinstance(path_item, dict):
                    continue

                common_params = path_item.get("parameters", [])

                for method in ["get", "post", "put", "delete", "patch", "options", "head"]:
                    if method in path_item and isinstance(path_item[method], dict):
                        op = path_item[method]

                        # Merge common path parameters with operation parameters
                        merged_params = []
                        if isinstance(common_params, list):
                            merged_params.extend(common_params)
                        if isinstance(op.get("parameters"), list):
                            merged_params.extend(op["parameters"])

                        # Extract Request Body (OpenAPI 3 vs Swagger 2)
                        req_body = op.get("requestBody")
                        if not req_body and is_swagger2:
                            # In Swagger 2, body param is inside parameters
                            body_params = [p for p in merged_params if p.get("in") == "body"]
                            if body_params:
                                req_body = {"schema": body_params[0].get("schema")}

                        # Normalize response keys to strings
                        responses_dict = None
                        if isinstance(op.get("responses"), dict):
                            responses_dict = {str(k): v for k, v in op["responses"].items()}

                        ep = ExtractedEndpoint(
                            path=path_str,
                            method=method.upper(),
                            summary=op.get("summary"),
                            description=op.get("description"),
                            parameters=merged_params if merged_params else None,
                            request_body=req_body,
                            responses=responses_dict,
                            security=op.get("security"),
                            tags=op.get("tags")
                        )
                        extracted_endpoints.append(ep)

        return OpenAPIDiscoveryResult(
            title=title,
            version=version,
            description=description,
            base_url=base_url,
            endpoints=extracted_endpoints,
            security_schemes=security_schemes,
            tags=tags
        )
