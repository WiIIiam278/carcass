# carcass

[![Discord](https://img.shields.io/discord/818135932103557162?color=7289da&logo=discord)](https://discord.gg/tVYhJfyDWG)

`carcass` is a Python CLI tool for spinning up a network of proxied Minecraft servers with configurable parameters and
plugins.

Useful for rapid testing of plugins that require a server network or that run on the proxy side.

## Usage

To use carcass, install Python 3.10+ and run `python ./carcass.py --eula true`. Alternatively, you can execute the bundled
Powershell script, `create_network.ps1`.

This will create a network of two PaperMC Minecraft servers (`/alpha` and `/beta`) connected to a Waterfall
proxy (`/proxy`). You can then use the `\.start_servers.ps1` script to start the servers (or use the individual
Batch/Powershell scripts generated in each server/the proxy directory).

### Arguments

You can pass various arguments to customize the network that will be spun up, including specifying the paths of plugins
and preconfigured data folders to copy over.

| Argument                                 | Name                 | Description                                       | Example                                     |
|------------------------------------------|----------------------|---------------------------------------------------|---------------------------------------------|
| `-h`, `--help`                           | HELP                 | Print the help menu                               | `-h`                                        |
| `-e`, `--eula`                           | EULA                 | Accept the Minecraft EULA                         | `-e true`                                   |
| `-bt`, `--type`                          | TYPE                 | Set the type of backend (Paper)                   | `-bt paper`                                 |
| `-pt`, `--proxy`                         | PROXY                | Set the type of proxy (Waterfall)                 | `-pt waterfall`                             |
| `-b`, `--backends`                       | BACKENDS             | List of backend names                             | `-b alpha beta gamma`                       |
| `-p`, `--ports`, `--backend-ports`       | PORTS                | List of backend ports (order matters)             | `-b 25566 25567 25568`                      |
| `-v`, `--version`, `--minecraft-version` | VERSION              | Minecraft version to use                          | `-v 1.19.2`                                 |
| `-pv`, `--proxy-version`                 | PROXY VERSION        | Proxy version group to use                        | `-v 1.19`                                   |
| `-r`, `--ram`, `--backend-ram`           | RAM                  | RAM (in MB) to allocate to each backend           | `-r 2048`                                   |
| `-pr`, `--proxy-ram`                     | PROXY RAM            | RAM (in MB) to allocate the proxy                 | `-pr 512`                                   |
| `-pp`, `--proxy-port`                    | PROXY PORT           | Port number to run the proxy on                   | `-pp 25565`                                 |
| `-ph`, `--proxy-host`                    | PROXY HOST           | Hostname to run the proxy with                    | `-ph localhost`                             |
| `-pn`, `--proxy-name`                    | PROXY NAME           | Name to call the proxy directory                  | `-pn proxy`                                 |
| `-bp`, `--plugins`                       | PLUGINS              | File paths of backend plugin jars to copy in      | `-bp path/to/a/plugin.jar also/another.jar` |
| `-bpf`, `--plugin-folders`               | PLUGIN FOLDERS       | File paths of backend plugin data folders to copy | `-bpf plugin/data/folder/ and/another/`     |
| `-pp`, `--proxy-plugins`                 | PROXY PLUGINS        | FIle paths of proxy plugin jars to copy in        | `-pp path/to/a/plugin.jar also/another.jar` |
| `-ppf`, `--proxy-plugin-folders`         | PROXY PLUGIN FOLDERS | File paths of proxy plugin data folders to copy   | `-ppf plugin/data/folder/ and/another/`     |
| `-o`, `--output`                         | OUTPUT               | Output directory; where the servers will be made  | `-o ./servers/`                             |

I recommend writing your own simple script that use carcass to spin up a network of servers and then use the `\.start_servers.ps1` script (of which you can pass an argument specifying the network directory to start) to start them.

## License
`carcass` is licensed under Apache-2.0.