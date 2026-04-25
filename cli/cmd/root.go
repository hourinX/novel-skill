package cmd

import "github.com/spf13/cobra"

var rootCmd = &cobra.Command{
	Use:   "novel-skill",
	Short: "AI 全程执笔的本地小说创作工具",
}
var currentChapter int = 1

func Execute() error {
	return rootCmd.Execute()
}
