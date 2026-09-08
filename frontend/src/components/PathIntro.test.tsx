import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, test } from 'vitest';
import { PathIntro } from './PathIntro';

beforeEach(() => localStorage.clear());

// The result line moved to JourneyHeading's tile on 2026-09-08 (UXR-T8), which
// is the one place the step count is stated now (UXR-D6). What is left here is
// the explainer alone.
test('states no count of its own', () => {
  render(<PathIntro stopRule="natural" />);
  expect(screen.queryByText(/we found a path/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/steps?\./i)).not.toBeInTheDocument();
});

// JourneyList already says the useful thing for this case, and there is no
// bypass control anywhere to explain.
test('stands down entirely when the two artists are adjacent', () => {
  render(<PathIntro stopRule="adjacent_only" />);
  expect(screen.queryByText(/how do i change the path/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/rebuilds the whole journey/i)).not.toBeInTheDocument();
});

test('the explainer is open on a first visit and says a press rebuilds everything', () => {
  render(<PathIntro stopRule="natural" />);
  expect(screen.getByText(/rebuilds the whole journey/i)).toBeInTheDocument();
});

// The explainer names the one control by its real label. If this string drifts
// from the detail's own wording, the help is wrong.
test('the explainer names the control by its real label', () => {
  render(<PathIntro stopRule="natural" />);
  expect(screen.getByText(/dig deeper/i)).toBeInTheDocument();
});

// UXR-D5. The control moved off the card and into the artist detail on
// 2026-09-08, and it now takes two presses to reach. Help that still describes
// the old placement is worse than no help: it sends the reader to the bottom of
// a card that has nothing there.
test('the explainer describes where the control actually is', () => {
  render(<PathIntro stopRule="natural" />);
  expect(screen.getByText(/open any artist in the middle/i)).toBeInTheDocument();
  expect(screen.queryByText(/along the bottom of their card/i)).not.toBeInTheDocument();
});

test('dismissal persists across a remount', async () => {
  const user = userEvent.setup();
  const { unmount } = render(<PathIntro stopRule="natural" />);
  await user.click(screen.getByRole('button', { name: /got it/i }));
  expect(screen.queryByText(/rebuilds the whole journey/i)).not.toBeInTheDocument();
  unmount();

  render(<PathIntro stopRule="natural" />);
  expect(screen.queryByText(/rebuilds the whole journey/i)).not.toBeInTheDocument();
  // Still reachable — dismissed is not deleted.
  expect(screen.getByRole('button', { name: /how do i change the path/i })).toBeInTheDocument();
});
