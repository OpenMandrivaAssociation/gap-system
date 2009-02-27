%define gapbin		gap
%define gapdir		%{_datadir}/%{gapbin}
%define gappkgdir	%{gapdir}/pkg
%define gapprg		%{_arch}/%{gapbin}
%define gapprgdir	%{gapdir}/bin/%{_arch}

Name:		gap-system
Summary:	GAP is a system for computational discrete algebra
Version:	4.4.12
Release:	%mkrel 1

# FIXME: check gap4r4/pkg/openmath/OMCv1.3c/src/copyright
# used in the opemath package, and linked statically
License:	GPL
Group:		Sciences/Mathematics
Source0:	ftp://ftp.gap-system.org/pub/gap/gap44/tar.bz2/gap4r4p12.tar.bz2

# Alnut requires kant (http://www.math.tu-berlin.de/~kant/kash.html)
# OpenMath (External needs: This package can be useful only with other applications that support OpenMath)
# singular requires singular (http://www.singular.uni-kl.de/)
Source1:	ftp://ftp.gap-system.org/pub/gap/gap4/tar.bz2/packages-2009_02_18-11_42_UTC.tar.bz2

Source2:	XGap

URL:		http://www.gap-system.org

BuildRequires:	libgmp-devel
BuildRequires:	libncurses-devel
BuildRequires:	libxaw-devel
BuildRequires:	p2c-devel

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

Patch0:		gap-Werror=format-security.patch

%description
GAP is a system for computational discrete algebra, with particular
emphasis on Computational Group Theory. GAP provides a  programming
language, a library of thousands of functions implementing algebraic
algorithms written in the GAP language as well as large data libraries
of algebraic objects. See also the overview and the description of the
mathematical capabilities. GAP is used in research and teaching for
studying groups and their representations, rings, vector spaces,
algebras, combinatorial structures, and more.

%package	packages
Group:		Science/Mathematics
Summary:	Optional gap packages
Requires:	%{name}
Requires:	tcl
Requires:	tk
Requires:	curl
Requires:	graphviz
Requires:	evince
Requires:	linalg-linbox
Requires:	polymake

%description	packages
Since 1992, sets of user contributed programs, called packages, have
been distributed with GAP. For convenience of the GAP users, the GAP
Group redistributes packages, but the package authors remain responsible
for their maintenance. 
Some packages represent a piece of work equivalent to a sizeable
mathematical publication. To acknowledge such work there has been a
refereeing process for packages since 1996.
Please refer to http://www.gap-system.org/Packages/packages.html
for more information.

%prep
%setup -q -n gap4r4

# unpack packages in pkg directory
pushd pkg
  bzip2 -dc %{SOURCE1} | tar -xf -
  pushd carat
    tar zxf carat-2.1b1.tgz
    for f in carat-2.1b1/{functions,include,info,lib,src,tables,tex}; do
      ln -sf $f .
    done
  popd
popd

%patch0	-p1

%build
# remove cygwin binaries
rm -fr bin/*

perl -pi							\
	-e 's|\@target\@-\@BASECC\@|%{_arch}|g;'		\
	-e 's|\@target\@-\@CC\@|%{_arch}|g;'			\
	-e 's|\@gapdir\@|%{gapdir}|;'				\
	Makefile.in gap.shi sysinfo.in

%configure
%make

# build packages that needs arch specific processing
pushd pkg

# only (optional) argument is GAPPATH
%define pkg_configure	./configure ../..

  # there are some cygwin binaries and one sparc directory tree
  rm -fr */bin

  for f in `find . -mindepth 1 -a -maxdepth 1 -type d`; do
    ln -sf ../../bin $f
  done

  pushd ace
    %{pkg_configure}
    # "make builddoc otherdoc" is broken
    make default
  popd

  pushd anupq
    %{pkg_configure}
    # gcc2 to gcc4 doesn't matter here...
    # GNU{INC,LIB} is where libgmp headers/libraries are found
    make							\
	GAP=../../../bin/%{_arch}/gap				\
	linux-iX86-gcc2-gmp					\
	GNUINC=%{_includedir}					\
	GNULIB=%{_libdir}
  popd

  pushd Browse
    %{pkg_configure}
    make default
  popd

# FIXME this most likely will generate incorrect binaries, as
# CFLAGS was set to include -fwritable-strings, but this option
# is not supported by gcc 4 anymore.
# Need to patch sources to ensure it makes copies of any literal
# strings it may attempt to overwrite.
%define carat_global GLOBAL=\'-DTOPDIR=\\\"%{gapdir}\\\" -DTABLES=\\\"%{gapdir}/tables/\\\" -DATOMS=\\\"%{gapdir}/tables/atoms/\\\" -DTABLEDIM=\\\"%{gapdir}/tables/dim\\\"\'
  pushd carat
    pushd functions
      for dir in `find . -mindepth 1 -maxdepth 1 -type d`; do
	pushd $dir
	  make							\
		TOPDIR=../..					\
		CFLAGS=-DDIAG1					\
		%{carat_global}					\
		ALL
	popd
      done
    popd
    pushd lib
      mv functions.a libfunctions.a
      for lib in lib*.a; do ranlib $lib; done
    popd
    pushd tables/symbol
      make ALL
    popd
%define carat_top	../../pkg/carat
    pushd bin/%{_arch}
	make -f %{carat_top}/carat-2.1b1/bin/Makefile		\
		CFLAGS=-DDIAG1					\
		TOPDIR=%{carat_top}				\
		%{carat_global}					\
		PROGRAMS
    popd
  popd

  pushd cohomolo
    %{pkg_configure}
    make
  popd

  pushd edim
    %{pkg_configure}
    make
  popd

  pushd example
    %{pkg_configure}
    make
  popd

  pushd fplsa
    %{pkg_configure}
    # "make manual" target is broken; but probably could use
    # convert.pl from other packages...
    make
  popd

  pushd fr
    make							\
	GAPPATH=../..
	LOCALBIN=bin/%{_arch}
  popd

  pushd grape
    %{pkg_configure}
    make binaries others
  popd

  pushd guava3.9
    %{pkg_configure}
    make
  popd

  pushd Hap1.8
    perl -pi							\
	-e 's|(^PKGDIR=).*|$1..|;'				\
	-e 's|(^GACDIR=).*|$1bin/%{_arch}|;'			\
	compile.sh
    sh ./compile.sh
    perl -pi							\
	-e 's|^#\!/usr/local/bin/perl|#!%{_bindir}/perl|;'	\
	lib/TDA/prog lib/TopologicalSpaces/prog
  popd

  pushd io
    %{pkg_configure}
    # Don't attempt to copy config.h to itself...
    perl -pi							\
	-e 's|(^\s+)(cp \$\(GAPPATH\)/bin/i386)|$1#$2|;'	\
	Makefile
    # "make doc" needs some tweaking, (but no need to remake?)
    make
  popd

  pushd kbmag
    # want a symbolic link, and not a sun-sparc tree
    rm -fr bin
    ln -sf ../../bin .
    %{pkg_configure}
    make
  popd

  pushd linboxing-0.5.1
    echo -n "nothing done, needs linboxing packaged"
  popd

  pushd nq-2.2
    perl -pi							\
	-e 's|\@target\@-\@BASECC\@|%{_arch}|g;'		\
	-e 's|\$\(GNU_MP_INC\)|%{_includedir}|;'		\
	-e 's|\$\(GNU_MP_LIB\)|%{_libdir}|;'			\
	Makefile.in
    # fix build due to implicit rules, and no static libc by default
    perl -pi							\
	-e 's|-static||;'					\
	-e 's|^(glimt.o)|#$1|;'					\
	-e 's|(.*-c glimt.c)|#$1|;'				\
	src/Makefile
    %configure
    make
  popd

  pushd openmath
    pushd OMCv1.3c/src
      %configure
      make
    popd
    %{pkg_configure}
    make
  popd

  pushd orb
    # only target is doc, that is up to date
    make GAP=bin/%{_arch}
  popd

  pushd pargap
    cp -f mpinu/procgroup bin/procgroup.in
    %{pkg_configure}
    # create pargap.sh target here to avoid massive patching...
    sed -e '/GAP_PRG=/ s|/gap|/pargapmpi|' bin/gap.sh > bin/pargap.sh
    # add default value for procgroup file
    perl -pi							\
	-e 's|(^{ char \*p4pg_file = ")(procgroup";)|$1%{gapdir}/$2|;'	\
	mpinu/mpi.c
    make
  popd

  pushd qaos
    %configure
    # only target is doc, that is up to date
    make
  popd

  pushd xgap
    # this is identical to the toplevel Makefile.in
    # FIXME can pass these extra files on top substitution
    perl -pi							\
	-e 's|\@target\@-\@BASECC\@|%{_arch}|g;'		\
	-e 's|\@target\@-\@CC\@|%{_arch}|g;'			\
	-e 's|\@gapdir\@|%{gapdir}|;'				\
	Makefile.in xgap.shi
    %configure
    make
    pushd src.x11
      sed							\
	-e 's|@srcdir@|.|g'					\
	-e 's|@CC@|gcc|'					\
	-e 's|^CFLAGS.*|CFLAGS=-O3 -g -I../bin/%{_arch}|'	\
	-e 's|^LDFLAGS|#LDFLAGS|'				\
	-e 's|^LIBS|#LIBS|'					\
	-e 's|^X_LIBS.*|X_LIBS = -lXaw -lXmu -lXt -lXext -lX11|'\
	-e 's|^X_CFLAGS|#X_CFLAGS|'				\
	../cnf/Makegap.in > Makefile
	make
	mv xgap ../bin/%{_arch}
    popd
  popd
popd

%install
#   gap wants to be used from it's build directory.
#   To avoid the risk of providing a broken package, only files
# that clearly don't need to be installed on a Linux setup are
# removed from the rpm packages.
#   Only the .o files in the main package should really be required,
# as gac wants them to build standalone binaries, but the other may
# be required to build binaries that actually access external packages.
mkdir -p %{buildroot}/%{_bindir}
cp -fa bin/gap.sh %{buildroot}/%{_bindir}/gap
chmod +x %{buildroot}/%{_bindir}/gap
cp -fa bin/xgap.sh %{buildroot}/%{_bindir}/xgap
cp -fa bin/pargap.sh %{buildroot}/%{_bindir}/pargap
ln -sf %{_bindir}/gap %{buildroot}/%{_bindir}/gap4

mkdir -p %{buildroot}/%{gapdir}
cp -fa bin/procgroup %{buildroot}/%{gapdir}

# bin
mkdir -p %{buildroot}/%{gapdir}/bin/%{_arch}
cp -far bin/%{_arch}/* %{buildroot}/%{gapdir}/bin/%{_arch}
pushd %{buildroot}/%{gapdir}/bin/%{_arch}
  # remaining files are required by gac to link new binaries
  rm -f config.status config.sub config.log configure ltmain*
  # gac was already used from inside buildroot
  perl -pi							\
	-e 's|(^gap_bin=).*|$1%{gapdir}|;'			\
	-e 's|GAPROOT|%{gapdir}|;'				\
	gac
popd
# guava3.9 package
cp -far bin/leon %{buildroot}/%{gapdir}/bin

# etc
mkdir -p %{buildroot}/%{_datadir}/emacs/site-lisp
cp -fa etc/emacs/* %{buildroot}/%{_datadir}/emacs/site-lisp
mkdir -p %{buildroot}/%{_datadir}/vim/indent
cp -fa etc/gap_indent.vim %{buildroot}/%{_datadir}/vim/indent
mkdir -p %{buildroot}/%{_datadir}/vim/syntax
cp -fa etc/gap.vim %{buildroot}/%{_datadir}/vim/syntax

# install full directories
cp -far grp lib prim small trans tst %{buildroot}/%{gapdir}

# pkg - install only processed or arch indendent files
cp -far pkg %{buildroot}/%{gapdir}
# leave previous version in build dir. binaries already in bin directory
pushd %{buildroot}/%{gapdir}/pkg
  rm -fr carat/carat-2.1b1* carat/tables/qcatalog.tar.gz
  rm -f */sedfile
  # remove wrong or unnecessary files
  rm -f ALLPKG PKGDIR
  rm -f happrime-0.3.2/make_tarball radiroot/.#pack-radiroot.sh
  rm -f sophus/gap/.#lienp.gi.1.5 rm -f toric1.4/.DS_Store
  rm -f HAPcryst/examples/3dimBieberbachFD.gap~
  # install doc & htm in docdir
  mkdir -p %{buildroot}/%{_docdir}/%{name}/pkg
  mv -f README.* %{buildroot}/%{_docdir}/%{name}/pkg
  for doc in `find . -name doc -o -name htm -o -name xmldoc -mindepth 2 -maxdepth 2`; do
    doc=`echo $doc | sed -e 's|^./||'`
    mkdir -p %{buildroot}/%{_docdir}/%{name}/pkg/$doc
    mv -f $doc/* %{buildroot}/%{_docdir}/%{name}/pkg/$doc
    rm -fr $doc
    ln -sf %{_docdir}/%{name}/pkg/$doc %{buildroot}/%{gappkgdir}/$doc
  done
popd

# doc - it is installed in %{_docdir}/%{name} but searched in %{_gapdir}/doc
ln -sf %{_docdir}/%{name} %{buildroot}/%{gapdir}/doc

mkdir -p %{buildroot}/%{_datadir}/X11/app-defaults
cp -fa %{SOURCE2} %{buildroot}/%{_datadir}/X11/app-defaults

# src
mkdir -p %{buildroot}/%{gapdir}/src
cp -far src/* %{buildroot}/%{gapdir}/src

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc doc/*
%{_bindir}/gap
%{_bindir}/gap4
%{_datadir}/emacs/site-lisp/*
%{_datadir}/vim/indent/*
%{_datadir}/vim/syntax/*
%dir %{gapdir}
%{gapdir}/doc
%dir %{gapdir}/grp
%{gapdir}/grp/*
%dir %{gapdir}/lib
%{gapdir}/lib/*
%dir %{gapdir}/prim
%{gapdir}/prim/*
%dir %{gapdir}/small
%{gapdir}/small/*
%dir %{gapdir}/trans
%{gapdir}/trans/*
%dir %{gapdir}/tst
%{gapdir}/tst/*
%dir %{gapdir}/src
%{gapdir}/src/*
%dir %{gappkgdir}
%dir %{gappkgdir}/tomlib
%{gappkgdir}/tomlib/*
%dir %{gapdir}/bin
%dir %{gapdir}/bin/leon
%{gapdir}/bin/leon/*
%dir %{gapprgdir}
%{gapprgdir}/gap
%{gapprgdir}/gac
%{gapprgdir}/config.h
%{gapprgdir}/Makefile
%{gapprgdir}/c_meths1.o
%{gapprgdir}/c_type1.o
%{gapprgdir}/c_oper1.o
%{gapprgdir}/c_filt1.o
%{gapprgdir}/c_random.o
%{gapprgdir}/ariths.o
%{gapprgdir}/blister.o
%{gapprgdir}/bool.o
%{gapprgdir}/calls.o
%{gapprgdir}/code.o
%{gapprgdir}/compiler.o
%{gapprgdir}/costab.o
%{gapprgdir}/cyclotom.o
%{gapprgdir}/desauto
%{gapprgdir}/dreadnautB
%{gapprgdir}/dt.o
%{gapprgdir}/dteval.o
%{gapprgdir}/exprs.o
%{gapprgdir}/finfield.o
%{gapprgdir}/float.o
%{gapprgdir}/funcs.o
%{gapprgdir}/gap.o
%{gapprgdir}/gasman.o
%{gapprgdir}/gvars.o
%{gapprgdir}/integer.o
%{gapprgdir}/intrprtr.o
%{gapprgdir}/iostream.o
%{gapprgdir}/listfunc.o
%{gapprgdir}/listoper.o
%{gapprgdir}/lists.o
%{gapprgdir}/ncurses.so
%{gapprgdir}/objcftl.o
%{gapprgdir}/objects.o
%{gapprgdir}/objfgelm.o
%{gapprgdir}/objpcgel.o
%{gapprgdir}/objscoll.o
%{gapprgdir}/objccoll.o
%{gapprgdir}/opers.o
%{gapprgdir}/permutat.o
%{gapprgdir}/plist.o
%{gapprgdir}/precord.o
%{gapprgdir}/range.o
%{gapprgdir}/rational.o
%{gapprgdir}/read.o
%{gapprgdir}/records.o
%{gapprgdir}/saveload.o
%{gapprgdir}/scanner.o
%{gapprgdir}/sctable.o
%{gapprgdir}/set.o
%{gapprgdir}/stats.o
%{gapprgdir}/streams.o
%{gapprgdir}/string.o
%{gapprgdir}/sysfiles.o
%{gapprgdir}/system.o
%{gapprgdir}/tietze.o
%{gapprgdir}/vars.o
%{gapprgdir}/vecgf2.o
%{gapprgdir}/vecffe.o
%{gapprgdir}/vec8bit.o
%{gapprgdir}/vector.o
%{gapprgdir}/weakptr.o
%{gapprgdir}/wtdist

%files		packages
%defattr(-,root,root)
%{_bindir}/xgap
%{_bindir}/pargap
%doc %{_docdir}/%{name}/pkg/README.*
%doc %{_docdir}/%{name}/pkg/*/doc
%doc %{_docdir}/%{name}/pkg/*/htm
%{gapdir}/procgroup
%{gapprgdir}/Add
%{gapprgdir}/Aut_grp
%{gapprgdir}/Bravais_catalog
%{gapprgdir}/Bravais_equiv
%{gapprgdir}/Bravais_grp
%{gapprgdir}/Bravais_inclusions
%{gapprgdir}/Bravais_type
%{gapprgdir}/Con
%{gapprgdir}/Conj_bravais
%{gapprgdir}/Conjugated
%{gapprgdir}/Conv
%{gapprgdir}/Datei
%{gapprgdir}/Elt
%{gapprgdir}/Extensions
%{gapprgdir}/Extract
%{gapprgdir}/First_perfect
%{gapprgdir}/Form_elt
%{gapprgdir}/Form_space
%{gapprgdir}/Formtovec
%{gapprgdir}/Full
%{gapprgdir}/Gauss
%{gapprgdir}/Graph
%{gapprgdir}/Idem
%{gapprgdir}/Inv
%{gapprgdir}/Invar_space
%{gapprgdir}/Is_finite
%{gapprgdir}/Isometry
%{gapprgdir}/KSubgroups
%{gapprgdir}/KSupergroups
%{gapprgdir}/Kron
%{gapprgdir}/Long_solve
%{gapprgdir}/Ltm
%{gapprgdir}/Mink_red
%{gapprgdir}/Minpol
%{gapprgdir}/Modp
%{gapprgdir}/Mtl
%{gapprgdir}/Mul
%{gapprgdir}/Name
%{gapprgdir}/Normalizer
%{gapprgdir}/Normalizer_in_N
%{gapprgdir}/Normlin
%{gapprgdir}/Orbit
%{gapprgdir}/Order
%{gapprgdir}/P_lse_solve
%{gapprgdir}/Pair_red
%{gapprgdir}/Pdet
%{gapprgdir}/Perfect_neighbours
%{gapprgdir}/Polyeder
%{gapprgdir}/Presentation
%{gapprgdir}/Q_catalog
%{gapprgdir}/QtoZ
%{gapprgdir}/Red_gen
%{gapprgdir}/Rein
%{gapprgdir}/Rest_short
%{gapprgdir}/Reverse_name
%{gapprgdir}/Rform
%{gapprgdir}/Same_generators
%{gapprgdir}/Scalarmul
%{gapprgdir}/Scpr
%{gapprgdir}/Short
%{gapprgdir}/Short_reduce
%{gapprgdir}/Shortest
%{gapprgdir}/Signature
%{gapprgdir}/Simplify_mat
%{gapprgdir}/Standard_affine_form
%{gapprgdir}/Sublattices
%{gapprgdir}/Symbol
%{gapprgdir}/TSubgroups
%{gapprgdir}/TSupergroups
%{gapprgdir}/Torsionfree
%{gapprgdir}/Tr
%{gapprgdir}/Tr_bravais
%{gapprgdir}/Trace
%{gapprgdir}/Trbifo
%{gapprgdir}/Vectoform
%{gapprgdir}/Vector_systems
%{gapprgdir}/Vor_vertices
%{gapprgdir}/ZZprog
%{gapprgdir}/Z_equiv
%{gapprgdir}/Zass_main
%{gapprgdir}/ace
%{gapprgdir}/autcos
%{gapprgdir}/autgroup
%{gapprgdir}/bool.o
%{gapprgdir}/calcpres.gap
%{gapprgdir}/cohomology.gap
%{gapprgdir}/coladjg4t
%{gapprgdir}/compstat.o
%{gapprgdir}/conrun
%{gapprgdir}/cpoly.o
%{gapprgdir}/crrun
%{gapprgdir}/drcanon4
%{gapprgdir}/drtogap4
%{gapprgdir}/ediv.so
%{gapprgdir}/egrun
%{gapprgdir}/enum4
%{gapprgdir}/enum4ca
%{gapprgdir}/execcmd.gap
%{gapprgdir}/extprun
%{gapprgdir}/float.o
%{gapprgdir}/fplsa4
%{gapprgdir}/fsaand
%{gapprgdir}/fsaandnot
%{gapprgdir}/fsabfs
%{gapprgdir}/fsaconcat
%{gapprgdir}/fsacount
%{gapprgdir}/fsaenumerate
%{gapprgdir}/fsaexists
%{gapprgdir}/fsafilter
%{gapprgdir}/fsagrowth
%{gapprgdir}/fsalabmin
%{gapprgdir}/fsalequal
%{gapprgdir}/fsamin
%{gapprgdir}/fsanot
%{gapprgdir}/fsaor
%{gapprgdir}/fsaprune
%{gapprgdir}/fsareverse
%{gapprgdir}/fsastar
%{gapprgdir}/fsaswapcoords
%{gapprgdir}/gap
%{gapprgdir}/gap4todr
%{gapprgdir}/gapmpi.o
%{gapprgdir}/gpaxioms
%{gapprgdir}/gpcheckmult
%{gapprgdir}/gpchecksubwa
%{gapprgdir}/gpcomp
%{gapprgdir}/gpdifflabs
%{gapprgdir}/gpgenmult
%{gapprgdir}/gpgenmult2
%{gapprgdir}/gpgeowa
%{gapprgdir}/gpipe
%{gapprgdir}/gpipe.o
%{gapprgdir}/gpmakefsa
%{gapprgdir}/gpmakesubwa
%{gapprgdir}/gpmicomp
%{gapprgdir}/gpmigenmult
%{gapprgdir}/gpmigenmult2
%{gapprgdir}/gpmigmdet
%{gapprgdir}/gpmimult
%{gapprgdir}/gpmimult2
%{gapprgdir}/gpminkb
%{gapprgdir}/gpmult
%{gapprgdir}/gpmult2
%{gapprgdir}/gprun
%{gapprgdir}/gpsubpres
%{gapprgdir}/gpsubwa
%{gapprgdir}/gpwa
%{gapprgdir}/grrun
%{gapprgdir}/hello
%{gapprgdir}/io.so
%{gapprgdir}/iostream.o
%{gapprgdir}/kbprog
%{gapprgdir}/kbprogcos
%{gapprgdir}/libmpi.a
%{gapprgdir}/makecosfile
%{gapprgdir}/matcalc
%{gapprgdir}/midfadeterminize
%{gapprgdir}/nfadeterminize
%{gapprgdir}/normrun
%{gapprgdir}/nq
%{gapprgdir}/nqmrun
%{gapprgdir}/nqrun
%{gapprgdir}/pcrun
%{gapprgdir}/polroots.so
%{gapprgdir}/ppgap
%{gapprgdir}/ppgap4
%{gapprgdir}/pq
%{gapprgdir}/readrels
%{gapprgdir}/scrun
%{gapprgdir}/selgen
%{gapprgdir}/sylrun
%{gapprgdir}/tcfrontend4
%{gapprgdir}/tcmainca4
%{gapprgdir}/tcmaingap4
%{gapprgdir}/wordreduce
%{gapprgdir}/xgap
%{gappkgdir}/ace
%{gappkgdir}/aclib
%{gappkgdir}/alnuth
%{gappkgdir}/anupq
%{gappkgdir}/atlasrep
%{gappkgdir}/automata
%{gappkgdir}/automgrp
%{gappkgdir}/autpgrp
%{gappkgdir}/Browse
%{gappkgdir}/carat
%{gappkgdir}/circle
%{gappkgdir}/cohomolo
%{gappkgdir}/crime
%{gappkgdir}/crisp
%{gappkgdir}/cryst
%{gappkgdir}/crystcat
%{gappkgdir}/ctbllib
%{gappkgdir}/cubefree
%{gappkgdir}/design
%{gappkgdir}/edim
%{gappkgdir}/example
%{gappkgdir}/factint
%{gappkgdir}/fga
%{gappkgdir}/format-1.1
%{gappkgdir}/forms
%{gappkgdir}/fplsa
%{gappkgdir}/fr
%{gappkgdir}/GAPDoc-1.2
%{gappkgdir}/gpd
%{gappkgdir}/grape
%{gappkgdir}/grpconst
%{gappkgdir}/guarana
%{gappkgdir}/guava3.9
%{gappkgdir}/Hap1.8
%{gappkgdir}/HAPcryst
%{gappkgdir}/happrime-0.3.2
%{gappkgdir}/idrel
%{gappkgdir}/if
%{gappkgdir}/io
%{gappkgdir}/irredsol
%{gappkgdir}/itc
%{gappkgdir}/kan
%{gappkgdir}/kbmag
%{gappkgdir}/laguna
%{gappkgdir}/liealgdb
%{gappkgdir}/linboxing-0.5.1
%{gappkgdir}/loops
%{gappkgdir}/monoid
%{gappkgdir}/nilmat
%{gappkgdir}/nq-2.2
%{gappkgdir}/nql
%{gappkgdir}/numericalsgps
%{gappkgdir}/openmath
%{gappkgdir}/orb
%{gappkgdir}/pargap
%{gappkgdir}/polenta
%{gappkgdir}/polycyclic
%{gappkgdir}/polymaking
%{gappkgdir}/qaos
%{gappkgdir}/quagroup
%{gappkgdir}/radiroot
%{gappkgdir}/rcwa
%{gappkgdir}/rds
%{gappkgdir}/repsn
%{gappkgdir}/resclasses
%{gappkgdir}/sgpviz
%{gappkgdir}/singular
%{gappkgdir}/sonata
%{gappkgdir}/sophus
# tomlib is in the main tarball
%{gappkgdir}/toric1.4
%{gappkgdir}/unipot-1.2
%{gappkgdir}/unitlib
%{gappkgdir}/wedderga
%{gappkgdir}/xgap
%{_datadir}/X11/app-defaults/XGap
%{gappkgdir}/xmod
