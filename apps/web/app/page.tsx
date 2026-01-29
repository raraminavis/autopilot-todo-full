"use client";

import { useState } from "react";

type ProposedBlock = {
  task_id: string;
  start_at: string;
  end_at: string;
  chunk_group_id?: string | null;
  chunk_index?: number | null;
  chunk_count?: number | null;
  explain_tags?: string[];
};

export default function Page() {
  const [text, setText] = useState("");
  const [log, setLog] = useState<string[]>([]);
  const [blocks, setBlocks] = useState<ProposedBlock[]>([]);

  async function capture() {
    if (!text.trim()) return;
    const r = await fetch("http://localhost:8000/v1/tasks/capture", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": "u_demo"
      },
      body: JSON.stringify({ text, client_timestamp: new Date().toISOString() })
    });
    const j = await r.json();
    setLog((prev) => [`Captured: ${j.task.task_id} — ${j.task.raw_text}`, ...prev]);
    setText("");
  }

  async function propose() {
    const r = await fetch("http://localhost:8000/v1/schedule/propose", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Id": "u_demo"
      },
      body: JSON.stringify({ horizon_days: 7, trigger: "manual", strategy: "AUTO" })
    });
    const j = await r.json();
    setLog((prev) => [`Proposal: ${j.proposal_id} (${j.proposed_blocks.length} blocks)`, ...prev]);
    setBlocks(j.proposed_blocks);
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1 style={{ marginTop: 0 }}>Autopilot Todo (Scaffold)</h1>

      <div style={{ display: "flex", gap: 12 }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder='Type a task like "email professor tomorrow 5pm"...'
          style={{ flex: 1, padding: 12, borderRadius: 10, border: "1px solid #ddd" }}
        />
        <button onClick={capture} style={{ padding: "12px 14px", borderRadius: 10 }}>
          Send
        </button>
        <button onClick={propose} style={{ padding: "12px 14px", borderRadius: 10 }}>
          Propose Schedule
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 20 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <h3 style={{ marginTop: 0 }}>Log</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {log.map((l, idx) => (
              <div key={idx} style={{ fontSize: 13, color: "#333" }}>{l}</div>
            ))}
          </div>
        </div>

        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <h3 style={{ marginTop: 0 }}>Proposed blocks</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {blocks.map((b, idx) => (
              <div key={idx} style={{ border: "1px solid #f0f0f0", borderRadius: 10, padding: 10 }}>
                <div style={{ fontWeight: 600 }}>{b.task_id} {b.chunk_count ? `(chunk ${Number(b.chunk_index)+1}/${b.chunk_count})` : ""}</div>
                <div style={{ fontSize: 12, color: "#555" }}>{b.start_at} → {b.end_at}</div>
                <div style={{ fontSize: 12, color: "#777" }}>{(b.explain_tags || []).join(", ")}</div>
              </div>
            ))}
            {blocks.length === 0 ? <div style={{ color: "#777", fontSize: 13 }}>No proposal yet.</div> : null}
          </div>
        </div>
      </div>
    </div>
  );
}
