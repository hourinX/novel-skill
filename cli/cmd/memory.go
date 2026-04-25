package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var memoryCmd = &cobra.Command{
	Use:   "memory",
	Short: "查看伏笔和人物状态",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("读取记忆库中...")
		// TODO: 读取 data/memory.md 并输出
	},
}

func init() {
	rootCmd.AddCommand(memoryCmd)
}
