---
category: Meta
---

# R2 Asset Storage

Large files (PDFs, images, videos) are stored in [Cloudflare R2](https://developers.cloudflare.com/r2/) rather than git.

## Why R2?

| Concern | Git | R2 |
|---------|-----|-----|
| Large binaries | Bloats repo | Designed for it |
| File limit | N/A | Pages has 20k limit |
| Egress fees | N/A | Free (unlike S3) |
| CDN | Separate | Same Cloudflare edge |

## Setup

### 1. Create R2 Bucket

Cloudflare Dashboard → R2 → **Create bucket**

Suggested name: `percybrain-assets`

### 2. Enable Public Access

Bucket → Settings → **Public Access** → Connect Domain

Example: `assets.percybrain.com`

### 3. Organize Assets

```
percybrain-assets/
├── images/
│   ├── diagrams/
│   ├── photos/
│   └── screenshots/
├── pdfs/
│   ├── papers/
│   └── references/
└── videos/
```

## Usage in MyST

### Using Substitutions (Recommended)

The `conf.py` defines an `{{assets}}` substitution for the R2 base URL:

```markdown
![Architecture diagram]({{assets}}/images/diagrams/architecture.png)

[Download PDF]({{assets}}/pdfs/papers/manifesto.pdf)
```

This renders to the full R2 URL automatically.

### Direct URLs

You can also use full URLs directly:

```markdown
![Photo](https://assets.percybrain.com/images/photo.jpg)
```

### Figures with Captions

```text
:::{figure} {{assets}}/images/diagrams/knowledge-graph.png
:alt: Knowledge graph visualization
:width: 80%

The PercyBrain knowledge graph showing concept relationships.
:::
```

## Uploading Assets

### Via Dashboard

Cloudflare Dashboard → R2 → Bucket → **Upload**

### Via Wrangler CLI

```bash
wrangler r2 object put percybrain-assets/images/photo.jpg --file=./photo.jpg
```

### Via rclone (Recommended for Bulk)

Configure rclone with R2:

```bash
rclone config
# Choose: s3
# Provider: Cloudflare
# Access Key ID: (from R2 API tokens)
# Secret Access Key: (from R2 API tokens)
# Endpoint: https://<account_id>.r2.cloudflarestorage.com
```

Sync a directory:

```bash
rclone sync ./local-assets/ r2:percybrain-assets/
```

## Free Tier Limits

| Resource | Free Allowance |
|----------|----------------|
| Storage | 10 GB |
| Class A ops (writes) | 1 million/month |
| Class B ops (reads) | 10 million/month |
| Egress | Unlimited |

## Best Practices

1. **Optimize images** before upload (WebP, compressed PNG)
2. **Use descriptive paths** (`/images/2024/dialectics-diagram.png`)
3. **Keep originals** locally as backup. *DO NOT* sync them to Git! This will result in a very large, unwieldy git file that takes forever to commit if you have a lot of files or large files. Or even worst, both. This is because of how git breaks files up. There are ways to work around this if you want to, however IMO that's overkill. Just add your files directory to .gitignore and push them to rsync. Some blob storages will even let you version the files but I haven't ried this for Cloudflare R2 so I wouldn't know.

## Integration with Obsidian

When editing in Neovim with obsidian.nvim, you can:

1. Store images locally in `private/images/` (not published)
2. Upload final versions to R2
3. Update links to use `{{assets}}` substitution

This keeps your working files local while published assets live on R2.
