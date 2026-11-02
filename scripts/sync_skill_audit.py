#!/usr/bin/env python3
"""Synchronize repository-local Skill inventory and auditable static-review artifacts.

Python 3.10+, standard library only. This does NOT perform a new expert review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / '.agents' / 'skills'
DOCS_DIR = ROOT / 'docs' / 'audit'
GENERATED = ('SKILL_INDEX.md', 'audit-register.json', 'AUDIT_VALIDATION_RESULTS.json', 'TECHNICAL_AUDIT.md')
README_START = '<!-- AUTO-SKILL-SUMMARY:START -->'
README_END = '<!-- AUTO-SKILL-SUMMARY:END -->'


def jread(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def jout(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False) + '\n'


def digest(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()


def fm_metadata(content: str):
    """Read the mandatory `name` and `description` from the existing frontmatter.

    Only a supported subset is checked, not a general-purpose YAML parser.
    In particular, multiline quoted and block scalar descriptions are supported.
    """
    lines = content.lstrip('\ufeff').splitlines()
    if not lines or lines[0].strip() != '---':
        return None, None, ['missing opening YAML frontmatter delimiter']
    stop = next((i for i in range(1, len(lines)) if lines[i].strip() == '---'), None)
    if stop is None:
        return None, None, ['missing closing YAML frontmatter delimiter']
    block = lines[1:stop]
    values = {}
    for i, line in enumerate(block):
        m = re.match(r'^([A-Za-z_-][\w-]*):\s*(.*?)\s*$', line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if key in values:
            return None, None, [f'duplicate frontmatter key: {key}']
        # Preserve continuation for quoted multi-line scalars and folded/plain block strings.
        parts = [value]
        for following in block[i+1:]:
            if re.match(r'^[A-Za-z_-][\w-]*:', following):
                break
            if following.strip() and not following.startswith((' ', '\t')):
                break
            if following.strip():
                parts.append(following.strip())
        if key in ('name', 'description'):
            if value in ('|', '|-', '>', '>-', '|+', '>+'):
                values[key] = ' '.join(parts[1:]).strip()
            else:
                values[key] = ' '.join(parts).strip().strip('"\'').strip()
    errors = []
    name = values.get('name', '')
    desc = values.get('description', '')
    if not name: errors.append('frontmatter name is missing')
    if not desc or desc.lower() in ('null', '~'):
        errors.append('frontmatter description is missing')
    if name and not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        errors.append('frontmatter name must be kebab-case')
    return name, desc, errors


def static_checks(skill_id: str, content: str, meta_name: str, is_support: bool):
    issues = []
    if meta_name and meta_name != skill_id:
        issues.append('folder name differs from frontmatter name')
    body = re.sub(r'\A(?:\ufeff)?---\n.*?\n---\n', '', content, count=1, flags=re.S)
    if not re.search(r'^#\s+\S', body, re.M):
        issues.append('missing Markdown H1 heading')
    # Count fences by delimiter, not programming language. This only tests balance.
    stacks = []
    for i, line in enumerate(body.splitlines(), 1):
        match = re.match(r'^\s{0,3}(`{3,}|~{3,})(?:\s*\w[^`]*)?\s*$', line)
        if match:
            marker = match.group(1)
            if stacks and marker[0] == stacks[-1][0] and len(marker) >= len(stacks[-1]):
                stacks.pop()
            elif not stacks:
                stacks.append(marker)
    if stacks:
        issues.append('unclosed Markdown code fence')
    return issues


def current_inventory():
    if not SKILLS_DIR.is_dir():
        raise RuntimeError(f'Skills directory missing: {SKILLS_DIR}')
    mapping = jread(DOCS_DIR / 'category-map.json')['categories']
    baseline = jread(DOCS_DIR / 'review-baseline.json')['reviews']
    records = []
    errors, warnings = [], []
    for path in sorted(SKILLS_DIR.glob('*/SKILL.md')):
        skill_id = path.parent.name
        raw = path.read_bytes()
        content = raw.decode('utf-8-sig')
        name, desc, fm_errors = fm_metadata(content)
        support = skill_id.endswith(('-skill-router', '-context-init'))
        category = 'Repository tools' if support else mapping.get(skill_id, 'Uncategorized')
        issues = fm_errors + static_checks(skill_id, content, name or '', support)
        if issues:
            errors.extend(f'{skill_id}: {issue}' for issue in issues)
        if category == 'Uncategorized':
            warnings.append(f'{skill_id}: add a category to docs/audit/category-map.json')
        prior = baseline.get(skill_id) if not support else None
        old_hash = prior.get('reviewed_sha256') if prior else None
        if support: status = 'not_applicable_support_skill'
        elif not prior or not old_hash: status = 'review_required_new_or_unreviewed'
        elif old_hash != digest(raw): status = 'review_required_content_changed'
        else: status = 'historical_static_review_current'
        if status.startswith('review_required_'):
            warnings.append(f'{skill_id}: substantive review required ({status})')
        records.append({
            'skill':skill_id,
            'category':category,
            'description':desc or '',
            'path':path.relative_to(ROOT).as_posix(),
            'sha256':digest(raw),
            'lines':len(content.splitlines()),
            'role':'support' if support else 'specialist',
            'static_checks':'passed' if not issues else 'failed',
            'static_issues':issues,
            'review_status':status,
            'historical_review_summary':str(prior.get('summary','')) if prior else '',
            'historical_review_source':'docs/audit/HISTORICAL_TECHNICAL_AUDIT.md' if prior else None,
            'historical_review_date':jread(DOCS_DIR / 'review-baseline.json').get('original_review_date') if prior else None,
        })
    specialists = [r for r in records if r['role']=='specialist']
    mapped_orphans = set(mapping) - {r['skill'] for r in specialists}
    if mapped_orphans:
        warnings.append('category-map has IDs no longer present: '+', '.join(sorted(mapped_orphans)))
    former_reviews = set(baseline) - {r['skill'] for r in specialists}
    if former_reviews:
        warnings.append('review baseline includes removed Skills (history retained): '+', '.join(sorted(former_reviews)))
    if len(records) != len(set(r['skill'] for r in records)):
        errors.append('duplicate Skill folder identifiers')
    return records, errors, warnings


def index_md(records):
    spec = [r for r in records if r['role']=='specialist']
    tools = [r for r in records if r['role']=='support']
    cats = {}
    for r in spec:
        cats.setdefault(r['category'],[]).append(r)
    lines = ['# Skill Index — '+ROOT.name, '',
        '> AUTO-GENERATED by `python scripts/sync_skill_audit.py --write`. Do not edit by hand.',
        '> This is a discovery catalog, not a claim that each methodology or API is currently correct.',
        '> An independent chat should select methods only from its current question; do not infer preferences from other chats.', '',
        f'**{len(spec)} specialists**, **{len(cats)} categories**, **{len(tools)} support Skills**, **{len(records)} Skills total**.', '',
        '## Specialist Skills', '']
    for category in sorted(cats, key=str.casefold):
        lines += [f'### {category} ({len(cats[category])})', '', '| Skill | When to use |', '|---|---|']
        for r in cats[category]:
            desc = re.sub(r'\s+',' ',r['description']).replace('|','\\|').replace('`',"'")
            lines.append(f"| [`{r['skill']}`]({r['path']}) | {desc} |")
        lines.append('')
    lines += ['## Support Skills', '', '| Skill | Purpose |', '|---|---|']
    for r in tools:
        desc = re.sub(r'\s+',' ',r['description']).replace('|','\\|')
        lines.append(f"| [`{r['skill']}`]({r['path']}) | {desc} |")
    lines += ['', '## How to select Skills', '',
        '1. Read this index or the appropriate descriptions; avoid reading all `SKILL.md` files.',
        '2. Read the router and only the specialist files relevant to the **current** request.',
        '3. To refresh this inventory after editing Skills, run `python scripts/sync_skill_audit.py --write`.',
        '4. The generator tracks static checks and historical review status; it does **not** perform fresh subject-matter verification.', '']
    return '\n'.join(lines)


def audit_report(records, errors, warnings):
    spec=[r for r in records if r['role']=='specialist']
    categories=Counter(r['category'] for r in spec)
    reviewed=sum(r['review_status']=='historical_static_review_current' for r in spec)
    changed=sum(r['review_status']=='review_required_content_changed' for r in spec)
    new=sum(r['review_status']=='review_required_new_or_unreviewed' for r in spec)
    lines=['# Technical Audit — '+ROOT.name,'',
        '> AUTO-GENERATED review-status report. This is **not** a fresh independent technical review.',
        '> The original substantive report is preserved at [`docs/audit/HISTORICAL_TECHNICAL_AUDIT.md`](docs/audit/HISTORICAL_TECHNICAL_AUDIT.md).','',
        '## Inventory and evidence boundaries','',
        f'- Specialized Skills: **{len(spec)}**; support Skills: **{len(records)-len(spec)}**; categories: **{len(categories)}**.',
        f'- Historical static review still matches SHA-256: **{reviewed}**.',
        f'- Modified since previous review and needing renewed expert assessment: **{changed}**.',
        f'- New/unreviewed Skills needing expert assessment: **{new}**.',
        f'- Structural validation errors: **{len(errors)}**; review/category warnings: **{len(warnings)}**.',
        '- Hash agreement means only that the file is unchanged since the **historical static review**. It does not certify APIs, claims, code or outcomes.',
        '- This automated pipeline cannot verify live integrations, legal/regulatory suitability, empirical performance, market data, or new technical claims.',
        '- Manual review results must be recorded in `docs/audit/review-baseline.json` with the actual reviewed SHA-256 and evidence after a real review.','',
        '## Current issues','']
    if errors:
        lines.extend(f'- **ERROR:** {e}' for e in errors)
    else:lines.append('- No structural errors detected by supported static checks.')
    if warnings:
        lines.extend(f'- **ACTION:** {w}' for w in warnings)
    else:lines.append('- No review/category warnings.')
    lines.extend(['','## Per-Skill status','', '| Skill | Category | Static checks | Review state | SHA-256 (prefix) |','|---|---|---|---|---|'])
    for r in spec:
        lines.append(f"| [`{r['skill']}`]({r['path']}) | {r['category']} | {r['static_checks']} | `{r['review_status']}` | `{r['sha256'][:12]}` |")
    lines+=['','## Historical evidence and follow-up','',
        'The detailed, historical per-Skill findings are stored in `docs/audit/HISTORICAL_TECHNICAL_AUDIT.md`.',
        '`audit-register.json` contains the current digest, automated signals and a **provenance-labeled** historical summary for each file.',
        'To confirm a modified Skill, perform an actual content review against applicable current source material and tests, then update its baseline hash and notes.',
        'Run `python scripts/sync_skill_audit.py --write` and commit the regenerated files.','']
    return '\n'.join(lines)


def generated_outputs(records, errors, warnings):
    spec=[r for r in records if r['role']=='specialist']
    status=Counter(r['review_status'] for r in spec)
    categories=Counter(r['category'] for r in spec)
    val={
      'schema_version':2,
      'repository':ROOT.name,
      'source':'current .agents/skills/*/SKILL.md and docs/audit/review-baseline.json',
      'generator':'scripts/sync_skill_audit.py',
      'total_skills':len(records),
      'specialist_skills':len(spec),
      'support_skills':len(records)-len(spec),
      'categories':len(categories),
      'category_counts':dict(sorted(categories.items())),
      'static_validation':'passed' if not errors else 'failed',
      'static_checks_performed':['frontmatter delimiters and mandatory name/description','folder and Skill identity','Markdown H1','balanced Markdown code fences','category assignment coverage','deterministic generated artifact consistency'],
      'expert_review_counts':dict(sorted(status.items())),
      'errors':errors,
      'warnings':warnings,
      'not_tested':['complete YAML schema beyond required metadata','source code compilation and execution','live APIs, networks, payment systems and markets','full expert re-review of every claim','all internal or external markdown links'],
      'expert_review_policy':'Changing a Skill SHA-256 invalidates the previous historical review match; generator never self-certifies substantive correctness.'
    }
    return {
       'SKILL_INDEX.md': index_md(records),
       'audit-register.json': jout(records),
       'AUDIT_VALIDATION_RESULTS.json': jout(val),
       'TECHNICAL_AUDIT.md': audit_report(records,errors,warnings)
    }


def summary_md(records):
    spec=[r for r in records if r['role']=='specialist']
    cats=Counter(r['category'] for r in spec)
    statuses=Counter(r['review_status'] for r in spec)
    return '\n'.join([README_START,
        f'**Live inventory:** {len(records)} Skills = {len(spec)} specialist + {len(records)-len(spec)} support; **{len(cats)} categories**.', '',
        'The up-to-date category/Skill catalog is [`SKILL_INDEX.md`](SKILL_INDEX.md). The automatically synchronized audit status is [`TECHNICAL_AUDIT.md`](TECHNICAL_AUDIT.md); machine-readable checks are [`AUDIT_VALIDATION_RESULTS.json`](AUDIT_VALIDATION_RESULTS.json) and [`audit-register.json`](audit-register.json).', '',
        f"**Historical review status:** {statuses['historical_static_review_current']} unchanged since prior static review; {statuses['review_required_content_changed']} changed and pending reassessment; {statuses['review_required_new_or_unreviewed']} new/unreviewed.", '',
        'Regenerate after editing Skills: `python scripts/sync_skill_audit.py --write`. GitHub Actions performs this on pushes to the default branch; pull requests are checked for synchronization. No new expert review is implied.',
        README_END])


def prepare_readme(readme, records):
    marker=summary_md(records)
    if README_START in readme and README_END in readme:
        i=readme.index(README_START); j=readme.index(README_END,i)+len(README_END)
        return readme[:i]+marker+readme[j:]
    title='## Automated Skill catalog and audit status\n\n'+marker+'\n\n'
    firstbreak=readme.find('\n')
    if firstbreak>=0:
        return readme[:firstbreak+1]+'\n'+title+readme[firstbreak+1:]
    return title+readme


def main():
    parser=argparse.ArgumentParser(description='Synchronize root Skill index, audit registry and validation evidence')
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true',help='Regenerate deterministic artifacts from local Skills')
    group.add_argument('--check',action='store_true',help='Fail if generated files are missing or stale')
    args=parser.parse_args()
    records, errors, warnings = current_inventory()
    outputs=generated_outputs(records,errors,warnings)
    readme_path=ROOT/'README.md'
    if readme_path.exists(): outputs['README.md']=prepare_readme(readme_path.read_text(encoding='utf-8'),records)
    stale=[]
    for n,content in outputs.items():
        p=ROOT/n
        if not p.exists() or p.read_text(encoding='utf-8') != content:
            stale.append(n)
            if args.write:
                p.write_text(content,encoding='utf-8')
    print(f'{ROOT.name}: Skills={len(records)}, categories={len({r["category"] for r in records if r["role"]=="specialist"})}, errors={len(errors)}, review warnings={len(warnings)}')
    if stale:
        print(('Updated: ' if args.write else 'Out of date: ')+', '.join(stale))
    if errors:
        for e in errors[:25]:print('ERROR:',e,file=sys.stderr)
        return 1
    if args.check and stale:
        print('Run: python scripts/sync_skill_audit.py --write',file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    sys.exit(main())
