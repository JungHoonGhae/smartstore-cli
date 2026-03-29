package client

import (
	"errors"
	"fmt"
	"strings"
)

var (
	ErrNoSession      = errors.New("no active session; run `storectl auth login`")
	ErrSessionExpired = errors.New("session has expired; run `storectl auth login` to re-authenticate")
	ErrRateLimited    = errors.New("rate limited by server; try again later")
)

type StatusError struct {
	StatusCode int
	Body       string
}

func (e *StatusError) Error() string {
	return fmt.Sprintf("HTTP %d: %s", e.StatusCode, e.Body)
}

type AuthError struct {
	Wrapped error
}

func (e *AuthError) Error() string {
	return fmt.Sprintf("authentication error: %v", e.Wrapped)
}

func (e *AuthError) Unwrap() error {
	return e.Wrapped
}

func IsAuthError(err error) bool {
	var ae *AuthError
	return errors.As(err, &ae)
}

func newStatusError(code int, body string) error {
	statusErr := &StatusError{StatusCode: code, Body: body}

	// Naver gateway authentication error pattern
	if strings.Contains(body, "GW.AUTHN") {
		return &AuthError{Wrapped: statusErr}
	}

	if code == 401 || code == 403 {
		return &AuthError{Wrapped: statusErr}
	}

	if code == 429 {
		return ErrRateLimited
	}

	return statusErr
}
