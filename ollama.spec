%undefine _debugsource_packages
Name:           ollama
Version:        0.4.0
Release:        1
Summary:        Tool for running AI models on-premise
License:        MIT
URL:            https://ollama.com
Source:         https://github.com/ollama/ollama/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# Generated by running, inside the source tree:
# export GOPATH=$(pwd)/.godeps
# go mod download
# tar cJf ../../godeps-for-godeps-for-ollama-0.3.2.tar.xz .godeps
Source1:        godeps-for-ollama-%{version}.tar.xz
Source2:        ollama.service
Source3:        %{name}-user.conf
BuildRequires:  cmake >= 3.24
BuildRequires:  git
BuildRequires:  zstd
BuildRequires:  golang
BuildRequires:  compiler(go-compiler)
BuildRequires:	systemd-rpm-macros

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
export GOPATH=$(pwd)/.godeps:$(pwd)/gopath
go build


%install
export GOPATH=$(pwd)/.godeps:$(pwd)/gopath
install -D -m 0755 %{name} %{buildroot}/%{_bindir}/%{name}
install -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}-user.conf
install -d %{buildroot}%{_localstatedir}/lib/%{name}

mkdir -p "%{buildroot}/%{_docdir}/%{name}"
cp -Ra docs/* "%{buildroot}/%{_docdir}/%{name}"

#pre -f %{name}.pre
#%service_add_pre %{name}.service

%post
%service_add_post %{name}.service

%preun
%service_del_preun %{name}.service

%postun
%service_del_postun %{name}.service

%files
%license LICENSE
%doc %{_docdir}/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}-user.conf
%attr(-, ollama, ollama) %{_localstatedir}/lib/%{name}
