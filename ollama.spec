%undefine _debugsource_packages
Name:		ollama
Version:	0.34.0
Release:	1
Summary:	Tool for running AI models on-premise
License:	MIT
Group:		Development/Other
URL:		https://ollama.com
Source0:	https://github.com/ollama/ollama/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# Generated inside the source tree (ABF has no network):
#	go mod vendor
#	tar cJf ../godeps-for-ollama-%{version}.tar.xz vendor
Source1:	godeps-for-ollama-%{version}.tar.xz
Source2:	ollama.service
Source3:	%{name}.sysusers
BuildRequires:	golang
BuildRequires:	compiler(go-compiler)
# go-sqlite3 (and optional native GPU probe) need a C compiler
BuildRequires:	clang
BuildRequires:	pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
# Inference is the cooker llama.cpp package (PGO, system ggml, Vulkan/ROCm
# via ggml-backend-*). Do not FetchContent the LLAMA_CPP_VERSION pin.
# 0.4.0-2+ carries Ollama's GGUF translation layer (llama/compat/).
Requires:	llama-cpp-server >= 0.4.0-2
# llama-quantize is used by `ollama create` (lives in the examples subpackage)
Recommends:	llama-cpp-examples

%description
Ollama is a tool for running AI models on one's own hardware.
It offers a command-line interface and a RESTful API.
New models can be created or existing ones modified in the
Ollama library using the Modelfile syntax.
Source model weights found on Hugging Face and similar sites
can be imported.

Inference is provided by the system llama-cpp package
(llama-server), not a bundled llama.cpp tree.

%prep
%autosetup -n %{name}-%{version} -a1 -p1

# RPM libdir is lib64; upstream discovery looks under lib/ollama.
# Pin the helper search path so the llama-server / llama-quantize
# symlinks installed below are found.
echo 'package ml

var LibOllamaPath string = "%{_libdir}/ollama"
' > ml/path.go

%build
# Offline Go modules from Source1
export GO111MODULE=on
export GOFLAGS="-mod=vendor"
export GOPROXY=off
export GOTOOLCHAIN=local
export CGO_ENABLED=1
export CC=clang
go build -trimpath \
	-ldflags "-s -w -X=github.com/ollama/ollama/version.Version=%{version} -X=github.com/ollama/ollama/server.mode=release" \
	-o ollama .

%install
install -D -m 0755 ollama %{buildroot}%{_bindir}/%{name}
install -D -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE3} %{buildroot}%{_sysusersdir}/%{name}.conf
install -d %{buildroot}%{_localstatedir}/lib/%{name}

mkdir -p %{buildroot}%{_docdir}/%{name}
cp -Ra docs/* %{buildroot}%{_docdir}/%{name}

# Helpers are looked up under LibOllamaPath; use the PGO system binaries.
install -d %{buildroot}%{_libdir}/ollama
ln -s %{_bindir}/llama-server %{buildroot}%{_libdir}/ollama/llama-server
ln -s %{_bindir}/llama-quantize %{buildroot}%{_libdir}/ollama/llama-quantize

%files
%license LICENSE
%doc %{_docdir}/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%attr(-, ollama, ollama) %{_localstatedir}/lib/%{name}
%{_libdir}/ollama/llama-server
%{_libdir}/ollama/llama-quantize
