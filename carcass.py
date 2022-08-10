import argparse
import os
import shutil

from tqdm import tqdm
import requests


# Parameters for starting a network of Minecraft servers
class Parameters:
    root_dir = "./servers/"
    proxy_version = "1.19"
    minecraft_version = "1.19.2"
    eula_agreement = "false"

    backend_names = ["alpha", "beta"]
    backend_ports = [25567, 25568]
    backend_type = "paper"
    backend_ram = 2048
    backend_plugins = []
    backend_plugin_folders = []
    operator_names = []
    operator_uuids = []

    proxy_name = "proxy"
    proxy_host = "0.0.0.0"
    proxy_port = 25565
    proxy_type = "waterfall"
    proxy_ram = 512
    proxy_plugins = []
    proxy_plugin_folders = []

    just_update_plugins = False


def main():
    # Prepare default parameters
    parameters = Parameters()

    # Parse arguments to set parameters
    parser = argparse.ArgumentParser(description="Spins up a network of Minecraft servers")
    parser.add_argument("-e", "--eula",
                        default="false",
                        help="Whether you agree to the Minecraft EULA",
                        required=False)
    parser.add_argument("-u", "--update",
                        default=False,
                        help="Whether to just update plugins",
                        type=bool,
                        required=False)
    parser.add_argument("-bt", "--type", "--backend-type",
                        default="paper",
                        help="Type of backend servers (e.g. paper)",
                        required=False)
    parser.add_argument("-pt", "--proxy", "--proxy-type",
                        default="waterfall",
                        help="Type of proxy servers (e.g. waterfall)",
                        required=False)
    parser.add_argument("-b", "--backends",
                        default=["alpha", "beta"],
                        help="Names of backend servers",
                        required=False,
                        nargs="+")
    parser.add_argument("-p", "--ports", "--backend-ports",
                        default=[25566, 25567],
                        help="Ports of backend servers",
                        required=False,
                        nargs="+")
    parser.add_argument("-v", "--version", "--minecraft-version",
                        default="1.19.1",
                        help="Minecraft version to run (e.g. 1.19.2)",
                        required=False)
    parser.add_argument("-pv", "--proxy-version",
                        default="1.19",
                        help="Proxy version to run (e.g. 1.19)",
                        required=False)
    parser.add_argument("-r", "--ram", "--backend-ram",
                        default=2048,
                        help="Specify the RAM to allocate to each backend server",
                        required=False)
    parser.add_argument("-pr", "--proxy-ram",
                        default=512,
                        help="Specify the RAM to allocate to the proxy server",
                        required=False)
    parser.add_argument("-pp", "--proxy-port",
                        default="25565",
                        type=int,
                        help="Port of the proxy server",
                        required=False)
    parser.add_argument("-ph", "--proxy-host",
                        default="0.0.0.0",
                        help="Hostname to use for the proxy server",
                        required=False)
    parser.add_argument("-pn", "--proxy-name",
                        default="proxy",
                        help="Name of the proxy server",
                        required=False)
    parser.add_argument("-bp", "--plugins", "--backend-plugins",
                        default=[],
                        help="List of backend plugin jar file paths to copy",
                        required=False,
                        nargs="*")
    parser.add_argument("-fp", "--proxy-plugins",
                        default=[],
                        help="List of proxy plugin jar file paths to copy",
                        required=False,
                        nargs="*")
    parser.add_argument("-bpf", "--plugin-folders", "--backend-plugin-folders",
                        default=[],
                        help="List of backend plugin data folder file paths to copy",
                        required=False,
                        nargs="*")
    parser.add_argument("-ppf", "--proxy-plugin-folders",
                        default=[],
                        help="List of proxy plugin data folder file paths to copy",
                        required=False,
                        nargs="*")
    parser.add_argument("-opn", "--operator-names",
                        default=[],
                        required=False,
                        nargs="*")
    parser.add_argument("-opu", "--operator-uuids",
                        default=[],
                        required=False,
                        nargs="*")
    parser.add_argument("-o", "--output",
                        default='./servers/',
                        help="Directory to create the servers folder in",
                        required=False)

    # Set parameters if present
    args = parser.parse_args()
    parameters.eula_agreement = args.eula
    parameters.backend_type = args.type
    parameters.proxy_type = args.proxy
    parameters.backend_names = args.backends
    parameters.backend_ports = args.ports
    parameters.minecraft_version = args.version
    parameters.proxy_version = args.proxy_version
    parameters.proxy_port = args.proxy_port
    parameters.proxy_host = args.proxy_host
    parameters.proxy_name = args.proxy_name
    parameters.backend_plugins = args.plugins
    parameters.proxy_plugins = args.proxy_plugins
    parameters.backend_plugin_folders = args.plugin_folders
    parameters.proxy_plugin_folders = args.proxy_plugin_folders
    parameters.operator_names = args.operator_names
    parameters.operator_uuids = args.operator_uuids
    parameters.root_dir = args.output
    parameters.just_update_plugins = args.update

    # Update plugins if necessary
    if parameters.just_update_plugins:
        for name in parameters.backend_names:
            plugin_dir = f"{parameters.root_dir}{name}/plugins"

            # Clear contents of the plugin_dir directory if it exists
            if os.path.exists(plugin_dir):
                shutil.rmtree(plugin_dir)

            # Create the plugin_dir directory if it doesn't exist
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)

            # Copy plugins in
            copy_plugins(parameters.backend_plugins, parameters.backend_plugin_folders, plugin_dir)
        return

    # Require EULA agreement
    if parameters.eula_agreement.lower() != "true":
        parser.print_help()
        return print("\nYou must agree to the Minecraft EULA:\t--eula true")

    # Create all backend servers
    for name, port in zip(parameters.backend_names, parameters.backend_ports):
        create_backend_server(name, port, parameters)

    # Create the proxy server
    create_proxy_server(parameters)


# Creates a backend server
def create_backend_server(name, port, parameters):
    print(f"Creating {parameters.backend_type} backend server, {name}")

    # Create a folder for the server. If it exists, delete it.
    server_dir = parameters.root_dir + name
    if os.path.exists(f"{server_dir}"):
        os.system(f"rm -rf {server_dir}")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    if parameters.backend_type == "paper":
        # Create necessary subdirectories
        create_subdirectories(["config", "plugins"], server_dir)

        # Download the latest paper for the version and place it in the server folder
        server_jar = "paper.jar"
        download_paper_build("paper", parameters.minecraft_version,
                             get_latest_paper_build_number("paper", parameters.minecraft_version),
                             f"{server_dir}/{server_jar}")

        # Create eula.text and set eula=true
        with open(server_dir + "/eula.txt", "w") as file:
            file.write(f"# Auto-generated eula.txt for server {name}\n")
            file.write(f"eula={parameters.eula_agreement}")

        # Create the spigot.yml and enable BungeeCord
        with open(server_dir + "/spigot.yml", "w") as file:
            file.write(f"# Auto-generated spigot.yml for server {name}\n")
            file.write(f"settings:\n")
            file.write(f"  bungeecord: true\n")

        # Create the paper-global.yml and enable BungeeCord
        with open(server_dir + "/config/paper-global.yml", "w") as file:
            file.write(f"# Auto-generated paper-global.yml for server {name}\n")
            file.write(f"proxies:\n")
            file.write(f"  bungee-cord:\n")
            file.write(f"    online-mode: true\n")

        # Create the server.properties file
        server_properties = server_dir + "/server.properties"
        with open(server_properties, "w") as file:
            file.write(f"# Auto-generated server.properties for server {name}\n")
            file.write(f"# {parameters.backend_type} server\n")
            file.write(f"server-port={port}\n")
            file.write(f"motd=Server {name}\n")
            file.write(f"enable-query=false\n")
            file.write(f"enable-rcon=false\n")
            file.write(f"spawn-protection=0\n")
            file.write(f"online-mode=false\n")

        # Create operators file if needed
        if len(parameters.operator_names) > 0 and len(parameters.operator_uuids) > 0:
            with open(server_dir + "/ops.json", "w") as file:
                file.write("[\n")
                operator_count = min(len(parameters.operator_names), len(parameters.operator_uuids))
                for i in range(0, operator_count):
                    file.write("  {\n")
                    file.write(f"   \"uuid\": \"{parameters.operator_uuids[i]}\",\n")
                    file.write(f"   \"name\": \"{parameters.operator_names[i]}\",\n")
                    file.write("    \"level\": 4,\n")
                    file.write("    \"bypassesPlayerLimit\": false\n")
                    if i < operator_count - 1:
                        file.write("  },\n")
                    else:
                        file.write("  }\n")
                file.write("]")

        # Copy plugins
        copy_plugins(parameters.backend_plugins, parameters.backend_plugin_folders, f"{server_dir}/plugins")

        # Create start scripts
        create_start_scripts(server_dir, f"-Xms{parameters.backend_ram}M -Xmx{parameters.backend_ram}M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -jar ./{server_jar} --nogui")


def create_proxy_server(parameters):
    print(f"Creating {parameters.proxy_type} proxy server, {parameters.proxy_name}")

    # Create folder for the proxy
    server_dir = parameters.root_dir + parameters.proxy_name
    if os.path.exists(f"{server_dir}"):
        os.system(f"rm -rf {server_dir}")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    if parameters.proxy_type == "waterfall":
        # Create necessary subdirectories
        create_subdirectories(["plugins"], server_dir)

        # Download the latest paper for the version and place it in the server folder
        proxy_jar = "waterfall.jar"
        download_paper_build("waterfall", parameters.proxy_version,
                             get_latest_paper_build_number("waterfall", parameters.proxy_version),
                             f"{server_dir}/{proxy_jar}")

        # Create the config.yml
        with open(server_dir + "/config.yml", "w") as file:
            file.write(f"# Auto-generated config.yml for proxy server {parameters.proxy_name}\n")

            # Write proxy settings
            file.write(f"listeners:\n")
            file.write(f"- query_port: {parameters.proxy_port}\n")
            file.write(f"  motd: '{parameters.proxy_version} Proxy Server'\n")
            file.write(f"  query_enabled: false\n")
            file.write(f"  proxy_protocol: false\n")
            file.write(f"  priorities:\n")
            file.write(f"  - {parameters.backend_names[0]}\n")
            file.write(f"  bind_local_address: true\n")
            file.write(f"  host: {parameters.proxy_host}:{parameters.proxy_port}\n")
            file.write(f"ip_forward: true\n")
            file.write(f"online_mode: true\n")

            # Write servers
            file.write(f"servers:\n")
            for i in range(len(parameters.backend_names)):
                file.write(f"  {parameters.backend_names[i]}:\n")
                file.write(
                    f"    motd: '&eBackend {parameters.backend_type} {parameters.backend_names[i]} (port {parameters.backend_ports[i]})'\n")
                file.write(f"    address: localhost:{parameters.backend_ports[i]}\n")
                file.write(f"    restricted: false\n")

        # Copy plugins
        copy_plugins(parameters.proxy_plugins, parameters.proxy_plugin_folders, f"{server_dir}/plugins")

        # Create startup scripts
        create_start_scripts(server_dir, f"-Xms{parameters.proxy_ram}M -Xmx{parameters.proxy_ram}M -XX:+UseG1GC -XX:G1HeapRegionSize=4M -XX:+UnlockExperimentalVMOptions -XX:+ParallelRefProcEnabled -XX:+AlwaysPreTouch -jar ./{proxy_jar}")


# Fetches the latest build number for a paper project
def get_latest_paper_build_number(project, version_set):
    url = f"https://api.papermc.io/v2/projects/{project}/versions/{version_set}/builds"
    return requests.get(url).json()["builds"][-1]["build"]


# Downloads a paper build for a project to the target file
def download_paper_build(project, version_set, build_number, target_file):
    url = f"https://api.papermc.io/v2/projects/{project}/versions/{version_set}/builds/{build_number}/downloads/{project}-{version_set}-{build_number}.jar"
    requests.get(url, stream=True)

    with open(target_file, "wb") as file:
        for chunk in tqdm(requests.get(url, stream=True).iter_content(chunk_size=1024)):
            if chunk:
                file.write(chunk)
                file.flush()


# Creates subdirectories for a server
def create_subdirectories(sub_directories, parent_directory):
    for subdirectory in sub_directories:
        if not os.path.exists(parent_directory + "/" + subdirectory):
            os.makedirs(parent_directory + "/" + subdirectory)


# Create batch and powershell start scripts
def create_start_scripts(server_directory, start_arguments):
    with open(server_directory + "/start.bat", "w") as file:
        file.write("@echo off\n")
        file.write(
            f"java {start_arguments}\n")
        file.write("pause")

    with open(server_directory + "/start.ps1", "w") as file:
        file.write(f"Set-Location -Path {server_directory}\n")
        file.write(f"Start-Process java -ArgumentList '{start_arguments}'")


# Copies plugins and plugin folders from the source to the target
def copy_plugins(plugins, plugin_folders, plugins_folder):
    # Copy each file from the plugin list to the server/plugins folder
    for plugin in plugins:
        # Skip if the plugin does not exist
        if not os.path.exists(plugin):
            # If the plugin name contains a *, find the plugin with the same name before the *
            if "*" in plugin:
                # Get the parent directory of the plugin by getting everything before the last /
                parent_directory = plugin.rsplit("/", 1)[0]
                plugin_name = plugin.split("*")[0].split("/")[-1]
                if os.path.exists(parent_directory):
                    hit = False
                    for file in os.listdir(parent_directory):
                        if file.startswith(plugin_name):
                            shutil.copy(parent_directory + "/" + file, plugins_folder + "/" + file)
                            hit = True
                            break
                    if not hit:
                        print(f"Plugin jar file {plugin} could not be found, skipping copy")
                    continue
                else:
                    print(f"Plugin jar file {plugin} is in an invalid directory, skipping copy")
                    continue
            else:
                print(f"Plugin jar file {plugin} does not exist, skipping copy")
                continue

        shutil.copy(plugin, plugins_folder)

    # Copy each plugin data folder from the plugin list to the server/plugins folder
    for folder in plugin_folders:
        # Skip if the plugin does not exist
        if not os.path.exists(folder):
            print(f"Plugin data folder {folder} does not exist, skipping copy")
            continue
        # Copy the contents of the folder to a subdirectory of the server/plugins folder
        shutil.copytree(folder, plugins_folder + "/" + folder.split("/")[-1])


# Execute the main function
if __name__ == "__main__":
    main()
