# go_libs - Go Shared Library

See [docs/shared-libraries/go-libs.md](../../docs/shared-libraries/go-libs.md) for complete documentation.

## Struct Validation

Go struct validation using struct tags and validation libraries for runtime data validation.

### Basic Validation with Tags

```go
import "github.com/go-playground/validator/v10"

type User struct {
    ID    int    `validate:"required,min=1"`
    Name  string `validate:"required,min=2,max=100"`
    Email string `validate:"required,email"`
    Age   int    `validate:"min=0,max=150"`
}

validate := validator.New()
user := User{ID: 1, Name: "John Doe", Email: "john@example.com", Age: 30}

err := validate.Struct(user)
if err != nil {
    for _, e := range err.(validator.ValidationErrors) {
        fmt.Printf("Field %s validation failed: %s\n", e.Field(), e.Tag())
    }
}
```

### Custom Validators

```go
type Product struct {
    Name  string  `validate:"required"`
    Price float64 `validate:"required,gt=0"`
    Stock int     `validate:"required,gte=0"`
}

validate := validator.New()
validate.RegisterValidation("positive_price", func(fl validator.FieldLevel) bool {
    price := fl.Field().Float()
    return price > 0
})

product := Product{Name: "Widget", Price: 9.99, Stock: 100}
err := validate.Struct(product)
```

### Nested Struct Validation

```go
type Address struct {
    Street string `validate:"required"`
    City   string `validate:"required"`
    ZIP    string `validate:"required,len=5"`
}

type Person struct {
    Name      string    `validate:"required"`
    Addresses []Address `validate:"required,dive"`
}

validate := validator.New()
person := Person{
    Name: "Jane",
    Addresses: []Address{
        {Street: "123 Main St", City: "NYC", ZIP: "10001"},
        {Street: "456 Oak Ave", City: "LA", ZIP: "90001"},
    },
}

err := validate.Struct(person)
```

### Conditional Validation

```go
type Account struct {
    Type     string `validate:"required,oneof=personal business"`
    TaxID    string `validate:"required_if=Type business"`
    Personal string `validate:"required_if=Type personal"`
}

validate := validator.New()
account := Account{Type: "business", TaxID: "123-45-6789"}
err := validate.Struct(account)
```
