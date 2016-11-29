# Project : Demo.cratica
# -----------------------------------------------------------------------------
# Authors : Ana Isabel Carvalho <a@manufacturaindependente.org>
#           Ricardo Lafuente <r@manufacturaindependente.org>
# -----------------------------------------------------------------------------
# License : GNU General Public License
# -----------------------------------------------------------------------------
# This file is part of the Demo.cratica package.
#
# Demo.cratica is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Demo.cratica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Demo.cratica. If not, see <http://www.gnu.org/licenses/>.

# This is *heavily* based on Edouard Richard's excellent Makefiles.
# See https://github.com/jplusplus/resonate2014/blob/master/Makefile for
# the basis from where this file was created.

# live
SSH_HOSTNAME = democratica
SSH_DIR = /web/demo.cratica.org/public_html/
# staging
STAGING_HOSTNAME = wf
STAGING_DIR = ~/webapps/democratica_staging/

SSH_PATH = $(SSH_HOSTNAME):$(SSH_DIR)
STAGING_PATH = $(STAGING_HOSTNAME):$(STAGING_DIR)
# server port for local server
SERVER_PORT = 8002
MAIN_SCRIPT = $(wildcard site-generator/generate.py)
OFFLINE_FLAG = "--offline"

html:
	. `pwd`/.env/bin/activate; python $(MAIN_SCRIPT)
	gulp build

html-quick:
	. `pwd`/.env/bin/activate; python $(MAIN_SCRIPT) --fast-run
	gulp build

install:
	virtualenv .env --no-site-packages --distribute --prompt=\(democratica\)
	. `pwd`/.env/bin/activate; pip install -r site-generator/requirements.txt

serve:
	. `pwd`/.env/bin/activate; cd dist && livereload --host 0.0.0.0 --port $(SERVER_PORT)

live-upload:
	rsync --compress --progress --recursive --update --delete dist/ $(SSH_PATH)

live-fakeupload:
	rsync --dry-run --compress --progress --recursive --update --delete dist/ $(SSH_PATH)

upload:
	rsync --compress --progress --recursive --update --delete dist/ $(STAGING_PATH)

fakeupload:
	rsync --dry-run --compress --progress --recursive --update --delete dist/ $(STAGING_PATH)

clean:
	rm -fr dist


