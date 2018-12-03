def find_header_by_index(index, headers):
    return headers.find_element_by_css_selector(f"th:nth-child({index})")


def extract_column_text(index, trs):
    return [
        tr.find_element_by_css_selector(f"td:nth-child({index})").text for tr in trs
    ]
