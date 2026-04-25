package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"

	"novel-skill/cmd"
)

func findProjectRoot() string {
	exe, err := os.Executable()
	if err == nil {
		dir := filepath.Dir(exe)
		if _, err := os.Stat(filepath.Join(dir, "config.yaml")); err == nil {
			return dir
		}
		parent := filepath.Dir(dir)
		if _, err := os.Stat(filepath.Join(parent, "config.yaml")); err == nil {
			return parent
		}
	}
	wd, err := os.Getwd()
	if err == nil {
		if _, err := os.Stat(filepath.Join(wd, "config.yaml")); err == nil {
			return wd
		}
	}
	_ = runtime.GOOS
	return "."
}

func checkUnfinishedDraft() {
	root := findProjectRoot()
	draftPath := filepath.Join(root, "draft", "current_draft.md")
	info, err := os.Stat(draftPath)
	if err != nil || info.Size() == 0 {
		return
	}
	fmt.Println("⚠️  检测到未确认的草稿！")
	fmt.Println("   输入 accept 确认，或 reject 丢弃，或 preview-draft 查看内容")
	fmt.Println(strings.Repeat("─", 40))
}

func main() {
	fmt.Println("🖊  novel-skill 交互式写作终端")
	fmt.Println("输入 help 查看命令，输入 exit 退出")
	fmt.Println(strings.Repeat("─", 40))

	checkUnfinishedDraft()

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("\n> ")
		if !scanner.Scan() {
			break
		}

		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if line == "exit" || line == "quit" {
			fmt.Println("再见！")
			break
		}

		args := strings.Fields(line)
		os.Args = append([]string{"novel-skill"}, args...)
		cmd.Execute()
	}
}