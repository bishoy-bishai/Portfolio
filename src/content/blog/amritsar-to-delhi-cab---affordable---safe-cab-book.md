---
title: "Amritsar to Delhi Cab | Affordable & Safe Cab Booking"
description: "Crafting Seamless Journeys: Building a Cab Booking App with Next.js and..."
pubDate: "Jan 23 2026"
heroImage: "../../assets/amritsar-to-delhi-cab---affordable---safe-cab-book.jpg"
---

# Crafting Seamless Journeys: Building a Cab Booking App with Next.js and TypeScript

Have you ever been stranded? Maybe after a late flight, or in an unfamiliar city, desperately trying to book a ride? The feeling when an app just *works* – quickly finds a cab, gives you a clear ETA, and handles payment without a hitch – is pure relief. Conversely, the frustration when it glitches, lags, or crashes can ruin your day.

As developers, we often marvel at the surface simplicity of these apps, knowing full well the intricate dance of data, state, and services happening beneath. Building a robust, user-friendly cab booking platform, like one for an "Amritsar to Delhi Cab" service, is a fantastic real-world challenge that beautifully showcases the power of a framework like Next.js, especially when paired with the safety net of TypeScript.

### Why Next.js for Your Digital Dispatcher?

When I first started building web applications beyond simple static sites, I quickly ran into the limitations of client-side rendering for data-heavy or SEO-sensitive projects. Next.js, with its hybrid rendering capabilities (SSR, SSG, ISR, CSR), became my go-to. For a cab booking app, this is huge.

Imagine the search results for "Amritsar to Delhi cab." You want that initial page to load instantly, showing available routes and base prices. That's where **Server-Side Rendering (SSR)** or even **Static Site Generation (SSG)** for less dynamic content (like city pairs) shines. You can pre-fetch critical data on the server, send a fully formed HTML page to the client, and dramatically improve perceived performance and SEO.

Then, as the user interacts – enters pick-up/drop-off, selects a car type – you need **Client-Side Rendering (CSR)** for a dynamic, real-time experience. Next.js lets you effortlessly blend these approaches.

**Here's the thing about real-world projects:** user experience isn't just a "nice-to-have"; it's a core feature. Slow loading times directly correlate to abandoned bookings. A jittery UI erodes trust. Next.js gives us the tools to fight that.

### Structuring the Journey: Routing and Components

Think about the user flow for booking a cab:
1.  **Search:** Enter origin, destination, date/time.
2.  **Select:** View available cabs, prices, driver ratings.
3.  **Confirm:** Review details, payment.
4.  **Track:** See driver's location, ETA.
5.  **Complete:** Post-ride feedback.

Each of these can be a distinct page or a logical section within your Next.js application.

```typescript
// pages/book/[tripId].tsx
import { GetServerSideProps } from 'next';
import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';

interface TripDetails {
  id: string;
  origin: string;
  destination: string;
  cabType: string;
  price: number;
  status: 'pending' | 'confirmed' | 'on-route' | 'completed';
  driverInfo?: { name: string; vehicle: string; rating: number };
}

interface BookingPageProps {
  initialTripData: TripDetails;
}

const BookingPage = ({ initialTripData }: BookingPageProps) => {
  const router = useRouter();
  const [trip, setTrip] = useState<TripDetails>(initialTripData);
  const [loading, setLoading] = useState(false);

  // In a real app, you'd use websockets or polling for real-time updates
  useEffect(() => {
    const fetchLiveUpdates = async () => {
      setLoading(true);
      // Simulate API call for live status
      const response = await fetch(`/api/trips/${trip.id}/status`); 
      const updatedStatus = await response.json();
      setTrip(prev => ({ ...prev, status: updatedStatus.status, driverInfo: updatedStatus.driverInfo || prev.driverInfo }));
      setLoading(false);
    };

    if (trip.status === 'confirmed' || trip.status === 'on-route') {
      const interval = setInterval(fetchLiveUpdates, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, [trip.id, trip.status]);

  if (!trip) {
    return <p>Loading trip details...</p>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Your Trip: {trip.origin} to {trip.destination}</h1>
      <p>Status: <span className={`font-semibold ${loading ? 'animate-pulse' : ''}`}>{trip.status}</span></p>
      <p>Cab Type: {trip.cabType}</p>
      <p>Price: ₹{trip.price}</p>
      {trip.driverInfo && (
        <div className="mt-4 p-3 bg-gray-100 rounded">
          <h2 className="text-xl font-semibold">Driver Details</h2>
          <p>Name: {trip.driverInfo.name}</p>
          <p>Vehicle: {trip.driverInfo.vehicle}</p>
          <p>Rating: {trip.driverInfo.rating}/5</p>
        </div>
      )}
      {/* ... more UI for map, cancellation, etc. */}
    </div>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { tripId } = context.params as { tripId: string };
  // In a real app, fetch from your backend API
  const res = await fetch(`http://localhost:3000/api/trips/${tripId}`); // Example API endpoint
  const initialTripData: TripDetails = await res.json();

  if (!initialTripData) {
    return { notFound: true };
  }

  return {
    props: {
      initialTripData,
    },
  };
};

export default BookingPage;
```

This snippet shows how `getServerSideProps` fetches the initial trip data, ensuring a fast first paint. Then, client-side React hooks (`useState`, `useEffect`) manage real-time status updates. `next/router` allows for clean, semantic URLs like `/book/TRIP123`.

### The Unsung Hero: TypeScript

Building a complex application without TypeScript feels like navigating a dark alley blindfolded. For a cab booking service, where data integrity is paramount (think prices, payment IDs, driver details, locations), TypeScript is not just helpful; it's *critical*.

Consider the `TripDetails` interface above. It strictly defines the shape of our data. If an API accidentally sends `status: "onRoute"` instead of `"on-route"`, TypeScript will catch it at compile time, preventing runtime bugs that could lead to a user not seeing their cab.

**In my experience:** the upfront investment in typing pays dividends in reduced debugging time, clearer code, and vastly improved collaboration across engineering teams. It's like having an extra pair of eyes constantly reviewing your data contracts.

### What Most Tutorials Miss: Real-World Insights

1.  **State Management is a Journey, Not a Destination:** For simple components, `useState` is fine. But for global state (like current user, active booking), consider `useContext` or even a library like Zustand or Jotai. Don't over-engineer early, but be prepared to refactor as complexity grows. The key is to keep related state co-located and accessible where needed, without props-drilling nightmares.

2.  **Optimistic UI vs. Pessimistic UI:** When a user taps "Confirm Booking," do you instantly show "Booking Confirmed" and then update if the API fails (optimistic)? Or do you show a loading spinner until the API confirms (pessimistic)? For a cab booking, where a failed booking has real-world consequences, a slightly more pessimistic approach, or at least a very robust rollback mechanism for optimistic updates, is safer. Trust is paramount.

3.  **Graceful Degradation for Real-Time Data:** What if your real-time driver tracking API momentarily goes down? Don't just show a blank screen. Display the *last known* location and a message like "Live updates temporarily unavailable." Keep the user informed and minimize perceived failure.

4.  **Security and Payment Integration are Not Afterthoughts:** These are fundamental. Always use secure, token-based authentication. Integrate with reputable payment gateways. Client-side code should *never* handle sensitive payment logic. Next.js API Routes can act as secure backend for frontend (BFF) layer for these interactions, shielding your frontend from direct communication with third-party payment APIs.

### Common Pitfalls to Dodge

*   **Ignoring Loading States:** An unresponsive UI with no feedback during data fetching is a user killer. Always show a loader, a skeleton, or a relevant message.
*   **Over-fetching/Under-fetching Data:** Only fetch the data you need, when you need it. Use tools like React Query or SWR to manage caching and revalidation effectively. Conversely, don't make 10 API calls when one well-designed endpoint could suffice.
*   **Lack of Error Boundaries:** When a component crashes, it shouldn't take the entire app down. Implement React Error Boundaries to gracefully catch and display errors in specific UI sections.
*   **Not Considering Internationalization (i18n) Early:** If your cab service expands beyond Amritsar, you'll want different languages, currencies, and date formats. Next.js offers built-in i18n routing. Plan for it.
*   **Performance Bottlenecks from Third-Party Scripts:** Maps (Google Maps, OpenStreetMap) and analytics scripts can be heavy. Use Next.js's `Script` component with `strategy="lazyOnload"` or `strategy="beforeInteractive"` to control when they load and prevent them from blocking your main thread.

### Beyond the Code: Empathy in Engineering

Building a service like an "Amritsar to Delhi Cab" booking app isn't just about writing elegant code. It's about deeply understanding the user's need, the stresses of travel, and the critical importance of reliability. When you choose technologies like Next.js and TypeScript, you're not just picking tools; you're making a statement about the robustness, scalability, and maintainability of the experience you want to deliver.

So, next time you effortlessly book that cab, take a moment to appreciate the engineering that makes it possible. And if you're building one yourself, remember: every line of code contributes to someone's journey. Make it a smooth one.
