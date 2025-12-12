import os
import json
import requests
import google.generativeai as genai
import xml.etree.ElementTree as ET
from datetime import datetime
import subprocess
import re

# --- Config ---
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]
DEVTO_KEY = os.environ.get("DEVTO_API_KEY")
MODE = os.environ.get("MODE", "trends")

# Site Configuration
SITE_URL = "https://bishoy-bishai.github.io"
SITE_BASE = "/portfolio"
AUTHOR_NAME = "Bishoy Bishai"
AUTHOR_TITLE = "Senior Frontend Engineer"

# Paths
TRENDS_FILE = "trends.json"
DRAFT_FILE = "draft.json"
REVIEW_DOC = "review_copy.md"
CONTENT_DIR = "src/content/blog"
ASSETS_DIR = "src/assets"

# --- Helpers ---
def run_git_commands(commit_msg):
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"])
        subprocess.run(["git", "config", "--global", "user.email", "actions@github.com"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", commit_msg])
        subprocess.run(["git", "push"])
    except Exception as e:
        print(f"Git Error: {e}")

def send_telegram(text, img_path=None, doc_path=None):
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    try:
        if doc_path:
            with open(doc_path, 'rb') as doc:
                requests.post(f"{base_url}/sendDocument",
                              data={"chat_id": CHAT_ID, "caption": text[:1000], "parse_mode": "Markdown"},
                              files={"document": doc})
        elif img_path:
            with open(img_path, 'rb') as photo:
                requests.post(f"{base_url}/sendPhoto", 
                              data={"chat_id": CHAT_ID, "caption": text[:1000], "parse_mode": "Markdown"}, 
                              files={"photo": photo})
        else:
            if len(text) > 4000:
                for x in range(0, len(text), 4000):
                    requests.post(f"{base_url}/sendMessage", 
                                  data={"chat_id": CHAT_ID, "text": text[x:x+4000], "parse_mode": "Markdown"})
            else:
                requests.post(f"{base_url}/sendMessage", 
                              data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_slug(title):
    return "".join([c if c.isalnum() else "-" for c in title])[:50].lower()

# --- LOGIC 1: DRAFTING ---
def run_draft_mode(is_retry=False):
    updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates").json()
    if not updates.get("result"): return
    last_text = updates["result"][-1]["message"].get("text", "").strip()

    if not is_retry and not last_text.isdigit(): return
    idx = int(last_text) - 1 if last_text.isdigit() else 0
    
    if not os.path.exists(TRENDS_FILE): return
    with open(TRENDS_FILE, 'r') as f: trends = json.load(f)
    
    if is_retry and os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, 'r') as f: old = json.load(f)
        topic = {"title": old['title'], "link": old.get('link', '')}
    elif 0 <= idx < len(trends):
        topic = trends[idx]
    else: return

    prefix = "🔄 Re-drafting" if is_retry else "✍️ Drafting"
    send_telegram(f"{prefix} package for: **{topic['title']}**...")

    try:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Topic: "{topic['title']}"
        Audience: Professional developers and engineering teams.
        
        WRITING STYLE (CRITICAL):
        Write in a clear, professional, and genuinely HUMAN tone.
        The style should feel natural — like an experienced developer explaining 
        the topic with confidence and warmth to a colleague over coffee.
        
        - Use smooth transitions and conversational flow
        - Include relatable examples and small storytelling touches
        - Show real understanding, not robotic repetition
        - Make it exciting, practical, and rich with real-world insights
        - Avoid stiff, mechanical, or AI-sounding wording
        - Write as a thoughtful expert who knows how to teach and simplify
        - Keep the reader engaged from start to finish
        - Use "I've found...", "In my experience...", "Here's the thing..."
        - Share lessons learned from real projects
        
        Generate 4 parts. Use STRICT separators.
        
        1. VIDEO SCRIPT (200 words):
           - Warm, confident narrator voice — like explaining to a friend
           - Start with a hook that makes them curious
           - Share a quick story or "aha moment" from real experience
           - End with actionable takeaway
        
        2. VISUAL PROMPT:
           - Dark background (#1A1A1A) with gold accents (#C9A227)
           - Minimalist, abstract tech illustration
           - Clean geometric shapes, no text
           - Professional, elegant aesthetic
        
        3. BLOG POST (Markdown, 800-1200 words):
           - Hook: Start with a relatable problem or story
           - Context: Why this matters in real projects
           - Deep Dive: Explain with practical code (React/TypeScript)
           - Insights: Share what most tutorials miss
           - Pitfalls: Common mistakes and how to avoid them
           - Wrap-up: Key takeaways, not a boring summary
           - NO quizzes, NO "In conclusion...", NO robotic endings
           - IMPORTANT: Write raw markdown, do NOT wrap in ```markdown``` code fences
           - Only use code fences for actual code examples (```typescript, ```bash, etc.)
        
        4. TWEETS (5-7 tweets):
           - Expert thread style (like Dan Abramov or Kent C. Dodds)
           - Punchy, insightful, opinionated
           - Each tweet should stand alone but flow together
           - End with a thought-provoking question or bold statement
        
        OUTPUT FORMAT:
        ===SCRIPT===
        (Text)
        ===PROMPT===
        (Text)
        ===BLOG===
        (Text)
        ===TWEETS===
        (Text)
        """
        
        response = model.generate_content(prompt)
        raw = response.text
        
        def extract(t, s, e):
            p = f"{s}(.*?){e}" if e else f"{s}(.*)"
            m = re.search(p, t, re.DOTALL)
            return m.group(1).strip() if m else "Missing"

        script = extract(raw, "===SCRIPT===", "===PROMPT===")
        prompt_txt = extract(raw, "===PROMPT===", "===BLOG===")
        blog = extract(raw, "===BLOG===", "===TWEETS===")
        tweets = extract(raw, "===TWEETS===", None)
        
        # Save Draft
        draft_data = {
            "title": topic['title'], "link": topic['link'],
            "script": script, "img_prompt": prompt_txt,
            "blog": blog, "tweets": tweets
        }
        
        with open(DRAFT_FILE, 'w', encoding='utf-8') as f: json.dump(draft_data, f, indent=2)
        
        # Create Review Doc
        review_content = f"# REVIEW: {topic['title']}\n\n## 🎥 Video Script\n{script}\n\n## 🐦 Expert Thread\n{tweets}\n\n## 📝 Blog Post\n{blog}"
        with open(REVIEW_DOC, 'w', encoding='utf-8') as f: f.write(review_content)
        
        # Generate Temp Image for Review (matching portfolio dark/gold theme)
        clean_prompt = re.sub(r'[^\w\s]', '', prompt_txt)[:120]
        style = "dark%20background%20black%20gold%20accent%20minimalist%20abstract%20geometric%20tech%20illustration"
        temp_img_url = f"https://image.pollinations.ai/prompt/{style}%20{clean_prompt.replace(' ', '%20')}?width=1200&height=630"
        
        # Send to Telegram
        send_telegram(f"🖼️ **Proposed Cover:** {temp_img_url}")
        send_telegram(f"✅ **Draft Ready!**\nAttached FULL content.\n\n👇 **Reply:**\n1️⃣ Publish\n2️⃣ Regenerate\n3️⃣ Cancel", doc_path=REVIEW_DOC)
        
        run_git_commands(f"Draft generated: {topic['title']}")

    except Exception as e:
        send_telegram(f"❌ Drafting Error: {e}")

# --- LOGIC 2: PUBLISHING ---
def run_publish_mode():
    if not os.path.exists(DRAFT_FILE): return
    updates = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates").json()
    if not updates.get("result"): return
    last_text = updates["result"][-1]["message"].get("text", "").strip()

    with open(DRAFT_FILE, 'r') as f: draft = json.load(f)

    if last_text == "1":
        send_telegram("🚀 Approved! Publishing...")
        
        # 1. Setup Directories
        if not os.path.exists(CONTENT_DIR): os.makedirs(CONTENT_DIR)
        if not os.path.exists(ASSETS_DIR): os.makedirs(ASSETS_DIR)
        
        slug = get_slug(draft['title'])
        image_filename = f"{slug}.jpg"
        local_image_path = os.path.join(ASSETS_DIR, image_filename)
        
        # 2. Download & Save Image Locally (matching portfolio dark/gold theme)
        try:
            clean_prompt = re.sub(r'[^\w\s]', '', draft['img_prompt'])[:120]
            # Style: Dark background with gold accents, minimalist tech aesthetic
            style = "dark%20background%20black%20gold%20accent%20minimalist%20abstract%20geometric%20tech%20illustration%20professional%20elegant"
            img_url = f"https://image.pollinations.ai/prompt/{style}%20{clean_prompt.replace(' ', '%20')}?width=1200&height=630"
            img_data = requests.get(img_url).content
            with open(local_image_path, 'wb') as f: f.write(img_data)
        except Exception as e:
            send_telegram(f"⚠️ Image download failed: {e}")

        # 3. Create Blog Post File
        md_filename = f"{slug}.md"
        md_path = os.path.join(CONTENT_DIR, md_filename)
        
        # Date Format: "Dec 12 2025"
        formatted_date = datetime.now().strftime("%b %d %Y")
        
        # Extract first sentence for description
        blog_text = draft['blog'].strip()
        first_para = blog_text.split('\n\n')[0] if '\n\n' in blog_text else blog_text[:200]
        description = re.sub(r'[#*`\[\]]', '', first_para)[:150].strip()
        if not description.endswith('.'):
            description = description.rsplit(' ', 1)[0] + '...'
        
        # Blog Content with Astro Frontmatter (relative path for image())
        file_content = f"""---
title: "{draft['title']}"
description: "{description}"
pubDate: "{formatted_date}"
heroImage: "../../assets/{image_filename}"
---

{draft['blog']}
"""
        with open(md_path, 'w', encoding='utf-8') as f: f.write(file_content)
        
        # 4. External Publish (Dev.to)
        my_url = f"{SITE_URL}{SITE_BASE}/blog/{slug}"
        if DEVTO_KEY:
            url = "https://dev.to/api/articles"
            # Uploading local images to dev.to via API is complex, usually we use a public URL.
            # For simplicity, we use the pollination URL for Dev.to, but local path for Astro.
            footer = f"\n\n---\n *> 🚀 Read on [My Blog]({my_url})*"
            data = { "article": { "title": draft['title'], "published": True, "body_markdown": draft['blog'] + footer, "main_image": img_url, "canonical_url": my_url, "tags": ["react","webdev"] } }
            requests.post(url, json=data, headers={"api-key": DEVTO_KEY, "Content-Type": "application/json"})

        # 5. Notify & Cleanup
        send_telegram(f"📜 **Video Script:**\n\n{draft['script']}")
        send_telegram(f"✅ **Published!**\n🌍 {my_url}")
        
        os.remove(DRAFT_FILE)
        if os.path.exists(REVIEW_DOC): os.remove(REVIEW_DOC)
        run_git_commands(f"Published: {draft['title']}")

    elif last_text == "2":
        send_telegram("🔄 Regenerating...")
        run_draft_mode(is_retry=True)

    elif last_text == "3":
        os.remove(DRAFT_FILE)
        send_telegram("❌ Cancelled.")
        run_git_commands("Draft cancelled")

# --- Entry Points ---
def get_trends():
    try:
        resp = requests.get("https://dev.to/feed/tag/react")
        root = ET.fromstring(resp.content)
        trends, msg = [], "☀️ **Daily Trends:**\n\n"
        for i, item in enumerate(root.findall('.//item')[:4]):
            trends.append({"title": item.find('title').text, "link": item.find('link').text})
            msg += f"{i+1}️⃣ {item.find('title').text}\n"
        with open(TRENDS_FILE, 'w') as f: json.dump(trends, f)
        send_telegram(msg + "\n👇 **Reply number to Draft.**")
        run_git_commands("Trends")
    except Exception as e: print(e)

if __name__ == "__main__":
    if MODE == "trends": get_trends()
    elif MODE == "draft": run_draft_mode()
    elif MODE == "publish": run_publish_mode()