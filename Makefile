# Project : Demo.cratica
# -----------------------------------------------------------------------------
# Author : Ricardo Lafuente <r@manufacturaindependente.org>
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

# your SSH target dir for rsync
SSH_HOSTNAME = "democratica"
SSH_DIR = "/home/rlafuente/public_html/"

SSH_PATH = "$(SSH_HOSTNAME):$(SSH_DIR)"
# server port for local server
SERVER_PORT = 8002
MAIN_SCRIPT = $(wildcard generate.py)
OFFLINE_FLAG = "--offline"

html:
	# . `pwd`/.env/bin/activate; python $(MAIN_SCRIPT)
	python $(MAIN_SCRIPT)

html-quick:
	# . `pwd`/.env/bin/activate; python $(MAIN_SCRIPT)
	python $(MAIN_SCRIPT) --fast-run

# FIXME: untested
install:
	virtualenv .env --no-site-packages --distribute --prompt=\(democratica\)
	. `pwd`/.env/bin/activate; pip install -r requirements.txt
	cp settings.conf.sample settings.conf

serve:
	cd _output && livereload --port $(SERVER_PORT)

upload:
	rsync --compress --progress --recursive --update --delete _output/ $(SSH_PATH)
	# SSH to host and copy files to a root-owned dir with sudo
	ssh -t $(SSH_HOSTNAME) 'sudo rsync --compress --recursive --update --delete $(SSH_DIR) /web/demo.cratica.org/public_html'

fakeupload:
	rsync --dry-run --compress --progress --recursive --update --delete _output/ $(SSH_PATH)

clean:
	rm -fr _output


