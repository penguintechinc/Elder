#!/bin/bash
ansible-playbook ansible/entrypoint.yml  -c local  --tags run
echo "Sleeping awaiting action!"
/bin/sleep infinity
