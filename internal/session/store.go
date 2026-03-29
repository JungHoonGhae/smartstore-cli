package session

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"time"
)

var ErrNoSession = errors.New("no stored session")

type Session struct {
	Provider    string            `json:"provider"`
	Cookies     map[string]string `json:"cookies,omitempty"`
	Headers     map[string]string `json:"headers,omitempty"`
	Storage     map[string]string `json:"storage,omitempty"`
	RetrievedAt time.Time         `json:"retrieved_at"`
	ExpiresAt   *time.Time        `json:"expires_at,omitempty"`
	LastUsedAt  *time.Time        `json:"last_used_at,omitempty"`
}

// TouchLastUsed updates LastUsedAt to the current time.
func (s *Session) TouchLastUsed() {
	now := time.Now().UTC()
	s.LastUsedAt = &now
}

type Store interface {
	Load(context.Context) (*Session, error)
	Save(context.Context, *Session) error
	Clear(context.Context) error
}

type FileStore struct {
	path string
}

func NewFileStore(path string) *FileStore {
	return &FileStore{path: path}
}

func (s Session) IsExpired(now time.Time) bool {
	if s.ExpiresAt == nil {
		return false
	}

	return now.After(*s.ExpiresAt)
}

func (s *FileStore) Load(context.Context) (*Session, error) {
	data, err := os.ReadFile(s.path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return nil, ErrNoSession
		}

		return nil, err
	}

	var sess Session
	if err := json.Unmarshal(data, &sess); err != nil {
		return nil, err
	}

	return &sess, nil
}

func (s *FileStore) Save(_ context.Context, sess *Session) error {
	return WriteFile(s.path, sess)
}

func (s *FileStore) Clear(_ context.Context) error {
	if err := os.Remove(s.path); err != nil && !errors.Is(err, os.ErrNotExist) {
		return err
	}

	return nil
}

func (s *FileStore) Path() string {
	return s.path
}

func WriteFile(path string, sess *Session) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(sess, "", "  ")
	if err != nil {
		return err
	}

	tmpPath := path + ".tmp"
	if err := os.WriteFile(tmpPath, data, 0o600); err != nil {
		return err
	}

	return os.Rename(tmpPath, path)
}
