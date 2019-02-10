# TelegramCompanion

> TelegramCompanion is simple userbot for Telegram to make your time spent on telegram more enjoyable. It runs in the background of your PC or server and gives you some new and usefull features

**Notice that this version is in BETA and some features are missing. Also there might be some small bugs there and there***

## Table of Contents

-   [Installation](#Installation)
-   [Setup](#Setup)
-   [Features](#Features)
-   [Plugins](#Plugins)
-   [Contributing](#Contributing)
-   [Support](#Support)
-   [License](#License)

## Installation

-   Install python3.7 and python3.7-dev. python3.6 and python3-dev works too:

```
sudo apt install python3.7 python3.7-dev
```

![Python Installation](/src/python.gif?raw=true)


-   Clone this repo by running:

```shell
git clone https://github.com/nitanmarcel/TelegramCompanion
```

-   Install all the requirements using pip3

```shell
pip3 install -r requirements.txt
```

![Requirements Installation](/src/requirements.gif?raw=true)

---

# Setup

#### Before starting the bot you have to configure it as per your requirements.
> -   Create a config.env file. Follow the example from sample.config.env.
> -   Write the next lines in the config
> -   You can always display the congiguration help with `python3 -m tg_companion --config`

#### The available config values are:

> -   `APP_ID` = (required) Your telegram app id from <https://my.telegram.org/apps>
>
> -   `APP_HASH` = (required) Your telegram app hash from <https://my.telegram.org/apps>
>
> -   `DB_URI` = (required) Your postgress database url. Leave empty to disable the modules that use it
>
> -   `SESSION_NAME` = (optional) Custom session name. Leave empty to use the default session name
>
> -   `STATS_TIMER` = (optional) Set the stats update time in seconds. Set it to 0 to completly disable stats.
>     - **WARNING** : If enabled the companion will not respond to your commands for 5 seconds when starting the bot for the first time
>
> -   `SUBPROCESS_ANIM` = (optional) (optional) Set to True if you want to enable animations when using a terminal command.
>     -   **WARNING** : When executing commands with long outputs it might trigger a flood wait that will restrict you from editing any send messages for a given time. Usualy just 250 seconds."
>
> -   `BLOCK_PM` = (optional) Set to True if you want to block new PMs. New PMs will be deleted and user blocked
>
> -   `NOPM_SPAM` = (optional) Set to True if you want to block users that are spamming your PMs.
>
> -   `PROXY_TYPE` = (optional) Your proxy type HTTP/SOCKS4/SOCKS5. Leave empty to disable proxy.
>
> -   `HOST` = (optional) The host of the used proxy.
>
> -   `PORT` = (optional) The port of the used proxy.
>
> -   `USERNAME` = (optional) The username of the used proxy. (If any)
>
> -   `PASSWORD` = (optional) The password of the used proxy. (If any)
>
> -   `ENABLE_SSH` = (optional) Set True if you want to execute or upload from a ssh server"
>
> -   `SSH_HOSTNAME` = (optional)  (optional) The hostname or address to connect to.
>
> -   `SSH_PORT` = (optional)  (optional) The port number to connect to.
>
> -   `SSH_USERNAME` = (optional)  (optional) Username to authenticate as on the server.
>
> -   `SSH_PASSWORD` = (optional)  (optional) The password to use for client password authentication
>
> -   `SSH_PASSPHRASE` = (optional)  (optional) The passphrase for your ssh connection.
>
> -   `SSH_KEY` = (optional)   (optional) The private key which will be used to authenticate this client"


---
# Features

> Tg_UserBot brings some small improvments to any Telegram Client
>
> You can some features using a command. Others are enabled from the config file and they work in background
>
> #### Available commands are:
>
> -   `.afk` `<optional-reason>` - Sets you as afk and tells everyone that you are away by sending them a message when they mention your username, sends you a PM or replies to your message. Send a message to any chat to dismiss your afk state
>
> -   `.ppic` - Reply to a photo/document to set it as your profile photo
>
> -   `.pbio` `<bio>` - Change your about message by sending `.pbio` followed by the bio you want to set.
>
> -   `.puname` `<username>` - Change your username by sending `.puname` followed by the username you want to set.
>
> -   `.pname` `<name>` - Change your name by sending `.pname` followed by the username you want to set. Use `\n` to separate your first and last name
>
> -   You can use `.cpic`, `.cpio`, `.cuname`, `.cname` to do the same for your chats
>
> -   `.ping` - Test your userbot response time
>
> -   `.stats` - Get your telegram stats. Works only if stats are not disabled from the config file
>
> -   `.info` `<optional-username>` - Send it as a message to get your info, reply to one or use the command followed by a username to get user info
>
> -   `.github` `<github-username>` - Get the info and repositories of any github user
>
> -   `.exec` `code` - Execute a python code in your local pc
> s
> -   `.term` `<command>` - Execute bash commands
>
> -   `.rterm` `<command>` - Execute bash commands on a ssh server
>
> -   `.upload` `<command>` - Upload files
>
> -   `.rupload` `<command>` - Upload files from a ssh server
>
> -   `$<language>` `<code>` - Execute code in any programming language using rextester.com api

-   Available languages are:
-   >
    > `ada`, `asm`, `bash`, `brainfuck`, `c`, `c#`, `c++`, `c_clang`, `c_gcc`, `clang`, `clang++`, `clangplusplus`, `clisp`, `common_lisp`, `cplusplus`, `cplusplus_clang`, `cplusplus_gcc`, `cpp`, `cpp_clang`, `cpp_gcc`, `csharp`, `d`, `elixir`, `erlang`, `f#`, `fortran`, `fpc`, `fsharp`, `g++`, `gcc`, `go`, `golang`, `haskell`, `java`, `javascript`, `js`, `kotlin`, `lisp`, `lua`, `msvc`, `mysql`, `nasm`, `node`, `objc`, `objective_c`, `ocaml`, `oracle`, `pas`, `pascal`, `perl`, `php`, `postgresql`, `prolog`, `py2`, `py3`, `python`, `python2`, `python3`, `r`, `ruby`, `scala`, `scheme`, `sql_server`, `swift`, `tcl`, `v8`, `vb`, `vb.net`, `vc++`, `visual_basic_dotnet`, `visual_c`, `visual_cplusplus`, `visual_cpp`

## Plugins

Plugins allow users to create their own plugins in a official [repo](https://github.com/nitanmarcel/TgCompanionPlugins) or on their own repo, so the user can install them using `python3 -m tg_companion --install` `<pluginname>` or `python3 -m tg_companion` `<githubusername>` `<reponame>` `pluginname`.

Check [TgCompanionPlugins](https://github.com/nitanmarcel/TgCompanionPlugins) repo for more informations.
## Contributing

Feel free to open an issue (or even better, send a **Pull Request**) for improving the bot's code. **Contributions** are very welcome !! :smiley:

Note that a PR needs to reach a certain level of engagement before it gets merged. This criteria is kept to maintain the quality of the bot. Also we won't accept any PR that uses a external api key to work. PR to [TgCompanionPlugins](https://github.com/nitanmarcel/TgCompanionPlugins) instead

## Support

You can ask for support or report a bug in our telegram [group](https://t.me/tgcompanion)


## Thanks
Thanks to everyone who helped me with ideas and with the project. Including @Yash-Garg for letting me host this project on his private repo, @baalajimaestro for the idea that gave birth to this userbot. (Alse check his [userbot](https://github.com/baalajimaestro/Telegram-UserBot)). And not last @sicrs for all the support he gave me.

## License

This code is licensed under [GPL v3](LICENSE).
