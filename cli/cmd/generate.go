package cmd

import (
	"fmt"
	"encoding/json"
	"novel-skill/client"
	"github.com/spf13/cobra"
	"os"
	"path/filepath"
)

var chapterNum int
var wordCount int

var generateCmd = &cobra.Command{
	Use:   "generate",
	Short: "生成指定章节",
	Run: func(cmd *cobra.Command, args []string) {
		// 检测是否有未完成草稿
		root := findProjectRoot()
		draftPath := filepath.Join(root, "draft", "current_draft.md")
		if info, err := os.Stat(draftPath); err == nil && info.Size() > 0 {
			fmt.Println("⚠️  当前有未确认的草稿，请先 accept 或 reject 再生成新章节")
			return
		}
		c := client.NewAIClient(getServiceURL())

		fmt.Printf("正在生成第 %d 章，目标字数：%d...\n", chapterNum, wordCount)
		fmt.Println("（写前分析中，请稍候）")

		data, err := c.Post("/generate", client.GenerateRequest{
			Chapter: chapterNum,
			Words:   wordCount,
		})
		if err != nil {
			fmt.Printf("生成失败: %v\n", err)
			return
		}

		var resp client.GenerateResponse
		if err := json.Unmarshal(data, &resp); err != nil {
			fmt.Printf("解析响应失败: %v\n", err)
			return
		}

		fmt.Println("\n========== 写前分析 ==========")
		fmt.Println(resp.Analysis)
		fmt.Printf("\n========== 生成完成 ==========\n")
		fmt.Printf("第 %d 章已写入草稿\n", resp.Chapter)
		fmt.Printf("目标字数：%d　实际字数：%d\n", resp.WordsTarget, resp.WordsActual)
		currentChapter = chapterNum
		fmt.Println("\n草稿已保存至 draft/current_draft.md")
		fmt.Println("使用 accept 确认，或 polish 润色，或 regenerate 重新生成")
	},
}

func init() {
	generateCmd.Flags().IntVar(&chapterNum, "chapter", 1, "章节编号")
	generateCmd.Flags().IntVar(&wordCount, "words", 8000, "目标字数")
	rootCmd.AddCommand(generateCmd)
}
