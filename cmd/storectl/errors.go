package main

import (
	"errors"
	"fmt"

	"github.com/junghoonkye/smartstore-cli/internal/client"
)

func userFacingCommandError(err error) error {
	if errors.Is(err, client.ErrNoSession) {
		return fmt.Errorf("no active session; run `storectl auth login` first")
	}
	if errors.Is(err, client.ErrSessionExpired) {
		return fmt.Errorf("session has expired; run `storectl auth login` to re-authenticate")
	}
	if errors.Is(err, client.ErrRateLimited) {
		return fmt.Errorf("rate limited by server; please wait a moment and try again")
	}
	if client.IsAuthError(err) {
		return fmt.Errorf("session is no longer valid; run `storectl auth login` to re-authenticate")
	}
	return err
}
