Name: python-passpersist
Version: 0.4.1
Release: 1
Summary: Net-SNMP pass_persist Python Module
License: Zymeworks
Group: Development/Libraries/Python
Source:	python-passpersist-%{version}.tar.bz2
# BuildRoot: %{_tmppath}/%{name}-%{version}-build
%{py_requires}

%description
Python module for implementing pass_persist scripts for Net-SNMP

%prep
%setup -q

%build
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=$RPM_BUILD_ROOT --record-rpm=INSTALLED_FILES

%files -f INSTALLED_FILES
%defattr(-,root,root)
