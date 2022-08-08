# Creates a Minecraft server network using carcass, comprised of two backend servers and a frontend proxy on localhost:25565
Param(
    [string]$proxyHost = "localhost",
    [string]$proxyPort = 25565,
    [string]$backendPlugins = "",
    [string]$backendPluginFolders = "",
    [string]$proxyPlugins = "",
    [string]$proxyPluginFolders = "",
    [string]$networkDirectory = "./servers/"
)

python ./carcass.py -e true -o $networkDirectory -ph $proxyHost -pp $proxyPort -bp $backendPlugins -bpf $backendPluginFolders -pp $proxyPlugins -ppf $proxyPluginFolders