"""Workflow-dispatch text must reach Python as data, never shell syntax."""

from pathlib import Path

workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/refresh-fdc.yml").read_text()
assert 'FDC_QUERY: ${{ inputs.query }}' in workflow
assert 'FDC_PAGE_SIZE: ${{ inputs.page_size }}' in workflow
assert '--query "$FDC_QUERY" --page-size "$FDC_PAGE_SIZE"' in workflow
assert '--query "${{ inputs.query }}"' not in workflow
print("FDC workflow input isolation passed")
