/* clines-config.h for the Asciiverse build (asciiverse/build.sh), in
 * place of the one configure writes: every target here is a current Unix
 * with the same answers. GPM (the Linux console mouse) is built in only
 * when build.sh is run with GPM=1, which defines HAVE_GPM itself. */
#ifndef CLINES_CONFIG_H
#define CLINES_CONFIG_H

#define PACKAGE_NAME	"clines"
#define PACKAGE_TARNAME	"clines"
#define PACKAGE_VERSION	"1.0.4"
#define PACKAGE_STRING	"clines 1.0.4"
#define PACKAGE_BUGREPORT "Pawel.Veselov@gmail.com"

#define ALLOW_HI_SCORES	1
#define HAVE_CMOUSE	1	/* curses mouse (xterm and the like) */
#define CURSES_CURSES	1	/* <curses.h> */

#define HAVE_CTYPE_H	1
#define HAVE_DIRENT_H	1
#define HAVE_FCNTL_H	1
#define HAVE_INTTYPES_H	1
#define HAVE_MEMORY_H	1
#define HAVE_NETINET_IN_H 1
#define HAVE_PWD_H	1
#define HAVE_SIGNAL_H	1
#define HAVE_STDARG_H	1
#define HAVE_STDINT_H	1
#define HAVE_STDIO_H	1
#define HAVE_STDLIB_H	1
#define HAVE_STRINGS_H	1
#define HAVE_STRING_H	1
#define HAVE_SYS_STAT_H	1
#define HAVE_SYS_TIME_H	1
#define HAVE_SYS_TYPES_H 1
#define HAVE_TERM_H	1
#define HAVE_TIME_H	1
#define HAVE_UNISTD_H	1
#define STDC_HEADERS	1
#define TIME_WITH_SYS_TIME 1

#ifdef HAVE_GPM
#define HAVE_GPM_H	1
#define HAVE_LIBGPM	1
#endif

#endif
