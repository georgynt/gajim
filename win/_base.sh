#!/usr/bin/env bash
# Copyright 2016 Christoph Reiter
# Copyright 2017 Philipp Hörist
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

set -e
DIR="$( cd "$( dirname "$0" )" && pwd )"
cd "${DIR}"

# CONFIG START

ARCH="i686"
PYTHON_VERSION="3"
BUILD_VERSION="0"

# CONFIG END

MISC="${DIR}"/misc
PYTHON_ID="python${PYTHON_VERSION}"
MINGW="mingw32"

QL_VERSION="0.0.0"
QL_VERSION_DESC="UNKNOWN"

function set_build_root {
    BUILD_ROOT="$1"
    REPO_CLONE="${BUILD_ROOT}/${MINGW}"/gajim
    MINGW_ROOT="${BUILD_ROOT}/${MINGW}"
    PACKAGE_DIR="${BUILD_ROOT}/${MINGW}/lib/python3.6/site-packages"
}

set_build_root "${DIR}/_build_root"

function build_pacman {
    pacman --root "${BUILD_ROOT}" "$@"
}

function build_pip {
    "${BUILD_ROOT}"/"${MINGW}"/bin/"${PYTHON_ID}".exe -m pip "$@"
}

function build_python {
    "${BUILD_ROOT}"/"${MINGW}"/bin/"${PYTHON_ID}".exe "$@"
}

function build_compileall {
    build_python -m compileall -b "$@"
}

function install_pre_deps {
    pacman -S --needed --noconfirm p7zip git \
        mingw-w64-"${ARCH}"-nsis wget intltool mingw-w64-"${ARCH}"-toolchain \
        mingw-w64-i686-python3
}

function create_root {
    mkdir -p "${BUILD_ROOT}"

    mkdir -p "${BUILD_ROOT}"/var/lib/pacman
    mkdir -p "${BUILD_ROOT}"/var/log
    mkdir -p "${BUILD_ROOT}"/tmp

    build_pacman -Syu
    build_pacman --noconfirm -S base
}

function install_deps {
    build_pacman --noconfirm -S mingw-w64-"${ARCH}"-gtk3 mingw-w64-"${ARCH}"-"${PYTHON_ID}" \
        mingw-w64-"${ARCH}"-"${PYTHON_ID}"-gobject \
        mingw-w64-"${ARCH}"-"${PYTHON_ID}"-pip \
        mingw-w64-"${ARCH}"-gstreamer \
        mingw-w64-"${ARCH}"-adwaita-icon-theme \
        mingw-w64-"${ARCH}"-libwebp \
        mingw-w64-"${ARCH}"-sqlite3 \
        mingw-w64-"${ARCH}"-goocanvas

    build_pip install setuptools_scm

    PIP_REQUIREMENTS="\
pyasn1
certifi
git+https://dev.gajim.org/gajim/python-nbxmpp.git
protobuf
git+https://github.com/dlitz/pycrypto.git
cryptography
pyopenssl
python-gnupg
docutils
qrcode
keyring
pillow
"

    build_pip install --no-binary ":all:" \
        --force-reinstall $(echo "$PIP_REQUIREMENTS" | tr ["\\n"] [" "])
    build_pip install python-axolotl

    # remove the large png icons, they should be used rarely and svg works fine
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/512x512"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/256x256"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/96x96"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/64x64"
    rm -Rf "${MINGW_ROOT}/share/icons/Adwaita/48x48"
    "${MINGW_ROOT}"/bin/gtk-update-icon-cache-3.0.exe --force \
        "${MINGW_ROOT}/share/icons/Adwaita"

    # Compile GLib schemas
    "${MINGW_ROOT}"/bin/glib-compile-schemas.exe "${MINGW_ROOT}"/share/glib-2.0/schemas

}

function install_gajim {
    [ -z "$1" ] && (echo "Missing arg"; exit 1)

    rm -Rf "${PACKAGE_DIR}"/gajim*

    cd ..

    build_pip install .

    QL_VERSION=$(MSYSTEM= build_python -c \
        "import gajim; import sys; sys.stdout.write(gajim.__version__.split('-')[0])")

    QL_VERSION_DESC=$(MSYSTEM= build_python -c \
        "import gajim; import sys; sys.stdout.write(gajim.__version__)")

    # Create launchers
    build_python "${MISC}"/create-launcher.py \
        "${QL_VERSION}" "${MINGW_ROOT}"/bin

    # Install plugin installer
    curl -o "${BUILD_ROOT}"/plugin_installer.zip https://ftp.gajim.org/plugins_1/plugin_installer.zip
    mkdir "${PACKAGE_DIR}"/gajim/data/plugins
    7z x -o"${PACKAGE_DIR}"/gajim/data/plugins "${BUILD_ROOT}"/plugin_installer.zip

    # Install themes
    # rm -Rf "${MINGW_ROOT}"/etc
    # rm -Rf "${MINGW_ROOT}"/share/themes
    # cp -r win/etc "${MINGW_ROOT}"
    # cp -r win/themes "${MINGW_ROOT}"/share

    # Install our own icons
    rm -Rf "${MINGW_ROOT}/share/icons/hicolor"
    cp -r gajim/data/icons/hicolor "${MINGW_ROOT}"/share/icons

    # Update icon cache
    "${MINGW_ROOT}"/bin/gtk-update-icon-cache-3.0.exe --force \
        "${MINGW_ROOT}/share/icons/hicolor"

}

function cleanup_install {

    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-shared-mime-info \
        mingw-w64-"${ARCH}"-"${PYTHON_ID}"-pip mingw-w64-"${ARCH}"-ncurses || true
    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-tk || true
    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-tcl || true
    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-gnome-common || true
    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-gsl || true
    build_pacman --noconfirm -Rdd mingw-w64-"${ARCH}"-libvpx || true

    #delete translations we don't support
    for d in "${MINGW_ROOT}"/share/locale/*/LC_MESSAGES; do
        if [ ! -f "${d}"/gajim.mo ]; then
            rm -Rf "${d}"
        fi
    done

    find "${MINGW_ROOT}" -regextype "posix-extended" -name "*.exe" -a ! \
        -iregex ".*/(gajim|python|history_manager)[^/]*\\.exe" \
        -exec rm -f {} \;

    rm -Rf "${MINGW_ROOT}"/libexec
    rm -Rf "${MINGW_ROOT}"/share/gtk-doc
    rm -Rf "${MINGW_ROOT}"/include
    rm -Rf "${MINGW_ROOT}"/var
    rm -Rf "${MINGW_ROOT}"/share/zsh
    rm -Rf "${MINGW_ROOT}"/share/pixmaps
    rm -Rf "${MINGW_ROOT}"/share/gnome-shell
    rm -Rf "${MINGW_ROOT}"/share/dbus-1
    rm -Rf "${MINGW_ROOT}"/share/gir-1.0
    rm -Rf "${MINGW_ROOT}"/share/doc
    rm -Rf "${MINGW_ROOT}"/share/man
    rm -Rf "${MINGW_ROOT}"/share/info
    rm -Rf "${MINGW_ROOT}"/share/mime
    rm -Rf "${MINGW_ROOT}"/share/gettext
    rm -Rf "${MINGW_ROOT}"/share/libtool
    rm -Rf "${MINGW_ROOT}"/share/licenses
    rm -Rf "${MINGW_ROOT}"/share/appdata
    rm -Rf "${MINGW_ROOT}"/share/aclocal
    rm -Rf "${MINGW_ROOT}"/share/ffmpeg
    rm -Rf "${MINGW_ROOT}"/share/vala
    rm -Rf "${MINGW_ROOT}"/share/readline
    rm -Rf "${MINGW_ROOT}"/share/xml
    rm -Rf "${MINGW_ROOT}"/share/bash-completion
    rm -Rf "${MINGW_ROOT}"/share/common-lisp
    rm -Rf "${MINGW_ROOT}"/share/emacs
    rm -Rf "${MINGW_ROOT}"/share/gdb
    rm -Rf "${MINGW_ROOT}"/share/libcaca
    rm -Rf "${MINGW_ROOT}"/share/gettext
    rm -Rf "${MINGW_ROOT}"/share/gst-plugins-base
    rm -Rf "${MINGW_ROOT}"/share/gtk-3.0
    rm -Rf "${MINGW_ROOT}"/share/nghttp2
    rm -Rf "${MINGW_ROOT}"/share/fontconfig
    rm -Rf "${MINGW_ROOT}"/share/gettext-*
    rm -Rf "${MINGW_ROOT}"/share/gstreamer-1.0

    find "${MINGW_ROOT}"/share/glib-2.0 -type f ! \
        -name "*.compiled" -exec rm -f {} \;

    rm -Rf "${MINGW_ROOT}"/lib/"${PYTHON_ID}".*/test
    rm -Rf "${MINGW_ROOT}"/lib/cmake
    rm -Rf "${MINGW_ROOT}"/lib/gettext
    rm -Rf "${MINGW_ROOT}"/lib/gtk-3.0
    rm -Rf "${MINGW_ROOT}"/lib/mpg123
    rm -Rf "${MINGW_ROOT}"/lib/p11-kit
    rm -Rf "${MINGW_ROOT}"/lib/ruby
    rm -Rf "${MINGW_ROOT}"/lib/tcl8
    rm -Rf "${MINGW_ROOT}"/lib/tcl8.6

    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstvpx.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstdaala.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstdvdread.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstopenal.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstopenexr.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstopenh264.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstresindvd.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstassrender.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstx265.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstwebp.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstopengl.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstmxf.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstfaac.dll
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstschro.dll

    rm -f "${MINGW_ROOT}"/bin/libharfbuzz-icu-0.dll
    rm -f "${MINGW_ROOT}"/lib/"${PYTHON_ID}".*/lib-dynload/_tkinter*
    rm -f "${MINGW_ROOT}"/lib/gstreamer-1.0/libgstcacasink.dll

    rm -Rf "${MINGW_ROOT}"/lib/python2.*

    find "${MINGW_ROOT}" -name "*.a" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.whl" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.h" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.la" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.sh" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.jar" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.def" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.cmd" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.cmake" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.pc" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.desktop" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.manifest" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.pyo" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "*.am" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name ".gitignore" -exec rm -f {} \;
    find "${MINGW_ROOT}" -name "pylint.rc" -exec rm -f {} \;

    find "${MINGW_ROOT}"/bin -name "*-config" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "easy_install*" -exec rm -f {} \;
    find "${MINGW_ROOT}" -regex ".*/bin/[^.]+" -exec rm -f {} \;
    find "${MINGW_ROOT}" -regex ".*/bin/[^.]+\\.[0-9]+" -exec rm -f {} \;

    find "${MINGW_ROOT}" -name "gtk30-properties.mo" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "gettext-tools.mo" -exec rm -rf {} \;

    find "${MINGW_ROOT}" -name "old_root.pem" -exec rm -rf {} \;
    find "${MINGW_ROOT}" -name "weak.pem" -exec rm -rf {} \;

    find "${MINGW_ROOT}"/lib/"${PYTHON_ID}".* -type d -name "test*" \
        -prune -exec rm -rf {} \;

    find "${MINGW_ROOT}"/lib/"${PYTHON_ID}".* -type d -name "*_test*" \
        -prune -exec rm -rf {} \;

    find "${MINGW_ROOT}"/bin -name "*.pyo" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "*.pyc" -exec rm -f {} \;
    # This file is not able to compile because of syntax errors
    find "${MINGW_ROOT}"/bin -name "glib-gettextize-script.py" -exec rm -f {} \;
    build_compileall -q "${MINGW_ROOT}"
    find "${MINGW_ROOT}" -name "*.py" ! -name "*theme.py" -exec rm -f {} \;
    find "${MINGW_ROOT}"/bin -name "*.pyc" -exec rm -f {} \;
    find "${MINGW_ROOT}" -type d -name "__pycache__" -prune -exec rm -rf {} \;

    build_python "${MISC}/depcheck.py"

    find "${MINGW_ROOT}" -type d -empty -delete

}

function build_installer {
    (cd "$BUILD_ROOT" && makensis -NOCD -DVERSION="$QL_VERSION_DESC" "${MISC}"/gajim.nsi)
    (cd "$BUILD_ROOT" && makensis -NOCD -DVERSION="$QL_VERSION_DESC" "${MISC}"/gajim-portable.nsi)
}
