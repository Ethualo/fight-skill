import json
import re
from pathlib import Path


root = Path(__file__).resolve().parents[1]
claude = json.loads((root / '.claude-plugin/plugin.json').read_text(encoding='utf-8'))
codex = json.loads((root / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
marketplace = json.loads((root / '.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
plugin = next(item for item in marketplace['plugins'] if item['name'] == codex['name'])
version = codex['version']
assert re.fullmatch(r'\d+\.\d+\.\d+', version), f'Invalid version: {version}'
assert claude['version'] == plugin['version'] == version, 'Manifest versions differ'

model_rows = []
for name in ('README.md', 'readme.ko.md'):
    content = (root / name).read_text(encoding='utf-8')
    badges = re.findall(r'img\.shields\.io/badge/version-([^/\s)]+)-blue', content)
    assert badges == [version], f'{name}: badge {badges} != {version}'
    rows = [line for line in content.splitlines() if line.startswith(('| Claude Code |', '| Codex |'))]
    assert len(rows) == 2, f'{name}: missing model rows'
    model_rows.append(rows)
assert model_rows[0] == model_rows[1], 'README model policies differ'

changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
latest = re.search(r'^## \[([^]]+)\]', changelog, re.MULTILINE)
assert latest and latest[1] == version, 'Latest changelog version differs'
print(f'Release checks passed: {version} (3 manifests, 2 READMEs, changelog)')
