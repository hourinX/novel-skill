package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var previewChapter int

var previewCmd = &cobra.Command{
	Use:   "preview",
	Short: "查看某章内容",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Printf("查看第 %d 章...\n", previewChapter)
		// TODO: 读取 data/chapters/ch00X.md 并输出
	},
}

func init() {
	previewCmd.Flags().IntVar(&previewChapter, "chapter", 1, "章节编号")
	rootCmd.AddCommand(previewCmd)
}
