# TikTok Scraper — Setup Guide

## 3 Bugs Fixed in This Version

### Bug 1 — Video Codec Error ("codec not supported by browser")
**Cause:** Direct download from TikTok sometimes returns HEVC/H.265 video.
**Fix:** After every download, `ffprobe` checks the codec. If not H.264, `ffmpeg` transcodes it automatically. yt-dlp format string also updated to strictly prefer H.264.

### Bug 2 — Batch Folder Missing (Critical)
**Cause:** GitHub Actions sets `BATCH_FOLDER_NAME=''` (empty string) when no input given. Python's `os.environ.get("KEY", default)` returns `''` not the default — so folder name was empty.
**Fix:** `_env = os.environ.get("BATCH_FOLDER_NAME", "").strip(); BATCH_FOLDER_NAME = _env if _env else f"Batch--{timestamp}"`

### Bug 3 — 10,000 links need parallel workers
**Fix:** GitHub Actions matrix runs 20 parallel jobs. Each job handles 1/20th of links.txt (500 links per worker). With 10 concurrent videos per worker = 200 parallel videos total.

---

## Repository Structure

```
repo/
├── scraper-fixed.py           ← main script (v5)
├── requirements.txt
├── links.txt                  ← your TikTok URLs (one per line)
├── Dockerfile                 ← for K8s option
├── k8s/
│   └── job.yaml               ← K8s Job (20 parallel pods)
└── .github/
    └── workflows/
        └── scrape.yml         ← GitHub Actions (20 parallel jobs)
```

---

## Option A: GitHub Actions (Recommended — Free, No Infrastructure)

### Setup (5 minutes)

**1. Create private GitHub repo, upload all files**

**2. Add Secret:**
```
Repo → Settings → Secrets and Variables → Actions → New secret
Name:  RCLONE_CONFIG_CONTENT
Value: paste your ~/.config/rclone/rclone.conf content
```

**3. Add your URLs to links.txt and commit**

**4. Run:**
```
Actions → TikTok Scraper → Run workflow
```

### How it works
- 20 parallel jobs launch simultaneously
- Job 0 processes links: 0, 20, 40, 60...
- Job 1 processes links: 1, 21, 41, 61...
- All jobs upload to same Batch folder on Mega
- If one job fails, others continue (fail-fast: false)

### Capacity
| Links | Workers | Links/Worker | Estimated Time |
|-------|---------|--------------|----------------|
| 1,000 | 20      | 50           | ~15 min        |
| 5,000 | 20      | 250          | ~1.5 hrs       |
| 10,000| 20      | 500          | ~3 hrs         |

---

## Option B: Kubernetes (For self-hosted / cloud cluster)

### Setup

```bash
# 1. Build and push Docker image
docker build -t YOUR_USERNAME/tiktok-scraper:latest .
docker push YOUR_USERNAME/tiktok-scraper:latest

# 2. Create rclone secret
kubectl create secret generic scraper-secrets \
  --from-literal=RCLONE_CONFIG="$(cat ~/.config/rclone/rclone.conf)"

# 3. Create links configmap
kubectl create configmap links-config --from-file=links.txt=./links.txt

# 4. Update BATCH_FOLDER_NAME in k8s/job.yaml

# 5. Run
kubectl apply -f k8s/job.yaml

# Monitor
kubectl get pods -l app=tiktok-scraper -w
kubectl logs -l app=tiktok-scraper --tail=50
```

---

## Mega Output Structure

```
vfx:/
└── Batch--2026-04-22-Wednesday_02-00-00-AM/
    ├── @username_caption_videoId/
    │   ├── RAW_meta__@username_caption_id.json
    │   ├── meta__@username_caption_id.json
    │   ├── caption__@username_caption_id.json
    │   ├── account__@username_caption_id.json
    │   ├── avatar__@username_caption_id.jpg
    │   ├── video__@username_caption_id.mp4  ← always H.264 now
    │   ├── audio__@username_caption_id.mp3
    │   ├── RAW_comments__@username_caption_id.json
    │   └── comments__@username_caption_id.json
    └── _Reports/
        ├── tracking_report_chunk0.txt
        ├── completed_chunk0.txt
        ├── failed_chunk0.txt
        └── scraper_log_chunk0.txt
```
