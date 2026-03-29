package config

import (
	"context"
	"path/filepath"
	"testing"
)

func TestService_Load_NoFile_ReturnsDefaults(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "config.json")
	svc := NewService(path)

	cfg, err := svc.Load(context.Background())
	if err != nil {
		t.Fatalf("Load returned error: %v", err)
	}

	if cfg.SchemaVersion != SchemaVersion {
		t.Errorf("SchemaVersion: got %d, want %d", cfg.SchemaVersion, SchemaVersion)
	}
	if cfg.Schema != DefaultSchemaURL {
		t.Errorf("Schema: got %q, want %q", cfg.Schema, DefaultSchemaURL)
	}
}

func TestService_Init_CreatesFile(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "subdir", "config.json")
	svc := NewService(path)

	result, err := svc.Init(context.Background())
	if err != nil {
		t.Fatalf("Init returned error: %v", err)
	}

	if !result.Created {
		t.Error("expected Created to be true on first Init")
	}
	if !result.Status.Exists {
		t.Error("expected Exists to be true after Init")
	}
	if result.Status.ConfigFile != path {
		t.Errorf("ConfigFile: got %q, want %q", result.Status.ConfigFile, path)
	}

	// Second Init should not recreate
	result2, err := svc.Init(context.Background())
	if err != nil {
		t.Fatalf("second Init returned error: %v", err)
	}
	if result2.Created {
		t.Error("expected Created to be false on second Init")
	}
}

func TestService_Status(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "config.json")
	svc := NewService(path)

	// Before Init: file doesn't exist
	status, err := svc.Status(context.Background())
	if err != nil {
		t.Fatalf("Status returned error: %v", err)
	}
	if status.Exists {
		t.Error("expected Exists to be false before Init")
	}
	if status.ConfigFile != path {
		t.Errorf("ConfigFile: got %q, want %q", status.ConfigFile, path)
	}

	// After Init: file exists
	if _, err := svc.Init(context.Background()); err != nil {
		t.Fatalf("Init failed: %v", err)
	}

	status, err = svc.Status(context.Background())
	if err != nil {
		t.Fatalf("Status returned error: %v", err)
	}
	if !status.Exists {
		t.Error("expected Exists to be true after Init")
	}
	if status.SchemaVersion != SchemaVersion {
		t.Errorf("SchemaVersion: got %d, want %d", status.SchemaVersion, SchemaVersion)
	}
}
