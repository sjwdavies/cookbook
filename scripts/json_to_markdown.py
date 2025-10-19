#!/usr/bin/env python3
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'data'/'recipes'
OUT = ROOT/'recipes'
def kebab(s): return re.sub(r'[^a-z0-9]+','-', s.lower()).strip('-')
def line(i):
  q=str(i.get('quantity','')).strip(); u=i.get('unit','').strip(); it=i.get('item','').strip(); n=i.get('note','') or ''
  parts=[p for p in [q,u,it] if p]; txt=' '.join(parts) if parts else it
  if n: txt+=f', {n}'; return f'- {txt}'
def convert(p):
  o=json.loads(p.read_text(encoding='utf-8'))
  title=o['title']; slug=o.get('slug') or kebab(title); cats=o.get('categories') or ['misc']; primary=cats[0]
  serves=o.get('serves',''); prep=o.get('prep_time',''); cook=o.get('cook_time','')
  equipment=', '.join(o.get('equipment',[])); difficulty=o.get('difficulty',''); tags=', '.join(o.get('tags',[]))
  ings='\n'.join(line(i) for i in o.get('ingredients',[]))
  method='\n'.join(f"{i}. {s}" for i,s in enumerate(o.get('method',[]),1))
  notes='\n'.join(f"- {n}" for n in o.get('notes',[]))
  out=(OUT/primary); out.mkdir(parents=True, exist_ok=True)
  md=f"""# {title}

- Category: {primary}
- Serves: {serves}
- Prep time: {prep}
- Cook time: {cook}
- Equipment: {equipment}
- Difficulty: {difficulty}
- Tags: {tags}

## Ingredients
{ings}

## Method
{method}

## Notes
{notes}
"""
  (out/f"{slug}.md").write_text(md.strip()+"\n", encoding='utf-8')
def main():
  for p in sorted(DATA.glob('*.json')): convert(p)
if __name__=='__main__': main()
