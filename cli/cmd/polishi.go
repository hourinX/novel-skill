package cmd

import (
	"fmt"
	"encoding/json"
	"novel-skill/client"
	"github.com/spf13/cobra"
)

var styleRef string
var polishChapter int

var polishCmd = &cobra.Command{
	Use:   "polish",
	Short: "RAG 润色当前草稿",
	Run: func(cmd *cobra.Command, args []string) {
		if !cmd.Flags().Changed("chapter") {
			polishChapter = currentChapter
		}
		c := client.NewAIClient(getServiceURL())

		if styleRef != "" {
			fmt.Printf("使用风格参考「%s」润色第 %d 章...\n", styleRef, polishChapter)
		} else {
			fmt.Printf("润色第 %d 章...\n", polishChapter)
		}

		data, err := c.Post("/polish", client.PolishRequest{
			Chapter: polishChapter,
			Style:   styleRef,
		})
		if err != nil {
			fmt.Printf("润色失败: %v\n", err)
			return
		}

		var resp client.PolishResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		fmt.Println("\n✅ 润色完成，草稿已更新")
		fmt.Println("使用 accept 确认，或继续 polish 再次润色")
	},
}

func init() {
	polishCmd.Flags().StringVar(&styleRef, "style", "", "指定风格参考来源")
	polishCmd.Flags().IntVar(&polishChapter, "chapter", 1, "章节编号")
	rootCmd.AddCommand(polishCmd)
}
