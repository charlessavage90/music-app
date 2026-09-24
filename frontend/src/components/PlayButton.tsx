interface Props {
  /** What pressing it will do — not what the player is currently doing. */
  state: 'play' | 'pause';
  /** 40px on a card, 36px on the bottom bar. */
  size: 'card' | 'bar';
  disabled?: boolean;
  /** Whose clip — appended to the accessible name, so eight buttons are eight names (G3-F4). */
  name?: string | null;
  onClick: () => void;
}

/**
 * The mockup draws both glyphs as CSS shapes rather than text characters, which
 * is what makes them optically centred at every size. Extracted because it
 * appears at two sizes with a disabled variant in four places.
 *
 * The aria-label is `Play`/`Pause`, followed by the artist's name when one is
 * given: a journey is eight of these, and a screen reader listing "Play, Play,
 * Play…" gave no way to tell them apart (G3-F4, issue #188). Tests match on
 * `/play/i` and `/pause/i` for that reason, never on the bare word.
 */
export function PlayButton({ state, size, disabled, name, onClick }: Props) {
  const verb = state === 'pause' ? 'Pause' : 'Play';
  const box = size === 'card' ? 'w-10 h-10' : 'w-9 h-9';
  const bar = size === 'card' ? 'w-[3.5px] h-3.5' : 'w-[3px] h-3';
  return (
    <button
      type="button"
      aria-label={name ? `${verb} ${name}` : verb}
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
