from difflib import Differ
from typing import Tuple

differ = Differ()


def html_diff(old: str, new: str) -> str:
    result = ""
    plus_accumulator: list = []
    minus_accumulator: list = []

    def flush_accumulator(
        result: str, accumulator: list, tag_name: str = "ins"
    ) -> Tuple[str, list]:
        if accumulator:
            result += f" <{tag_name}>{' '.join(accumulator)}</{tag_name}>"
            accumulator = []
        return result, accumulator

    for item in differ.compare(old.split(), new.split()):
        if item.startswith("+ "):
            result, minus_accumulator = flush_accumulator(
                result, minus_accumulator, tag_name="del"
            )
            plus_accumulator.append(item[2:].strip())
        elif item.startswith("- "):
            result, plus_accumulator = flush_accumulator(result, plus_accumulator)
            minus_accumulator.append(item[2:].strip())
        else:
            if item.startswith("? "):
                pass
            else:
                result, plus_accumulator = flush_accumulator(result, plus_accumulator)
                result, minus_accumulator = flush_accumulator(
                    result, minus_accumulator, tag_name="del"
                )
                result += f" {item[2:]}"

    result, plus_accumulator = flush_accumulator(result, plus_accumulator)
    result, minus_accumulator = flush_accumulator(
        result, minus_accumulator, tag_name="del"
    )
    return result.strip()
