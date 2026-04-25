package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var rejectCmd = &cobra.Command{
	Use:   "reject",
	Short: "丢弃当前草稿",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("草稿已丢弃。")
		// TODO: 调用 ai_client 发请求
	},
}

func init() {
	rootCmd.AddCommand(rejectCmd)
}
