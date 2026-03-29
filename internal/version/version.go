package version

type Info struct {
	Version string `json:"version"`
	Commit  string `json:"commit"`
	Date    string `json:"date,omitempty"`
}

var (
	Version = "dev"
	Commit  = "unknown"
	Date    = ""
)

func Current() Info {
	return Info{
		Version: Version,
		Commit:  Commit,
		Date:    Date,
	}
}
