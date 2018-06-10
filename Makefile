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
	gulp build
	. `pwd`/.env/bin/activate; python $(MAIN_SCRIPT)

html-quick:
	gulp build

install:
	virtualenv .env --no-site-packages --distribute --prompt=\(democratica\)
	. `pwd`/.env/bin/activate; pip install -r site-generator/requirements.txt

serve:
	gulp watch

live-deploy:
	rsync --compress --checksum --progress --recursive --update --delete dist/ $(SSH_PATH)

live-deploy-dry:
	rsync --dry-run --compress --checksum --progress --recursive --update --delete dist/ $(SSH_PATH)

deploy:
	rsync --compress --checksum --progress --recursive --update --delete dist/ $(STAGING_PATH)

deploy-dry:
	rsync --dry-run --compress --checksum --progress --recursive --update --delete dist/ $(STAGING_PATH)

clean:
	rm -fr dist


