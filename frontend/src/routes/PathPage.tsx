import { useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { useEndpoints } from '@/hooks/useEndpoints';
import { JourneyList, type JourneyControls } from '@/components/JourneyList';
import { PathStatus } from '@/components/PathStatus';
import { PathSkeleton } from '@/components/PathSkeleton';
import { PathIntro } from '@/components/PathIntro';
import { RerollNotice, type RerollReason } from '@/components/RerollNotice';
import { addExclusion, clearExclusions, decodeExclusions } from '@/lib/exclusions';
import type { BypassReason } from '@/api/types';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();
  const journey = useRef<JourneyControls>(null);

  // Which control started the rebuild currently in flight. Drives the message
  // over the held path; cleared the moment a path lands.
  const [reason, setReason] = useState<RerollReason | null>(null);
  useEffect(() => {
    if (state.status !== 'loading') setReason(null);
  }, [state.status]);

  // Only needed while there is nothing on screen to name the endpoints.
  const endpoints = useEndpoints(from, to, state.artists.length > 0);

  // Every control that leaves or rebuilds the path silences the audio on the press
  // itself. Leaving it to the rebuild meant a clip carried on over a darkened page
  // until the new path arrived, which reads as the button not having worked.
  function go(next: URLSearchParams, why: RerollReason) {
    journey.current?.stop();
    setReason(why);
    const qs = next.toString();
    navigate(`/path/${from}/${to}${qs ? `?${qs}` : ''}`);
  }

  function handleBypass(mbid: string, why: BypassReason) {
    go(addExclusion(params, mbid, why), why);
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

  const rebuilding = state.status === 'loading' && state.artists.length > 0;

  return (
    <main className="mx-auto w-full max-w-[620px] px-5 py-6 pb-40 sm:py-9">
      <div className="mb-6 flex items-center gap-5 text-[13px] sm:text-[13.5px]">
        {/* Without this the path page is a dead end: every route back to
            picking two artists was the browser's Back button. The pair
            travels along so the boxes arrive filled in. */}
        <Link
          to={`/?${newPathParams.toString()}`}
          onClick={() => journey.current?.stop()}
          className="text-[var(--color-muted)] hover:text-[var(--color-text)]"
        >
          ← New path
        </Link>
        {/* Only offered once there is something to undo. */}
        {hasBypasses && (
          <button
            type="button"
            onClick={() => go(clearExclusions(params), 'reset')}
            className="text-[var(--color-muted)] hover:text-[var(--color-text)]"
          >
            ↺ Reset path
          </button>
        )}
      </div>

      {state.status === 'error' && state.error ? (
        <PathStatus
          error={state.error}
          onClearExclusions={() => go(clearExclusions(params), 'reset')}
          onRetry={state.retry}
        />
      ) : state.artists.length === 0 ? (
        <PathSkeleton from={endpoints.from} to={endpoints.to} />
      ) : (
        <div className="relative">
          <PathIntro count={state.artists.length - 2} stopRule={state.stopRule} />
          <div className={rebuilding ? 'opacity-60 transition-opacity' : ''}>
            <JourneyList
              ref={journey}
              artists={state.artists}
              stopRule={state.stopRule}
              onBypass={handleBypass}
            />
          </div>
          {rebuilding && reason && <RerollNotice reason={reason} />}
        </div>
      )}
    </main>
  );
}
