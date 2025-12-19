package validation

import (
	"fmt"
	"strings"
	"sync"

	"github.com/go-playground/validator/v10"
)

// validate is the singleton validator instance.
var (
	validate *validator.Validate
	once     sync.Once
)

// getValidator returns the singleton validator instance, initializing it once.
func getValidator() *validator.Validate {
	once.Do(func() {
		validate = validator.New()
		RegisterCustomValidators()
	})
	return validate
}

// RegisterCustomValidators registers custom validation functions for the validator.
// Currently registered validators:
//   - village_id: Validates Elder Village ID format (TTTT-OOOO-IIIIIIII)
//   - strong_password: Validates password strength (min 8 chars, uppercase, lowercase, digit, special char)
func RegisterCustomValidators() {
	v := validate
	if v == nil {
		v = validator.New()
	}

	// Register village_id validator
	err := v.RegisterValidation("village_id", validateVillageID)
	if err != nil && !strings.Contains(err.Error(), "already exists") {
		fmt.Printf("Failed to register village_id validator: %v\n", err)
	}

	// Register strong_password validator
	err = v.RegisterValidation("strong_password", validateStrongPassword)
	if err != nil && !strings.Contains(err.Error(), "already exists") {
		fmt.Printf("Failed to register strong_password validator: %v\n", err)
	}
}

// ValidateStruct validates a struct using go-playground/validator/v10.
// Returns a slice of ValidationError with field-level error details.
// If validation succeeds, returns an empty slice.
//
// Example usage:
//
//	type User struct {
//	    Name  string `validate:"required,min=3"`
//	    Email string `validate:"required,email"`
//	}
//	user := User{Name: "John", Email: "john@example.com"}
//	errs := ValidateStruct(user)
//	if len(errs) > 0 {
//	    for _, err := range errs {
//	        fmt.Printf("Field: %s, Message: %s\n", err.Field, err.Message)
//	    }
//	}
func ValidateStruct(s interface{}) []ValidationError {
	v := getValidator()

	// Validate the struct
	err := v.Struct(s)
	if err == nil {
		return []ValidationError{}
	}

	// Convert validator errors to our ValidationError type
	validationErrors := convertValidatorErrors(err)
	return validationErrors
}

// ValidateStructPartial validates only specified fields of a struct.
// fieldNames should be the names of fields to validate (case-sensitive).
//
// Example usage:
//
//	errs := ValidateStructPartial(user, "Email", "Phone")
func ValidateStructPartial(s interface{}, fieldNames ...string) []ValidationError {
	v := getValidator()

	err := v.StructPartial(s, fieldNames...)
	if err == nil {
		return []ValidationError{}
	}

	validationErrors := convertValidatorErrors(err)
	return validationErrors
}

// ValidateVar validates a single variable against validation tags.
// This is useful for validating custom types or primitives.
//
// Example usage:
//
//	email := "invalid-email"
//	errs := ValidateVar(email, "required,email")
func ValidateVar(field interface{}, tag string) []ValidationError {
	v := getValidator()

	err := v.Var(field, tag)
	if err == nil {
		return []ValidationError{}
	}

	validationErrors := convertValidatorErrors(err)
	return validationErrors
}

// convertValidatorErrors converts validator.ValidationErrors to a slice of ValidationError.
// Handles the conversion and formats error messages in a user-friendly way.
func convertValidatorErrors(err error) []ValidationError {
	if err == nil {
		return []ValidationError{}
	}

	var validationErrors []ValidationError

	// Type assertion to get validator.ValidationErrors
	validationErrs, ok := err.(validator.ValidationErrors)
	if !ok {
		// If it's not a ValidationErrors type, return a generic error
		return []ValidationError{
			{
				Field:   "unknown",
				Message: err.Error(),
			},
		}
	}

	// Convert each validation error
	for _, fieldErr := range validationErrs {
		message := formatValidationMessage(fieldErr)
		validationErrors = append(validationErrors, ValidationError{
			Field:   fieldErr.Field(),
			Message: message,
		})
	}

	return validationErrors
}

// formatValidationMessage formats a validator.FieldError into a user-friendly message.
func formatValidationMessage(fieldErr validator.FieldError) string {
	switch fieldErr.Tag() {
	case "required":
		return fmt.Sprintf("field is required")
	case "email":
		return fmt.Sprintf("invalid email format")
	case "min":
		return fmt.Sprintf("must be at least %s", fieldErr.Param())
	case "max":
		return fmt.Sprintf("must be at most %s", fieldErr.Param())
	case "len":
		return fmt.Sprintf("must be exactly %s characters long", fieldErr.Param())
	case "village_id":
		return fmt.Sprintf("invalid Village ID format (expected: TTTT-OOOO-IIIIIIII)")
	case "strong_password":
		return fmt.Sprintf("password must be at least 8 characters with uppercase, lowercase, digit, and special character")
	case "url":
		return fmt.Sprintf("invalid URL format")
	case "ipv4":
		return fmt.Sprintf("invalid IPv4 address")
	case "ipv6":
		return fmt.Sprintf("invalid IPv6 address")
	case "ip":
		return fmt.Sprintf("invalid IP address")
	case "alpha":
		return fmt.Sprintf("must contain only alphabetic characters")
	case "alphaNum":
		return fmt.Sprintf("must contain only alphanumeric characters")
	case "numeric":
		return fmt.Sprintf("must be numeric")
	case "oneof":
		return fmt.Sprintf("must be one of: %s", fieldErr.Param())
	case "startswith":
		return fmt.Sprintf("must start with %s", fieldErr.Param())
	case "endswith":
		return fmt.Sprintf("must end with %s", fieldErr.Param())
	case "contains":
		return fmt.Sprintf("must contain %s", fieldErr.Param())
	case "eqfield":
		return fmt.Sprintf("must equal field %s", fieldErr.Param())
	case "nefield":
		return fmt.Sprintf("must not equal field %s", fieldErr.Param())
	case "gtfield":
		return fmt.Sprintf("must be greater than field %s", fieldErr.Param())
	case "gtefield":
		return fmt.Sprintf("must be greater than or equal to field %s", fieldErr.Param())
	case "ltfield":
		return fmt.Sprintf("must be less than field %s", fieldErr.Param())
	case "ltefield":
		return fmt.Sprintf("must be less than or equal to field %s", fieldErr.Param())
	default:
		return fmt.Sprintf("failed validation: %s", fieldErr.Tag())
	}
}
