FROM ghcr.io/libcxx/actions-builder:testing AS base

RUN sudo apt update && sudo apt-get install -y --no-install-recommends python3-pip python3-venv python3-dev python3-full \
    && sudo apt-get clean && sudo rm -rf /var/lib/apt/lists/*

COPY <<EOF /tmp/requirements.txt
PyGithub
actions-toolkit
rich
pydantic>2.0.0
EOF

RUN python3 -m venv ~/venv  && echo "source ~/venv/bin/activate" >> ~/.bashrc

RUN . ~/venv/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install -r /tmp/requirements.txt

RUN  curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
  | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt-get update \
    && sudo apt-get install gh -y
