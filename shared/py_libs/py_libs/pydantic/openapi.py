"""Flask-RESTX integration for OpenAPI schema generation from Pydantic models."""

# flake8: noqa: E501


from typing import Any, Dict, Optional, Type, get_args, get_origin

from flask_restx import fields as restx_fields
from pydantic import BaseModel
from pydantic.fields import FieldInfo


def pydantic_to_restx_field(field_info: FieldInfo, annotation: Any) -> restx_fields.Raw:
    """Convert Pydantic field to Flask-RESTX field.

    Args:
        field_info: Pydantic field information
        annotation: Type annotation for the field

    Returns:
        Flask-RESTX field instance
    """
    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handle Optional types
    if origin is type(None) or (origin and type(None) in args):
        if args:
            annotation = args[0] if args[0] is not type(None) else args[1]
            origin = get_origin(annotation)
            args = get_args(annotation)

    # Handle List types
    if origin is list:
        item_type = args[0] if args else str
        item_field = pydantic_to_restx_field(field_info, item_type)
        return restx_fields.List(item_field, required=field_info.is_required())

    # Handle Dict types
    if origin is dict:
        return restx_fields.Raw(required=field_info.is_required())

    # Map Python types to RESTX fields
    type_map = {
        str: restx_fields.String,
        int: restx_fields.Integer,
        float: restx_fields.Float,
        bool: restx_fields.Boolean,
    }

    field_class = type_map.get(annotation, restx_fields.String)
    return field_class(
        required=field_info.is_required(), description=field_info.description
    )


def pydantic_to_restx_model(
    api: Any, model_class: Type[BaseModel], name: Optional[str] = None
) -> Any:
    """Convert Pydantic model to Flask-RESTX model for Swagger.

    Args:
        api: Flask-RESTX API instance
        model_class: Pydantic model class
        name: Optional name for the RESTX model

    Returns:
        Flask-RESTX model instance
    """
    model_name = name or model_class.__name__
    fields = {}

    for field_name, field_info in model_class.model_fields.items():
        annotation = field_info.annotation
        fields[field_name] = pydantic_to_restx_field(field_info, annotation)

    return api.model(model_name, fields)


def generate_openapi_schema(model_class: Type[BaseModel]) -> Dict[str, Any]:
    """Generate OpenAPI 3.0 schema from Pydantic model.

    Args:
        model_class: Pydantic model class

    Returns:
        OpenAPI 3.0 schema dictionary
    """
    return model_class.model_json_schema()
