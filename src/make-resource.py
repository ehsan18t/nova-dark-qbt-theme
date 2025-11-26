import subprocess
import glob
import argparse
import os
import os.path
import sys
import fnmatch
import re
import shutil


def allFiles(glob):
    [dir, pattern] = os.path.split(glob)
    l = list()
    for root, subdir, files in os.walk(dir):
        l.extend([os.path.join(root, x)
                 for x in files if fnmatch.fnmatch(x, pattern)])
    return l


def collect_files(root, prefix=None):
    entries = []
    for path in allFiles(os.path.join(root, '*')):
        alias = os.path.relpath(path, root)
        if prefix:
            alias = os.path.join(prefix, alias)
        entries.append((alias.replace('\\', '/'), path))
    return entries


parser = argparse.ArgumentParser(description='helper to create qbtthemes')
parser.add_argument('-output', type=str,
                    help='output qbtheme file', default='style.qbtheme')
parser.add_argument('-style', type=str, help='stylesheet', required=True)
parser.add_argument('-base-dir', type=str, dest='baseDir', default='.')
parser.add_argument('-icons-dir', type=str, dest='iconsDir',
                    default='', help='directory which contains custom icons')
parser.add_argument('-dir-prefix', type=str, default='',
                    dest='dirPrefix', help='prefix added to all files')
parser.add_argument('-config', type=str, dest='config',
                    default=None, help='file used as config.json')
parser.add_argument('-find-files', action='store_true', dest='findFiles',
                    help='find files included in qss and only include those')
parser.add_argument('-include-dir', action='append', dest='includeDirs', default=[],
                    help='additional directories to scan for resources; aliases are prefixed by the directory name')
parser.add_argument('files', metavar='files', type=str,
                    nargs='*', default=['*'], help='files to include in resources from baseDir, supports glob patterns')

args = parser.parse_args()

if not args.output.endswith('.qbtheme'):
    args.output += '.qbtheme'

if os.path.exists(args.output):
    print("WARNING! %s already exists. overwriting" % (args.output))


files = collect_files(args.baseDir)

for extra_dir in args.includeDirs:
    if not os.path.isabs(extra_dir):
        candidate = os.path.join(args.baseDir, extra_dir)
    else:
        candidate = extra_dir

    if not os.path.isdir(candidate):
        print(f"warning: include dir '{extra_dir}' not found")
        continue

    prefix = os.path.basename(os.path.normpath(candidate))
    files.extend(collect_files(candidate, prefix))
if args.findFiles:
    print('finding files')
    args.files = []
    stylesheet = open(os.path.join(args.baseDir, args.style)).read()
    for match in re.findall(r':/uitheme/(.*?)\)', stylesheet):
        args.files.append(match)

config_file = None
if args.config:
    if os.path.exists(args.config):
        config_file = args.config
    elif os.path.exists(os.path.join(args.baseDir, args.config)):
        config_file = os.path.join(args.baseDir, args.config)

ResourceFiles = list()
for alias, path in files:
    for pattern in args.files:
        if fnmatch.fnmatch(alias, pattern):
            ResourceFiles.append((alias, path))
            print('adding ' + path)
            break

IconFiles = list() if not args.iconsDir else [
    f for f in glob.glob(os.path.join(args.iconsDir, '*'))]
print(IconFiles)

with open('resources.qrc', 'w') as rcc:
    rcc.write('<!DOCTYPE RCC><RCC version="1.0">\n')
    rcc.write('\t<qresource %s>\n' %
              ('prefix=\'' + args.dirPrefix + '\'' if args.dirPrefix else ''))
    rcc.writelines(['\t\t<file alias=\'%s\'>%s</file>\n' %
                   x for x in ResourceFiles])
    rcc.write('\t</qresource>\n')
    rcc.write('\t<qresource>\n')
    rcc.write('\t\t<file alias=\'stylesheet.qss\'>%s</file>\n' %
              (os.path.join(args.baseDir, args.style)))
    rcc.writelines(['\t\t<file alias=\'icons/%s\'>%s</file>\n' %
                   (os.path.split(x)[1], x) for x in IconFiles if x.endswith('.svg') or x.endswith('.png')])
    if config_file:
        rcc.write('\t\t<file alias=\'config.json\'>%s</file>\n' %
                  (config_file))
    rcc.write('\t</qresource>\n')
    rcc.write('</RCC>')


rcc_candidates = []

env_rcc = os.environ.get('QBT_THEME_RCC')
if env_rcc:
    rcc_candidates.append(env_rcc)

for which_name in ('rcc', 'rcc.exe'):
    resolved = shutil.which(which_name)
    if resolved and resolved not in rcc_candidates:
        rcc_candidates.append(resolved)

tools_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools')
tools_rcc = os.path.join(tools_dir, 'rcc')
tools_rcc_exe = tools_rcc + '.exe'

for candidate in (tools_rcc, tools_rcc_exe):
    if candidate not in rcc_candidates:
        rcc_candidates.append(candidate)

rcc_path = next((c for c in rcc_candidates if c and os.path.exists(c)), None)

if not rcc_path:
    sys.stderr.write(
        '[error] Qt rcc tool not found. Install Qt tools or set QBT_THEME_RCC to the executable path.\n')
    sys.exit(1)

cmd = [rcc_path, '-binary', '-o', args.output, 'resources.qrc']
print(' '.join(cmd))

if not subprocess.call(cmd):
    os.remove('resources.qrc')
