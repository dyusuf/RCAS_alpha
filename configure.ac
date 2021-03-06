dnl -*- Autoconf -*-

AC_INIT(RCAS, 0.0.0)
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([color-tests -Wall -Wno-portability foreign])
AM_SILENT_RULES([yes])

# Load Python support for Automake and ensure we have a Python
# interpreter for at least version 3.  This sets the "PYTHON"
# variable.
# https://www.gnu.org/software/automake/manual/html_node/Python.html
AM_PATH_PYTHON([3])

# Check for any variant of "awk" and store path in "AWK" variable
AC_PROG_AWK
AC_PROG_SED

AC_ARG_VAR(SNAKEMAKE, override location of "snakemake" executable)
AC_ARG_VAR(BASH, override location of "bash" executable)
AC_ARG_VAR(BEDTOOLS, override location of "bedtools" executable)
AC_ARG_VAR(FASTA_FROM_BED, override location of "fastaFromBed" executable)
AC_ARG_VAR(MEME_CHIP, override location of "meme-chip" executable)
AC_ARG_VAR(PANDOC, override location of "pandoc" executable)
AC_ARG_VAR(RSCRIPT, override location of "Rscript" executable)
AC_ARG_VAR(R, override location of "R" executable)

# Check for required programmes and store their full path in the given
# variables.  The variables are used to substitute placeholders in the
# scripts such as RCAS.snakemake.
AS_IF([test -z "$SNAKEMAKE"],
      [AC_PATH_PROG([SNAKEMAKE], [snakemake])],
      [AC_MSG_NOTICE([Using $SNAKEMAKE as snakemake executable.])])
AS_IF([test -z "$BASH"],
      [AC_PATH_PROG([BASH], [bash])],
      [AC_MSG_NOTICE([Using $BASH as bash executable.])])
AS_IF([test -z "$BEDTOOLS"],
      [AC_PATH_PROG([BEDTOOLS], [bedtools])],
      [AC_MSG_NOTICE([Using $BEDTOOLS as bedtools executable.])])
AS_IF([test -z "$FASTA_FROM_BED"],
      [AC_PATH_PROG([FASTA_FROM_BED], [fastaFromBed])],
      [AC_MSG_NOTICE([Using $FASTA_FROM_BED as fastaFromBed executable.])])
AS_IF([test -z "$MEME_CHIP"],
      [AC_PATH_PROG([MEME_CHIP], [meme-chip])],
      [AC_MSG_NOTICE([Using $MEME_CHIP as meme-chip executable.])])
AS_IF([test -z "$PANDOC"],
      [AC_PATH_PROG([PANDOC], [pandoc])],
      [AC_MSG_NOTICE([Using $PANDOC as pandoc executable.])])
AS_IF([test -z "$RSCRIPT"],
      [AC_PATH_PROG([RSCRIPT], [Rscript])],
      [AC_MSG_NOTICE([Using $RSCRIPT as Rscript executable.])])
AS_IF([test -z "$R"],
      [AC_PATH_PROG([R], [R])],
      [AC_MSG_NOTICE([Using $R as R executable.])])

AC_DEFUN([AX_TEST_R_PACKAGE], [
    pushdef([PKG],$1)
    AC_MSG_CHECKING([for R package "PKG"])
    TEST=$( R --silent --vanilla -e 'if(!require("PKG")) stop("not found")' 2>/dev/null )
    AS_IF([test $? != 0],
          [AC_MSG_ERROR([R package PKG could not be loaded])],
          [AC_MSG_RESULT([OK])])
    popdef([PKG])
])

if test "x$R" == x
then
  AC_MSG_ERROR([R could not be found, so we cannot test for R packages.])
else
  AX_TEST_R_PACKAGE([genomation])
  AX_TEST_R_PACKAGE([data.table])
  AX_TEST_R_PACKAGE([biomaRt])
  AX_TEST_R_PACKAGE([org.Hs.eg.db])
  AX_TEST_R_PACKAGE([org.Ce.eg.db])
  AX_TEST_R_PACKAGE([org.Dm.eg.db])
  AX_TEST_R_PACKAGE([org.Mm.eg.db])
  AX_TEST_R_PACKAGE([topGO])
  AX_TEST_R_PACKAGE([DT])
  AX_TEST_R_PACKAGE([plotly])
  AX_TEST_R_PACKAGE([dplyr])
  AX_TEST_R_PACKAGE([GenomicFeatures])
  AX_TEST_R_PACKAGE([rtracklayer])
  AX_TEST_R_PACKAGE([rmarkdown])
fi

# Substitute placeholders to generate these target files
AC_CONFIG_FILES([Makefile                     \
                 src/RCAS.snakefile           \
                 src/RCAS.anot.snakefile      \
                 src/RCAS.GOrich.snakefile    \
                 src/RCAS.motif.snakefile     \
                 src/RCAS.PATHrich.snakefile  \
                 src/generate_report.sh])

basedir="$datadir/RCAS/base"
AC_SUBST([basedir])

# Create wrapper for snakemake.  This wrapper is appended to at "make"
# time, so we keep the ".in" ending.
AC_CONFIG_FILES([src/RCAS.in], [chmod +x src/RCAS.in])

AC_OUTPUT
