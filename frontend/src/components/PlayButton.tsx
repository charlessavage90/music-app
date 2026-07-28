interface Props {
  /** What pressing it will do — not what the player is currently doing. */
  state: 'play' | 'pause';
  /** 40px on a card, 36px on the bottom bar. */
  size: 'card' | 'bar';
  disabled?: boolean;
  onClick: () => void;
}

/**
 * The mockup draws both glyphs as CSS shapes rather than text characters, which
 * is what makes them optically centred at every size. Extracted because it
 * appears at two sizes with a disabled variant in four places.
 *
 * The aria-label is `Play`/`Pause` exactly: nine tests resolve this by name.
 */
export function PlayButton({ state, size, disabled, onClick }: Props) {
  const box = size === 'card' ? 'w-10 h-10' : 'w-9 h-9';
  const bar = size === 'card' ? 'w-[3.5px] h-3.5' : 'w-[3px] h-3';
  return (
    <button
      type="button"
      aria-label={state === 'pause' ? 'Pause' : 'Play'}
      disabled={disabled}
      onClick={onClick}
      className={`${box} flex-none rounded-full flex items-center justify-center gap-[3.5px] ${
        disabled
          ? 'bg-[var(--color-inert)] border border-[var(--color-border)] cursor-default'
          : 'bg-[var(--color-accent)] hover:bg-[#5b9ce0]'
      }`}
    >
      {state === 'pause' ? (
        <>
          <span className={`${bar} block rounded-[1px] bg-white`} />
          <span className={`${bar} block rounded-[1px] bg-white`} />
        </>
      ) : (
        <span
          className="block w-0 h-0 ml-[3px] border-y-[6.5px] border-y-transparent border-l-[11px]"
          style={{ borderLeftColor: disabled ? 'var(--color-inert-fg)' : '#fff' }}
        />
      )}
    </button>
  );
}
