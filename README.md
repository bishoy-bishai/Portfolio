# Bishoy Bishai — Portfolio

A modern, professional portfolio website showcasing 10+ years of frontend development experience.

🔗 **Live Site**: [Coming Soon]

## ✨ Features

- **Modern Design** — Clean, Wix-inspired aesthetic with elegant typography
- **Dark/Light Sections** — Dramatic contrast with gold accent highlights
- **Responsive** — Looks great on desktop, tablet, and mobile
- **Blog** — Integrated blog for sharing thoughts and insights
- **Fast Performance** — Built with Astro for optimal loading speed
- **SEO Optimized** — Canonical URLs, OpenGraph data, and sitemap

## 🛠️ Tech Stack

- **Framework**: [Astro](https://astro.build)
- **Styling**: Scoped CSS with CSS Variables
- **Typography**: Cormorant Garamond + Montserrat (Google Fonts)
- **Content**: Markdown & MDX for blog posts
- **Deployment**: Ready for Vercel, Netlify, or any static host

## 📁 Project Structure

```text
├── public/
│   ├── favicon.svg
│   └── fonts/
├── src/
│   ├── components/     # Reusable UI components
│   ├── content/blog/   # Blog posts (Markdown/MDX)
│   ├── layouts/        # Page layouts
│   ├── pages/          # Routes (index, blog, etc.)
│   └── styles/         # Global styles
├── astro.config.mjs
├── package.json
└── tsconfig.json
```

## 🚀 Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📝 Adding Blog Posts

Create a new `.md` or `.mdx` file in `src/content/blog/`:

```markdown
---
title: "Your Post Title"
description: "A brief description"
pubDate: "Dec 12 2025"
heroImage: "/path/to/image.jpg"
---

Your content here...
```

## 🧞 Commands

| Command           | Action                                       |
| :---------------- | :------------------------------------------- |
| `npm install`     | Install dependencies                         |
| `npm run dev`     | Start dev server at `localhost:4321`         |
| `npm run build`   | Build production site to `./dist/`           |
| `npm run preview` | Preview build locally before deploying       |

## 📄 License

© 2025 Bishoy Bishai. All rights reserved.
