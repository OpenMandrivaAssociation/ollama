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
# Pinned by LLAMA_CPP_VERSION (b10760). CMake would git-clone this otherwise.
#	https://github.com/ggml-org/llama.cpp/archive/refs/tags/b10760.tar.gz
Source2:	llama.cpp-b10760.tar.gz
Source3:	ollama.service
Source4:	%{name}.sysusers
BuildRequires:	cmake
BuildRequires:	make
BuildRequires:	ccache
BuildRequires:	git
BuildRequires:	zstd
BuildRequires:	golang
BuildRequires:	compiler(go-compiler)
BuildRequires:	pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
BuildRequires:	pkgconfig(vulkan)
BuildRequires:	glslc
BuildRequires:	glslang
BuildRequires:	cmake(SPIRV-Headers)

%description
Ollama is a tool for running AI models on one's own hardware.
It offers a command-line interface and a RESTful API.
New models can be created or existing ones modified in the
Ollama library using the Modelfile syntax.
Source model weights found on Hugging Face and similar sites
can be imported.

%prep
%autosetup -n %{name}-%{version} -a1 -p1
tar -C .. -xf %{SOURCE2}
# Ollama's llama-server compat hooks (normally a FetchContent PATCH_COMMAND)
patch -p1 -d ../llama.cpp-b10760 < llama/compat/001-llama-cpp-hooks.patch

# RPM libdir is lib64; cmake default and the Go discovery path are lib/ollama.
echo 'package ml

var LibOllamaPath string = "%{_libdir}/ollama"
' > ml/path.go

%build
# Offline Go modules from Source1
export GO111MODULE=on
export GOFLAGS="-mod=vendor"
export GOPROXY=off
export GOTOOLCHAIN=local
%cmake \
	-DOLLAMA_LIB_DIR=%{_lib}/ollama \
	-DOLLAMA_LLAMA_BACKENDS=vulkan \
	-DOLLAMA_VERSION=%{version} \
	-DFETCHCONTENT_SOURCE_DIR_LLAMA_CPP=$(cd .. && pwd)/llama.cpp-b10760 \
	-DOLLAMA_LLAMA_CPP_SKIP_COMPAT_PATCH=ON
%cmake_build

%install
export GO111MODULE=on
export GOFLAGS="-mod=vendor"
export GOPROXY=off
%cmake_install

install -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE4} %{buildroot}%{_sysusersdir}/%{name}.conf
install -d %{buildroot}%{_localstatedir}/lib/%{name}

mkdir -p %{buildroot}%{_docdir}/%{name}
cp -Ra docs/* %{buildroot}%{_docdir}/%{name}

install -d %{buildroot}%{_sysconfdir}/ld.so.conf.d
cat > %{buildroot}%{_sysconfdir}/ld.so.conf.d/ollama.conf <<EOF
%{_libdir}/ollama
EOF

%files
%license LICENSE
%doc %{_docdir}/%{name}
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_sysusersdir}/%{name}.conf
%{_sysconfdir}/ld.so.conf.d/%{name}.conf
%attr(-, ollama, ollama) %{_localstatedir}/lib/%{name}
%{_libdir}/ollama/
