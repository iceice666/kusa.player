import yaml

with open('./config/settings.yml', encoding='utf-8') as f:
    config = yaml.safe_load(f)

with open('./cmd_help.md', encoding='utf-8') as f:
    help_md = f.read()
