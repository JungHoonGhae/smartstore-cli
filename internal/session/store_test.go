package session

import (
	"context"
	"path/filepath"
	"testing"
	"time"
)

func TestSession_IsExpired_NilExpiresAt(t *testing.T) {
	s := Session{ExpiresAt: nil}
	if s.IsExpired(time.Now()) {
		t.Error("expected session with nil ExpiresAt to not be expired")
	}
}

func TestSession_IsExpired_Future(t *testing.T) {
	future := time.Now().Add(24 * time.Hour)
	s := Session{ExpiresAt: &future}
	if s.IsExpired(time.Now()) {
		t.Error("expected session with future ExpiresAt to not be expired")
	}
}

func TestSession_IsExpired_Past(t *testing.T) {
	past := time.Now().Add(-24 * time.Hour)
	s := Session{ExpiresAt: &past}
	if !s.IsExpired(time.Now()) {
		t.Error("expected session with past ExpiresAt to be expired")
	}
}

func TestSession_TouchLastUsed(t *testing.T) {
	s := Session{}
	if s.LastUsedAt != nil {
		t.Fatal("expected LastUsedAt to be nil initially")
	}

	before := time.Now().UTC()
	s.TouchLastUsed()
	after := time.Now().UTC()

	if s.LastUsedAt == nil {
		t.Fatal("expected LastUsedAt to be set after TouchLastUsed")
	}
	if s.LastUsedAt.Before(before) || s.LastUsedAt.After(after) {
		t.Errorf("LastUsedAt %v not in expected range [%v, %v]", *s.LastUsedAt, before, after)
	}
}

func TestFileStore_SaveAndLoad(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "session.json")
	store := NewFileStore(path)
	ctx := context.Background()

	expires := time.Date(2026, 12, 31, 0, 0, 0, 0, time.UTC)
	sess := &Session{
		Provider: "naver",
		Cookies:  map[string]string{"NID_AUT": "abc123"},
		Headers:  map[string]string{"Authorization": "Bearer tok"},
		ExpiresAt:   &expires,
		RetrievedAt: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
	}

	if err := store.Save(ctx, sess); err != nil {
		t.Fatalf("Save failed: %v", err)
	}

	loaded, err := store.Load(ctx)
	if err != nil {
		t.Fatalf("Load failed: %v", err)
	}

	if loaded.Provider != sess.Provider {
		t.Errorf("Provider: got %q, want %q", loaded.Provider, sess.Provider)
	}
	if loaded.Cookies["NID_AUT"] != "abc123" {
		t.Errorf("Cookies[NID_AUT]: got %q, want %q", loaded.Cookies["NID_AUT"], "abc123")
	}
	if loaded.ExpiresAt == nil || !loaded.ExpiresAt.Equal(expires) {
		t.Errorf("ExpiresAt: got %v, want %v", loaded.ExpiresAt, expires)
	}
}

func TestFileStore_Load_NoFile(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "nonexistent.json")
	store := NewFileStore(path)

	_, err := store.Load(context.Background())
	if err != ErrNoSession {
		t.Errorf("expected ErrNoSession, got %v", err)
	}
}

func TestFileStore_Clear(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "session.json")
	store := NewFileStore(path)
	ctx := context.Background()

	sess := &Session{Provider: "naver", RetrievedAt: time.Now().UTC()}
	if err := store.Save(ctx, sess); err != nil {
		t.Fatalf("Save failed: %v", err)
	}

	if err := store.Clear(ctx); err != nil {
		t.Fatalf("Clear failed: %v", err)
	}

	_, err := store.Load(ctx)
	if err != ErrNoSession {
		t.Errorf("expected ErrNoSession after Clear, got %v", err)
	}
}

func TestFileStore_Clear_NoFile(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "nonexistent.json")
	store := NewFileStore(path)

	if err := store.Clear(context.Background()); err != nil {
		t.Errorf("Clear on nonexistent file should not error, got %v", err)
	}
}
