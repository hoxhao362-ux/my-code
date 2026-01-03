from core.config import config

config.check_dirs()

print(config.get('global.env'))
print(config.get('database'))
print(config.get('admin'))
print(config.get('journal'))
print(config.get('user'))
