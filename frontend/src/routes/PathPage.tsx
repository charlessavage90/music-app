import { useRef } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { JourneyList, type JourneyControls } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { addExclusion, clearExclusions, decodeExclusions } from '@/lib/exclusions';
import type { BypassReason } from '@/api/types';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();
  const journey = useRef<JourneyControls>(null);

  // Every control that leaves or rebuilds the path silences the audio on the press
  // itself. Leaving it to the rebuild meant a clip carried on over a darkened page
  // until the new path arrived, which reads as the button not having worked.
  function go(next: URLSearchParams) {
    journey.current?.stop();
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
    <main className="max-w-2xl mx-auto px-4 py-6 sm:py-10 pb-32">
      <div className="flex items-center gap-4 mb-6 text-sm">
        {/* Without this the path page is a dead end: every route back to
            picking two artists was the browser's Back button. The pair
            travels along so the boxes arrive filled in. */}
        <Link
          to={`/?${newPathParams.toString()}`}
          onClick={() => journey.current?.stop()}
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
            <JourneyList
              ref={journey}
              artists={state.artists}
              stopRule={state.stopRule}
              onBypass={handleBypass}
            />
          ) : (
            <p className="text-[var(--color-muted)]">Building your path…</p>
          )}
        </div>
      )}
    </main>
  );
}
