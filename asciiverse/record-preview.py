"""Records Console Lines' catalog preview (hub/RECORDING.md): 100x30, about 50 s.

Runs the game under `asciinema rec` in a 100x30 pseudo-terminal, reads the
board through pyte (each chip's colour) and plays with the mouse, as xterm
reports it (SGR mouse reports): for every chip and every free cell it can
reach it works out the line that move would make, takes the longest
(five in a row clears them), and clicks the chip, then the cell. At the
end it quits. Usage, from the repo root after asciiverse/build.sh (the
binary in out/), with pyte installed:

    python3 asciiverse/record-preview.py

The game runs by name from out/ on PATH, so the cast's header holds no local
path. The cast goes to asciiverse/clines.cast.
"""
import fcntl, os, pty, random, re, select, shutil, struct, sys, tempfile, termios, time

import pyte

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLS, ROWS = 100, 30
N = 9                            # the board is 9x9 (the default)
LENGTH = 46.0                    # seconds of play before quitting

random.seed(3)

# ncurses repeats a character with REP (CSI n b) and scrolls part of the
# screen with SU and SD (CSI n S, CSI n T), which pyte does not know
_draw = pyte.Screen.draw


def _draw_remembering(self, data):
    if data:
        self.last_char = data[-1]
    _draw(self, data)


def _repeat_last(self, n=1, *rest, **kw):
    if getattr(self, "last_char", None):
        _draw(self, self.last_char * max(1, n))


def _scroll_up(self, n=1, *rest, **kw):
    """SU (CSI n S), which ncurses uses inside a scroll region."""
    top, bottom = self.margins or pyte.screens.Margins(0, self.lines - 1)
    for _ in range(max(1, n)):
        for y in range(top, bottom):
            self.buffer[y] = self.buffer[y + 1]
        self.buffer.pop(bottom, None)
    self.dirty.update(range(self.lines))


def _scroll_down(self, n=1, *rest, **kw):
    """SD (CSI n T)."""
    top, bottom = self.margins or pyte.screens.Margins(0, self.lines - 1)
    for _ in range(max(1, n)):
        for y in range(bottom, top, -1):
            self.buffer[y] = self.buffer[y - 1]
        self.buffer.pop(top, None)
    self.dirty.update(range(self.lines))


pyte.Screen.draw = _draw_remembering
pyte.Screen.repeat_last = _repeat_last
pyte.Screen.scroll_up = _scroll_up
pyte.Screen.scroll_down = _scroll_down
pyte.Stream.csi = dict(pyte.Stream.csi, b="repeat_last", S="scroll_up", T="scroll_down")


class Rec:
    def __init__(self):
        self.home = tempfile.mkdtemp(prefix="clines-rec-")
        env = {
            "PATH": f"{os.path.join(ROOT, 'out')}:{os.environ['PATH']}",
            "HOME": self.home,
            "XDG_DATA_HOME": os.path.join(self.home, "data"),
            "USER": "player",
            "LOGNAME": "player",
            "TERM": "xterm-256color",
            "COLORTERM": "truecolor",
            "LANG": "C.UTF-8",
        }
        self.cast = os.path.join(ROOT, "asciiverse", "clines.cast")
        self.screen = pyte.Screen(COLS, ROWS)
        self.stream = pyte.ByteStream(self.screen)
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.chdir(self.home)
            os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "--idle-time-limit", "2",
                "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
                "--title", "Console Lines", "--command", "clines", self.cast], env)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
        self.start = time.time()

    def pump(self, t):
        end = time.time() + t
        while True:
            left = end - time.time()
            r, _, _ = select.select([self.fd], [], [], max(0.0, min(0.01, left)))
            if r:
                try:
                    self.stream.feed(os.read(self.fd, 65536))
                except OSError:
                    return False
            if left <= 0:
                return True

    def key(self, k, wait=0.0):
        os.write(self.fd, k.encode() if isinstance(k, str) else k)
        self.pump(wait)

    def type(self, text, gap=0.12):
        for ch in text:
            self.key(ch, gap)

    def text(self):
        return "\n".join(self.screen.display)

    def finish(self):
        end = time.time() + 5
        while time.time() < end:
            if not self.pump(0.1):
                break
            done, _ = os.waitpid(self.pid, os.WNOHANG)
            if done:
                break
        else:
            os.kill(self.pid, 9)    # SIGKILL: nothing more is written to the cast
        try:
            os.waitpid(self.pid, 0)
        except ChildProcessError:
            pass
        shutil.rmtree(self.home, ignore_errors=True)
        print(f"{self.cast}: {os.path.getsize(self.cast) // 1024} KB, {time.time() - self.start:.0f} s",
              file=sys.stderr)




def geometry():
    """Cell size and the board's origin, as rinit() in render.c works them out."""
    s = min((COLS - 1) // N, (ROWS - 1) // N)
    return s, (ROWS - (s * N + 1)) // 2, (COLS - (s * N + 1)) // 2


def board(rec):
    """grid[y][x]: a chip's colour name, or None."""
    s, oy, ox = geometry()
    buf = rec.screen.buffer
    grid = [[None] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            for dy in range(s - 1):
                for dx in range(s - 1):
                    ch = buf[oy + y * s + 1 + dy][ox + x * s + 1 + dx]
                    if ch.data not in " " and ch.fg not in ("default", "white"):
                        grid[y][x] = ch.fg
    return grid


def reach(grid, sx, sy):
    seen, todo = {(sx, sy)}, [(sx, sy)]
    while todo:
        x, y = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N and (nx, ny) not in seen and grid[ny][nx] is None:
                seen.add((nx, ny))
                todo.append((nx, ny))
    seen.discard((sx, sy))
    return seen


def line_at(grid, x, y, colour):
    best = 1
    for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
        n = 1
        for sgn in (1, -1):
            cx, cy = x + dx * sgn, y + dy * sgn
            while 0 <= cx < N and 0 <= cy < N and grid[cy][cx] == colour:
                n += 1
                cx, cy = cx + dx * sgn, cy + dy * sgn
        best = max(best, n)
    return best


def best_move(grid):
    best = None
    for y in range(N):
        for x in range(N):
            c = grid[y][x]
            if not c:
                continue
            stay = line_at(grid, x, y, c)
            grid[y][x] = None
            for tx, ty in reach(grid, x, y):
                v = line_at(grid, tx, ty, c) * 10 - stay * 6 + random.random()
                if best is None or v > best[0]:
                    best = (v, (x, y), (tx, ty))
            grid[y][x] = c
    return best


def click(rec, x, y):
    """Press and release the left button on cell (x, y), as xterm's SGR mode reports it."""
    s, oy, ox = geometry()
    col = ox + x * s + 1 + (s - 1) // 2 + 1        # 1-based for the report
    row = oy + y * s + 1 + (s - 1) // 2 + 1
    rec.key(f"\x1b[<0;{col};{row}M", 0.05)
    rec.key(f"\x1b[<0;{col};{row}m", 0.1)


def main():
    rec = Rec()
    rec.pump(1.5)
    end = rec.start + LENGTH
    last, still = None, 0.0
    while time.time() < end:
        rec.pump(0.1)
        if "Game over" in rec.text():
            break
        g = board(rec)
        if g != last:
            last, still = g, time.time()
            continue
        if time.time() - still < 0.5:              # chips still moving or arriving
            continue
        m = best_move(g)
        if not m:
            break
        _, (x, y), (tx, ty) = m
        click(rec, x, y)
        rec.pump(0.7)                               # it jumps while selected
        click(rec, tx, ty)
        last = None
    rec.pump(1.0)
    rec.key("q", 0.5)
    rec.key(" ", 0.5)
    rec.finish()


if __name__ == "__main__":
    main()
