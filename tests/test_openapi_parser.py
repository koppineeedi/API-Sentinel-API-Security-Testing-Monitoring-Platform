import pytest
from app.services.openapi_parser import OpenAPIParser

SAMPLE_OPENAPI_JSON = """{
  "openapi": "3.0.0",
  "info": {
    "title": "Petstore Microservice",
    "version": "2.1.0",
    "description": "Authorized Petstore API Lab"
  },
  "servers": [
    { "url": "http://api.petstore.local/v1" }
  ],
  "paths": {
    "/pets": {
      "get": {
        "summary": "List all pets",
        "responses": { "200": { "description": "OK" } }
      },
      "post": {
        "summary": "Add a new pet",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": { "type": "object" }
            }
          }
        },
        "responses": { "201": { "description": "Created" } }
      }
    },
    "/pets/{id}": {
      "get": {
        "summary": "Get pet by ID",
        "parameters": [
          { "name": "id", "in": "path", "required": true, "schema": { "type": "integer" } }
        ]
      }
    }
  }
}"""

SAMPLE_OPENAPI_YAML = """
swagger: "2.0"
info:
  title: "Legacy YAML API"
  version: "1.0.0"
host: "legacy.api.local"
basePath: "/v1"
schemes:
  - "https"
paths:
  /users:
    get:
      summary: "List users"
      responses:
        200:
          description: "Success"
"""

def test_openapi_json_parsing():
    result = OpenAPIParser.parse(SAMPLE_OPENAPI_JSON)
    assert result.title == "Petstore Microservice"
    assert result.version == "2.1.0"
    assert result.base_url == "http://api.petstore.local/v1"
    assert len(result.endpoints) == 3

    methods = [ep.method for ep in result.endpoints]
    assert "GET" in methods
    assert "POST" in methods

def test_openapi_yaml_parsing():
    result = OpenAPIParser.parse(SAMPLE_OPENAPI_YAML)
    assert result.title == "Legacy YAML API"
    assert result.version == "1.0.0"
    assert result.base_url == "https://legacy.api.local/v1"
    assert len(result.endpoints) == 1
    assert result.endpoints[0].path == "/users"

def test_invalid_openapi_format():
    with pytest.raises(ValueError, match="Invalid OpenAPI format"):
        OpenAPIParser.parse("::Invalid YAML and JSON text::")
