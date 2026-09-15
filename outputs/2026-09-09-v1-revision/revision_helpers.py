"""Apply the approved structural revisions. Source snapshots make reruns deterministic."""
from pathlib import Path
from bs4 import BeautifulSoup as BS
from html import escape as E
import re, json, subprocess, shutil
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
BEFORE = OUT/'source/before-v1'
HTML = ROOT/'v1/html'

def read(name):
    return BS((BEFORE/(name+'.txt')).read_text(), 'html.parser')

def fragment(text):
    return BS(text, 'html.parser')

def put(name, soup):
    if not soup.select_one('link[href*="revision.css"]'):
        soup.head.append(fragment('<link rel="stylesheet" href="../css/revision.css?v=20260909">'))
    (HTML/name).write_text(str(soup))

def hero(soup, src, pos='50% 50%'):
    h=soup.select_one('.page-hero')
    h['class']=list(dict.fromkeys(h.get('class',[])+['has-photo']))
    h['style']=f"--hero-img: url('{src}'); background-position: {pos};"

def picker(options, selected=None):
    selected=selected or options[0][0]
    label=dict(options)[selected]
    return fragment('<div class="term-bar"><span class="term-bar-label">屆次 / Year</span><div class="term-picker" data-term-picker><button type="button" class="term-trigger" id="term-trigger" aria-haspopup="listbox" aria-controls="term-menu" aria-expanded="false"><span data-term-label>'+E(label)+'</span><span aria-hidden="true">⌄</span></button><ul class="term-menu" id="term-menu" role="listbox" aria-labelledby="term-trigger" hidden>'+''.join(f'<li class="term-option" role="option" data-value="{value}" aria-selected="{str(value==selected).lower()}">{E(label)}</li>' for value,label in options)+'</ul></div></div>')

def redirect(name, target, label, en=False):
    s=read(name)
    s.head.append(fragment(f'<meta http-equiv="refresh" content="0; url={E(target)}"><link rel="canonical" href="{E(target)}">'))
    s.main.clear()
    s.main.append(fragment(f'<section class="page-section"><div class="container"><h1>{E(label)}</h1><p><a class="btn btn-primary" href="{E(target)}">{E(label)} →</a></p></div></section>'))
    put(name,s)

