Web page and other files for my personal website at https://richardhsu.net
This repository is used as a backup, versioning, and sync to my NearlyFreeSpeech.NET hosted website.

## Blog Generation

The blog is generated using the `process-posts.py` script, which processes posts from the `posts/` directory and generates static HTML files.

### Dependencies

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Configuration

The script uses `config.yaml` for configuration. You can override the output directory with `--output-dir`.

### Running

```bash
chmod ugo+x ./process-posts.py && ./process-posts.py
```

Or with custom output:

```bash
./process-posts.py --output-dir /path/to/output
```

Preview the website locally:

```bash
cd /path/to/output
python3 -m http.server 8000 --bind 0.0.0.0
```


### Post Format

Posts are text files with metadata:

```
title: Post Title
name: post-slug
date: YYYY-MM-DD HH:MM:SS
text:
Content here...
```

Markdown files (.md) are supported and converted to HTML.

Nothing interesting to see here.
