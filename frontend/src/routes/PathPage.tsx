import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { JourneyList } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { addExclusion, clearExclusions, decodeExclusions } from '@/lib/exclusions';
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

  const hasBypasses = decodeExclusions(params).length > 0;

  // The names come from the path itself; the ids from the URL, so the link
  // still works while the first path is loading or has failed.
  const newPathParams = new URLSearchParams();
  if (from) newPathParams.set('from', from);
  if (to) newPathParams.set('to', to);
  if (state.artists.length > 1) {
    newPathParams.set('fromName', state.artists[0].name);
    newPathParams.set('toName', state.artists[state.artists.length - 1].name);
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-10 pb-24">
      <div className="flex items-center gap-4 mb-6 text-sm">
        {/* Without this the path page is a dead end: every route back to
            picking two artists was the browser's Back button. The pair
            travels along so the boxes arrive filled in. */}
        <Link
          to={`/?${newPathParams.toString()}`}
          className="text-[var(--color-muted)] hover:text-[var(--color-accent)]"
        >
          ← New path
        </Link>
        {/* Only offered once there is something to undo. */}
        {hasBypasses && (
          <button
            type="button"
            onClick={() => go(clearExclusions(params))}
            className="text-[var(--color-muted)] hover:text-[var(--color-accent)]"
          >
            ↺ Reset path
          </button>
        )}
      </div>
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
