import { useEffect, useRef } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { usePath } from '@/hooks/usePath';
import { useEndpoints } from '@/hooks/useEndpoints';
import { useRerollFeedback } from '@/hooks/useRerollFeedback';
import { Brand } from '@/components/Brand';
import { JourneyList, type JourneyControls } from '@/components/JourneyList';
import { JourneyHeading } from '@/components/JourneyHeading';
import { PathStatus } from '@/components/PathStatus';
import { PathSkeleton } from '@/components/PathSkeleton';
import { PathIntro } from '@/components/PathIntro';
import { ShareButton } from '@/components/ShareButton';
import { RerollNotice, type RerollReason } from '@/components/RerollNotice';
import { RouteHistory } from '@/components/RouteHistory';
import { addExclusion, clearExclusions, decodeExclusions } from '@/lib/exclusions';
import { journeyLength } from '@/lib/journeyLength';
import { linkIntegrity } from '@/lib/exclusions';
import { journeyTitle, useDocumentTitle } from '@/hooks/useDocumentTitle';
import { useFocusAfterReroll } from '@/hooks/useFocusAfterReroll';
import { LinkDamageNotice } from '@/components/LinkDamageNotice';

export function PathPage() {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const state = usePath();
  const journey = useRef<JourneyControls>(null);

  // Confirmation of a press, on its own clock rather than the request's. The
  // message used to be cleared the moment a path landed, which meant a fast
  // rebuild showed it for less time than it takes to read.
  const feedback = useRerollFeedback(state.status, state.artists);

  // Only needed while there is nothing on screen to name the endpoints.
  const endpoints = useEndpoints(from, to, state.artists.length > 0);

  // Issues #191 / #188 / #187 — tab title naming both ends, focus to the
  // heading once a rebuild lands, and a warning for a link cut in transit.
  const heading = useRef<HTMLHeadingElement>(null);
  useDocumentTitle(journeyTitle(
    state.artists[0]?.name ?? endpoints.from?.name,
    state.artists.at(-1)?.name ?? endpoints.to?.name,
  ));
  useFocusAfterReroll(feedback.notice, state.status, heading);
  const damage = linkIntegrity(params);

  // Every control that leaves or rebuilds the path silences the audio on the press
  // itself. Leaving it to the rebuild meant a clip carried on over a darkened page
  // until the new path arrived, which reads as the button not having worked.
  function go(next: URLSearchParams, why: RerollReason) {
    journey.current?.stop();
    feedback.begin(why);
    const qs = next.toString();
    navigate(`/path/${from}/${to}${qs ? `?${qs}` : ''}`);
  }

  // Back and Forward change the path too, and are not routed through go() — Back
  // is the documented undo for a bypass (G3-F10). Stop on the URL change itself,
  // as the buttons do on their press. For a press this is a second, harmless stop.
  const pathUrl = `${from}/${to}?${params.toString()}`;
  useEffect(() => {
    journey.current?.stop();
  }, [pathUrl]);

  // One signal since LUX-1. `addExclusion` still writes the URL parameter for the
  // signal it is handed, and `decodeExclusions` still reads BOTH, so a link shared
  // before this change keeps resolving exactly as it did.
  function handleBypass(mbid: string) {
    go(addExclusion(params, mbid, 'known'), 'known');
  }

  // Whether "Reset path" has anything to undo. The names and ids for the
  // panel itself come from the path response, not the URL (LUX-2b) — this
  // reads the URL only to answer yes/no.
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

  // Dim while a press is being answered AND while its message is still being
  // held. Without the second half the path would brighten underneath a notice
  // that still says it is working. The trailing clause keeps the dim for a
  // rebuild nobody pressed — Back undoing a bypass — which has no message.
  const rebuilding =
    feedback.notice !== null || (state.status === 'loading' && state.artists.length > 0);

  return (
    // Widened from 620px with the docked detail (UXR-T7): the dock is a 400px
    // column beside the rail, and at 620 the page scrolled sideways at 1280.
    // UXR-T8 restyles the header inside this width.
    //
    // pb-40 is the reserve for the fixed player bar, and it is a separate
    // utility from the top padding on purpose (issue #206): `sm:py-9` used to
    // sit beside it, compiles to padding-block, comes later in the stylesheet,
    // and so removed the reserve from 640px up — the last skipped artist sat
    // under the bar. Never a `py-` here, at any breakpoint; a test pins that.
    <main className="mx-auto w-full max-w-[1200px] px-5 pt-6 pb-40 sm:pt-9">
      <div className="mb-8 flex items-center justify-between gap-5 text-[13px] sm:text-[13.5px]">
        <Brand size="nav" href="/" onNavigate={() => journey.current?.stop()} />
        <div className="flex items-center gap-2.5">
          {/* Only offered once there is something to undo. */}
          {hasBypasses && (
            <button
              type="button"
              onClick={() => go(clearExclusions(params), 'reset')}
              className="rounded-full border border-[var(--color-border-strong)] px-[15px] py-2 text-[13.5px] text-[var(--color-muted)] hover:text-[var(--color-text)]"
            >
              Reset path
            </button>
          )}
          <ShareButton />
          {/* Without this the path page is a dead end: every route back to
              picking two artists was the browser's Back button. The pair
              travels along so the boxes arrive filled in. */}
          <Link
            to={`/?${newPathParams.toString()}`}
            onClick={() => journey.current?.stop()}
            className="rounded-full border border-[var(--color-start)] px-[15px] py-2 text-[13.5px] text-[var(--color-text)]"
          >
            New path
          </Link>
        </div>
      </div>

      {damage && <LinkDamageNotice damage={damage} />}

      {state.status === 'error' && state.error ? (
        <PathStatus
          error={state.error}
          message={state.message}
          limit={state.limit}
          onClearExclusions={() => go(clearExclusions(params), 'reset')}
          onRetry={state.retry}
        />
      ) : state.artists.length === 0 ? (
        <PathSkeleton from={endpoints.from} to={endpoints.to} />
      ) : (
        <div>
          <div className="mb-6">
            <JourneyHeading
              from={state.artists[0].name}
              to={state.artists.at(-1)!.name}
              stops={journeyLength(state.artists)}
              headingRef={heading}
            />
          </div>
          <PathIntro stopRule={state.stopRule} />
          {/* The positioning context is the PATH, not the path plus the
              explainer above it. It used to wrap both, so on a first visit —
              when the explainer is open and tall — the notice landed on top of
              the explainer instead of over the journey it describes. Reported
              2026-07-28 and cosmetic while the notice only flashed; holding it
              for NOTICE_MIN_MS made it something you always see. */}
          <div className="relative">
            <div className={rebuilding ? 'opacity-60 transition-opacity' : ''}>
              <JourneyList
                ref={journey}
                artists={state.artists}
                stopRule={state.stopRule}
                onBypass={handleBypass}
                changed={feedback.changed}
              />
              {/* Dimmed together with the journey (not rendered outside it):
                  while a press is being answered, the panel still names the
                  PREVIOUS path's skips, so leaving it undimmed would have the
                  page disagree with itself about whether it has settled. */}
              <RouteHistory bypassed={state.bypassed} unresolved={state.unresolved} />
            </div>
            {feedback.notice && <RerollNotice reason={feedback.notice} />}
          </div>
        </div>
      )}
    </main>
  );
}
