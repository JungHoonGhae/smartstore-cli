package client

import (
	"errors"
	"testing"
)

func TestNewStatusError_401_ReturnsAuthError(t *testing.T) {
	err := newStatusError(401, "Unauthorized")
	var ae *AuthError
	if !errors.As(err, &ae) {
		t.Errorf("expected AuthError for 401, got %T: %v", err, err)
	}
}

func TestNewStatusError_403_ReturnsAuthError(t *testing.T) {
	err := newStatusError(403, "Forbidden")
	var ae *AuthError
	if !errors.As(err, &ae) {
		t.Errorf("expected AuthError for 403, got %T: %v", err, err)
	}
}

func TestNewStatusError_429_ReturnsRateLimited(t *testing.T) {
	err := newStatusError(429, "Too Many Requests")
	if !errors.Is(err, ErrRateLimited) {
		t.Errorf("expected ErrRateLimited for 429, got %v", err)
	}
}

func TestNewStatusError_500_ReturnsStatusError(t *testing.T) {
	err := newStatusError(500, "Internal Server Error")
	var se *StatusError
	if !errors.As(err, &se) {
		t.Fatalf("expected StatusError for 500, got %T: %v", err, err)
	}
	if se.StatusCode != 500 {
		t.Errorf("StatusCode: got %d, want 500", se.StatusCode)
	}
}

func TestNewStatusError_GW_AUTHN_Pattern(t *testing.T) {
	// GW.AUTHN pattern should return AuthError regardless of status code
	err := newStatusError(200, `{"errorCode":"GW.AUTHN.0001"}`)
	var ae *AuthError
	if !errors.As(err, &ae) {
		t.Errorf("expected AuthError for GW.AUTHN pattern, got %T: %v", err, err)
	}
}

func TestIsAuthError(t *testing.T) {
	authErr := &AuthError{Wrapped: errors.New("test")}
	if !IsAuthError(authErr) {
		t.Error("IsAuthError should return true for *AuthError")
	}

	plainErr := errors.New("not an auth error")
	if IsAuthError(plainErr) {
		t.Error("IsAuthError should return false for plain error")
	}
}
