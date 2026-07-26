import { Link } from 'react-router-dom';

/**
 * Any URL that is not the landing page or a path. After the deploy that
 * includes every mistyped or truncated shared link, and shared links are how
 * this app travels — a blank page is the worst possible landing for one.
 */
export function NotFound() {
  return (
    <main className="max-w-xl mx-auto px-4 py-10 sm:py-16">
      <h1 className="text-2xl font-semibold mb-3">Nothing here</h1>
      <p className="text-[var(--color-muted)] mb-6">
        That link doesn&rsquo;t point at a journey. It may have been cut short on its way to you.
      </p>
      <Link to="/" className="text-[var(--color-accent)]">
        Start a journey
      </Link>
    </main>
  );
}
