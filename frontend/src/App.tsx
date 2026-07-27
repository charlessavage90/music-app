import { Route, Routes } from 'react-router-dom';
import { LandingPage } from '@/routes/LandingPage';
import { NotFound } from '@/routes/NotFound';
import { PathPage } from '@/routes/PathPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/path/:from/:to" element={<PathPage />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
