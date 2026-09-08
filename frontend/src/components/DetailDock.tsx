import type { ReactNode } from 'react';

/** The desktop container for ArtistDetail (UXR-D3): docked, sticky, beside the rail. */
export function DetailDock({ children }: { children: ReactNode }) {
  return (
    <aside className="hidden lg:block">
      <div className="sticky top-6 overflow-hidden rounded-[18px] border border-[var(--color-detail-border)] bg-[linear-gradient(180deg,#101420,#0c0c12_55%)]">
        {children}
      </div>
    </aside>
  );
}
