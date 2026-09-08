interface Props {
  /** 30 px mark in a page header, 38 px on the landing hero. */
  size: 'nav' | 'hero';
}

/**
 * The mark and the wordmark, as one accessible name (UXR-D1).
 *
 * The mark is the owner's PNG at /unsung-mark.png — his to export from the
 * Design project; nothing here depends on it existing. The wordmark is split
 * only visually: "unsung" bright, ".fm" dim, exactly as drawn.
 */
export function Brand({ size }: Props) {
  const px = size === 'hero' ? 38 : 30;
  const text = size === 'hero' ? 'text-[19px]' : 'text-[16px]';
  return (
    <span className="inline-flex items-center gap-2.5" aria-label="Unsung.fm" role="img">
      <img src="/unsung-mark.png" alt="" width={px} height={px} className="block" />
      <span aria-hidden className={`font-display font-semibold tracking-[-.02em] ${text}`}>
        unsung<span className="font-normal text-[var(--color-label)]">.fm</span>
      </span>
    </span>
  );
}
