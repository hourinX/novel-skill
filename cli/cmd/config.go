package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"gopkg.in/yaml.v3"
)

type Config struct {
	Service struct {
		Host string `yaml:"host"`
		Port int    `yaml:"port"`
	} `yaml:"service"`
}

func findProjectRoot() string {
	// 先尝试可执行文件所在目录
	exe, err := os.Executable()
	if err == nil {
		dir := filepath.Dir(exe)
		if _, err := os.Stat(filepath.Join(dir, "config.yaml")); err == nil {
			return dir
		}
		// 向上一级找（cli/ 的上级是项目根目录）
		parent := filepath.Dir(dir)
		if _, err := os.Stat(filepath.Join(parent, "config.yaml")); err == nil {
			return parent
		}
	}
	// 再尝试当前工作目录
	wd, err := os.Getwd()
	if err == nil {
		if _, err := os.Stat(filepath.Join(wd, "config.yaml")); err == nil {
			return wd
		}
	}
	_ = runtime.GOOS
	return "."
}

func loadConfig() *Config {
	root := findProjectRoot()
	data, err := os.ReadFile(filepath.Join(root, "config.yaml"))
	if err != nil {
		return nil
	}

	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil
	}

	return &cfg
}

func getServiceURL() string {
	cfg := loadConfig()
	if cfg == nil {
		return "http://localhost:8000"
	}
	return fmt.Sprintf("http://%s:%d", cfg.Service.Host, cfg.Service.Port)
}