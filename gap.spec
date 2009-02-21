%define gapbin		gap
%define gapdir		%{_datadir}/%{gapbin}
%define gappkgdir	%{gapdir}/pkg
%define gapprg		%{_arch}/%{gapbin}

Name:		gap-system
Summary:	GAP is a system for computational discrete algebra
Version:	4.4.12
Release:	%mkrel 1
License:	GPL
Group:		Sciences/Mathematics
Source0:	ftp://ftp.gap-system.org/pub/gap/gap44/tar.bz2/gap4r4p12.tar.bz2

# Alnut requires kant (http://www.math.tu-berlin.de/~kant/kash.html)
# hap requires polymake (http://www.math.tu-berlin.de/polymake/), graphviz (http://www.graphviz.org/), simplicial gap package (somewhere in http://www.cis.udel.edu/~dumas/)
# HAPcryst requires polymake (http://www.math.tu-berlin.de/polymake/)
# linboxing requires LinBox (http://www.linalg.org/) with version >= 1.1.5
# NumericalSgps requires graphviz (http://www.graphviz.org/),
# OpenMath (External needs: This package can be useful only with other applications that support OpenMath)
# polymaking requires polymake (http://www.math.tu-berlin.de/polymake/)
# qaos requires needs cURL (http://curl.haxx.se)
#	The QaoS package provides gateway functions to access the QaoS
#	databases of algebraic objects in Berlin. QaoS is primarily intended
#	to query for transitive groups or algebraic number fields and turn
#	retrieved results into GAP objects for further computing. 
# singular requires singular (http://www.singular.uni-kl.de/)
# SgpViz requires evince (http://www.gnome.org/projects/evince/), graphviz (http://www.graphviz.org/), and tcl/tk (http://www.tcl.tk/)
Source1:	ftp://ftp.gap-system.org/pub/gap/gap4/tar.bz2/packages-2009_02_18-11_42_UTC.tar.bz2

URL:		http://www.gap-system.org

BuildRequires:	libgmp-devel
BuildRequires:	libxaw-devel

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
cd pkg
bzip2 -dc %{SOURCE1} | tar -xf -
cd ..

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
  # there are some cygwin binaries and one sparc directory tree
  rm -fr */bin

  for f in `find . -mindepth 1 -a -maxdepth 1 -type d`; do
    ln -sf ../../bin $f
  done

  pushd ace
    ./configure
    make
  popd

  pushd anupq
    ./configure
    # gcc2 to gcc4 doesn't matter here...
    # GNU{INC,LIB} is where libgmp headers/libraries are found
    make							\
	GAP=../../../bin/%{_arch}/gap				\
	linux-iX86-gcc2-gmp					\
	GNUINC=%{_includedir}					\
	GNULIB=%{_libdir}
  popd

  pushd carat
    tar zxf carat-2.1b1.tgz
    mv carat-2.1b1/{functions,include,info,lib,src,tables,tex} .
    rm -fr carat-2.1b1*
    mv -f carat-2.1b1/bin/Makefile .
%define carat_top	../../pkg/carat
    pushd bin/%{_arch}
	make -f %{carat_top}/Makefile				\
		CFLAGS=-DDIAG1					\
		TOPDIR=%{gapdir}				\
		SRC=%{carat_top}/src				\
		INCL=%{carat_top}/include			\
		PROGRAMS
    popd
  popd

  pushd cohomolo
    ./configure
    make
  popd

  pushd edim
    ./configure
    make GAPPATH=../..
  popd

  pushd example
    ./configure
    make
  popd

  pushd fplsa
    ./configure
    make
  popd

  pushd fr
    ./configure
    make GAPPATH=../..
  popd

  pushd grape
    ./configure
    pushd src
      make BINDIR=%{_arch} main others
    popd

    push nauty22
      %configure
      make
    popd
  popd

  pushd Hap1.8
    perl -pi							\
	-e 's|(^PKGDIR=).*|$1..|';'				\
	-e 's|(^GACDIR=).*|$1bin/%{_arch}|;'			\
	compile.sh
    sh ./compile.sh
  popd

  pushd io
    ./configure
    make GAPPATH=../..
  popd

  pushd kbmap
    # want a symbolic link, and not a sun-sparc tree
    rm -fr bin
    ./configure
    make GAPPATH=../..
  popd

  pushd linboxing-0.5.1
    echo -n "nothing done, needs linboxing packaged"
  popd

  pushd nq-2.2
    perl -pi							\
	-e 's|\@target\@-\@BASECC\@|%{_arch}|g;'		\
	-e 's|GNU_MP_INC|%{_includedir}|;'			\
	-e 's|GNU_MP_LIB|%{_libdir}|;'				\
	Makefile.in
    %configure
    make
  popd

  pushd openmath
    pushd OMCv1.3c/src
      %configure
      make
    popd
    ./configure
    make
  popd

  pushd orb
    make GAP=bin/%{_arch}
  popd

  pushd pargap
    sed								\
	-e 's|@PWD@|../..|g'					\
	-e 's|@GAPPATH@|.|g'					\
	-e 's|@GAPARCH@|%{_arch}|g'				\
	Makefile.in > Makefile
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
  popd
popd

%install
#   gap wants to be used from it's build directory.
#   It also doesn't generate libraries, instead, programs are linked
# with the .o files
rm -f bin/%{_arch}/config*
mkdir -p %{buildroot}/%{_bindir}
cp -fa bin/gap.sh %{buildroot}/%{_bindir}/gap

# bin - don't install windows dlls, .bat, .pif, etc
mkdir -p %{buildroot}/%{gapdir}/bin/%{_arch}
cp -far bin/%{_arch}/*.o bin/%{_arch}/ga{c,p} %{buildroot}/%{gapdir}/bin/%{_arch}

# install full directories
perl -pi -e 's|gap4|gap|' tst/remake.sh
cp -far grp lib prim small trans tst %{buildroot}/%{gapdir}

# pkg - don't install some rebuild files as they are not fully patched
#       for rebuild, and it should not be required.
rm -f pkg/*/configure* pkg/*/Makefile* pkg/*/sedfile pkg/*/src
cp -far pkg %{buildroot}/%{gapdir}

# doc - it is installed in %{_docdir} but searched in %{_gapdir}/doc
ln -sf %{_docdir}/%{name} %{buildroot}/%{gapdir}/doc

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc doc/*
%{_bindir}/gap
%dir %{gapdir}
%dir %{gappkgdir}
%dir %{gappkgdir}/tomlib

%files	packages
%defattr(-,root,root)
%doc %{gappkgdir}/README.*
%doc %{gappkgdir}/*/doc
%doc %{gappkgdir}/*/htm
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
%{gappkgdir}/org
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
%{gappkgdir}/xmod
