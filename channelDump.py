import re

if __name__ == "__main__":
    with open("iptv.stream", encoding="utf-8") as f:
        s_channels = re.findall("Authentication.CUSetConfig\('Channel['|\"],['|\"](.*?)['|\"]\);", f.read())
        channels = {}
        for s_channel in s_channels:
            channel_ = re.findall("(.*?)=['|\"](.*?)['|\"],*", s_channel)
            channel = {}
            for channel_s in channel_:
                channel[channel_s[0]] = channel_s[1]
            channels[channel["ChannelID"]] = channel
        print(channels)
