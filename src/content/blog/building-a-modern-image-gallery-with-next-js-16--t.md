---
title: "Building a Modern Image Gallery with Next.js 16, TypeScript & Unsplash API"
description: "A practical guide to building a performant image gallery with Server Components, next/image optimization, and type-safe API integration."
pubDate: "Dec 12 2025"
heroImage: "../../assets/building-a-modern-image-gallery-with-next-js-16--t.jpg"
---

# Building a Modern Image Gallery That Actually Performs

Here's the thing about image galleries: they look simple until you actually build one for production. Then you're suddenly dealing with layout shifts, slow loads, SEO nightmares, and users complaining that your "simple gallery" takes 10 seconds to load on mobile.

I've rebuilt image galleries more times than I'd like to admit. Over the years, I've learned that the difference between a good gallery and a frustrating one usually comes down to a few key decisions made early on. Let me walk you through how I approach this today using Next.js 16, TypeScript, and the Unsplash API.

## Why Most Image Galleries Fall Short

Before we dive into code, let's talk about what usually goes wrong. In my experience, these are the usual suspects:

**Performance killers:** Giant image files, no lazy loading, everything renders on the client. Your Lighthouse score cries.

**SEO blindspots:** Client-side rendered galleries show blank content to search crawlers. All those beautiful images? Invisible to Google.

**The layout shift dance:** Images pop in at random sizes, pushing content around. Users try to click something and—oops—it moved.

**Developer frustration:** No types, API responses that could be anything, tightly coupled components. Good luck maintaining this in six months.

The good news? Next.js 16's App Router solves most of these problems elegantly. Let me show you how.

## The Architecture That Works

We're going to leverage three things that play beautifully together:

1. **Server Components** for data fetching (no client-side waterfall)
2. **next/image** for automatic optimization (WebP, responsive sizes, lazy loading)
3. **TypeScript** for sanity (because "data might be undefined" errors at runtime are no fun)

Let's build this step by step.

## Setting Up the Project

First, create a fresh Next.js project with TypeScript:

```bash
npx create-next-app@latest my-gallery --typescript --app
cd my-gallery
```

Grab an API key from [Unsplash Developers](https://unsplash.com/developers) and add it to `.env.local`:

```
UNSPLASH_ACCESS_KEY=your_key_here
```

Quick tip: Notice I'm *not* using `NEXT_PUBLIC_` prefix. This key stays server-side only, which is exactly what we want since we're fetching data in Server Components.

## Type Safety First

Before fetching anything, let's define what we're working with. This saves so much debugging time later:

```typescript
// types/unsplash.ts
export interface UnsplashImage {
  id: string;
  width: number;
  height: number;
  alt_description: string | null;
  urls: {
    regular: string;
    small: string;
    thumb: string;
  };
  user: {
    name: string;
    links: {
      html: string;
    };
  };
}
```

I'm only typing the fields I actually use. No need to map the entire API response—that's just noise.

## The Server Component Magic

Here's where Next.js 16 shines. We can fetch data directly in our page component, and it runs on the server:

```typescript
// app/page.tsx
import { UnsplashImage } from '@/types/unsplash';
import { ImageCard } from '@/components/ImageCard';

async function getImages(): Promise<UnsplashImage[]> {
  const res = await fetch(
    `https://api.unsplash.com/photos?per_page=20&client_id=${process.env.UNSPLASH_ACCESS_KEY}`,
    { next: { revalidate: 3600 } } // Cache for 1 hour
  );

  if (!res.ok) {
    throw new Error('Failed to fetch images');
  }

  return res.json();
}

export default async function GalleryPage() {
  const images = await getImages();

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Gallery</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {images.map((image) => (
          <ImageCard key={image.id} image={image} />
        ))}
      </div>
    </main>
  );
}
```

Notice the `revalidate: 3600`. This gives us ISR (Incremental Static Regeneration) out of the box. The page is statically generated but refreshes every hour. Fast *and* fresh.

## The Image Card Component

This is where `next/image` does the heavy lifting:

```typescript
// components/ImageCard.tsx
import Image from 'next/image';
import { UnsplashImage } from '@/types/unsplash';

interface Props {
  image: UnsplashImage;
}

export function ImageCard({ image }: Props) {
  return (
    <div className="group relative overflow-hidden rounded-lg bg-gray-100">
      <Image
        src={image.urls.regular}
        alt={image.alt_description || 'Gallery image'}
        width={image.width}
        height={image.height}
        className="object-cover transition-transform duration-300 group-hover:scale-105"
        sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
        placeholder="blur"
        blurDataURL={image.urls.thumb}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
        <p className="absolute bottom-3 left-3 text-white text-sm">
          Photo by {image.user.name}
        </p>
      </div>
    </div>
  );
}
```

A few things I want to highlight:

**The `sizes` prop matters.** It tells the browser which image size to download based on viewport width. Without this, you're probably serving desktop-sized images to mobile users.

**`placeholder="blur"` with `blurDataURL`** creates that smooth loading effect. I'm using the thumbnail URL as a quick blur preview—it's not perfect, but it works well enough.

**Width and height from the API** means no layout shift. The browser reserves exactly the right amount of space before the image loads.

## What Most Tutorials Skip

Here's something that bit me on a real project: if you're using Next.js with external images, you need to configure the domains in `next.config.js`:

```javascript
// next.config.js
module.exports = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
    ],
  },
};
```

Without this, you'll get a runtime error that's not particularly helpful.

## Performance Wins

With this setup, you automatically get:

- **Server-side rendering** for instant first paint and SEO
- **Automatic WebP conversion** when the browser supports it
- **Responsive image srcsets** so mobile users don't download 4K images
- **Lazy loading** for images below the fold
- **Caching** at both the data level (ISR) and image level (CDN)

Run a Lighthouse audit on this and you'll see scores in the 90s without any extra optimization work. That's the power of making good architectural decisions upfront.

## Common Pitfalls to Avoid

A few things I've learned the hard way:

**Don't skip the `alt` text.** It's not just for accessibility—it's SEO juice. Unsplash provides descriptions; use them.

**Watch your API rate limits.** Unsplash gives you 50 requests per hour on free tier. That `revalidate: 3600` isn't just for performance—it keeps you under the limit.

**Handle errors gracefully.** Wrap your fetch in a try-catch and show a proper error state. Nothing worse than a blank page when the API is down.

**Test on slow connections.** Chrome DevTools lets you throttle network speed. Try "Slow 3G" and see if your gallery is still usable.

## Wrapping Up

Building a performant image gallery isn't magic—it's about choosing the right tools and understanding how they work together. Next.js 16's Server Components eliminate the client-side data fetching problem. `next/image` handles optimization automatically. TypeScript keeps everything predictable.

The result? A gallery that loads fast, ranks well in search engines, and doesn't make your users wait. That's the kind of frontend work I enjoy shipping.

Give this a try on your next project. Once you see how smooth it feels, you won't want to go back to the old way.
