package config

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
)

const (
	SchemaVersion    = 1
	DefaultSchemaURL = "https://raw.githubusercontent.com/JungHoonGhae/smartstore-cli/main/schemas/config.schema.json"
)

type File struct {
	Schema        string `json:"$schema,omitempty"`
	SchemaVersion int    `json:"schema_version"`
}

type Status struct {
	ConfigFile    string `json:"config_file"`
	Exists        bool   `json:"exists"`
	Schema        string `json:"$schema,omitempty"`
	SchemaVersion int    `json:"schema_version"`
}

type InitResult struct {
	Status  Status `json:"status"`
	Created bool   `json:"created"`
}

type Service struct {
	path string
}

func NewService(path string) *Service {
	return &Service{path: path}
}

func DefaultFile() File {
	return File{
		Schema:        DefaultSchemaURL,
		SchemaVersion: SchemaVersion,
	}
}

func (s *Service) Load(context.Context) (File, error) {
	cfg, _, err := s.load()
	return cfg, err
}

func (s *Service) Status(context.Context) (Status, error) {
	cfg, exists, err := s.load()
	if err != nil {
		return Status{}, err
	}
	return Status{
		ConfigFile:    s.path,
		Exists:        exists,
		Schema:        cfg.Schema,
		SchemaVersion: cfg.SchemaVersion,
	}, nil
}

func (s *Service) Init(context.Context) (InitResult, error) {
	if _, err := os.Stat(s.path); err == nil {
		status, err := s.Status(context.Background())
		if err != nil {
			return InitResult{}, err
		}
		return InitResult{Status: status, Created: false}, nil
	} else if !errors.Is(err, os.ErrNotExist) {
		return InitResult{}, err
	}

	cfg := DefaultFile()
	if err := s.save(cfg); err != nil {
		return InitResult{}, err
	}
	status, err := s.Status(context.Background())
	if err != nil {
		return InitResult{}, err
	}
	return InitResult{Status: status, Created: true}, nil
}

func (s *Service) load() (File, bool, error) {
	data, err := os.ReadFile(s.path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return DefaultFile(), false, nil
		}
		return File{}, false, err
	}

	var cfg File
	if err := json.Unmarshal(data, &cfg); err != nil {
		return File{}, true, err
	}

	if cfg.Schema == "" {
		cfg.Schema = DefaultSchemaURL
	}
	cfg.SchemaVersion = SchemaVersion

	return cfg, true, nil
}

func (s *Service) save(cfg File) error {
	if err := os.MkdirAll(filepath.Dir(s.path), 0o755); err != nil {
		return err
	}

	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}

	tmpPath := s.path + ".tmp"
	if err := os.WriteFile(tmpPath, data, 0o600); err != nil {
		return err
	}
	return os.Rename(tmpPath, s.path)
}
