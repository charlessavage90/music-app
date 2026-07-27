import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

test('landing page renders at root', () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByRole('heading', { name: /artist path/i })).toBeInTheDocument();
});

test('an unknown URL offers a way back rather than a blank page', () => {
  // After the deploy this covers every mistyped or truncated shared link, and
  // shared links are how this app is meant to travel.
  render(
    <MemoryRouter initialEntries={['/path/only-one-id']}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /start a journey/i })).toHaveAttribute('href', '/');
});
