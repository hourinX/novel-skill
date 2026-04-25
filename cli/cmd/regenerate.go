package cmd

import (
	"encoding/json"
	"fmt"

	"novel-skill/client"
	"github.com/spf13/cobra"
)

var regenerateWords int
var regenerateNote string

var regenerateCmd = &cobra.Command{
	Use:   "regenerate",
	Short: "重新生成当前章节草稿",
	Run: func(cmd *cobra.Command, args []string) {
		c := client.NewAIClient(getServiceURL())

		fmt.Printf("重新生成第 %d 章...\n", currentChapter)
		if regenerateNote != "" {
			fmt.Printf("纠错备注：%s\n", regenerateNote)
		}

		data, err := c.Post("/regenerate", client.RegenerateRequest{
			Chapter: currentChapter,
			Words:   regenerateWords,
			Note:    regenerateNote,
		})
		if err != nil {
			fmt.Printf("重新生成失败: %v\n", err)
			return
		}

		var resp client.RegenerateResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		fmt.Printf("\n✅ 第 %d 章重新生成完成，实际字数：%d\n", resp.Chapter, resp.WordsActual)
		fmt.Println("草稿已覆盖，使用 accept 确认或 polish 润色")
	},
}

func init() {
	regenerateCmd.Flags().IntVar(&regenerateWords, "words", 0, "目标字数（默认使用偏好设置）")
	regenerateCmd.Flags().StringVar(&regenerateNote, "note", "", "纠错备注，告诉AI需要修正什么")
	rootCmd.AddCommand(regenerateCmd)
}