# Corr-CLI

A command-line interface to read articles from
[The Correspondent](https://www.thecorrespondent.com). This tool is not
affiliated with The Correspondent.

![](example.gif)

## Usage

1. `git clone git@github.com:stfwn/corr-cli.git && cd corr-cli`
2. `pip install -r --user requirements.txt`
3. Corr-CLI expects to find a config file with your login credentials for The
   Correspondent in an OS-standard location. This is typically:

    * Linux: `~/.config/corr-cli/config`
    * macOS: `~/Library/Preferences/corr-cli/config`
    * Windows: `C:\Users\<username>\AppData\Local\stfwn\corr-cli\config`

  If not there, the expected location will be printed on stderr.

  This is the format for the config file:

  ```
  [thecorrespondent.com]
  name=Bob
  email=your-email@provider.com
  password=pwnagepw123
  ```

  `name` should be your first name _exactly_ as it appears in the top right
  of your homepage after you first log in.

4. `python main.py`. The first run takes a while because it is caching all the
   articles locally.
5. Use `up`/`down` or `j`/`k` to navigate, `enter` to select, `l` to search and
   `escape` to return or exit.

### Options
```
optional arguments:
  -h, --help          show this help message and exit
  -o, --offline-mode  enable offline mode
  -c, --clear-cache   clear the articles cache and refetch
  -u, --update-only   update the cache and exit
```

## Backlog

- [x] Add some command line options.
- [ ] Have status messages on start-up.
- [ ] Add some commonly expected keybinds.
- [ ] Have a log in flow instead of having to create a config file manually.
