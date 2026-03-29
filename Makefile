BINARY := bin/storectl
VERSION ?= dev
COMMIT ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
DATE ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
LDFLAGS := -X github.com/junghoonkye/smartstore-cli/internal/version.Version=$(VERSION) \
	-X github.com/junghoonkye/smartstore-cli/internal/version.Commit=$(COMMIT) \
	-X github.com/junghoonkye/smartstore-cli/internal/version.Date=$(DATE)

.PHONY: build run test fmt tidy clean

build:
	mkdir -p bin
	go build -ldflags "$(LDFLAGS)" -o $(BINARY) ./cmd/storectl

run:
	go run -ldflags "$(LDFLAGS)" ./cmd/storectl

test:
	go test ./...

fmt:
	gofmt -w ./cmd ./internal

tidy:
	go mod tidy

clean:
	rm -rf bin coverage.out
