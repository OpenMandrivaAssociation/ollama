%undefine _debugsource_packages
Name:           ollama
Version:        0.5.12
Release:        1
Summary:        Tool for running AI models on-premise
License:        MIT
URL:            https://ollama.com
Source:         https://github.com/ollama/ollama/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# Generated by running, inside the source tree:
# go mod vendor
# tar cJf ../../godeps-for-ollama-0.5.11.tar.xz vendor
Source1:        godeps-for-ollama-%{version}.tar.xz
Source2:        ollama.service
Source3:        %{name}.sysusers
BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  zstd
BuildRequires:  golang
BuildRequires:  compiler(go-compiler)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  systemd-rpm-macros

%patchlist
#ollama-0.4.0-compile.patch

%description
Ollama is a tool for running AI models on one's own hardware.
It offers a command-line interface and a RESTful API.
New models can be created or existing ones modified in the
Ollama library using the Modelfile syntax.
Source model weights found on Hugging Face and similar sites
can be imported.

%prep
%autosetup -a1 -p1

%build
export GOPATH=$(pwd)/vendor:$(pwd)/gopath
go build
%cmake
%make_build

%install
export GOPATH=$(pwd)/vendor:$(pwd)/gopath
install -D -m 0755 %{name} %{buildroot}/%{_bindir}/%{name}
install -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf
install -d %{buildroot}%{_localstatedir}/lib/%{name}

# Looks like runners was merged inside binary
#mkdir -p "%{buildroot}%{_prefix}/lib/%{name}"
#cp -a dist/*/lib/%{name}/runners %{buildroot}%{_prefix}/lib/%{name}/

mkdir -p "%{buildroot}/%{_docdir}/%{name}"
cp -Ra docs/* "%{buildroot}/%{_docdir}/%{name}"

%files
%license LICENSE
%doc %{_docdir}/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%attr(-, ollama, ollama) %{_localstatedir}/lib/%{name}
#{_prefix}/lib/%{name}
