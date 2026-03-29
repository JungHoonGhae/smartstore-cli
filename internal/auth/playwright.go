package auth

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/junghoonkye/smartstore-cli/internal/session"
)

type playwrightStorageState struct {
	Cookies []playwrightCookie         `json:"cookies"`
	Origins []playwrightStorageOrigins `json:"origins"`
}

type playwrightCookie struct {
	Name    string  `json:"name"`
	Value   string  `json:"value"`
	Domain  string  `json:"domain"`
	Path    string  `json:"path"`
	Expires float64 `json:"expires"`
}

type playwrightStorageOrigins struct {
	Origin       string                   `json:"origin"`
	LocalStorage []playwrightStorageEntry `json:"localStorage"`
}

type playwrightStorageEntry struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

func (s *Service) ImportPlaywrightState(ctx context.Context, path string) (*session.Session, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read playwright storage state: %w", err)
	}

	var state playwrightStorageState
	if err := json.Unmarshal(data, &state); err != nil {
		return nil, fmt.Errorf("failed to parse playwright storage state: %w", err)
	}

	cookies := make(map[string]string)
	headers := make(map[string]string)
	storage := make(map[string]string)

	for _, c := range state.Cookies {
		cookies[c.Name] = c.Value
	}

	for _, origin := range state.Origins {
		if origin.Origin == "https://sell.smartstore.naver.com" ||
			origin.Origin == "https://nid.naver.com" {
			for _, entry := range origin.LocalStorage {
				storage["localStorage:"+entry.Name] = entry.Value
			}
		}
	}

	// Derive headers from captured state (like tossinvest-cli pattern).
	headers["Referer"] = "https://sell.smartstore.naver.com/"

	now := time.Now().UTC()
	sess := &session.Session{
		Provider:    "playwright",
		Cookies:     cookies,
		Headers:     headers,
		Storage:     storage,
		RetrievedAt: now,
	}

	if err := s.store.Save(ctx, sess); err != nil {
		return nil, err
	}

	return sess, nil
}
