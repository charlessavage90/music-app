import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import { ShareButton } from './ShareButton';

afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); });

test('uses the Web Share API when the browser has one', async () => {
  const user = userEvent.setup();
  const share = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('navigator', { ...navigator, share });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(share).toHaveBeenCalledWith({ title: 'Unsung.fm', url: window.location.href });
});

test('falls back to the clipboard and says so for a moment', async () => {
  const user = userEvent.setup();
  const writeText = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('navigator', { ...navigator, share: undefined, clipboard: { writeText } });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(writeText).toHaveBeenCalledWith(window.location.href);
  expect(await screen.findByText(/link copied/i)).toBeInTheDocument();
});

// UI-7's rule for a decoration applies to a convenience too: a browser that
// refuses the clipboard (an insecure origin, a denied permission) must not
// take the page down with it. The address bar still holds the journey.
test('a refused clipboard leaves the page alone', async () => {
  const user = userEvent.setup();
  const writeText = vi.fn().mockRejectedValue(new Error('denied'));
  vi.stubGlobal('navigator', { ...navigator, share: undefined, clipboard: { writeText } });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(screen.queryByText(/link copied/i)).not.toBeInTheDocument();
  expect(screen.getByRole('button', { name: /share/i })).toBeInTheDocument();
});

// A share sheet the user swipes away rejects. That is a dismissal, not a
// failure, and it must not fall through to the clipboard branch and claim a
// copy the user never asked for.
test('a dismissed share sheet does not fall back to the clipboard', async () => {
  const user = userEvent.setup();
  const share = vi.fn().mockRejectedValue(new DOMException('Abort', 'AbortError'));
  const writeText = vi.fn().mockResolvedValue(undefined);
  vi.stubGlobal('navigator', { ...navigator, share, clipboard: { writeText } });
  render(<ShareButton />);
  await user.click(screen.getByRole('button', { name: /share/i }));
  expect(writeText).not.toHaveBeenCalled();
  expect(screen.queryByText(/link copied/i)).not.toBeInTheDocument();
});
