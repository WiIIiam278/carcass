import os
from tqdm import tqdm
import requests

root_dir = "./servers/"
proxy_version = "1.19"
minecraft_version = "1.19.2"
eula_agreement = "true"

backend_names = ["alpha", "beta"]
backend_ports = [25567, 25568]
backend_type = "paper"
backend_ram = 2048

proxy_name = "proxy"
proxy_host = "0.0.0.0"
proxy_port = 25565
proxy_type = "waterfall"
proxy_ram = 512


def main():
    # Create all backend servers
    for name, port in zip(backend_names, backend_ports):
        create_backend_server(name, backend_type, port)

    # Create the proxy server
    create_proxy_server(proxy_name, proxy_type, proxy_port, backend_names, backend_ports)


# Creates a backend server
def create_backend_server(name, server_type, port):
    print(f"Creating {server_type} backend server, {name}")

    # Create a folder for the server. If it exists, delete it.
    server_dir = root_dir + name
    if os.path.exists(f"{server_dir}"):
        os.system(f"rm -rf {server_dir}")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    if server_type == "paper":
        # Create necessary subdirectories
        sub_directories = ["config", "plugins"]
        for subdirectory in sub_directories:
            if not os.path.exists(server_dir + "/" + subdirectory):
                os.makedirs(server_dir + "/" + subdirectory)

        # Download the latest paper for the version and place it in the server folder
        builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{minecraft_version}/builds"
        latest_build = requests.get(builds_url).json()["builds"][-1]["build"]

        download_url = builds_url + f"/{latest_build}/downloads/paper-{minecraft_version}-{latest_build}.jar"
        requests.get(download_url, stream=True)

        with open(server_dir + "/paper.jar", "wb") as file:
            for chunk in tqdm(requests.get(download_url, stream=True).iter_content(chunk_size=1024)):
                if chunk:
                    file.write(chunk)
                    file.flush()
        print(f"Downloaded paper {minecraft_version} build {latest_build} for server {name}")

        # Create eula.text and set eula=true
        with open(server_dir + "/eula.txt", "w") as file:
            file.write(f"# Auto-generated eula.txt for server {name}\n")
            file.write(f"eula={eula_agreement}")

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
            file.write(f"# {server_type} server\n")
            file.write(f"server-port={port}\n")
            file.write(f"motd=Server {name}\n")
            file.write(f"enable-query=false\n")
            file.write(f"enable-rcon=false\n")
            file.write(f"spawn-protection=0\n")
            file.write(f"online-mode=false\n")


def create_proxy_server(name, server_type, port, backend_names, backend_ports):
    print(f"Creating {server_type} proxy server, {name}")

    # Create folder for the proxy
    server_dir = root_dir + name
    if os.path.exists(f"{server_dir}"):
        os.system(f"rm -rf {server_dir}")
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)

    if server_type == "waterfall":
        # Create necessary subdirectories
        sub_directories = ["plugins"]
        for subdirectory in sub_directories:
            if not os.path.exists(server_dir + "/" + subdirectory):
                os.makedirs(server_dir + "/" + subdirectory)

        # Download the latest paper for the version and place it in the server folder
        builds_url = f"https://api.papermc.io/v2/projects/waterfall/versions/{proxy_version}/builds"
        latest_build = requests.get(builds_url).json()["builds"][-1]["build"]

        download_url = builds_url + f"/{latest_build}/downloads/waterfall-{proxy_version}-{latest_build}.jar"
        requests.get(download_url, stream=True)

        with open(server_dir + "/waterfall.jar", "wb") as file:
            for chunk in tqdm(requests.get(download_url, stream=True).iter_content(chunk_size=1024)):
                if chunk:
                    file.write(chunk)
                    file.flush()
        print(f"Downloaded waterfall {minecraft_version} build {latest_build} for proxy server {name}")

        # Create the config.yml
        with open(server_dir + "/config.yml", "w") as file:
            file.write(f"# Auto-generated config.yml for proxy server {name}\n")

            # Write proxy settings
            file.write(f"listeners:\n")
            file.write(f"- query_port: {proxy_port}\n")
            file.write(f"  motd: '{proxy_version} Proxy Server'\n")
            file.write(f"  query_enabled: false\n")
            file.write(f"  proxy_protocol: false\n")
            file.write(f"  priorities:\n")
            file.write(f"  - {backend_names[0]}\n")
            file.write(f"  bind_local_address: true\n")
            file.write(f"  host: {proxy_host}:{proxy_port}\n")
            file.write(f"ip_forward: true\n")
            file.write(f"online_mode: true\n")

            # Write servers
            file.write(f"servers:\n")
            for i in range(len(backend_names)):
                file.write(f"  {backend_names[i]}:\n")
                file.write(f"    motd: '&eBackend {backend_type} {backend_names[i]} (port {backend_ports[i]})'\n")
                file.write(f"    address: localhost:{backend_ports[i]}\n")
                file.write(f"    restricted: false\n")

# Execute the main function
if __name__ == "__main__":
    main()
