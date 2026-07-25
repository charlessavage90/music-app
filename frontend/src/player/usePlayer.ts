import { useEffect, useMemo, useRef, useState } from 'react';
import { HtmlAudioPlayer } from './Player';

interface Playable {
  mbid: string;
  url: string;
}

export function usePlayer(playables: Playable[]) {
  const player = useMemo(() => new HtmlAudioPlayer(), []);
  const [currentMbid, setCurrentMbid] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const listRef = useRef(playables);
  listRef.current = playables;

  useEffect(() => {
    player.onEnded(() => {
      const list = listRef.current;
      setCurrentMbid((cur) => {
        const idx = list.findIndex((p) => p.mbid === cur);
        const next = idx >= 0 ? list[idx + 1] : undefined;
        if (next) {
          player.play(next.url);
          setIsPlaying(true);
          return next.mbid;
        }
        setIsPlaying(false);
        return null;
      });
    });
    return () => player.dispose();
  }, [player]);

  function playFrom(mbid: string) {
    const entry = listRef.current.find((p) => p.mbid === mbid);
    if (!entry) return;
    player.play(entry.url);
    setCurrentMbid(mbid);
    setIsPlaying(true);
  }

  function stop() {
    player.pause();
    setIsPlaying(false);
    setCurrentMbid(null);
  }

  function toggle() {
    if (isPlaying) {
      player.pause();
      setIsPlaying(false);
    } else if (currentMbid) {
      playFrom(currentMbid);
    }
  }

  return { currentMbid, isPlaying, playFrom, toggle, stop };
}
