# If any of the following macros should be set otherwise,
# you can wrap any of them with the following conditions:
# - %%if 0%%{centos} == 7
# - %%if 0%%{?rhel} == 7
# - %%if 0%%{?fedora} == 23
# Or just test for particular distribution:
# - %%if 0%%{centos}
# - %%if 0%%{?rhel}
# - %%if 0%%{?fedora}
#
# Be aware, on centos, both %%rhel and %%centos are set. If you want to test
# rhel specific macros, you can use %%if 0%%{?rhel} && 0%%{?centos} == 0 condition.
# (Don't forget to replace double percentage symbol with single one in order to apply a condition)

# Generate devel rpm
%global with_devel 1
# Build project from bundled dependencies
%global with_bundled 0
# Build with debug info rpm
%global with_debug 0
# Run tests in check section
%global with_check 1
# Generate unit-test rpm
%global with_unit_test 1

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         go-inf
%global repo            inf
# https://github.com/go-inf/inf
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     speter.net/go/exp/math/dec/inf
%global sec_import_path gopkg.in/inf.v0
%global commit          3887ee99ecf07df5b447e9b00d9c0b2adaa9f3e4
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-googlecode-go-decimal-inf
Version:        0.9.0
Release:        0.6.git%{shortcommit}%{?dist}
Summary:        Package implementing "infinite-precision" decimal arithmetic
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
Patch0:         0001-Fix-formatting.patch

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
Package inf (type inf.Dec) implements "infinite-precision" decimal arithmetic.
"Infinite precision" describes two characteristics: practically unlimited
precision for decimal number representation and no support for calculating
with any specific fixed precision.
Although there is no practical limit on precision,
inf.Dec can only represent finite decimals.

This package is currently in experimental stage and the API may change.

%if 0%{?with_devel}
%package devel
Summary:        %{summary}
BuildArch:      noarch

%if 0%{?with_check}
%endif

Provides:       golang(%{import_path}) = %{version}-%{release}
Provides:       golang(%{sec_import_path}) = %{version}-%{release}

%description devel
Package inf (type inf.Dec) implements "infinite-precision" decimal arithmetic.
"Infinite precision" describes two characteristics: practically unlimited
precision for decimal number representation and no support for calculating
with any specific fixed precision.
Although there is no practical limit on precision,
inf.Dec can only represent finite decimals.

This package is currently in experimental stage and the API may change.

This package contains library source intended for 
building other packages which use speter.net/go/exp/math/dec/inf.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}
%patch0 -p1

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.$ext" \! -iname "*_test.go") ; do
      install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
      cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
      echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list

      install -d -p %{buildroot}/%{gopath}/src/%{sec_import_path}/$(dirname $file)
      cp -pav $file %{buildroot}/%{gopath}/src/%{sec_import_path}/$file
      echo "%%{gopath}/src/%%{sec_import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{sec_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{sec_import_path}/$file
    echo "%%{gopath}/src/%%{sec_import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

#%%gotest %{sec_import_path}
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%license LICENSE
%endif

%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-0.6.git3887ee9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-0.5.git3887ee9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-0.4.git3887ee9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-0.3.git3887ee9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.0-0.2.git3887ee9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan 20 2017 Jan Chaloupka <jchaloup@redhat.com> - 0.9.0-0.1.git3887ee9
- Bump to upstream 3887ee99ecf07df5b447e9b00d9c0b2adaa9f3e4
  related: #1250518

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.8.hg42ca6cd68aa9
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.7.hg42ca6cd68aa9
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.6.hg42ca6cd68aa9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.5.hg42ca6cd68aa9
- Make devel noarch
  related: #1250518

* Thu Aug 20 2015 jchaloup <jchaloup@redhat.com> - 0-0.4.hg42ca6cd68aa9
- Use gotest instead of go test
  related: #1250518

* Wed Aug 19 2015 jchaloup <jchaloup@redhat.com> - 0-0.3.hg42ca6cd68aa9
- Update spec file to spec-2.0
  resolves: #1250518

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.2.hg42ca6cd68aa9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jan 12 2015 jchaloup <jchaloup@redhat.com> - 0-0.1.hg42ca6cd68aa9
- First package for Fedora
  resolves: #1181212

