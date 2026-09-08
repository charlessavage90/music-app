import { useEffect, type ReactNode } from 'react';

interface Props { open: boolean; onClose: () => void; children: ReactNode }

/**
 * The phone container for ArtistDetail (UXR-D3): a bottom sheet over a scrim.
 * lg:hidden — at lg the same children render in DetailDock instead.
 */
export function DetailSheet({ open, onClose, children }: Props) {
  useEffect(() => {
    // Bound to `open` so a closed sheet left mounted does not go on answering
    // Escape for the page behind it.
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-30 lg:hidden">
      <div data-testid="scrim" onClick={onClose} className="absolute inset-0 bg-black/60" />
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Artist detail"
        className="absolute inset-x-0 bottom-0 max-h-[88vh] overflow-y-auto rounded-t-[22px] border-t border-[var(--color-detail-border)] bg-[linear-gradient(180deg,#101420,#0b0b11_55%)] shadow-[0_-30px_60px_-20px_rgba(0,0,0,.9)]"
      >
        <div className="flex justify-center pb-1 pt-2.5">
          <span className="h-1 w-11 rounded-full bg-[var(--color-detail-border)]" />
        </div>
        {children}
      </div>
    </div>
  );
}
