def count_chinese_words(text: str) -> int:
    """统计中文字符数（含标点）"""
    return sum(1 for c in text if '\u4e00' <= c <= '\u9fff' or c in '，。！？；：""''、…—')


def check_word_count(text: str, target: int, tolerance: float = 0.1) -> tuple[bool, int]:
    """
    检查字数是否达标
    返回 (是否达标, 实际字数)
    tolerance: 允许的误差比例，默认 10%
    """
    actual = count_chinese_words(text)
    min_count = int(target * (1 - tolerance))
    return actual >= min_count, actual


def check_coherence(prev_ending: str, current_beginning: str) -> bool:
    """
    简单连贯性检查：当前章节开头是否与上章结尾有重叠关键词
    后续可替换为 AI 判断
    """
    if not prev_ending or not current_beginning:
        return True
    prev_words = set(prev_ending[-200:])
    curr_words = set(current_beginning[:200])
    overlap = prev_words & curr_words
    return len(overlap) > 5


def split_into_segments(total_words: int, words_per_segment: int) -> list[int]:
    """将目标字数拆分为多个段落的字数列表"""
    segments = []
    remaining = total_words
    while remaining > 0:
        seg = min(words_per_segment, remaining)
        segments.append(seg)
        remaining -= seg
    return segments