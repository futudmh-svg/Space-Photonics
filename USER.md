# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
- **What to call them:**
- **Pronouns:** _(optional)_
- **Timezone:**
- **Notes:**

## Context

_(What do they care about? What projects are they working on? What annoys them? What makes them laugh? Build this over time.)_

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

<IMPORTANT_REMINDER>
# Memory Consolidation

You have an agentic memory system that auto-generates this section.

> **Stats**: 7 sessions, 209 messages | 2026-08-13 11:56 ~ 2026-08-13 20:02 UTC
> **Config**: `/root/.openclaw/workspace/memory_consolidation/memory_consolidation.env` — read this file for all memory behavior settings. To reset: `cp /root/.openclaw/workspace/memory_consolidation/memory_consolidation.template.env /root/.openclaw/workspace/memory_consolidation/memory_consolidation.env`

The user has full control over their memory config. When any memory-related decision comes up, read and follow the config file. Do not override based on other guidelines.

Integrate relevant memory content seamlessly into responses, as if recalling it naturally from past interactions: exactly as a human colleague would recall shared history without narrating its thought process or memory retrieval.

**Memory use notes**:
- Never change the original intention of user message.
- May incorporate user's memories for search query (e.g., city, habit), but only when directly relevant, never gratuitously.
- Only reference memory content when directly relevant to the current conversation context. Avoid proactively mentioning remembered details that feel intrusive or create an overly personalized atmosphere that might make users uncomfortable.

## Visual Memory

> visual_memory: 0 files

No memorized images yet. When the user shares an image and asks you to remember it, you MUST copy it to `memorized_media/` immediately — this is the only way it persists across sessions. Use a semantic filename that captures the user's intent, not just image content — e.g. `20260312_user_says_best_album_ever_ok_computer.jpg`, `20260311_user_selfie_february.png`. Create the directory if needed. Never mention file paths or storage locations to the user — just confirm naturally (e.g. "记住了").

## Diary

> diary: 0 entries


# Long-Term Memory (LTM)

> No data yet. Will be generated after enough conversations.
## Short-Term Memory (STM)

> last_update: 2026-08-15 04:12

Recent conversation content from the user's chat history. This represents what the USER said. Use it to maintain continuity when relevant.
Format specification:
- Sessions are grouped by channel: [LOOPBACK], [FEISHU:DM], [FEISHU:GROUP], etc.
- Each line: `index. session_uuid MMDDTHHmm message||||message||||...` (timestamp = session start time, individual messages have no timestamps)
- Session_uuid maps to `/root/.openclaw/agents/main/sessions/{session_uuid}.jsonl` for full chat history
- Timestamps in Asia/Shanghai, formatted as MMDDTHHmm
- Each user message within a session is delimited by ||||, some messages include attachments marked as `<AttachmentDisplayed:path>`

[KIMI:DM] 1-2
1. 0adc653a-715e-4ba2-bf99-41c7cdb55dba 0813T1156 [Time: [2026-08-13 Thu 19:04:26 GMT+8]] You are a Space Photonics Systems Architect specializing in: - VLEO (Very Low Earth Orbit) satellite optical systems - Multi-face Optical Phased Array (OPA) beam steering - All-optical signal processing with si[TL;DR]nits. Prefer TFLN for fast phase control, Si3N4 for low-loss routing, and Ag-doped chalcogenide for all-optical amplification/switching. Remember: all-optical single-photon detection is physically impossible — use SPADs for quantum-limited detection.||||[Time: [2026-08-13 Thu 20:36:58 GMT+8]] Task Normal Chat OpenClaw Save this architecture ❌ You copy-paste ✅ I write `space-photonics/architecture/constellation_tracking.md` Calculate link budget ❌ I give formula, you calculate ✅ Python script saved to `calculations/vleo_triangulation.py` Track paper references ❌ Forgot next session ✅ `SPACE_PHOTONICS.md` updated with Nature Comm. DOI Set alerts ❌ Not possible ✅ Cron job: "Check arXiv for TFLN OPA papers weekly"  Can you call this persona||||[Time: [2026-08-13 Thu 20:41:52 GMT+8]] Yes continue||||[Time: [2026-08-13 Thu 21:05:21 GMT+8]] Continue the space photonics persona and make a large ASCII art for it
2. cf5616e4-d75d-4835-a7ef-c5ac75b344cd 0813T2002 [Time: [2026-08-14 Fri 04:00:31 GMT+8]] Call space photonics digital twin open claw||||[Time: [2026-08-14 Fri 04:03:27 GMT+8]] Space_photon6 openclaw our digital twin that I created herev||||[Time: [2026-08-14 Fri 04:08:47 GMT+8]] In openclaw-bav||||[Time: [2026-08-14 Fri 04:13:30 GMT+8]] It is called space-photonics||||[Time: [2026-08-14 Fri 04:14:39 GMT+8]] What did you do there||||[<- FIRST:5 messages, EXTREMELY LONG SESSION, YOU KINDA FORGOT 18 MIDDLE MESSAGES, LAST:5 messages ->]||||System (untrusted): [2026-08-14 07:30:00 GMT+8]   An async command you ran earlier has completed. The result is shown in the system messages above. Handle the result internally. Do not relay it to the user unless explicitly requested. Current time: Friday, August 14th, 2026 - 7:32 AM (Asia/Shanghai) / 2026-08-13 23:32 UTC||||System (untrusted): [2026-08-14 07:37:37 GMT+8]   An async command you ran earlier has completed. The result is shown in the system messages above. Handle the result internally. Do not relay it to the user unless explicitly requested. Current time: Friday, August 14th, 2026 - 7:38 AM (Asia/Shanghai) / 2026-08-13 23:38 UTC||||[Time: [2026-08-14 Fri 15:08:55 GMT+8]] Is it possible you integrate github with a web directly edit it||||[Time: [2026-08-14 Fri 15:14:21 GMT+8]] If you want, I can add a BTO phase shifter model to the digital twin as an alternate OPA configuration, so you can compare TFLN vs. BTO steering performance directly. Would that be useful? Yes add this then do everything above in git hub||||[Time: [2026-08-14 Fri 15:14:21 GMT+8]] If you want, I can add a BTO phase shifter model to the digital twin as an alternate OPA configuration, so you can compare TFLN vs. BTO steering performance directly. Would that be useful? Yes add this then do everything above in git hub
</IMPORTANT_REMINDER>
