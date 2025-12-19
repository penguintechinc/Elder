package validation

import (
	"testing"
)

// TestValidateStruct tests the ValidateStruct function with various struct types
func TestValidateStruct(t *testing.T) {
	tests := []struct {
		name      string
		input     interface{}
		expectErr bool
		errCount  int
		errFields []string
	}{
		{
			name: "valid struct",
			input: struct {
				Name  string `validate:"required,min=3"`
				Email string `validate:"required,email"`
			}{
				Name:  "John Doe",
				Email: "john@example.com",
			},
			expectErr: false,
			errCount:  0,
		},
		{
			name: "missing required field",
			input: struct {
				Name string `validate:"required"`
			}{
				Name: "",
			},
			expectErr: true,
			errCount:  1,
			errFields: []string{"Name"},
		},
		{
			name: "invalid email",
			input: struct {
				Email string `validate:"required,email"`
			}{
				Email: "invalid-email",
			},
			expectErr: true,
			errCount:  1,
			errFields: []string{"Email"},
		},
		{
			name: "min length violation",
			input: struct {
				Name string `validate:"required,min=5"`
			}{
				Name: "Jo",
			},
			expectErr: true,
			errCount:  1,
			errFields: []string{"Name"},
		},
		{
			name: "max length violation",
			input: struct {
				Name string `validate:"required,max=10"`
			}{
				Name: "This is a very long name",
			},
			expectErr: true,
			errCount:  1,
			errFields: []string{"Name"},
		},
		{
			name: "multiple validation errors",
			input: struct {
				Name  string `validate:"required,min=3"`
				Email string `validate:"required,email"`
			}{
				Name:  "Jo",
				Email: "invalid",
			},
			expectErr: true,
			errCount:  2,
			errFields: []string{"Name", "Email"},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateStruct(tt.input)

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected errors, got none")
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no errors, got %d: %v", len(errs), errs)
			}

			if len(errs) != tt.errCount {
				t.Errorf("expected %d errors, got %d", tt.errCount, len(errs))
			}

			if tt.expectErr {
				for i, expectedField := range tt.errFields {
					if i < len(errs) && errs[i].Field != expectedField {
						t.Errorf("error %d: expected field %s, got %s", i, expectedField, errs[i].Field)
					}
				}
			}
		})
	}
}

// TestValidateStructPartial tests partial struct validation
func TestValidateStructPartial(t *testing.T) {
	type User struct {
		Name  string `validate:"required,min=3"`
		Email string `validate:"required,email"`
		Phone string `validate:"required,min=10"`
	}

	tests := []struct {
		name        string
		user        User
		fieldNames  []string
		expectErr   bool
		errCount    int
		errContains string
	}{
		{
			name: "validate only email field",
			user: User{
				Name:  "Jo",
				Email: "invalid",
				Phone: "123",
			},
			fieldNames: []string{"Email"},
			expectErr:  true,
			errCount:   1,
		},
		{
			name: "validate multiple fields",
			user: User{
				Name:  "Jo",
				Email: "invalid",
				Phone: "123",
			},
			fieldNames: []string{"Name", "Email"},
			expectErr:  true,
			errCount:   2,
		},
		{
			name: "validate valid fields",
			user: User{
				Name:  "John Doe",
				Email: "john@example.com",
				Phone: "1234567890",
			},
			fieldNames: []string{"Email", "Name"},
			expectErr:  false,
			errCount:   0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateStructPartial(tt.user, tt.fieldNames...)

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected errors, got none")
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no errors, got %d: %v", len(errs), errs)
			}

			if len(errs) != tt.errCount {
				t.Errorf("expected %d errors, got %d", tt.errCount, len(errs))
			}
		})
	}
}

// TestValidateVar tests validation of single variables
func TestValidateVar(t *testing.T) {
	tests := []struct {
		name      string
		value     interface{}
		tag       string
		expectErr bool
	}{
		{
			name:      "valid email",
			value:     "john@example.com",
			tag:       "required,email",
			expectErr: false,
		},
		{
			name:      "invalid email",
			value:     "invalid-email",
			tag:       "email",
			expectErr: true,
		},
		{
			name:      "empty required field",
			value:     "",
			tag:       "required",
			expectErr: true,
		},
		{
			name:      "valid numeric string",
			value:     "12345",
			tag:       "numeric",
			expectErr: false,
		},
		{
			name:      "invalid numeric string",
			value:     "abc123",
			tag:       "numeric",
			expectErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateVar(tt.value, tt.tag)

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected errors, got none")
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no errors, got %d: %v", len(errs), errs)
			}
		})
	}
}

// TestVillageIDValidator tests the custom village_id validator
func TestVillageIDValidator(t *testing.T) {
	tests := []struct {
		name      string
		villageID string
		expectErr bool
		desc      string
	}{
		{
			name:      "valid village id",
			villageID: "a1b2-c3d4-e5f67890",
			expectErr: false,
			desc:      "full hierarchy ID",
		},
		{
			name:      "valid tenant id",
			villageID: "a1b2-0000-00000000",
			expectErr: false,
			desc:      "tenant level ID",
		},
		{
			name:      "valid organization id",
			villageID: "a1b2-c3d4-00000000",
			expectErr: false,
			desc:      "organization level ID",
		},
		{
			name:      "uppercase hex valid",
			villageID: "A1B2-C3D4-E5F67890",
			expectErr: false,
			desc:      "uppercase hex characters",
		},
		{
			name:      "mixed case valid",
			villageID: "A1b2-C3d4-E5f67890",
			expectErr: false,
			desc:      "mixed case hex characters",
		},
		{
			name:      "invalid format - missing dashes",
			villageID: "a1b2c3d4e5f67890",
			expectErr: true,
			desc:      "no dashes",
		},
		{
			name:      "invalid format - wrong dash positions",
			villageID: "a1b2-c3d4e5f67890",
			expectErr: true,
			desc:      "second dash missing",
		},
		{
			name:      "invalid format - non-hex characters",
			villageID: "a1b2-c3d4-e5f6789g",
			expectErr: true,
			desc:      "invalid hex character 'g'",
		},
		{
			name:      "invalid format - too short",
			villageID: "a1b2-c3d4-e5f6789",
			expectErr: true,
			desc:      "last segment too short",
		},
		{
			name:      "invalid format - too long",
			villageID: "a1b2-c3d4-e5f678901",
			expectErr: true,
			desc:      "last segment too long",
		},
		{
			name:      "invalid format - special characters",
			villageID: "a1b2-c3d4-e5f6789@",
			expectErr: true,
			desc:      "contains special character",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type TestData struct {
				ID string `validate:"village_id"`
			}

			errs := ValidateStruct(TestData{ID: tt.villageID})

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected validation error for %s, got none", tt.desc)
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no error for %s, got: %v", tt.desc, errs)
			}
		})
	}
}

// TestStrongPasswordValidator tests the custom strong_password validator
func TestStrongPasswordValidator(t *testing.T) {
	tests := []struct {
		name      string
		password  string
		expectErr bool
		reason    string
	}{
		{
			name:      "valid strong password",
			password:  "MyP@ssw0rd",
			expectErr: false,
			reason:    "has uppercase, lowercase, digit, special char, length >= 8",
		},
		{
			name:      "valid complex password",
			password:  "C0mpl3x!P@ssw0rd!",
			expectErr: false,
			reason:    "complex with multiple special chars",
		},
		{
			name:      "missing uppercase",
			password:  "myp@ssw0rd",
			expectErr: true,
			reason:    "no uppercase letter",
		},
		{
			name:      "missing lowercase",
			password:  "MYP@SSW0RD",
			expectErr: true,
			reason:    "no lowercase letter",
		},
		{
			name:      "missing digit",
			password:  "MyP@ssword",
			expectErr: true,
			reason:    "no digit",
		},
		{
			name:      "missing special character",
			password:  "MyPassword0",
			expectErr: true,
			reason:    "no special character",
		},
		{
			name:      "too short",
			password:  "My@12",
			expectErr: true,
			reason:    "length < 8",
		},
		{
			name:      "exactly 8 chars valid",
			password:  "MyP@ssw0",
			expectErr: false,
			reason:    "minimum length met with all requirements",
		},
		{
			name:      "7 chars invalid",
			password:  "MyP@ss0",
			expectErr: true,
			reason:    "length < 8",
		},
		{
			name:      "special char !",
			password:  "MyP!ssw0rd",
			expectErr: false,
			reason:    "! is valid special character",
		},
		{
			name:      "special char @",
			password:  "MyP@ssw0rd",
			expectErr: false,
			reason:    "@ is valid special character",
		},
		{
			name:      "special char #",
			password:  "MyP#ssw0rd",
			expectErr: false,
			reason:    "# is valid special character",
		},
		{
			name:      "special char $",
			password:  "MyP$ssw0rd",
			expectErr: false,
			reason:    "$ is valid special character",
		},
		{
			name:      "special char %",
			password:  "MyP%ssw0rd",
			expectErr: false,
			reason:    "% is valid special character",
		},
		{
			name:      "special char ^",
			password:  "MyP^ssw0rd",
			expectErr: false,
			reason:    "^ is valid special character",
		},
		{
			name:      "special char &",
			password:  "MyP&ssw0rd",
			expectErr: false,
			reason:    "& is valid special character",
		},
		{
			name:      "special char *",
			password:  "MyP*ssw0rd",
			expectErr: false,
			reason:    "* is valid special character",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type TestData struct {
				Password string `validate:"strong_password"`
			}

			errs := ValidateStruct(TestData{Password: tt.password})

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("%s: expected validation error, got none (reason: %s)", tt.name, tt.reason)
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("%s: expected no error, got: %v (reason: %s)", tt.name, errs, tt.reason)
			}
		})
	}
}

// TestCombinedValidation tests struct with both custom validators
func TestCombinedValidation(t *testing.T) {
	type Account struct {
		VillageID string `validate:"required,village_id"`
		Password  string `validate:"required,strong_password"`
	}

	tests := []struct {
		name      string
		account   Account
		expectErr bool
		errCount  int
	}{
		{
			name: "valid account",
			account: Account{
				VillageID: "a1b2-c3d4-e5f67890",
				Password:  "MyP@ssw0rd",
			},
			expectErr: false,
			errCount:  0,
		},
		{
			name: "invalid village id only",
			account: Account{
				VillageID: "invalid-id",
				Password:  "MyP@ssw0rd",
			},
			expectErr: true,
			errCount:  1,
		},
		{
			name: "invalid password only",
			account: Account{
				VillageID: "a1b2-c3d4-e5f67890",
				Password:  "weak",
			},
			expectErr: true,
			errCount:  1,
		},
		{
			name: "both invalid",
			account: Account{
				VillageID: "invalid",
				Password:  "short",
			},
			expectErr: true,
			errCount:  2,
		},
		{
			name: "missing village id",
			account: Account{
				VillageID: "",
				Password:  "MyP@ssw0rd",
			},
			expectErr: true,
			errCount:  1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateStruct(tt.account)

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected errors, got none")
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no errors, got %d: %v", len(errs), errs)
			}

			if len(errs) != tt.errCount {
				t.Errorf("expected %d errors, got %d", tt.errCount, len(errs))
			}
		})
	}
}

// TestValidationErrorMessages tests error message formatting
func TestValidationErrorMessages(t *testing.T) {
	type TestData struct {
		Email    string `validate:"email"`
		Name     string `validate:"min=3"`
		VillageID string `validate:"village_id"`
		Password string `validate:"strong_password"`
	}

	tests := []struct {
		name        string
		data        TestData
		expectField string
		checkMsg    string
	}{
		{
			name:        "email error message",
			data:        TestData{Email: "invalid"},
			expectField: "Email",
			checkMsg:    "invalid email format",
		},
		{
			name:        "village_id error message",
			data:        TestData{VillageID: "invalid"},
			expectField: "VillageID",
			checkMsg:    "invalid Village ID format",
		},
		{
			name:        "strong_password error message",
			data:        TestData{Password: "weak"},
			expectField: "Password",
			checkMsg:    "password must be at least 8 characters",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateStruct(tt.data)

			found := false
			for _, err := range errs {
				if err.Field == tt.expectField {
					found = true
					if !containsSubstring(err.Message, tt.checkMsg) {
						t.Errorf("expected message to contain '%s', got '%s'", tt.checkMsg, err.Message)
					}
					break
				}
			}

			if !found && tt.expectField != "" {
				t.Errorf("expected error for field %s, but not found", tt.expectField)
			}
		})
	}
}

// TestEmptyStruct tests validation of empty structs
func TestEmptyStruct(t *testing.T) {
	type Empty struct{}

	errs := ValidateStruct(Empty{})
	if len(errs) != 0 {
		t.Errorf("expected no errors for empty struct, got %d", len(errs))
	}
}

// TestNestedStruct tests validation of nested structs
func TestNestedStruct(t *testing.T) {
	type Address struct {
		Street string `validate:"required"`
		City   string `validate:"required"`
	}

	type Person struct {
		Name    string  `validate:"required"`
		Address Address `validate:"required"`
	}

	tests := []struct {
		name      string
		person    Person
		expectErr bool
	}{
		{
			name: "valid nested struct",
			person: Person{
				Name: "John",
				Address: Address{
					Street: "123 Main St",
					City:   "Anytown",
				},
			},
			expectErr: false,
		},
		{
			name: "invalid nested field",
			person: Person{
				Name: "John",
				Address: Address{
					Street: "",
					City:   "Anytown",
				},
			},
			expectErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			errs := ValidateStruct(tt.person)

			if tt.expectErr && len(errs) == 0 {
				t.Errorf("expected errors, got none")
			}
			if !tt.expectErr && len(errs) > 0 {
				t.Errorf("expected no errors, got %d: %v", len(errs), errs)
			}
		})
	}
}

// TestValidationErrorInterface tests ValidationError implements error interface
func TestValidationErrorInterface(t *testing.T) {
	err := ValidationError{
		Field:   "Email",
		Message: "invalid format",
	}

	// Should implement error interface
	errStr := err.Error()
	if errStr != "Email: invalid format" {
		t.Errorf("expected 'Email: invalid format', got '%s'", errStr)
	}

	// Test with empty field
	err2 := ValidationError{
		Field:   "",
		Message: "validation failed",
	}
	errStr2 := err2.Error()
	if errStr2 != "validation failed" {
		t.Errorf("expected 'validation failed', got '%s'", errStr2)
	}
}

// Helper function to check if a string contains a substring
func containsSubstring(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
