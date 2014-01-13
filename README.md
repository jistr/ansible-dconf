ansible-dconf
=============

Ansible module for setting DConf entries.

See also
[ansible-gsetting](https://github.com/jistr/ansible-gsetting).

Installation
------------

    curl https://raw.github.com/jistr/ansible-dconf/master/dconf.py > ~/ansible_dir/library/dconf

Usage examples
--------------

    - name: gnome-terminal default-show-menubar
      dconf: user=jistr
             key=/org/gnome/terminal/legacy/default-show-menubar
             value=false

Be careful with string values, which should be passed into DConf
single-quoted. You'll need to quote the value twice in YAML:

    - name: shortcut help
      dconf: user=jistr
             key=/org/gnome/terminal/legacy/keybindings/help
             value="'disabled'"
