---
title: "Implementation Mistakes by Devs: How you should not use useEffect"
description: "useEffect: The Powerhouse Hook That's Often..."
pubDate: "Jan 08 2026"
heroImage: "../../assets/implementation-mistakes-by-devs--how-you-should-no.jpg"
---

# `useEffect`: The Powerhouse Hook That's Often Misunderstood

Alright team, let’s talk about `useEffect`. If you’ve been building React applications for any length of time, you’ve undoubtedly used it. It’s a core hook, a true workhorse, and arguably one of the most powerful tools in our React toolkit. But, and this is a big *but*, it's also probably the most commonly misused. I've found that many developers, myself included during earlier days, treat `useEffect` as a generic "do stuff" hook, a place to dump any logic that doesn't quite fit into a render. And honestly, that mindset can lead to some serious headaches.

### The Elephant in the Room: Why `useEffect` Deserves More Respect

Think about it: how many times have you stared at a `useEffect` hook, scratching your head, trying to figure out why something's re-running endlessly, or not running when it should, or creating some bizarre race condition? I've seen entire components become fragile, hard to reason about, and a nightmare to test, all because of a single, poorly implemented `useEffect`.

The core issue? A misunderstanding of its fundamental purpose. `useEffect` isn't just for "side effects" in the generic sense; it's specifically for *synchronizing external systems with your component's props and state*. When you think of it this way, a lot of the confusion starts to melt away.

Let's dive into some of the most common implementation mistakes and, more importantly, how to steer clear of them.

### Mistake #1: The Missing or Misunderstood Dependency Array

This is probably the granddaddy of all `useEffect` mistakes. You either omit the dependency array, making your effect run on every render (which is almost never what you want for anything substantial), or you provide an incorrect one.

**The Bad:**
```typescript
import React, { useEffect, useState } from 'react';

function BadCounter() {
  const [count, setCount] = useState(0);

  // This will run on *every* render, potentially leading to performance issues
  // or unexpected behavior if `someExternalService.log` has side effects.
  useEffect(() => {
    console.log('Component rendered or count changed:', count);
    // Imagine calling an API or subscribing to something here. Chaos!
  }); // No dependency array! Runs after every render.

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

**The Better:**
You want the effect to run only when `count` changes, or perhaps only once on mount.

```typescript
import React, { useEffect, useState } from 'react';

function BetterCounter() {
  const [count, setCount] = useState(0);

  // Runs only when `count` changes.
  useEffect(() => {
    console.log('Count changed to:', count);
  }, [count]); // Dependency array includes `count`.

  // Runs only once on mount.
  useEffect(() => {
    console.log('Component mounted!');
    // This is where you might set up an event listener or fetch initial data.
    return () => {
      console.log('Component unmounted!');
      // Clean up event listeners or subscriptions here.
    };
  }, []); // Empty dependency array. Runs once on mount and cleans up on unmount.

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
      <button onClick={() => setCount(0)}>Reset</button>
    </div>
  );
}
```

**Insight:** The dependency array isn't just an optimization; it's a contract. It tells React: "Re-synchronize this effect whenever any of these values change." If a value used inside your effect changes and it's *not* in the dependency array, your effect is operating on a stale closure, leading to bugs. Always make sure your dependencies are exhaustive and correct. React ESLint rules are your friend here!

### Mistake #2: Over-specifying Dependencies (The Object/Array Trap)

Sometimes, you *do* want to react to a prop or state change, but that prop/state is an object or an array. Putting these directly into the dependency array can cause unintended re-runs because JavaScript's equality check for non-primitive types compares references, not values.

**The Bad:**
```typescript
import React, { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
}

function UserProfile({ user }: { user: User }) {
  const [localUser, setLocalUser] = useState(user);

  useEffect(() => {
    // This will re-run on every parent re-render *even if* user.name and user.id are the same,
    // because the `user` object reference might be new each time.
    console.log('User data updated:', localUser);
    // Imagine making an API call to update local state based on `user` prop
    // This could lead to infinite loops if `setLocalUser` is called unconditionally.
    setLocalUser(user);
  }, [user]); // `user` is an object, its reference changes often.

  return (
    <div>
      <h2>{localUser.name}</h2>
      <p>ID: {localUser.id}</p>
    </div>
  );
}
```

**The Better:**
React to the *specific primitive values* within the object that your effect actually depends on, or use `useMemo`/`useCallback` if the object/function itself is a dependency.

```typescript
import React, { useEffect, useState } from 'react';

interface User {
  id: string;
  name: string;
}

function UserProfile({ user }: { user: User }) {
  const [localUser, setLocalUser] = useState(user);

  useEffect(() => {
    // Only re-run if the user's ID or name actually changes.
    // This performs a shallow comparison of relevant properties.
    if (localUser.id !== user.id || localUser.name !== user.name) {
      console.log('User data updated:', user);
      setLocalUser(user);
    }
  }, [user.id, user.name]); // React to primitive properties.

  return (
    <div>
      <h2>{localUser.name}</h2>
      <p>ID: {localUser.id}</p>
    </div>
  );
}
```

**Insight:** When a dependency is an object or array, ask yourself: "Do I truly need to react to a *new instance* of this object/array, or just changes to its *contents*?" If it's the contents, extract those primitive values. If it's a function, use `useCallback`. If it's an object you control, ensure its creation is memoized with `useMemo` in the parent component.

### Mistake #3: Using `useEffect` for Derived State or Memoization

This is a subtle one. Sometimes developers reach for `useEffect` to compute a new value based on existing state or props, storing it in another piece of state. This is almost always an anti-pattern. If a value can be computed synchronously during render from existing state or props, it's *derived state*, and `useEffect` is overkill (and can lead to bugs or performance issues).

**The Bad:**
```typescript
import React, { useEffect, useState } from 'react';

function ProductDisplay({ price, quantity }: { price: number; quantity: number }) {
  const [total, setTotal] = useState(0);

  // Unnecessary use of useEffect for derived state
  useEffect(() => {
    const newTotal = price * quantity;
    setTotal(newTotal);
  }, [price, quantity]); // This works, but it's more complex than needed.

  return (
    <div>
      <p>Price: ${price}</p>
      <p>Quantity: {quantity}</p>
      <h3>Total: ${total}</h3>
    </div>
  );
}
```

**The Better:**
Calculate derived state directly during render. If the calculation is expensive, *then* consider `useMemo`.

```typescript
import React, { useMemo } from 'react';

function ProductDisplay({ price, quantity }: { price: number; quantity: number }) {
  // Directly calculate derived state during render. Clean and simple.
  const total = price * quantity;

  // If the calculation was computationally expensive, use useMemo:
  // const total = useMemo(() => price * quantity, [price, quantity]);

  return (
    <div>
      <p>Price: ${price}</p>
      <p>Quantity: {quantity}</p>
      <h3>Total: ${total}</h3>
    </div>
  );
}
```

**Insight:** `useEffect` runs *after* render. If you're setting state in `useEffect` based on props/state, you're causing an extra re-render cycle for something that could have been handled in the initial render. Use `useEffect` when you need to *synchronize* with something *outside* React's render phase (like the DOM, a third-party library, an API, etc.).

### Mistake #4: Forgetting Cleanup Functions (Memory Leaks Ahoy!)

If your `useEffect` sets up a subscription, adds an event listener, or starts a timer, you *must* provide a cleanup function. Forgetting this is a surefire way to introduce memory leaks, performance issues, and unexpected behavior in long-running applications, especially when components mount and unmount frequently.

**The Bad:**
```typescript
import React, { useEffect, useState } from 'react';

function BadTimer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    // This timer will keep running even if the component unmounts,
    // potentially causing errors when `setSeconds` is called on an unmounted component.
    const intervalId = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);
  }, []); // Runs once on mount.

  return <p>Timer: {seconds}s</p>;
}
```

**The Better:**
```typescript
import React, { useEffect, useState } from 'react';

function BetterTimer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const intervalId = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);

    // This cleanup function will run when the component unmounts
    // or when the dependencies change (though in this case, deps are empty).
    return () => {
      clearInterval(intervalId); // Crucial cleanup!
    };
  }, []);

  return <p>Timer: {seconds}s</p>;
}
```

**Insight:** The cleanup function is returned from your effect and runs *before* the component unmounts, or *before* the effect re-runs due to dependency changes. It’s essential for undoing anything your effect did to avoid lingering side effects.

### Wrapping It Up: A Mindset Shift

The biggest lesson I've learned about `useEffect` is that it requires a fundamental shift in how we think about side effects in React. It's not a direct replacement for `componentDidMount`, `componentDidUpdate`, and `componentWillUnmount` in the class component lifecycle model, even though it can achieve similar results.

Instead, embrace this mental model: **`useEffect` synchronizes something external with React state/props.**

*   **Think synchronization:** What external system (DOM, API, event listener, timer, third-party library) needs to be kept in sync with my component's current state or props?
*   **Be meticulous about dependencies:** Every value from your component's scope (props, state, functions) used inside `useEffect` *must* be in its dependency array, unless you explicitly know it's stable (`useCallback`, `useMemo`, or truly static values).
*   **Clean up after yourself:** If your effect does anything that requires "undoing" (subscriptions, listeners, timers), return a cleanup function.
*   **Prefer derived state:** If a value can be computed from existing props or state during render, do it directly. Save `useEffect` for true side effects.

Mastering `useEffect` is a cornerstone of writing robust, performant, and maintainable React applications. It’s a powerful tool, and with the right understanding, you’ll wield it like a pro, avoiding those frustrating bugs and building experiences that feel solid and predictable. Keep coding smartly!
