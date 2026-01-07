"""Tests for Flask integration with Pydantic models."""

import pytest
from flask import Flask
from pydantic import ValidationError, field_validator

from py_libs.pydantic.base import ImmutableModel, RequestModel
from py_libs.pydantic.flask_integration import (
    ValidationErrorResponse,
    validate_body,
    validate_query_params,
    validated_request,
    model_response,
)


class TestModel(RequestModel):
    """Test request model."""

    name: str
    age: int
    email: str

    @field_validator("name", "email")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        """Validate that string fields are not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("String should have at least 1 character")
        return v


class TestResponseModel(ImmutableModel):
    """Test response model."""

    id: int
    name: str
    status: str


class QueryModel(RequestModel):
    """Test query model."""

    page: int = 1
    limit: int = 10


@pytest.fixture
def app():
    """Create Flask test application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestValidationErrorResponse:
    """Tests for ValidationErrorResponse class."""

    def test_from_pydantic_error_single_field(self):
        """Test converting single field validation error."""
        try:
            TestModel(name="John", age="invalid", email="john@example.com")
        except ValidationError as e:
            response, status_code = ValidationErrorResponse.from_pydantic_error(e)

        assert status_code == 400
        assert response["error"] == "Validation failed"
        assert "validation_errors" in response
        assert len(response["validation_errors"]) > 0
        assert response["validation_errors"][0]["field"] == "age"
        assert "message" in response["validation_errors"][0]
        assert "type" in response["validation_errors"][0]

    def test_from_pydantic_error_multiple_fields(self):
        """Test converting multiple field validation errors."""
        try:
            TestModel(name="", age="invalid", email="")
        except ValidationError as e:
            response, status_code = ValidationErrorResponse.from_pydantic_error(e)

        assert status_code == 400
        assert response["error"] == "Validation failed"
        assert len(response["validation_errors"]) >= 2

    def test_from_pydantic_error_missing_required(self):
        """Test converting missing required field error."""
        try:
            TestModel(name="John")  # type: ignore
        except ValidationError as e:
            response, status_code = ValidationErrorResponse.from_pydantic_error(e)

        assert status_code == 400
        assert response["error"] == "Validation failed"
        assert len(response["validation_errors"]) == 2  # age and email missing


class TestValidateBody:
    """Tests for validate_body function."""

    def test_validate_body_valid(self, app):
        """Test validating valid request body."""
        with app.test_request_context(
            json={"name": "John", "age": 30, "email": "john@example.com"}
        ):
            result = validate_body(TestModel)

        assert isinstance(result, TestModel)
        assert result.name == "John"
        assert result.age == 30
        assert result.email == "john@example.com"

    def test_validate_body_invalid_type(self, app):
        """Test validating request body with invalid type."""
        with app.test_request_context(
            json={"name": "John", "age": "invalid", "email": "john@example.com"}
        ):
            with pytest.raises(ValidationError):
                validate_body(TestModel)

    def test_validate_body_missing_field(self, app):
        """Test validating request body with missing required field."""
        with app.test_request_context(json={"name": "John", "age": 30}):
            with pytest.raises(ValidationError):
                validate_body(TestModel)

    def test_validate_body_extra_fields_rejected(self, app):
        """Test that RequestModel rejects extra fields."""
        with app.test_request_context(
            json={
                "name": "John",
                "age": 30,
                "email": "john@example.com",
                "admin": True,  # Extra field
            }
        ):
            with pytest.raises(ValidationError):
                validate_body(TestModel)


class TestValidateQueryParams:
    """Tests for validate_query_params function."""

    def test_validate_query_params_valid(self, app):
        """Test validating valid query parameters."""
        with app.test_request_context("/?page=2&limit=50"):
            result = validate_query_params(QueryModel)

        assert isinstance(result, QueryModel)
        assert result.page == 2
        assert result.limit == 50

    def test_validate_query_params_defaults(self, app):
        """Test query parameter defaults when not provided."""
        with app.test_request_context("/?page=3"):
            result = validate_query_params(QueryModel)

        assert result.page == 3
        assert result.limit == 10  # Default value

    def test_validate_query_params_invalid_type(self, app):
        """Test validating query parameters with invalid type."""
        with app.test_request_context("/?page=abc&limit=50"):
            with pytest.raises(ValidationError):
                validate_query_params(QueryModel)

    def test_validate_query_params_extra_fields_rejected(self, app):
        """Test that RequestModel rejects extra query parameters."""
        with app.test_request_context("/?page=1&limit=10&extra_param=value"):
            with pytest.raises(ValidationError):
                validate_query_params(QueryModel)


class TestValidatedRequestDecorator:
    """Tests for validated_request decorator."""

    def test_decorated_function_body_validation(self, app, client):
        """Test decorator validates request body."""

        @app.route("/test", methods=["POST"])
        @validated_request(body_model=TestModel)
        def test_endpoint(body):
            return {"success": True, "name": body.name}

        response = client.post(
            "/test", json={"name": "Alice", "age": 25, "email": "alice@example.com"}
        )

        assert response.status_code == 200
        assert response.json["name"] == "Alice"

    def test_decorated_function_query_validation(self, app, client):
        """Test decorator validates query parameters."""

        @app.route("/test", methods=["GET"])
        @validated_request(query_model=QueryModel)
        def test_endpoint(query):
            return {"page": query.page, "limit": query.limit}

        response = client.get("/test?page=2&limit=25")

        assert response.status_code == 200
        assert response.json["page"] == 2
        assert response.json["limit"] == 25

    def test_decorated_function_both_validations(self, app, client):
        """Test decorator validates both body and query parameters."""

        @app.route("/test", methods=["POST"])
        @validated_request(body_model=TestModel, query_model=QueryModel)
        def test_endpoint(body, query):
            return {
                "name": body.name,
                "page": query.page,
                "limit": query.limit,
            }

        response = client.post(
            "/test?page=3&limit=30",
            json={"name": "Bob", "age": 35, "email": "bob@example.com"},
        )

        assert response.status_code == 200
        assert response.json["name"] == "Bob"
        assert response.json["page"] == 3
        assert response.json["limit"] == 30

    def test_decorated_function_invalid_body(self, app, client):
        """Test decorator returns validation error response for invalid body."""

        @app.route("/test", methods=["POST"])
        @validated_request(body_model=TestModel)
        def test_endpoint(body):
            return {"success": True, "name": body.name}

        response = client.post(
            "/test",
            json={"name": "Alice", "age": "not_a_number", "email": "alice@example.com"},
        )

        assert response.status_code == 400
        assert response.json["error"] == "Validation failed"
        assert "validation_errors" in response.json

    def test_decorated_function_invalid_query(self, app, client):
        """Test decorator returns validation error response for invalid query."""

        @app.route("/test", methods=["GET"])
        @validated_request(query_model=QueryModel)
        def test_endpoint(query):
            return {"page": query.page}

        response = client.get("/test?page=not_a_number")

        assert response.status_code == 400
        assert response.json["error"] == "Validation failed"
        assert "validation_errors" in response.json

    def test_decorated_async_function_body_validation(self, app, client):
        """Test decorator works with async functions."""

        @app.route("/async-test", methods=["POST"])
        @validated_request(body_model=TestModel)
        async def async_endpoint(body):
            return {"success": True, "name": body.name}

        response = client.post(
            "/async-test",
            json={"name": "Charlie", "age": 40, "email": "charlie@example.com"},
        )

        assert response.status_code == 200
        assert response.json["name"] == "Charlie"

    def test_decorated_async_function_invalid_body(self, app, client):
        """Test decorator returns validation error for async functions."""

        @app.route("/async-test", methods=["POST"])
        @validated_request(body_model=TestModel)
        async def async_endpoint(body):
            return {"success": True, "name": body.name}

        response = client.post(
            "/async-test",
            json={"name": "Charlie", "age": "invalid", "email": "charlie@example.com"},
        )

        assert response.status_code == 400
        assert response.json["error"] == "Validation failed"


class TestModelResponse:
    """Tests for model_response function."""

    def test_model_response_default(self):
        """Test model_response with default parameters."""
        model = TestResponseModel(id=1, name="Test", status="active")
        response, status_code = model_response(model)

        assert status_code == 200
        assert response.get_json() == {"id": 1, "name": "Test", "status": "active"}

    def test_model_response_custom_status(self):
        """Test model_response with custom status code."""
        model = TestResponseModel(id=1, name="Test", status="active")
        response, status_code = model_response(model, status_code=201)

        assert status_code == 201
        assert response.get_json() == {"id": 1, "name": "Test", "status": "active"}

    def test_model_response_exclude_none(self):
        """Test model_response with exclude_none parameter."""

        class OptionalModel(ImmutableModel):
            id: int
            name: str
            description: str | None = None

        model = OptionalModel(id=1, name="Test", description=None)
        response, status_code = model_response(model, exclude_none=True)

        json_data = response.get_json()
        assert "description" not in json_data
        assert json_data == {"id": 1, "name": "Test"}

    def test_model_response_include_none(self):
        """Test model_response including None values."""

        class OptionalModel(ImmutableModel):
            id: int
            name: str
            description: str | None = None

        model = OptionalModel(id=1, name="Test", description=None)
        response, status_code = model_response(model, exclude_none=False)

        json_data = response.get_json()
        assert "description" in json_data
        assert json_data["description"] is None
