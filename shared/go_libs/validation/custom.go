package validation

import (
	"regexp"
	"unicode"

	"github.com/go-playground/validator/v10"
)

// validateVillageID validates Elder Village ID format (TTTT-OOOO-IIIIIIII)
// Format: 4 hex chars - 4 hex chars - 8 hex chars (18 chars with dashes)
func validateVillageID(fl validator.FieldLevel) bool {
	villageID := fl.Field().String()

	// Pattern: TTTT-OOOO-IIIIIIII where each is hex
	pattern := `^[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{8}$`
	matched, err := regexp.MatchString(pattern, villageID)
	if err != nil {
		return false
	}

	return matched
}

// validateStrongPassword validates password strength
// Requirements: min 8 chars, at least one uppercase, one lowercase, one digit, one special char
func validateStrongPassword(fl validator.FieldLevel) bool {
	password := fl.Field().String()

	// Minimum length check
	if len(password) < 8 {
		return false
	}

	hasUpper := false
	hasLower := false
	hasDigit := false
	hasSpecial := false

	specialChars := "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"

	for _, char := range password {
		switch {
		case unicode.IsUpper(char):
			hasUpper = true
		case unicode.IsLower(char):
			hasLower = true
		case unicode.IsDigit(char):
			hasDigit = true
		case contains(specialChars, char):
			hasSpecial = true
		}
	}

	return hasUpper && hasLower && hasDigit && hasSpecial
}

// contains checks if a string contains a rune
func contains(s string, r rune) bool {
	for _, char := range s {
		if char == r {
			return true
		}
	}
	return false
}
