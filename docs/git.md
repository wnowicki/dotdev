# GIT Recipes

## Orphan Branch

```shell
git checkout --orphan=branch_name
git rm -rf .
git commit --allow-empty -m "Empty commit"
```

## Remove Stale Branches

To **remove local branches** that no longer exist on the remote repository (often called "stale" or "orphaned" branches), you can use the following multi-step command in your terminal:

```shell
git fetch -p && git branch -vv | awk '/: gone]/{print $1}' | xargs git branch -d
```

## Multiple GitHub Accounts

Exchange `kind` with the type of a connection, ex. work, personal etc.

Create key

```shell
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/id_ed25519_kind
```

SSH Agent

```shell
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_kind
```

Display key

```shell
cat ~/.ssh/id_ed25519_kind.pub
```

Add key to account [here](https://github.com/settings/keys)

Configuration

```shell
nano ~/.ssh/config 
```

```text
Host gh-kind
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_kind
```

Clone repository

```shell
git clone git@gh-kind:wnowicki/dotdev.git
```

## Set local user

```shell
git config user.name "username"
git config user.email "your_email@example.com"
```
