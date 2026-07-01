from markdown_it import MarkdownIt

HTML_TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ResearchGraph Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.6; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f5f5f5; }}
    code {{ background: #f5f5f5; padding: 2px 4px; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""

def markdown_to_html(markdown: str) -> str:
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    return HTML_TEMPLATE.format(body=md.render(markdown))