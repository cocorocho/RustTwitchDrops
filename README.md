# Rust Twitch Drops


## Automatically farm Twitch drops for ~~Rust~~ 🔴 *Any Game* 🔴

- #### Twitch Drops Round 23 🏁
- #### Twitch Drops Round 17 🏁

## Requirements

- Latest version of Google Chrome
- Twitch account paired with Steam account
- **[IMPORTANT] Make sure that you have paired your Twitch and Steam accounts**

## To Use 🚀

### *[IMPORTANT] When changing streams, the browser will be the active window. Keep that in mind!*

1. Download the latest release from [releases](https://github.com/cocorocho/RustTwitchDrops/releases/tag/v1.0.0 "go to releases") or [download directly](https://github.com/cocorocho/RustTwitchDrops/releases/latest/download/RustTwitchDrops.zip)

2. Unzip ```Rust Twitch Drops.exe```

3. Open Chrome and login on Twitch

4.  Run the bot
	- Running the file through command prompt is ** *recommended* **
	or
	- Double click the file

5. Follow instructions

    Press `Enter` if you have successfully logged in on Chrome (Not automated browser)

    At this point cookies from your actual browser will be copied and used for collecting drops
    on automated browser.

6. This bot was initially made for Rust Twitch drops but can be used for any game now.

    - **Rust Twitch Drops**

        When there are drops for Rust, streamer list will be automatically loaded.

    - **Other games**
        
        If you want to use the bot to collect drops for other games, you will need to use `user_defined_streams.json` file which can be found in the directory.

        Open the file and add URLs for streams.

        Example:

            user_defined_streams.json

            [
                "https://twitch.tv/foo",
                "https://twitch.tv/bar"
            ]

7. Leave the rest to RustTwitchDrops

## FAQ
**Q: What does this do?**

A: This bot automatically farms Rust Twitch drops for you.

**Q: But how?**

A: It uses an automated browser (**chromedriver**) in this case and does what you do, but without you.

**Q: My bot crashed, what do i do?**

**A**: Crashes may happen, there will be a ```log.txt``` file inside the directory. You can share the error with me.

## Caveats
- Using your twitch account on other devices simultaneously may cause drops to not progress.
- Minimizing browser may cause drops to not progress. 
