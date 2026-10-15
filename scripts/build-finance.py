"""Merge the upstream securities and HK bank lists into one Mihomo rule set."""
from pathlib import Path
import argparse
from collections import Counter
import ipaddress
import json
import urllib.request

REPOSITORY = 'LingJingMaster/Shadowrocket-Rules'
SOURCES = ('HK_Broker.list', 'HSBC_HK.list', 'HK_Banks_Direct.list')
ROOT = Path(__file__).resolve().parents[1]

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'Finance-rules-builder'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode('utf-8-sig')

def build(ref):
    commit = json.loads(fetch(f'https://api.github.com/repos/{REPOSITORY}/commits/{ref}'))
    sha = commit['sha']
    base = f'https://raw.githubusercontent.com/{REPOSITORY}/{sha}/'
    rules = []
    seen = set()
    counts = {}
    translated = []
    for source in SOURCES:
        count = 0
        for raw in fetch(base + source).splitlines():
            line = raw.strip()
            if not line or line.startswith(('#', '!', ';')):
                continue
            count += 1
            fields = [field.strip() for field in line.split(',')]
            kind = fields[0]
            if kind == 'URL-REGEX':
                if fields != ['URL-REGEX', r'^https?://www\.sc\.com/hk/']:
                    raise ValueError(f'Unsupported URL match in {source}: {line}')
                translated.append({'source': source, 'from': line, 'to': 'DOMAIN,www.sc.com'})
                fields = ['DOMAIN', 'www.sc.com']
            elif kind in ('DOMAIN', 'DOMAIN-SUFFIX', 'DOMAIN-KEYWORD'):
                if len(fields) != 2:
                    raise ValueError(f'Unexpected domain rule in {source}: {line}')
                fields[1] = fields[1].lower()
            elif kind in ('IP-CIDR', 'IP-CIDR6'):
                if len(fields) not in (2, 3) or (len(fields) == 3 and fields[2] != 'no-resolve'):
                    raise ValueError(f'Unexpected IP rule in {source}: {line}')
                fields[1] = str(ipaddress.ip_network(fields[1], strict=False))
                fields = [kind, fields[1], 'no-resolve']
            else:
                raise ValueError(f'Unsupported rule type in {source}: {line}')
            normalized = ','.join(fields)
            if normalized not in seen:
                seen.add(normalized)
                rules.append(normalized)
        counts[source] = count

    license_text = fetch(base + 'LICENSE')
    header = [
        '# NAME: Finance',
        '# DESCRIPTION: Securities and Hong Kong banks; one policy for all entries.',
        f'# SOURCE: https://github.com/{REPOSITORY}',
        f'# SOURCE-COMMIT: {sha}',
        f"# SOURCE-DATE: {commit['commit']['committer']['date']}",
        '# SOURCES: ' + ', '.join(SOURCES),
        '# FORMAT: Mihomo classical/text (domain, keyword, IPv4/IPv6).',
        '# ADAPTATION: URL path matching is unavailable; www.sc.com/hk/ becomes DOMAIN,www.sc.com.',
        '# The www.sc.com rule covers every URL path on that host.',
        f'# TOTAL: {len(rules)}',
        '#',
    ]
    header.extend('# ' + line if line else '#' for line in license_text.splitlines())
    destination = ROOT / 'mihomo/classical/Finance.list'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text('\n'.join(header) + '\n\n' + '\n'.join(rules) + '\n', encoding='utf-8')
    report = {
        'upstream': REPOSITORY,
        'commit': sha,
        'source_date': commit['commit']['committer']['date'],
        'sources': counts,
        'unique_rules': len(rules),
        'rule_types': dict(Counter(rule.split(',')[0] for rule in rules)),
        'translated': translated,
    }
    manifest = destination.with_name('Finance.sources.json')
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref', default='main', help='Upstream commit or branch to merge.')
    build(parser.parse_args().ref)
