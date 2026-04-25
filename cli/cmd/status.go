package cmd

import (
	"fmt"
	"encoding/json"
	"novel-skill/client"
	"github.com/spf13/cobra"
)

var statusCmd = &cobra.Command{
	Use:   "status",
	Short: "查看当前写作进度",
	Run: func(cmd *cobra.Command, args []string) {
		c := client.NewAIClient(getServiceURL())

		data, err := c.Get("/status")
		if err != nil {
			fmt.Printf("查询失败: %v\n", err)
			return
		}

		var resp client.StatusResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		fmt.Println("\n========== 写作进度 ==========")
		fmt.Printf("已完成章节：%d 章\n", resp.TotalChapters)

		if resp.HasDraft {
			fmt.Printf("当前草稿：%d 字（未确认）\n", resp.DraftWords)
		} else {
			fmt.Println("当前草稿：无")
		}

		fmt.Println("\n========== 偏好设置 ==========")
		if genre, ok := resp.Preferences["preferred_genre"]; ok {
			fmt.Printf("类型：%v\n", genre)
		}
		if style, ok := resp.Preferences["writing_style"]; ok {
			fmt.Printf("风格：%v\n", style)
		}
		if length, ok := resp.Preferences["chapter_length"]; ok {
			fmt.Printf("章节字数：%v\n", length)
		}
		if perspective, ok := resp.Preferences["narrative_perspective"]; ok {
			fmt.Printf("叙事视角：%v\n", perspective)
		}
	},
}

func init() {
	rootCmd.AddCommand(statusCmd)
}
