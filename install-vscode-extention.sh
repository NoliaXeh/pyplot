#!/bin/sh

# find the vsocde config directory
if [ -z "$VSCODE_CONFIG_DIR" ]; then
  VSCODE_CONFIG_DIR="$HOME/.vscode/extensions"
fi

# copy the extension to the vscode config directory
cp -rfv ./vscode-extension/* "$VSCODE_CONFIG_DIR"

