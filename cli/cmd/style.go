package cmd

import (
	"encoding/json"
	"fmt"

	"novel-skill/client"
	"github.com/spf13/cobra"
)

type IndexStyleResponse struct {
	Indexed []string `json:"indexed"`
	Skipped []string `json:"skipped"`
}

var styleCmd = &cobra.Command{
	Use:   "style-index",
	Short: "扫描 style_refs 目录，向量化风格参考入库",
	Run: func(cmd *cobra.Command, args []string) {
		c := client.NewAIClient(getServiceURL())

		fmt.Println("正在扫描 data/style_refs/ 目录并向量化入库...")

		data, err := c.Post("/style/index", map[string]interface{}{})
		if err != nil {
			fmt.Printf("索引失败: %v\n", err)
			return
		}

		var resp IndexStyleResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		if len(resp.Indexed) > 0 {
			fmt.Println("\n✅ 已入库：")
			for _, name := range resp.Indexed {
				fmt.Printf("  - %s\n", name)
			}
		}

		if len(resp.Skipped) > 0 {
			fmt.Println("\n⚠️  已跳过：")
			for _, name := range resp.Skipped {
				fmt.Printf("  - %s\n", name)
			}
		}

		if len(resp.Indexed) == 0 && len(resp.Skipped) == 0 {
			fmt.Println("data/style_refs/ 目录为空，请放入 .txt 格式的参考小说")
		}
	},
}

func init() {
	rootCmd.AddCommand(styleCmd)
}