import { useEffect, useState } from 'react';

/**
 * Share the journey (UXR-D9). The URL already IS the journey — endpoints and
 * every bypass — so there is nothing to build; the button hands the address
 * bar to the OS share sheet where one exists and to the clipboard elsewhere.
 */
export function ShareButton() {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const t = setTimeout(() => setCopied(false), 2000);
    return () => clearTimeout(t);
  }, [copied]);

  async function share() {
    const url = window.location.href;
    if (typeof navigator.share === 'function') {
      // A swiped-away share sheet rejects. That is a dismissal, not a failure,
      // so it returns rather than falling through to the clipboard and
      // claiming a copy the user never asked for.
      try { await navigator.share({ title: 'Unsung.fm', url }); } catch { /* user dismissed */ }
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
    } catch { /* nothing to say: the address bar still has it */ }
  }

  return (
    <button
      type="button"
      onClick={share}
      className="rounded-full border border-[var(--color-border-strong)] px-[15px] py-2 text-[13.5px] text-[var(--color-muted)] hover:text-[var(--color-text)]"
      aria-live="polite"
    >
      {copied ? 'Link copied' : 'Share'}
    </button>
  );
}
