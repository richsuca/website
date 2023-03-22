#!/usr/bin/env python3

from pathlib import Path
import re
import os
import shutil
from datetime import datetime
from string import Template
from titlecase import titlecase
import markdown
import glob

class Post:
    def __init__(self, title, name, date, text):
        self.title = titlecase(title)
        self.name = name
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.text = text

    def __lt__(self, other):
        return self.date < other.date

    def __le__(self, other):
        return self.date <= other.date

    def __eq__(self, other):
        return self.date == other.date

    def __ne__(self, other):
        return self.date != other.date

    def __gt__(self, other):
        return self.date > other.date

    def __ge__(self, other):
        return self.date >= other.date

posts = []

title_re = re.compile('(?<=title:[\s*]).*')
name_re = re.compile('(?<=name:[\s*]).*')
date_re = re.compile('(?<=date:[\s*]).*')

root_dir = '.'
base_url = 'https://richardhsu.net'

md = markdown.Markdown(extensions=['footnotes'])

# get posts
post_dir = Path(root_dir + '/posts')
for post_file in post_dir.iterdir():
    # print('reading ' + post_file.name)
    with open(str(post_dir) + '/' + post_file.name, encoding='utf-8') as p:
        file_text = ''.join(p.readlines())
        m = title_re.search(file_text)
        if m:
            title = m.group(0)
        m = name_re.search(file_text)
        if m:
            name = m.group(0)
        m = date_re.search(file_text)
        if m:
            date = m.group(0)

        text_idx = file_text.find("text:")
        text = file_text[text_idx + len("text:") + 1:]
        
        if post_file.name[-3:] == '.md':
            text = md.convert(text)
            md.reset()

        posts.append(Post(title, name, date, text))

# archive previous output
archive_dir_name = 'output-' + datetime.now().strftime('%Y%m%d%H%M%S%f')
try:
    os.rename(root_dir + '/output', root_dir + '/' + archive_dir_name)
except FileExistsError:
    print('cannot move ' + root_dir + '/output' + ' --> ' + root_dir + '/'
          + archive_dir_name)
    sys.exit()
except:
    print("Unexpected error:", sys.exc_info()[0])
    sys.exit()

try:
    os.mkdir(root_dir + '/output')
except OSError:
    print('cannot create output directory')
    sys.exit()
except:
    print("Unexpected error:", sys.exc_info()[0])
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
with open(root_dir + '/templates/main-top.txt', encoding='utf-8') as mtt:
    top_template = ''.join(mtt.readlines())

with open(root_dir + '/templates/main-bottom.txt', encoding='utf-8') as mtb:
    bottom_template = ''.join(mtb.readlines())

with open(root_dir + '/templates/posts.txt', encoding='utf-8') as pt:
    post_template = ''.join(pt.readlines())

with open(root_dir + '/templates/title-only.txt', encoding='utf-8') as tt:
    title_only_template = ''.join(tt.readlines())

with open(root_dir + '/templates/rss-top.txt', encoding='utf-8') as ft:
    rss_top_template = ''.join(ft.readlines())

with open(root_dir + '/templates/rss-bottom.txt', encoding='utf-8') as ft:
    rss_bottom_template = ''.join(ft.readlines())

with open(root_dir + '/templates/rss-post.txt', encoding='utf-8') as ft:
    rss_post_template = ''.join(ft.readlines())

with open(root_dir + '/templates/contact-page.txt', encoding='utf-8') as cp:
    contact_page = ''.join(cp.readlines())

with open(root_dir + '/templates/others-page.txt', encoding='utf-8') as op:
    others_page = ''.join(op.readlines())

year_string = ""
month_string = ""
day_string = ""

# by date descending, this helps with getting a recent post list
posts.sort(reverse=True)

os.mkdir(root_dir + '/output/archives')
os.mkdir(root_dir + '/output/feed')

# write header to TOC page
with open(root_dir + '/output/archives/index.html', encoding='utf-8',
          mode='w') as pt:
    pt.write(top_template)

# write header to main page
with open(root_dir + '/output/index.html', encoding='utf-8', mode='w') as pt:
    pt.write(top_template)

# write header to RSS page
with open(root_dir + '/output/feed/rss.xml', encoding='utf-8', mode='w') as ft:
    rss_build_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S -0400')
    ft.write(Template(rss_top_template).substitute(date=rss_build_date))

processed = 0

# write posts
for p in posts:
    # create year archive directory if needed
    p_year_string = p.date.strftime('%Y')

    # print('Generating ' + p.name + ' ' + p.date.strftime('%Y-%m-%d'))

    if p_year_string != year_string:
        os.mkdir(root_dir + '/output/' + p_year_string)
        with open(root_dir + '/output/' + p_year_string + '/index.html',
                  encoding='utf-8', mode='w') as nyp:
            nyp.write(top_template)
        # add footer to previous year
        if year_string != "":
            with open(root_dir + '/output/' + year_string + '/index.html',
                      encoding='utf-8', mode='a') as nyp:
                nyp.write(bottom_template)

    # create year/month archive directory if needed
    p_month_string = p.date.strftime('%m')
    if p_year_string + p_month_string != year_string + month_string:
        os.mkdir(root_dir + '/output/' + p_year_string + "/" + p_month_string)
        with open(root_dir + '/output/' + p_year_string + "/"
                  + p_month_string + '/index.html',
                  encoding='utf-8', mode='w') as nmp:
            nmp.write(top_template)

        # add footer to previous year/month
        if year_string != "" and month_string != "":
            with open(root_dir + '/output/' + year_string + '/'
                      + month_string + '/index.html', encoding='utf-8',
                      mode='a') as nyp:
                nyp.write(bottom_template)

    # create year/month/day archive directory if needed
    p_day_string = p.date.strftime('%d')
    p_key = p_year_string + p_month_string + p_day_string
    key = year_string + month_string + day_string
    if p_key != key:
        os.mkdir(root_dir + '/output/' + p_year_string
                 + "/" + p_month_string + "/" + p_day_string)
        with open(root_dir + '/output/' + p_year_string + "/"
                  + p_month_string + '/' + p_day_string + '/index.html',
                  encoding='utf-8', mode='w') as ndp:
            ndp.write(top_template)

        # add footer to previous year/month/day
        if year_string != "" and month_string != "" and day_string != "":
            with open(root_dir + '/output/' + year_string + '/'
                      + month_string + '/' + day_string + '/index.html',
                      encoding='utf-8', mode='a') as nyp:
                nyp.write(bottom_template)

    permalink_rel = "/" + p_year_string + "/" + p_month_string + "/" \
                    + p_day_string + "/" + p.name + "/"
    p_date_string = p.date.strftime('%b %d, %Y')

    # write to year archive
    with open(root_dir + '/output/' + p_year_string + '/index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write to year/month archive
    with open(root_dir + '/output/' + p_year_string + "/"
              + p_month_string + '/index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write to year/month/day archive
    with open(root_dir + '/output/' + p_year_string + "/" + p_month_string
              + '/' + p_day_string + '/index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write("<hr />")

    # write the post page
    os.mkdir(root_dir + '/output/' + p_year_string + "/" + p_month_string
             + "/" + p_day_string + "/" + p.name)
    with open(root_dir + '/output/' + p_year_string + "/" + p_month_string
              + '/' + p_day_string + '/' + p.name + '/index.html',
              encoding='utf-8', mode='a') as pt:
        pt.write(top_template)
        pt.write(Template(post_template).substitute(permalink=permalink_rel,
                                                    title=p.title,
                                                    text=p.text,
                                                    date=p_date_string))
        pt.write(bottom_template)

    # main page to show only 10 recent entries
    if processed < 10:
        # generate main page with recent posts
        with open(root_dir + '/output/index.html',
                  encoding='utf-8', mode='a') as pt:
            pt.write(Template(post_template).substitute(
                                                permalink=permalink_rel,
                                                title=p.title,
                                                text=p.text,
                                                date=p_date_string))
            pt.write("<hr />")

    p_date_string_rss = p.date.strftime('%a, %d %b %Y %H:%M:%S -0400')
    # RSS page to show 20 recent entries
    if processed < 20:
        with open(root_dir + '/output/feed/rss.xml',
                  encoding='utf-8', mode='a') as ft:
            ft.write(Template(rss_post_template).substitute(
                permalink=base_url + permalink_rel,
                title=p.title,
                text=p.text,
                date=p_date_string_rss))

    p_date_string_short = p.date.strftime('%Y.%m')
    # add to TOC page
    with open(root_dir + '/output/archives/index.html',
              encoding='utf-8', mode='a') as pt:
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
with open(root_dir + '/output/index.html', encoding='utf-8', mode='a') as pt:
    pt.write(bottom_template)

# add footer to TOC page
with open(root_dir + '/output/archives/index.html',
          encoding='utf-8', mode='a') as pt:
    pt.write(bottom_template)

# add footer to RSS
with open(root_dir + '/output/feed/rss.xml', encoding='utf-8',
          mode='a') as pt:
    pt.write(rss_bottom_template)

# Contact page
os.mkdir(root_dir + '/output/contact')
with open(root_dir + '/output/contact/index.html',
          encoding='utf-8', mode='w') as cp:
    cp.write(top_template)
    cp.write(contact_page)
    cp.write(bottom_template)

# Others page
os.mkdir(root_dir + '/output/others')
with open(root_dir + '/output/others/index.html',
          encoding='utf-8', mode='w') as op:
    op.write(top_template)
    op.write(others_page)
    op.write(bottom_template)

shutil.copyfile('styles.css', 'output/styles.css')

# Favicons
os.mkdir(root_dir + '/output/favicons')
shutil.copyfile('icons/icon-32.png', 'output/favicons/icon-32.png')
shutil.copyfile('icons/icon-128.png', 'output/favicons/icon-128.png')
shutil.copyfile('icons/icon-152.png', 'output/favicons/icon-152.png')
shutil.copyfile('icons/icon-180.png', 'output/favicons/icon-180.png')
shutil.copyfile('icons/icon-192.png', 'output/favicons/icon-192.png')
shutil.copyfile('icons/icon-196.png', 'output/favicons/icon-196.png')

# Images
img_dir = root_dir + '/output/images' 
os.mkdir(img_dir)
for file in glob.glob('images/*'):
    shutil.copy(file, img_dir)
