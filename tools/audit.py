#!/usr/bin/env python3
"""Base-aware link audit + index-coverage check for the Ai Metaverse static site.

Usage: python3 tools/audit.py [repo_root]
- Resolves every href/src against each page's <base href> and verifies the target exists on disk.
- Skips external/scheme URLs, pure fragments, JS template concatenations and the <base> tag itself.
- Coverage: every KNOWN flat page must be linked from index.html (directory form or flat form).
Exit code 0 = clean, 1 = problems found.
"""
import os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..'))

SKIP_SCHEMES = ('http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:', 'blob:', 'ftp:')

def pages():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in ('store', 'tools', 'py', 'faceforge', 'node_modules', '.git', 'assets')]
        for f in filenames:
            if f.endswith('.html'):
                yield os.path.join(dirpath, f)

def audit():
    broken = []
    total = 0
    for path in sorted(pages()):
        html = open(path, encoding='utf-8', errors='replace').read()
        # strip script/style contents so JS template strings don't produce fake attrs
        scan = re.sub(r'<script\b.*?</script>', ' ', html, flags=re.S | re.I)
        scan = re.sub(r'<style\b.*?</style>', ' ', scan, flags=re.S | re.I)
        m = re.search(r'<base\s+href="([^"]+)"', scan, re.I)
        basedir = os.path.dirname(path)
        if m:
            basedir = os.path.normpath(os.path.join(os.path.dirname(path), m.group(1)))
        for tag in re.findall(r'<[a-zA-Z][^>]*>', scan):
            if re.match(r'<base\b', tag, re.I):
                continue
            for attr in re.findall(r'(?:href|src)="([^"]*)"', tag):
                a = attr.strip()
                if not a or a.startswith('#') or a.startswith(SKIP_SCHEMES):
                    continue
                if "' +" in a or '${' in a or '"+' in a:
                    continue  # JS template concat leftovers
                total += 1
                clean = a.split('#')[0].split('?')[0]
                if not clean:
                    continue
                target = os.path.normpath(os.path.join(basedir, clean))
                if not os.path.exists(target):
                    broken.append((os.path.relpath(path, ROOT), a, os.path.relpath(target, ROOT)))
    return total, broken

def coverage():
    ix = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    known = [f for f in sorted(os.listdir(ROOT)) if f.endswith('.html') and f != 'index.html']
    missing = []
    for k in known:
        dirform = k[:-5] + '/index.html'
        if dirform not in ix and ('"' + k + '"') not in ix and ("'" + k + "'") not in ix:
            missing.append(k)
    return known, missing

def main():
    total, broken = audit()
    known, missing = coverage()
    print(f'links checked: {total}')
    if broken:
        print(f'BROKEN ({len(broken)}):')
        for src, a, tgt in broken[:40]:
            print(f'  {src}: {a} -> {tgt}')
    else:
        print('broken: 0')
    print(f'flat pages: {len(known)}')
    print('subpages NOT linked from index:', ', '.join(missing) if missing else 'NONE')
    sys.exit(1 if (broken or missing) else 0)

if __name__ == '__main__':
    main()
