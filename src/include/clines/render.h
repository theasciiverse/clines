/*
 * file: $RCSfile: render.h,v $
 * author: Pawel S. Veselov
 * created: 2002/10/07
 * last modified: $Date: 2006/08/28 20:23:12 $
 * version: $Revision: 1.7 $
 */

#ifndef _CLINES_RENDER_H_
#define _CLINES_RENDER_H_

// #define GETCH_DELAY 200

struct board;

void render(struct board *);
void rinit(struct board *, int);
void rfini();
void rborder(struct board *);
void render1(struct board *, int, int);
void rscore(struct board *);
void rgo(struct board *);

#ifdef HAVE_GPM
extern Gpm_Event * latest_gpm_event;
#endif

extern int r_can_render;
extern int r_ox, r_oy;     /* where the board starts on the screen */
extern int r_has_color;

#endif
