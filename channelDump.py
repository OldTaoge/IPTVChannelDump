import re
import urllib.request

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
    del channel, channel_, channel_s
    name = []
    nkvi = {}
    nkvcn = {}
    rub_name_keys = [
        "高清",
        "-",
        "测试"
    ]
    for key in list(channels.keys()):
        channel = channels[key]
        rub_name_bit = 0
        cle_n = channel["ChannelName"]
        for rub_name_key in rub_name_keys:
            if rub_name_key in cle_n:
                cle_n = cle_n.replace(rub_name_key, "")
                rub_name_bit += 1
        if cle_n not in name:
            name.append(cle_n)
            nkvi[cle_n] = key
        elif nkvcn.get(cle_n, 0) < rub_name_bit:
            channels.pop(nkvi[cle_n])
            nkvi[cle_n] = key
        else:
            channels.pop(key)
        nkvcn[cle_n] = rub_name_bit
        if rub_name_bit > 0:
            channel["ChannelName"] = cle_n
    del name, nkvi, nkvcn

    pis = ['北京', '湖南', '天津', '广东', '河北', '广西', '山西', '海南', '内蒙古', '重庆', '辽宁', '四川', '吉林', '贵州',
           '黑龙江', '云南', '上海', '西藏', '江苏', '陕西', '浙江', '甘肃', '安徽', '青海', '福建', '宁夏', '江西', '新疆',
           '山东', '台湾', '河南', '香港', '湖北', '澳门']

    sis = ['市南', '市北', '李沧', '崂山', '黄岛', '城阳', '即墨', '胶州', '平度', '莱西']

    for channel in channels.values():
        if "CCTV" in channel["ChannelName"] or "CGTN" in channel["ChannelName"] or "CETV" in channel[
            "ChannelName"] or "中国教育" in channel["ChannelName"]:
            channel["g"] = "中央台"
        if "山东" in channel["ChannelName"] or "齐鲁" in channel["ChannelName"]:
            channel["g"] = "山东台"
        for si in sis:
            if si in channel["ChannelName"]:
                channel["g"] = "青岛台"
        for pi in pis:
            if pi in channel["ChannelName"]:
                channel["g"] = "省台"

    epg = urllib.request.urlopen("http://epg.51zmt.top:8000/e.xml").read().decode('utf-8')

    cis = dict(re.findall("<channel id=\"(.*?)\"><display-name lang=\"zh\">(.*?)</display-name></channel>", epg))

    for channel in channels.values():
        for k, ci in cis.items():
            if channel["ChannelName"] in ci:
                channel["EpgId"] = k
                break

    with open("iptv.m3u8", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for channel in channels.values():
            cn = channel["ChannelName"]
            cu = "http://192.168.8.1:4022/udp/" + channel["ChannelURL"][7:]
            p = {
                "group-title": channel.get("g", "默认"),
                "tvg-id": channel.get("EpgId", None),
                "channel-id": channel["ChannelID"]
            }
            if p["tvg-id"] is not None:
                f.write("#EXTINF:-1 tvg-name=\"" + cn + "\" tvg-id=\"" + p["tvg-id"] + "\" group-title=\""
                        + p["group-title"] + "\" channel-id=\"" + p["channel-id"] + "\",")
            else:
                f.write("#EXTINF:-1 tvg-name=\"" + cn + "\" group-title=\"" + p["group-title"]
                        + "\" channel-id=\"" + p["channel-id"] + "\",")
            f.write("\n" + cu + "\n")
