package cmd

import (
	"encoding/json"
	"fmt"

	"novel-skill/client"
	"github.com/spf13/cobra"
)

var extendFromChapter int
var extendCount int
var extendNote string

var extendOutlineCmd = &cobra.Command{
	Use:   "extend-outline",
	Short: "根据 novel.md 与提示词续写后续章节大纲（默认补齐到下一个5的倍数）",
	Run: func(cmd *cobra.Command, args []string) {
		c := client.NewAIClient(getServiceURL())
		fmt.Println("正在续写大纲...")
		if extendNote != "" {
			fmt.Printf("提示词：%s\n", extendNote)
		}

		data, err := c.Post("/outline/extend", client.ExtendOutlineRequest{
			FromChapter: extendFromChapter,
			Count:       extendCount,
			Note:        extendNote,
		})
		if err != nil {
			fmt.Printf("续写失败: %v\n", err)
			return
		}

		var resp client.ExtendOutlineResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		if resp.Count == 0 {
			fmt.Println("⚠️ 模型返回内容无法解析为表格行，outline.md 未变更")
			return
		}
		fmt.Printf("\n📋 大纲已续写，从第 %d 章之后新增 %d 章\n", resp.FromChapter, resp.Count)
		fmt.Println("查看 data/outline.md 确认内容")
	},
}

func init() {
	extendOutlineCmd.Flags().IntVar(&extendFromChapter, "from", 0, "从哪章之后开始续写（0=自动取当前大纲最大章节号）")
	extendOutlineCmd.Flags().IntVar(&extendCount, "count", 0, "续写章节数（0=自动补齐到下一个5的倍数）")
	extendOutlineCmd.Flags().StringVar(&extendNote, "note", "", "提示词，指导后续剧情走向")
	rootCmd.AddCommand(extendOutlineCmd)
}