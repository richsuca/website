#!/usr/bin/env python3

import argparse
import logging
from dataclasses import dataclass, field
from pathlib import Path
import re
import os
import shutil
import sys
from datetime import datetime
from string import Template
from titlecase import titlecase
import markdown
import glob
import yaml
from typing import List

@dataclass(order=True)
class Post:
    date: datetime = field(compare=True)
    title: str = field(compare=False)
    name: str = field(compare=False)
    text: str = field(compare=False)

    def __post_init__(self):
        self.title = titlecase(self.title)

posts: List[Post] = []

title_re = re.compile(r'title:\s*(.*)')
name_re = re.compile(r'name:\s*(.*)')
date_re = re.compile(r'date:\s*(.*)')

parser = argparse.ArgumentParser(description='Generate static blog')
parser.add_argument('--config', type=str, default='config.yaml', help='Config file path')
parser.add_argument('--output-dir', type=str, help='Output directory (overrides config)')
args = parser.parse_args()

root_dir = Path('.')

config_file = root_dir / args.config
with open(config_file) as f:
    config = yaml.safe_load(f)

logging_level = config.get('logging_level', 'INFO').upper()
logging_level_num = getattr(logging, logging_level, logging.INFO)

logging.basicConfig(level=logging_level_num, format='%(levelname)s: %(message)s')

base_url = config['base_url']
main_page_posts = config['main_page_posts']
rss_posts = config['rss_posts']
timezone = config['timezone']
markdown_extensions = config['markdown_extensions']
templates_dir_rel = config['templates_dir']
posts_dir_rel = config['posts_dir']
output_dir_rel = config['output_dir']
icons_dir_rel = config['icons_dir']
images_dir_rel = config['images_dir']
styles_css_rel = config['styles_css']

templates_dir = root_dir / templates_dir_rel
posts_dir = root_dir / posts_dir_rel
if args.output_dir:
    output_dir = Path(args.output_dir)
else:
    output_dir = root_dir / output_dir_rel
icons_dir = root_dir / icons_dir_rel
images_dir = root_dir / images_dir_rel
styles_css = root_dir / styles_css_rel

md = markdown.Markdown(extensions=markdown_extensions)

# get posts
post_dir = posts_dir
for post_file in post_dir.iterdir():
    # logging.debug(f'Reading {post_file.name}')
    with open(post_file, encoding='utf-8') as p:
        file_text = p.read()
        m = title_re.search(file_text)
        if m:
            title = m.group(1)
        m = name_re.search(file_text)
        if m:
            name = m.group(1)
        m = date_re.search(file_text)
        if m:
            date_str = m.group(1)
            date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        text_idx = file_text.find("text:")
        text = file_text[text_idx + len("text:") + 1:]
        
        if post_file.name[-3:] == '.md':
            text = md.convert(text)
            md.reset()

        posts.append(Post(date, title, name, text))

logging.info(f'Loaded {len(posts)} posts')

# archive previous output
output_dir_path = output_dir
archive_dir_name = 'output-' + datetime.now().strftime('%Y%m%d%H%M%S%f')
archive_dir = root_dir / archive_dir_name
try:
    output_dir_path.rename(archive_dir)
    logging.info(f'Archived previous output to {archive_dir}')
except FileExistsError:
    logging.error(f'Cannot move {output_dir_path} --> {archive_dir}')
    sys.exit()
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit()

try:
    output_dir_path.mkdir()
    logging.info(f'Created output directory {output_dir_path}')
except OSError:
    logging.error('Cannot create output directory')
    sys.exit()
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit()

post_template = ""
top_template = ""
bottom_template = ""
title_only_template = ""
rss_top_template = ""
rss_post_template = ""
rss_bottom_template = ""
contact_page = ""
others_page = ""

# get templates
templates_dir = root_dir / 'templates'
with open(templates_dir / 'main-top.txt', encoding='utf-8') as mtt:
    top_template = mtt.read()

with open(templates_dir / 'main-bottom.txt', encoding='utf-8') as mtb:
    bottom_template = mtb.read()

with open(templates_dir / 'posts.txt', encoding='utf-8') as pt:
    post_template = pt.read()

with open(templates_dir / 'title-only.txt', encoding='utf-8') as tt:
    title_only_template = tt.read()

with open(templates_dir / 'rss-top.txt', encoding='utf-8') as ft:
    rss_top_template = ft.read()

with open(templates_dir / 'rss-bottom.txt', encoding='utf-8') as ft:
    rss_bottom_template = ft.read()

with open(templates_dir / 'rss-post.txt', encoding='utf-8') as ft:
    rss_post_template = ft.read()

with open(templates_dir / 'contact-page.txt', encoding='utf-8') as cp:
    contact_page = cp.read()

with open(templates_dir / 'others-page.txt', encoding='utf-8') as op:
    others_page = op.read()

year_string = ""
month_string = ""
day_string = ""

# by date descending, this helps with getting a recent post list
posts.sort(reverse=True)

archives_dir = output_dir / 'archives'
feed_dir = output_dir / 'feed'
archives_dir.mkdir()
feed_dir.mkdir()

# write header to TOC page
with open(archives_dir / 'index.html', encoding='utf-8', mode='w') as pt:
    pt.write(top_template)

# write header to main page
with open(output_dir / 'index.html', encoding='utf-8', mode='w') as pt:
    pt.write(top_template)

# write header to RSS page
with open(feed_dir / 'rss.xml', encoding='utf-8', mode='w') as ft:
    rss_build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S ') + timezone
    ft.write(Template(rss_top_template).substitute(date=rss_build_date))

processed = 0

# write posts
for p in posts:
    # create year archive directory if needed
    p_year_string = p.date.strftime('%Y')

    # print('Generating ' + p.name + ' ' + p.date.strftime('%Y-%m-%d'))

    if p_year_string != year_string:
        year_dir = output_dir / p_year_string
        year_dir.mkdir(exist_ok=True)
        with open(year_dir / 'index.html', encoding='utf-8', mode='w') as nyp:
            nyp.write(top_template)
        # add footer to previous year
        if year_string:
            with open(output_dir / year_string / 'index.html', encoding='utf-8', mode='a') as nyp:
                nyp.write(bottom_template)

    # create year/month archive directory if needed
    p_month_string = p.date.strftime('%m')
    if p_year_string + p_month_string != year_string + month_string:
        month_dir = output_dir / p_year_string / p_month_string
        month_dir.mkdir(exist_ok=True)
        with open(month_dir / 'index.html', encoding='utf-8', mode='w') as nmp:
            nmp.write(top_template)

        # add footer to previous year/month
        if year_string and month_string:
            with open(output_dir / year_string / month_string / 'index.html', encoding='utf-8', mode='a') as nyp:
                nyp.write(bottom_template)

    # create year/month/day archive directory if needed
    p_day_string = p.date.strftime('%d')
    p_key = p_year_string + p_month_string + p_day_string
    key = year_string + month_string + day_string
    if p_key != key:
        day_dir = output_dir / p_year_string / p_month_string / p_day_string
        day_dir.mkdir(exist_ok=True)
        with open(day_dir / 'index.html', encoding='utf-8', mode='w') as ndp:
            ndp.write(top_template)

        # add footer to previous year/month/day
        if year_string and month_string and day_string:
            with open(output_dir / year_string / month_string / day_string / 'index.html', encoding='utf-8', mode='a') as nyp:
                nyp.write(bottom_template)

    permalink_rel = "/" + p_year_string + "/" + p_month_string + "/" \
                    + p_day_string + "/" + p.name + "/"
    p_date_string = p.date.strftime('%b %d, %Y')

    # write to year archive
    with open(output_dir_path / p_year_string / 'index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write to year/month archive
    with open(output_dir_path / p_year_string / p_month_string / 'index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write to year/month/day archive
    with open(day_dir / 'index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write the post page
    post_dir = day_dir / p.name
    post_dir.mkdir(exist_ok=True)
    with open(post_dir / 'index.html',
              encoding='utf-8', mode='w') as pt:
        pt.write(top_template)
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write(bottom_template)

    # main page to show only 10 recent entries
    if processed < main_page_posts:
        # generate main page with recent posts
        with open(output_dir_path / 'index.html',
                  encoding='utf-8', mode='a') as pt:
            pt.write(Template(post_template).substitute(
                                                permalink=permalink_rel,
                                                title=p.title,
                                                text=p.text,
                                                date=p_date_string))
            pt.write("<hr />")

    p_date_string_rss = p.date.strftime('%a, %d %b %Y %H:%M:%S ') + timezone
    # RSS page to show 20 recent entries
    if processed < rss_posts:
        with open(feed_dir / 'rss.xml', encoding='utf-8', mode='a') as ft:
            ft.write(Template(rss_post_template).substitute(
                permalink=base_url + permalink_rel,
                title=p.title,
                text=p.text,
                date=p_date_string_rss))

    p_date_string_short = p.date.strftime('%Y.%m')
    # add to TOC page
    with open(archives_dir / 'index.html', encoding='utf-8', mode='a') as pt:
        pt.write(Template(title_only_template).substitute(
                 permalink=permalink_rel,
                 title=p.title,
                 date=p_date_string_short))

    # set variables for comparison with next post
    year_string = p_year_string
    month_string = p_month_string
    day_string = p_day_string
    processed += 1

# add footer to main page
with open(output_dir_path / 'index.html', encoding='utf-8', mode='a') as pt:
    pt.write(bottom_template)

# add footer to TOC page
with open(archives_dir / 'index.html', encoding='utf-8', mode='a') as pt:
    pt.write(bottom_template)

# add footer to RSS
with open(feed_dir / 'rss.xml', encoding='utf-8', mode='a') as pt:
    pt.write(rss_bottom_template)

# Contact page
contact_dir = output_dir_path / 'contact'
contact_dir.mkdir(exist_ok=True)
with open(contact_dir / 'index.html', encoding='utf-8', mode='w') as cp:
    cp.write(top_template)
    cp.write(contact_page)
    cp.write(bottom_template)

# Others page
others_dir = output_dir_path / 'others'
others_dir.mkdir(exist_ok=True)
with open(others_dir / 'index.html', encoding='utf-8', mode='w') as op:
    op.write(top_template)
    op.write(others_page)
    op.write(bottom_template)

shutil.copyfile(styles_css, output_dir_path / 'styles.css')

# Favicons
favicons_dir = output_dir_path / 'favicons'
favicons_dir.mkdir(exist_ok=True)
shutil.copyfile(icons_dir / 'icon-32.png', favicons_dir / 'icon-32.png')
shutil.copyfile(icons_dir / 'icon-128.png', favicons_dir / 'icon-128.png')
shutil.copyfile(icons_dir / 'icon-152.png', favicons_dir / 'icon-152.png')
shutil.copyfile(icons_dir / 'icon-180.png', favicons_dir / 'icon-180.png')
shutil.copyfile(icons_dir / 'icon-192.png', favicons_dir / 'icon-192.png')
shutil.copyfile(icons_dir / 'icon-196.png', favicons_dir / 'icon-196.png')

# Images
img_dir = output_dir_path / 'images'
img_dir.mkdir(exist_ok=True)
for file in (images_dir).glob('*'):
    shutil.copy(file, img_dir)

logging.info('Blog generation complete')
