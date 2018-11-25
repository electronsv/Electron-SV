#!/usr/bin/env python3

# python setup.py sdist --format=zip,gztar

from setuptools import setup
import os
import sys
import platform
import imp
import argparse

with open('contrib/requirements/requirements.txt') as f:
    requirements = f.read().splitlines()

with open('contrib/requirements/requirements-hw.txt') as f:
    requirements_hw = f.read().splitlines()

version = imp.load_source('version', 'lib/version.py')

if sys.version_info[:3] < (3, 5, 2):
    sys.exit("Error: Electron Cash requires Python version >= 3.5.2...")

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--user', dest='is_user', action='store_true', default=False)
    parser.add_argument('--system', dest='is_user', action='store_false', default=False)
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    parser.add_argument('--prefix=', dest='prefix_path', metavar='prefix', nargs='?', const='/', default=sys.prefix)
    opts, _ = parser.parse_known_args(sys.argv[1:])

    # Use per-user */share directory if the global one is not writable or if a per-user installation
    # is attempted
    user_share   = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
    system_share = os.path.join(opts.prefix_path, "share")
    if not opts.is_user:
        # Not neccarily a per-user installation try system directories
        if os.access(opts.root_path + system_share, os.W_OK):
            # Global /usr/share is writable for us – so just use that
            share_dir = system_share
        elif not os.path.exists(opts.root_path + system_share) and os.access(opts.root_path, os.W_OK):
            # Global /usr/share does not exist, but / is writable – keep using the global directory
            # (happens during packaging)
            share_dir = system_share
        else:
            # Neither /usr/share (nor / if /usr/share doesn't exist) is writable, use the
            # per-user */share directory
            share_dir = user_share
    else:
        # Per-user installation
        share_dir = user_share
    data_files += [
        # Menu icon
        (os.path.join(share_dir, 'icons/hicolor/128x128/apps/'), ['icons/electron-cash.png']),
        (os.path.join(share_dir, 'pixmaps/'),                    ['icons/electron-cash.png']),
        # Menu entry
        (os.path.join(share_dir, 'applications/'), ['electron-sv.desktop']),
        # App stream (store) metadata
        (os.path.join(share_dir, 'metainfo/'), ['org.electronsv.Electronsv.appdata.xml']),
    ]

setup(
    name="Electron Cash",
    version=version.PACKAGE_VERSION,
    install_requires=[
        'pyaes>=0.1a1',
        'ecdsa>=0.9',
        'requests',
        'qrcode',
        'protobuf',
        'dnspython',
        'jsonrpclib-pelix',
        'PySocks>=1.6.6',
        'pyqt5',
    ],
    extras_require={
        'hardware': requirements_hw,
    },
    packages=[
        'electronsv',
        'electronsv_gui',
        'electronsv_gui.qt',
        'electronsv_plugins',
        'electronsv_plugins.audio_modem',
        'electronsv_plugins.cosigner_pool',
        'electronsv_plugins.email_requests',
        'electronsv_plugins.hw_wallet',
        'electronsv_plugins.keepkey',
        'electronsv_plugins.labels',
        'electronsv_plugins.ledger',
        'electronsv_plugins.trezor',
        'electronsv_plugins.digitalbitbox',
        'electronsv_plugins.virtualkeyboard',
    ],
    package_dir={
        'electronsv': 'lib',
        'electronsv_gui': 'gui',
        'electronsv_plugins': 'plugins',
    },
    package_data={
        'electronsv': [
            'servers.json',
            'servers_testnet.json',
            'currencies.json',
            'www/index.html',
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electron-case.mo',
        ]
    },
    scripts=['electron-sv'],
    data_files=data_files,
    description="Lightweight Bitcoin Cash Wallet",
    author="Jonald Fyookball",
    author_email="jonf@electronsv.org",
    license="MIT Licence",
    url="http://electronsv.org",
    long_description="""Lightweight Bitcoin Cash Wallet"""
)
