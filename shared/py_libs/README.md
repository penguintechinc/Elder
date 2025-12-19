# py_libs - Python Shared Library

See [docs/shared-libraries/py-libs.md](../../docs/shared-libraries/py-libs.md) for complete documentation.

## Pydantic 2 Data Validation

Pydantic 2 provides powerful runtime data validation and serialization with full type checking support.

### Basic Usage

```python
from pydantic import BaseModel, Field, validator

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = Field(gt=0, le=150)

    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email address')
        return v

# Create and validate
user = User(id=1, name="John Doe", email="john@example.com", age=30)
print(user.model_dump())
print(user.model_dump_json())
```

### Nested Models

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class Person(BaseModel):
    name: str
    addresses: List[Address]

data = {
    "name": "Jane",
    "addresses": [
        {"street": "123 Main St", "city": "NYC", "zip_code": "10001"},
        {"street": "456 Oak Ave", "city": "LA", "zip_code": "90001"}
    ]
}
person = Person(**data)
```

### Custom Validators

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float
    stock: int

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Price must be positive')
        return v

    @field_validator('stock')
    @classmethod
    def stock_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Stock cannot be negative')
        return v
```
