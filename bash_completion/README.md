# odoo-bin autocomplete

Bash autocomplete helper for odoo-bin

- autocomplete some comand line parametters (after typing the first '-')
- list available database after -d
- list available modules after -i and -u
- partial support of comma separated addons-path (trailing / must be removed)

Most of that logic is hardcoded for performance and simplicity reasons

## setup

```
sudo apt update
sudo apt install bash-completion
```

Create symbolic link
```
ln -s "$(pwd)/odoo-bin" /home/${USER}/.local/share/bash-completion/completions/odoo-bin
```

Create optional link for alias
```
complete -F _odoo_bin odoo
```

Reload bash
```
exec bash
```
