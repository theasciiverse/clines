/*
 * file: $RCSfile: play.h,v $
 * author: Pawel S. Veselov
 * created: 2002/10/06
 * last modified: $Date: 2006/07/09 07:47:59 $
 * version: $Revision: 1.4 $
 */

#ifndef _CLINES_PLAY_H_
#define _CLINES_PLAY_H_

struct board;

void play(struct board *);

#ifdef HAVE_GPM
int my_gpm_handler(Gpm_Event *, void *);
#endif

extern struct board * c_board;

#endif
