import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { usePlayer } from './usePlayer';

const ended: Array<() => void> = [];
vi.mock('./Player', () => ({
  HtmlAudioPlayer: class {
    play = vi.fn();
    pause = vi.fn();
    dispose = vi.fn();
    onEnded(cb: () => void) { ended.push(cb); }
  },
}));

function Harness() {
  // Miles and Kraftwerk are playable; a middle artist with no clip is absent from the list.
  const p = usePlayer([{ mbid: 'miles', url: 'u1' }, { mbid: 'kraftwerk', url: 'u2' }]);
  return (
    <div>
      <span data-testid="current">{p.currentMbid ?? 'none'}</span>
      <button onClick={() => p.playFrom('miles')}>play</button>
    </div>
  );
}

test('auto-advances to the next playable on track end', async () => {
  const user = userEvent.setup();
  render(<Harness />);
  await user.click(screen.getByText('play'));
  expect(screen.getByTestId('current')).toHaveTextContent('miles');
  act(() => ended.forEach((cb) => cb()));
  expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk');
});
