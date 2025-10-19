#!/usr/bin/env python3
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
REC = ROOT/'recipes'
def files():
  for p in REC.glob('*/*.md'):
    if p.name.startswith('_'): continue
    yield p
def title(md):
  for l in md.splitlines():
    if l.startswith('# '): return l[2:].strip()
  return None
def category(md):
  for l in md.splitlines():
    if l.lower().startswith('- category:'):
      return l.split(':',1)[1].strip()
  return 'misc'
def tags(md):
  for l in md.splitlines():
    if l.lower().startswith('- tags:'):
      return [t.strip().lower() for t in l.split(':',1)[1].split(',') if t.strip()]
  return []
def ingredients(md):
  items=[]; in_sec=False
  for l in md.splitlines():
    if l.strip().lower()=='## ingredients': in_sec=True; continue
    if in_sec and l.startswith('## '): break
    if in_sec and l.strip().startswith('- '): items.append(l.strip()[2:])
  return items
def main():
  entries=[]; by_cat={}; by_tag={}
  for p in files():
    md=p.read_text(encoding='utf-8'); t=title(md) or p.stem; c=category(md); rel=str(p.relative_to(ROOT))
    entries.append((t,rel,md)); by_cat.setdefault(c,[]).append((t,rel))
    for tg in tags(md): by_tag.setdefault(tg,[]).append((t,rel))
  # all index
  (REC/'_all.md').write_text('# All Recipes (A–Z)\n\n'+'\n'.join(f'- [{t}]({r})' for t,r,_ in sorted(entries))+"\n", encoding='utf-8')
  # category indexes
  for c, items in by_cat.items():
    out=REC/c/'_index.md'; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f"# {c.replace('-', ' ').title()}\n\n"+'\n'.join(f'- [{t}]({Path(r).name})' for t,r in sorted(items))+"\n", encoding='utf-8')
  # tags
  tagdir=REC/'tags'; tagdir.mkdir(exist_ok=True)
  (REC/'tags.md').write_text('# Tags\n\n'+'\n'.join(f'- [{tg}](tags/{tg}.md)' for tg in sorted(by_tag))+"\n", encoding='utf-8')
  for tg, items in by_tag.items():
    (tagdir/f'{tg}.md').write_text(f"# Tag: {tg}\n\n"+'\n'.join(f'- [{t}]({r})' for t,r in sorted(items))+"\n", encoding='utf-8')
  # ingredient catalog
  payload=[{'title':t,'path':r,'ingredients':ingredients(md)} for t,r,md in entries]
  (REC/'ingredients.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
if __name__=='__main__': main()
