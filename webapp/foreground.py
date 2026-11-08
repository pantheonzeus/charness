"""The quick voice in front of the Chief of Staff: a fast agent keeps the conversation going while the slow one works.

The main session's first spoken sentence comes 2.4–4.3 s after you stop talking (README, Voice). A warm Haiku
session hears the same request and says in a few words what is being done with it ("Looking up the latest on the
renewal."), ~1 s after the transcript (measured 2026-11-08: 1.02–1.08 s warm, 2.2 s on a cold session's first turn,
hence warm()). It never answers: no fact, number, time or name the user didn't say. Whichever is ready first is
said first; an acknowledgement that loses the race is dropped (server.py Conversation.acknowledge).
"""
import asyncio
import json
import tempfile

MODEL = "haiku"
WAIT_S = 2.0      # later than this, the main reply is about to start and the acknowledgement is no use
RESTART = 40      # turns before a fresh session, so the history it carries stays small
SKIP = "-"
PROMPT = """You are the quick voice in front of a slower assistant. The user just spoke; the assistant behind you is working on it.
Reply with one short spoken sentence, at most eight words, that says what is being done with the request, like "Pulling up your afternoon." or "Looking at the mail from Acme."
Never answer, never state a fact, number, time or name the user didn't say, never ask a question.
If the request needs no acknowledgement (thanks, stop, yes, no, a greeting, small talk, or a short answer to a question), reply with exactly: -"""


class Foreground:
    def __init__(self, env):
        self.env, self.proc, self.turns = env, None, 0
        self.lock = asyncio.Lock()

    async def _ask(self, text):
        if self.proc is None or self.proc.returncode is not None or self.turns >= RESTART:
            await self.close()
            self.proc = await asyncio.create_subprocess_exec(
                "claude", "-p", "--model", MODEL, "--input-format", "stream-json", "--output-format", "stream-json",
                "--verbose", "--tools", "", "--setting-sources", "user", "--strict-mcp-config", "--no-session-persistence",
                "--system-prompt", PROMPT, cwd=tempfile.gettempdir(), env=self.env,   # outside the repo: no CLAUDE.md, no hooks
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            self.turns = 0
        self.turns += 1
        self.proc.stdin.write((json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n").encode())
        await self.proc.stdin.drain()
        async for raw in self.proc.stdout:
            ev = json.loads(raw)
            if ev.get("type") == "result":
                return "" if ev.get("is_error") else ev.get("result") or ""
        raise OSError("foreground session ended")

    async def ack(self, text):
        """One short sentence for what was asked, or None (nothing to acknowledge, too slow, or the session failed)."""
        async with self.lock:
            try:
                out = (await asyncio.wait_for(self._ask(text), WAIT_S)).strip()
            except (asyncio.TimeoutError, OSError, ValueError):
                await self.close()                # a reply still in flight would answer the next request
                return None
        return None if not out or out == SKIP or len(out.split()) > 12 else out

    async def warm(self):
        """The first turn of a new session is twice as slow: spend it before anyone is waiting."""
        async with self.lock:
            try:
                await asyncio.wait_for(self._ask("yes"), 30)
            except (asyncio.TimeoutError, OSError, ValueError):
                await self.close()

    async def close(self):
        p, self.proc = self.proc, None
        if p and p.returncode is None:
            try:
                p.terminate()
                await asyncio.wait_for(p.wait(), 5)
            except (asyncio.TimeoutError, ProcessLookupError):
                try:
                    p.kill()
                except ProcessLookupError:
                    pass
