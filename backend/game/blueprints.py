import yaml


def load_base_blueprints():
    with open('blueprints.yml') as fp:
        return yaml.safe_load(fp)


base_blueprints = load_base_blueprints()
