import os
import requests
import urllib.parse

def generate_new_m3u(m3u_path):
    target_m3u = open(m3u_path, "w")
    target_m3u.write('#EXTM3U - Generated by Home Broadcaster\n')
    target_m3u.close()


def generate_m3u_if_not_exists(m3u_path):
    if not os.path.exists(m3u_path):
        generate_new_m3u(m3u_path)


def remove_channel(channel, m3u_dir):
    target_m3u_path = m3u_dir + 'tv.m3u'
    with open(target_m3u_path, "r") as f:
        lines = f.readlines()
    with open(target_m3u_path, "w") as f:
        for line in lines:
            if not (str("tvg-ID=" + channel + ".tv") in line) and not (str("/" + channel + ".m3u8") in line):
                f.write(line)


def add_channel(channel, port, auth, m3u_dir):
    add_channel_with_logo(channel, None, port, auth, m3u_dir)


def add_channel_with_logo(channel, logo_file_name, port, auth, m3u_dir):
    target_m3u_path = m3u_dir
    if not target_m3u_path.endswith('/'):
        target_m3u_path = target_m3u_path + '/'
    target_m3u_path = target_m3u_path + 'tv.m3u'
    generate_m3u_if_not_exists(target_m3u_path)

    with open(target_m3u_path) as f:
        if 'tvg-name=' + channel in f.read():
            # Channel already exists so leave m3u as is
            return
    target_m3u = open(target_m3u_path, "a")

    host_ip = requests.get('https://api.ipify.org').text

    if not (logo_file_name is None):
        logo_file_addr = "http://" + host_ip + "/tv/logos/" + logo_file_name
        target_m3u.write(
            '\n#EXTINF:-1 tvg-ID=' + channel + '.tv' + ' tvg-name=' + channel + ' tvg-logo=' + logo_file_addr + ' group-title=,' + channel)
    else:
        target_m3u.write('\n#EXTINF:-1 tvg-ID=' + channel + '.tv' + ' tvg-name=' + channel + ' group-title=,' + channel)

    if not (auth is None):
        user = urllib.parse.quote(auth['username'])
        password = urllib.parse.quote(auth['password'])
        if not (port is None):
            target_m3u.write('\nhttp://' + user + ':' + password + '@' + host_ip + ':' + port + '/tv/' + channel + '.m3u8')
        else:
            target_m3u.write('\nhttp://' + user + ':' + password + '@' + host_ip + '/tv/' + channel + '.m3u8')
    else:
        if not (port is None):
            target_m3u.write('\nhttp://' + host_ip + ':' + port + '/tv/' + channel + '.m3u8')
        else:
            target_m3u.write('\nhttp://' + host_ip + '/tv/' + channel + '.m3u8')
    target_m3u.close()
