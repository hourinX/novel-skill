package cmd

import (
	"fmt"
	"encoding/json"
	"novel-skill/client"
	"github.com/spf13/cobra"
)

var acceptChapter int

var acceptCmd = &cobra.Command{
	Use:   "accept",
	Short: "确认草稿，同步所有文件",
	Run: func(cmd *cobra.Command, args []string) {
		if !cmd.Flags().Changed("chapter") {
			acceptChapter = currentChapter
		}
		c := client.NewAIClient(getServiceURL())

		fmt.Printf("正在确认第 %d 章，AI 提取摘要中...\n", acceptChapter)

		data, err := c.Post("/accept", client.AcceptRequest{
			Chapter: acceptChapter,
		})
		if err != nil {
			fmt.Printf("确认失败: %v\n", err)
			return
		}

		var resp client.AcceptResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		fmt.Println("\n========== 本章摘要 ==========")
		fmt.Println(resp.Summary)

		if len(resp.NewForeshadowing) > 0 {
			fmt.Println("\n📌 新埋伏笔：")
			for _, f := range resp.NewForeshadowing {
				fmt.Printf("  - %s\n", f)
			}
		}

		if len(resp.CharacterUpdates) > 0 {
			fmt.Println("\n👤 人物状态更新：")
			for _, u := range resp.CharacterUpdates {
				fmt.Printf("  - %s\n", u)
			}
		}

		if len(resp.UnresolvedConflicts) > 0 {
			fmt.Println("\n⚔️  未解决冲突：")
			for _, conflict := range resp.UnresolvedConflicts {
				fmt.Printf("  - %s\n", conflict)
			}
		}

		if resp.OutlineExtended {
			fmt.Println("\n📋 大纲已自动续写，新增5章")
		}
		fmt.Println("\n✅ 章节已确认，文件同步完成")
	},
}

func init() {
	acceptCmd.Flags().IntVar(&acceptChapter, "chapter", 1, "章节编号")
	rootCmd.AddCommand(acceptCmd)
}
