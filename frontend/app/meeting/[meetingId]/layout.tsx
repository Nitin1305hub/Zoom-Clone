"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { LoaderCircle, Users } from "lucide-react";
import { api, Meeting } from "@/lib/api";

export default function MeetingLayout({ children }: { children: React.ReactNode }) {
  const { meetingId } = useParams<{ meetingId: string }>();
  const router = useRouter();
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [ready, setReady] = useState(false);
  const [hasName, setHasName] = useState(false);
  const [joining, setJoining] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const savedName = sessionStorage.getItem("meetly-display-name");
    if (savedName) { setDisplayName(savedName); setHasName(true); }
    api.get(meetingId).then(setMeeting).catch(reason => setError(reason.message)).finally(() => setReady(true));
  }, [meetingId]);

  async function join(event: React.FormEvent) {
    event.preventDefault();
    if (!displayName.trim()) return setError("Enter a display name to join this meeting.");
    setJoining(true);
    setError("");
    try {
      await api.join(meetingId, displayName.trim());
      window.location.reload();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to join this meeting.");
    } finally {
      setJoining(false);
    }
  }

  if (!ready) return <main className="room"><div className="room-loading"><LoaderCircle className="spin" /> Preparing your meeting...</div></main>;
  if (hasName) return <>{children}</>;

  return <main className="room"><style jsx global>{`.room-join{width:min(420px,calc(100% - 40px));margin:auto;background:#192335;border:1px solid #33425e;border-radius:16px;padding:34px;text-align:center;box-shadow:0 24px 60px #00000033}.room-join-icon{height:54px;width:54px;margin:0 auto 16px;border-radius:15px;background:#315ed5;display:grid;place-items:center}.room-join h1{font-size:24px;margin:8px 0}.room-join>p:not(.eyebrow){color:#b8c2d3;font-size:14px;margin:0 0 22px}.room-join form{text-align:left;display:grid;gap:14px}.room-join label{font-size:12px;font-weight:700;color:#eaf0fc}.room-join input{display:block;width:100%;margin-top:7px;padding:11px;border-radius:8px;border:1px solid #536176;background:#111827;color:#fff;outline:none}.room-join input:focus{border-color:#6f91ff;box-shadow:0 0 0 3px #3568f133}.join-error{color:#ffb4ba;background:#4a2028;padding:9px;border-radius:7px;font-size:12px}.back-link{margin-top:17px;background:transparent;color:#b8c7e8;font-size:13px}`}</style><div className="room-join">
    <div className="room-join-icon"><Users size={26} /></div><p className="eyebrow">READY TO JOIN</p><h1>{meeting?.title || "Join meeting"}</h1><p>Enter the name people will see in this meeting.</p>
    <form onSubmit={join}><label>Display name<input autoFocus value={displayName} onChange={event => setDisplayName(event.target.value)} placeholder="Your name" /></label>{error && <span className="join-error">{error}</span>}<button className="primary wide" disabled={joining}>{joining ? "Joining..." : "Join meeting"}</button></form>
    <button className="back-link" onClick={() => router.push("/")}>Back to home</button>
  </div></main>;
}
