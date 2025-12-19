package validation

import (
	"testing"

	"github.com/go-playground/validator/v10"
)

// TestValidateVillageID tests the validateVillageID function with various inputs
func TestValidateVillageID(t *testing.T) {
	v := validator.New()
	v.RegisterValidation("villageID", validateVillageID)

	tests := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{
			name:    "valid village id",
			input:   "a1b2-c3d4-e5f67890",
			wantErr: false,
		},
		{
			name:    "valid village id uppercase hex",
			input:   "A1B2-C3D4-E5F67890",
			wantErr: false,
		},
		{
			name:    "valid village id mixed case",
			input:   "aAbB-cCdD-eEfF1234",
			wantErr: false,
		},
		{
			name:    "valid all zeros",
			input:   "0000-0000-00000000",
			wantErr: false,
		},
		{
			name:    "valid all f",
			input:   "ffff-ffff-ffffffff",
			wantErr: false,
		},
		{
			name:    "invalid missing dashes",
			input:   "a1b2c3d4e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid wrong format first segment",
			input:   "a1b2-c3d4-e5f67890",
			wantErr: false, // This should be valid
		},
		{
			name:    "invalid first segment too short",
			input:   "a1b-c3d4-e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid second segment too short",
			input:   "a1b2-c3d-e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid third segment too short",
			input:   "a1b2-c3d4-e5f6789",
			wantErr: true,
		},
		{
			name:    "invalid first segment too long",
			input:   "a1b2c-c3d4-e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid second segment too long",
			input:   "a1b2-c3d4e-e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid third segment too long",
			input:   "a1b2-c3d4-e5f678900",
			wantErr: true,
		},
		{
			name:    "invalid non-hex characters",
			input:   "g1h2-i3j4-k5l67890",
			wantErr: true,
		},
		{
			name:    "invalid with spaces",
			input:   "a1b2 -c3d4-e5f67890",
			wantErr: true,
		},
		{
			name:    "invalid empty string",
			input:   "",
			wantErr: true,
		},
		{
			name:    "invalid too many dashes",
			input:   "a1b2-c3d4-e5f6-7890",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type testStruct struct {
				VillageID string `validate:"villageID"`
			}

			ts := testStruct{VillageID: tt.input}
			err := v.Struct(ts)

			if (err != nil) != tt.wantErr {
				t.Errorf("validateVillageID(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
			}
		})
	}
}

// TestValidateStrongPassword tests the validateStrongPassword function with various inputs
func TestValidateStrongPassword(t *testing.T) {
	v := validator.New()
	v.RegisterValidation("strongPassword", validateStrongPassword)

	tests := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{
			name:    "valid strong password",
			input:   "MyPassword123!",
			wantErr: false,
		},
		{
			name:    "valid strong password with multiple special chars",
			input:   "StrongP@ss#2024",
			wantErr: false,
		},
		{
			name:    "valid strong password minimum length",
			input:   "Pass1@bc",
			wantErr: false,
		},
		{
			name:    "valid strong password with long length",
			input:   "VeryLongPassword123!@#$%^&*()",
			wantErr: false,
		},
		{
			name:    "invalid too short",
			input:   "Pass1@",
			wantErr: true,
		},
		{
			name:    "invalid missing uppercase",
			input:   "password123!",
			wantErr: true,
		},
		{
			name:    "invalid missing lowercase",
			input:   "PASSWORD123!",
			wantErr: true,
		},
		{
			name:    "invalid missing digit",
			input:   "Password!@#$",
			wantErr: true,
		},
		{
			name:    "invalid missing special character",
			input:   "Password123",
			wantErr: true,
		},
		{
			name:    "invalid only uppercase",
			input:   "PASSWORD",
			wantErr: true,
		},
		{
			name:    "invalid only lowercase",
			input:   "password",
			wantErr: true,
		},
		{
			name:    "invalid only digits",
			input:   "12345678",
			wantErr: true,
		},
		{
			name:    "invalid empty string",
			input:   "",
			wantErr: true,
		},
		{
			name:    "invalid single character",
			input:   "P",
			wantErr: true,
		},
		{
			name:    "valid with different special chars",
			input:   "Test1Pass$",
			wantErr: false,
		},
		{
			name:    "valid with exclamation mark",
			input:   "TestPass1!",
			wantErr: false,
		},
		{
			name:    "valid with parenthesis",
			input:   "TestPass1()",
			wantErr: false,
		},
		{
			name:    "valid with equals",
			input:   "TestPass1=",
			wantErr: false,
		},
		{
			name:    "invalid special char not in list",
			input:   "TestPass1©",
			wantErr: true,
		},
		{
			name:    "invalid exactly 7 chars",
			input:   "Test1P!",
			wantErr: true,
		},
		{
			name:    "invalid with space",
			input:   "Test Pass1!",
			wantErr: false, // spaces are allowed, just need all requirements
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type testStruct struct {
				Password string `validate:"strongPassword"`
			}

			ts := testStruct{Password: tt.input}
			err := v.Struct(ts)

			if (err != nil) != tt.wantErr {
				t.Errorf("validateStrongPassword(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
			}
		})
	}
}

// TestContains tests the contains helper function
func TestContains(t *testing.T) {
	tests := []struct {
		name string
		s    string
		r    rune
		want bool
	}{
		{
			name: "contains exclamation",
			s:    "!@#$%",
			r:    '!',
			want: true,
		},
		{
			name: "contains at sign",
			s:    "!@#$%",
			r:    '@',
			want: true,
		},
		{
			name: "does not contain",
			s:    "!@#$%",
			r:    'a',
			want: false,
		},
		{
			name: "empty string",
			s:    "",
			r:    'a',
			want: false,
		},
		{
			name: "single char match",
			s:    "x",
			r:    'x',
			want: true,
		},
		{
			name: "single char no match",
			s:    "x",
			r:    'y',
			want: false,
		},
		{
			name: "contains special char at start",
			s:    "*()_+-",
			r:    '*',
			want: true,
		},
		{
			name: "contains special char at end",
			s:    "!@#$%^&*",
			r:    '*',
			want: true,
		},
		{
			name: "unicode rune",
			s:    "café",
			r:    'é',
			want: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := contains(tt.s, tt.r)
			if got != tt.want {
				t.Errorf("contains(%q, %q) = %v, want %v", tt.s, tt.r, got, tt.want)
			}
		})
	}
}

// BenchmarkValidateVillageID benchmarks the village ID validation
func BenchmarkValidateVillageID(b *testing.B) {
	v := validator.New()
	v.RegisterValidation("villageID", validateVillageID)

	type testStruct struct {
		VillageID string `validate:"villageID"`
	}

	ts := testStruct{VillageID: "a1b2-c3d4-e5f67890"}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v.Struct(ts)
	}
}

// BenchmarkValidateStrongPassword benchmarks the password validation
func BenchmarkValidateStrongPassword(b *testing.B) {
	v := validator.New()
	v.RegisterValidation("strongPassword", validateStrongPassword)

	type testStruct struct {
		Password string `validate:"strongPassword"`
	}

	ts := testStruct{Password: "MyPassword123!"}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		v.Struct(ts)
	}
}

// TestValidateVillageIDEdgeCases tests edge cases for village ID validation
func TestValidateVillageIDEdgeCases(t *testing.T) {
	v := validator.New()
	v.RegisterValidation("villageID", validateVillageID)

	tests := []struct {
		name    string
		input   string
		wantErr bool
	}{
		{
			name:    "tenant format with zeros",
			input:   "a1b2-0000-00000000",
			wantErr: false,
		},
		{
			name:    "organization format with zeros",
			input:   "a1b2-c3d4-00000000",
			wantErr: false,
		},
		{
			name:    "all zeros",
			input:   "0000-0000-00000000",
			wantErr: false,
		},
		{
			name:    "all f uppercase",
			input:   "FFFF-FFFF-FFFFFFFF",
			wantErr: false,
		},
		{
			name:    "hyphen at wrong position",
			input:   "-a1b2-c3d4-e5f6789",
			wantErr: true,
		},
		{
			name:    "missing first segment",
			input:   "-c3d4-e5f67890",
			wantErr: true,
		},
		{
			name:    "trailing hyphen",
			input:   "a1b2-c3d4-e5f67890-",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type testStruct struct {
				VillageID string `validate:"villageID"`
			}

			ts := testStruct{VillageID: tt.input}
			err := v.Struct(ts)

			if (err != nil) != tt.wantErr {
				t.Errorf("validateVillageID(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
			}
		})
	}
}

// TestValidateStrongPasswordAllSpecialChars tests all allowed special characters
func TestValidateStrongPasswordAllSpecialChars(t *testing.T) {
	v := validator.New()
	v.RegisterValidation("strongPassword", validateStrongPassword)

	specialChars := "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
	basePassword := "TestPass1"

	for i, char := range specialChars {
		t.Run("special_char_"+string(char), func(t *testing.T) {
			password := basePassword + string(char)
			type testStruct struct {
				Password string `validate:"strongPassword"`
			}

			ts := testStruct{Password: password}
			err := v.Struct(ts)

			if err != nil {
				t.Errorf("validateStrongPassword with special char %q (index %d) failed: %v", char, i, err)
			}
		})
	}
}

// TestValidateStrongPasswordMultipleRequirements validates all requirements together
func TestValidateStrongPasswordMultipleRequirements(t *testing.T) {
	v := validator.New()
	v.RegisterValidation("strongPassword", validateStrongPassword)

	tests := []struct {
		name         string
		password     string
		hasUpper     bool
		hasLower     bool
		hasDigit     bool
		hasSpecial   bool
		minLength    bool
		shouldPass   bool
	}{
		{
			name:       "all requirements met",
			password:   "ValidPass123!",
			hasUpper:   true,
			hasLower:   true,
			hasDigit:   true,
			hasSpecial: true,
			minLength:  true,
			shouldPass: true,
		},
		{
			name:       "missing one requirement - no upper",
			password:   "validpass123!",
			hasUpper:   false,
			hasLower:   true,
			hasDigit:   true,
			hasSpecial: true,
			minLength:  true,
			shouldPass: false,
		},
		{
			name:       "missing one requirement - no lower",
			password:   "VALIDPASS123!",
			hasUpper:   true,
			hasLower:   false,
			hasDigit:   true,
			hasSpecial: true,
			minLength:  true,
			shouldPass: false,
		},
		{
			name:       "missing one requirement - no digit",
			password:   "ValidPass!abc",
			hasUpper:   true,
			hasLower:   true,
			hasDigit:   false,
			hasSpecial: true,
			minLength:  true,
			shouldPass: false,
		},
		{
			name:       "missing one requirement - no special",
			password:   "ValidPass123abc",
			hasUpper:   true,
			hasLower:   true,
			hasDigit:   true,
			hasSpecial: false,
			minLength:  true,
			shouldPass: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			type testStruct struct {
				Password string `validate:"strongPassword"`
			}

			ts := testStruct{Password: tt.password}
			err := v.Struct(ts)

			if (err != nil) != !tt.shouldPass {
				t.Errorf("validateStrongPassword(%q) shouldPass=%v, but got error=%v", tt.password, tt.shouldPass, err)
			}
		})
	}
}
