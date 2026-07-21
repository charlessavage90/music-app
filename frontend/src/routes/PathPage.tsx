import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { JourneyList } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { addExclusion, clearExclusions } from '@/lib/exclusions';
import type { BypassReason } from '@/api/types';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();

  function go(next: URLSearchParams) {
    const qs = next.toString();
    navigate(`/path/${from}/${to}${qs ? `?${qs}` : ''}`);
  }

  function handleBypass(mbid: string, reason: BypassReason) {
    go(addExclusion(params, mbid, reason));
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-10 pb-24">
      {state.status === 'error' && state.error ? (
        <PathStatus error={state.error} onClearExclusions={() => go(clearExclusions(params))} />
      ) : (
        <div className={state.status === 'loading' ? 'opacity-60 transition-opacity' : ''}>
          {state.artists.length > 0 ? (
            <JourneyList artists={state.artists} onBypass={handleBypass} />
          ) : (
            <p className="text-[var(--color-muted)]">Building your path…</p>
          )}
        </div>
      )}
    </main>
  );
}
