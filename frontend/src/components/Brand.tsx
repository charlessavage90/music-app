import { Link } from 'react-router-dom';

interface Props {
  /** 30 px mark in a page header, 38 px on the landing hero. */
  size: 'nav' | 'hero';
  /**
   * Where the mark leads. Given, the brand is a link there with "home" in its
   * name (issue #203: on the journey page the logo is the way back, as a site
   * logo conventionally is). Omitted, it is a plain image — the landing page,
   * which is home already.
   */
  href?: string;
  /** Runs before the navigation, so the journey page can stop its audio. */
  onNavigate?: () => void;
}

/**
 * The mark and the wordmark, as one accessible name (UXR-D1).
 *
 * The mark is the owner's PNG at /unsung-mark.png — his to export from the
 * Design project; nothing here depends on it existing. The wordmark is split
 * only visually: "unsung" bright, ".fm" dim, exactly as drawn.
 */
export function Brand({ size, href, onNavigate }: Props) {
  const px = size === 'hero' ? 38 : 30;
  const text = size === 'hero' ? 'text-[19px]' : 'text-[16px]';
  const inner = (
    <>
      <img src="/unsung-mark.png" alt="" width={px} height={px} className="block" />
      <span aria-hidden className={`font-display font-semibold tracking-[-.02em] ${text}`}>
        unsung<span className="font-normal text-[var(--color-label)]">.fm</span>
      </span>
    </>
  );
  const layout = 'inline-flex items-center gap-2.5';
  if (href) {
    return (
      <Link to={href} onClick={onNavigate} aria-label="Unsung.fm — home" className={`${layout} rounded-md`}>
        {inner}
      </Link>
    );
  }
  return (
    <span className={layout} aria-label="Unsung.fm" role="img">
      {inner}
    </span>
  );
}
