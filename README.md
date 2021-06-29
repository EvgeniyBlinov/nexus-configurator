[![MIT License][license-image]][license-url]

# NexusConfigurator

Simple script for nexus configuration

## Usage

```
cp .env.example .env
$EDITOR .env

set -o allexport;
source .env;
set +o allexport;
```

Apply configuration

```
./nc.py -v apply
```

## License

[![MIT License][license-image]][license-url]

## Author

- [Blinov Evgeniy](mailto:evgeniy_blinov@mail.ru) ([https://evgeniyblinov.ru/](https://evgeniyblinov.ru/))

[license-image]: http://img.shields.io/badge/license-MIT-blue.svg?style=flat
[license-url]: LICENSE
