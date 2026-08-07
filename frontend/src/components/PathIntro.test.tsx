import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, expect, test } from 'vitest';
import { PathIntro } from './PathIntro';

beforeEach(() => localStorage.clear());

// The count sits in its own <span> for the brighter colour, so the sentence is
// split across three text nodes. getByText matches a node's OWN text children,
// which is why these read the whole line's textContent instead.
test('states the number of artists in between', () => {
  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.getByText(/we found a path/i)).toHaveTextContent(/in 3 steps\./i);
});

test('uses the singular for one', () => {
  render(<PathIntro count={1} stopRule="natural" />);
  expect(screen.getByText(/we found a path/i)).toHaveTextContent(/in 1 step\./i);
});

// JourneyList already says the useful thing for this case, and there is no
// step count to state and no footer strip anywhere to explain.
test('stands down entirely when the two artists are adjacent', () => {
  render(<PathIntro count={0} stopRule="adjacent_only" />);
  expect(screen.queryByText(/we found a path/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/how do i change the path/i)).not.toBeInTheDocument();
});

test('the explainer is open on a first visit and says a press rebuilds everything', () => {
  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.getByText(/either one rebuilds the whole journey/i)).toBeInTheDocument();
});

// The explainer's job changed with the tray: it now has to say where the
// control IS, because it is no longer two buttons sitting in plain view. If
// these three strings drift from the card's own wording, the help is wrong.
test('the explainer names the strip and both directions by their real labels', () => {
  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.getByText(/rebuild from here/i)).toBeInTheDocument();
  expect(screen.getByText(/steer away/i)).toBeInTheDocument();
  expect(screen.getByText(/go deeper/i)).toBeInTheDocument();
});

test('dismissal persists across a remount', async () => {
  const user = userEvent.setup();
  const { unmount } = render(<PathIntro count={3} stopRule="natural" />);
  await user.click(screen.getByRole('button', { name: /got it/i }));
  expect(screen.queryByText(/either one rebuilds the whole journey/i)).not.toBeInTheDocument();
  unmount();

  render(<PathIntro count={3} stopRule="natural" />);
  expect(screen.queryByText(/either one rebuilds the whole journey/i)).not.toBeInTheDocument();
  // Still reachable — dismissed is not deleted.
  expect(screen.getByRole('button', { name: /how do i change the path/i })).toBeInTheDocument();
});
