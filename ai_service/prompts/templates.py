from .writing_rules import WRITING_RULES, NARRATIVE_RULES


def build_generate_prompt(
    chapter_info: dict,
    outline: str,
    worldview: str,
    character: str,
    memory: str,
    recent_chapters: list[str],
    segment_index: int,
    total_segments: int,
    words: int,
    previous_segments: str = "",
    fanfic_context: str = "",
) -> str:
    recent_text = "\n\n---\n\n".join(recent_chapters) if recent_chapters else "（暂无）"
    prev_text = previous_segments if previous_segments else "（本段为第一段）"
    worldview_section = f"\n## 世界线设定\n{worldview}\n" if worldview else ""
    character_section = f"\n## 主角设定\n{character}\n" if character else ""
    fanfic_section = f"\n{fanfic_context}\n" if fanfic_context else ""
    correction_section = f"\n## ⚠️ 纠错要求（必须严格遵守）\n{chapter_info.get('correction_note', '')}\n" if chapter_info.get('correction_note') else ""

    return f"""你是一位专业的中文小说作家。请根据以下所有信息，创作小说第{chapter_info.get('chapter', '')}的第{segment_index+1}/{total_segments}段，目标字数约{words}字。

## 本章信息
- 标题：{chapter_info.get('title', '')}
- 核心事件：{chapter_info.get('core_event', '')}
- 人物弧光：{chapter_info.get('character_arc', '')}
- 伏笔：{chapter_info.get('foreshadowing', '')}
- 情绪基调：{chapter_info.get('tone', '')}
- 结尾钩子类型：{chapter_info.get('hook_type', '')}
{worldview_section}{character_section}
## 章节大纲
{outline}

## 记忆库（伏笔/人物状态）
{memory}
{fanfic_section}
## 最近章节全文
{recent_text}

## 本章已写内容
{prev_text}
{correction_section}
{WRITING_RULES}
{NARRATIVE_RULES}

## 创作要求
- 严格控制字数在{words}字左右
- {"本段是最后一段，必须使用上述钩子类型收尾" if segment_index == total_segments - 1 else "本段不是最后一段，保持叙事流畅，不要收尾"}
- 严禁重复已写内容，每段必须推进情节，不得出现与本章已写内容相同或相似的场景
- 严格遵守时间线，不得让尚未出现的角色提前登场
- 直接输出正文，不要任何解释或标注

请开始创作："""


def build_pre_analysis_prompt(
    chapter_info: dict,
    worldview: str,
    character: str,
    memory: str,
) -> str:
    worldview_section = f"\n## 世界线设定\n{worldview}\n" if worldview else ""
    character_section = f"\n## 主角设定\n{character}\n" if character else ""

    return f"""你是一个专业的小说策划编辑。请根据以下信息，对即将创作的章节做写前分析。

## 本章大纲信息
- 章节：{chapter_info.get('chapter', '')}
- 标题：{chapter_info.get('title', '')}
- 核心事件：{chapter_info.get('core_event', '')}
- 人物弧光：{chapter_info.get('character_arc', '')}
- 伏笔：{chapter_info.get('foreshadowing', '')}
- 情绪基调：{chapter_info.get('tone', '')}
- 结尾钩子类型：{chapter_info.get('hook_type', '')}
{worldview_section}{character_section}
## 当前记忆库
{memory}

## 请输出以下分析：
1. 上章结尾状态（根据记忆库推断）
2. 本章核心事件拆解
3. 需要呼应的伏笔
4. 情绪基调把控建议
5. 结尾钩子设计思路

请用简洁的条目格式输出："""


def build_polish_prompt(
    draft: str,
    style_refs: list[str],
    chapter_info: dict,
) -> str:
    style_text = "\n\n---\n\n".join(style_refs) if style_refs else "（无风格参考）"

    return f"""你是一位专业的中文小说编辑。请根据风格参考片段，对以下草稿进行润色，保持原有情节不变，提升文学质量。

## 风格参考片段
{style_text}

## 本章信息
- 情绪基调：{chapter_info.get('tone', '')}
- 结尾钩子类型：{chapter_info.get('hook_type', '')}

## 待润色草稿
{draft}

{WRITING_RULES}

## 润色要求
- 保持原有情节、人物、伏笔完全不变
- 向风格参考的语言风格靠拢
- 字数变化不超过原文的 10%
- 直接输出润色后的正文，不要任何解释

请开始润色："""


def build_accept_summary_prompt(chapter_content: str, chapter_num: int) -> str:
    return f"""请对以下小说第{chapter_num}章内容进行摘要提取，用于更新记忆库。

## 章节内容
{chapter_content}

## 请输出以下内容（JSON格式）：
{{
  "summary": "本章100字以内的情节摘要",
  "new_foreshadowing": ["新埋下的伏笔1", "新埋下的伏笔2"],
  "character_updates": ["人物A：当前状态变化", "人物B：当前状态变化"],
  "unresolved_conflicts": ["未解决冲突1", "未解决冲突2"]
}}

只输出 JSON，不要任何其他内容："""


def build_outline_extend_prompt(
    worldview: str,
    current_outline: str,
    memory: str,
    last_chapter_num: int,
    count: int = 5,
    recent_novel: str = "",
    note: str = "",
) -> str:
    format_lines = "\n".join(
        f"| 第{last_chapter_num + i}章 | 标题 | 核心事件 | 人物弧光 | 伏笔 | 情绪基调 | 结尾钩子类型 |"
        for i in range(1, count + 1)
    )
    novel_section = f"\n## 已完成章节正文（末尾片段，用于剧情衔接）\n{recent_novel}\n" if recent_novel else ""
    note_section = f"\n## 用户补充要求（必须严格遵守）\n{note}\n" if note else ""

    return f"""你是一位专业的中文小说策划编辑。请根据世界线设定和当前进度，为小说续写接下来{count}章的大纲。

## 世界线设定
{worldview}

## 当前大纲
{current_outline}

## 当前记忆库
{memory}
{novel_section}{note_section}
## 严格要求
1. 从第{last_chapter_num + 1}章开始，连续生成{count}章
2. 每章必须是完整的表格行，包含全部7列，每列不能为空
3. 只输出{count}行表格数据，不输出表头，不输出任何解释文字
4. 每列内容50字以内，简洁精准
5. 严格遵循世界线剧情走向
6. 剧情必须与已完成章节正文自然衔接，不得出现时间线或人物状态矛盾

## 输出格式（严格按此格式，共{count}行）
{format_lines}

请用实际内容替换上面的占位词，直接输出{count}行："""