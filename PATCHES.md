# Changes from upstream

This is the Asciiverse packaging of Console Lines 1.0.4, Pawel S.
Veselov's curses version of Color Lines (C, 2002 to 2006): move chips on
a 9x9 board to line up five of a colour before the board fills. 1.0.4
(2006-10-08) is the last release; its home, manticore.2y.net, is gone.

History here starts from the release tarball (clines-1.0.4.tar.bz2,
sha256 4fc55ceacde15cc67e7376cdb09106cd3d14aea8892153c00481bd8ebe06f7a9),
unchanged, tagged `1.0.4`. The copy is from OpenBSD's distfiles mirror
(ftp.openbsd.org/pub/OpenBSD/distfiles/); OpenBSD's games/clines port
pins that sha256, and the tree ALT Linux keeps in its packaging repo is
file for file the same.

## Licence

COPYING is the GPL version 2; the source files carry no licence notice,
and the README and man page do not name one. ALT's spec says GPL-2,
OpenBSD's port says GPL. The catalog says GPL-2.0-only, the version
shipped.

## Distribution patches

ALT Linux (git.altlinux.org/gears/c/clines.git, the `altlinux` remote,
tags not fetched) carries one patch file,
clines-1.0.4-alt-makefile-strange_command_fix.patch, here as its two
parts with their authors, tagged `altlinux/1.0.4-alt5`:

- Makefile.am (Slava Semushin, 1.0.4-alt1, 2006): the install no longer
  makes the score folder root-owned and world-writable (chown 0, chmod
  1777) or puts data/version1 in it.
- src/gameplay.c (Fr. Br. George, 1.0.4-alt5, 2026-04-25): builds with
  GCC 15 (resume_timer() takes no argument; the GPM read through
  Gpm_Wgetch()).

OpenBSD's port (games/clines) has two patches, patch-Makefile_in and
patch-configure, doing the same for its install (no chown or chmod, and
the scores in /var/games/clines); they are not applied, since the build
here does not use configure and the scores moved to the player's folder.

## Ours

- **Scores in the player's own folder.** Scores were one file per user in
  a shared folder (CLINES_DATA_DIR, /var/tmp by default). They now go in
  `$XDG_DATA_HOME/clines` (else `~/.local/share/clines`); the shared
  folder only when there is no home. The man page says so. Starting
  without a user name (getpwuid() failing, as in some containers) no
  longer crashes in strchr().
- **No curses in signal handlers.** The selected chip jumped from a
  SIGALRM timer whose handler drew with curses, and SIGWINCH's handler
  ran endwin() and initscr() again. The move loop now waits for a key
  with a 200 ms timeout and moves the chip in between, and takes
  KEY_RESIZE from curses, laying the board out again; a too-small
  terminal waits for a resize (or q).
- **Board centred.** The board grows with the terminal but sat in the top
  left corner; it is centred now (render.c draws through an origin), and
  mouse clicks are taken relative to it.
- **Score file.** The record is written in one checked call, and the path
  is freed (LeakSanitizer); two warnings fixed.
- **GPM optional and only on the console.** The build leaves GPM (the
  Linux console mouse, a shared library and a daemon) out unless
  `GPM=1`, so the static release builds have none; the terminal mouse
  works through curses either way. Built with GPM, the game called
  Gpm_Open() in any terminal, and in a terminal emulator the Gpm_Close()
  after libgpm's xterm answer switched the terminal's mouse reports off
  (checked in tmux), so clicks never arrived. GPM is now tried only when
  TERM is a Linux console, and the curses mouse is switched on again
  after an xterm answer. The GPM read passes its WINDOW * through a cast
  to Gpm_Wgetch's real prototype, which gpm.h leaves out.

Windows: not built. The game is plain curses now (no signals or timers),
so PDCurses would mostly do; what remains is getpwuid() for the score
file's name (the user name from the environment instead) and mkdir()'s
mode argument.
- **How to play it, at the top of README.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.

## Packaging (new files)

- `asciiverse/clines-config.h`, `asciiverse/build.sh`: one compiler call
  with a fixed config header instead of configure; `GPM=1` adds GPM.
- `asciiverse/package.sh`: one archive per target with the binary, the
  man page, README, COPYING and this file.
- `asciiverse/record-preview.py`, `asciiverse/clines.cast`: the catalog
  preview (100x30, 47 s) and the player that recorded it, reading the
  board's colours through pyte and playing with xterm (SGR) mouse
  clicks: each move is the one that makes the longest line.
- `.github/workflows/release.yml`: static Linux in Alpine (x86_64,
  aarch64, no GPM) and macOS (x86_64, arm64), plus SHA256SUMS, on a tag.
