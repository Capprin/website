# journal.py
# interprets markdown entries as HTML
# expects filenames to be in YYYY-MM-DD_title.md

import argparse
from bs4 import BeautifulSoup
from datetime import datetime
from markdown import markdown as md_to_html
import os

PROJECT_ROOT = '.'
TEMPLATE_NAME = '.template.html'

# turns all .md files from source into .html files in dest
# creates directory html file at supplied location
def interpret(source, dest, directory_file='journal.html'):
  # setup
  links = []
  proj_root_abs = os.path.abspath(PROJECT_ROOT)
  template_path = os.path.join(proj_root_abs, TEMPLATE_NAME)
  source_abs = os.path.abspath(source)
  dest_abs = os.path.abspath(dest)
  # recursively read files in source
  for root, _, files in os.walk(source_abs):
    for filename in files:
      # convert md files only
      name, ext = os.path.splitext(filename)
      if ext != '.md':
        continue
      # get fullpath to open
      md_abs = os.path.join(root, filename)
      # convert contents to html
      with open(md_abs, 'r', encoding='utf-8') as md_file:
        content = md_file.read()
      md_html = md_to_html(content)
      md_soup = BeautifulSoup(md_html, 'html.parser')
      # open template
      with open(template_path, 'r') as template_file:
        template_soup = BeautifulSoup(template_file.read(), 'html.parser')
      # add md content to template
      template_soup.find_all('div', class_='content')[0].append(md_soup)
      # fix links, badly
      template_soup.find_all('a', href=True, text='Me')[0]['href'] = '../index.html'
      template_soup.find_all('a', href=True, text='Work')[0]['href'] = '../work.html'
      template_soup.find_all('a', href=True, text='Play')[0]['href'] = '../play.html'
      template_soup.find_all('a', href=True, text='Journal')[0]['href'] = '../journal.html'
      template_soup.find_all('link', href='style.css')[0]['href'] = '../style.css'
      # add relative link to "links" list
      dest_name = os.path.join(dest_abs, name+'.html')
      dest_rel = os.path.relpath(dest_name, proj_root_abs)
      links.append(dest_rel)
      # don't write if exists
      if os.path.exists(dest_name):
        with open(dest_name, 'r') as old:
          old_contents = old.read()
        if old_contents == template_soup.prettify():
          continue
      # write html to dest
      os.makedirs(os.path.dirname(dest_name), exist_ok=True)
      with open(dest_name, 'w', encoding="utf-8", errors="xmlcharrefreplace") as dest_html:
        dest_html.write(template_soup.prettify())
  # use links to write directory (if exist)
  if not links:
    return
  # start with template
  with open(template_path, 'r') as template_file:
    template_soup = BeautifulSoup(template_file.read(), 'html.parser')
  heading_tag = template_soup.new_tag("h2")
  heading_tag.string = 'Journal Entries'
  template_soup.find_all('div', class_='content')[0].append(heading_tag)
  # generate links
  links.reverse()
  for link_text in links:
    # do some formatting
    base_name = os.path.splitext(os.path.basename(link_text))[0]
    parts = base_name.split('_')
    parts[0] = datetime.strptime(parts[0], '%Y-%m-%d').strftime('%m/%d/%Y')
    # generate link tags
    a_tag = template_soup.new_tag("h3")
    a_tag.append(template_soup.new_tag("a", href=link_text))
    a_tag.a.string = f'{parts[0]}: {parts[1]}'
    template_soup.find_all('div', class_='content')[0].append(a_tag)
  with open(os.path.join(proj_root_abs, directory_file), 'w',
            encoding="utf-8", errors="xmlcharrefreplace") as dir_html:
    dir_html.write(template_soup.prettify())

# CLI
if __name__ == '__main__':
  proj_root_abs = os.path.abspath(PROJECT_ROOT)
  parser = argparse.ArgumentParser(description='Converts supplied markdown files into HTML')
  parser.add_argument('-s', '--source', 
                      default=os.path.join(proj_root_abs,'journal_md'),
                      type=str,
                      help='Source directory for markdown files')
  parser.add_argument('-d', '--dest', 
                      default=os.path.join(proj_root_abs,'journal'),
                      type=str,
                      help='Destination directory for HTML files')
  parser.add_argument('-f', '--file',
                      default='journal.html',
                      type=str,
                      help='HTML filename for directory file')
  args = parser.parse_args()
  interpret(args.source, args.dest, args.file)